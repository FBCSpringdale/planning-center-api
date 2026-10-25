# Webhooks (guide + webhooks/v2 API)

Base URL: `https://api.planningcenteronline.com/webhooks/v2`
Documented version: `2022-10-20` (also 2018-08-01). **No OAuth scope required** for the Webhooks endpoints.
2022-10-20 change: `Subscription` replaced by `WebhookSubscription`.
OpenAPI: `https://api.planningcenteronline.com/webhooks/v2/open_api/2022-10-20`
Docs: `https://api.planningcenteronline.com/docs/apps/webhooks/versions/2022-10-20/vertices/<snake_case_resource>` and `https://api.planningcenteronline.com/docs/overview/webhooks`
UI: `https://api.planningcenteronline.com/webhooks` (create subscriptions, inspect requests/responses, redeliver manually).

## How webhooks behave (from the guide)

- Any user who can log in can create and manage subscriptions. Subscriptions are created under a specific user and only deliver data that user can see.
- Deliveries are HTTP POST only. Respond with 200 to acknowledge. Responding **410 Gone** deactivates the subscription.
- Each delivery carries a unique id, a type/name, and an attempt number (use for idempotency and logging).
- No rate limits on webhook deliveries.
- Retry schedule on non-200: up to 16 retries after the first failure at 30s, 1m, 2m, 4m, 8m, 16m, 32m, 64m, 2.1h, 4.2h, 8.5h, 17h, then once per day for up to 4 days. After 16 consecutive failures the subscription is deactivated (about 5.4 days). Emails go out after 1 hour of failures and again on the final try (only for subscriptions the user created themselves, not ones created by an OAuth app on their behalf). A very high failure rate for one endpoint within 24 hours also deactivates it.
- `Retry-After` on your 429/503 is honored (seconds or HTTP-date), capped at 1 hour; the normal backoff wins if longer. The attempt still counts as a failure.
- Authenticity: header `X-PCO-Webhooks-Authenticity` = hex HMAC-SHA256 over the raw request body, keyed with the subscription's `authenticity_secret`. Verify before trusting a payload.

```python
import hmac, hashlib
def verify(raw_body: bytes, secret: str, header: str) -> bool:
    digest = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, header)
```

## Delivery payload shape

```json
{"data":[{"id":"<delivery uuid>","type":"EventDelivery",
  "attributes":{"name":"people.v2.events.person.updated","attempt":1,
    "payload":"<JSON string: the resource as the API would return it, with data/included/meta>"},
  "relationships":{"organization":{"data":{"type":"Organization","id":"127"}}}}]}
```
`attributes.payload` is a **string** containing JSON (double-encoded): parse it to get `{data: {type, id, attributes, relationships, links}, included, meta}`. `meta.parent` identifies the parent resource (e.g. `{"id":"127","type":"Organization"}`).

## Event names

Pattern: `<app>.v2.events.<resource>.<action>`, e.g. `people.v2.events.person.created`, `people.v2.events.person.updated`, `people.v2.events.person.destroyed`, `services.v2.events.plan.created`, `giving.v2.events.donation.created`, `check-ins.v2.events.check_in.created`, `groups.v2.events.membership.created`, `calendar.v2.events.event.created`. The authoritative list for the organization is `GET /webhooks/v2/available_events` — query it rather than guessing; not every resource emits every action.

## Resource index (5)

AvailableEvent, Delivery, Event, Organization, WebhookSubscription

```
Organization ── webhook_subscriptions (WebhookSubscription) ── events (Event) ── deliveries (Delivery)
             └─ available_events (AvailableEvent)
```

## AvailableEvent
An event type webhooks support (read-only).
Endpoints: GET /available_events; …/{id}
Attributes: action (string); app (string); id; name (string, the full event name); resource (string); type (string); version (string)

## Delivery
One HTTP delivery attempt of an event (read-only).
Endpoints: GET /webhook_subscriptions/{ws}/events/{event_id}/deliveries; …/{id}
Attributes: created_at; id; object_url; request_body; request_headers; response_body; response_headers; status (integer HTTP status); timing (float); updated_at
Relationships: event -> Event. Order: created_at

## Event
A single webhook event belonging to a subscription.
Endpoints: GET /webhook_subscriptions/{ws}/events; …/{id}
Attributes: created_at; id; payload (JSON string); status (pending | delivered | failed | skipped | duplicated | ignored_failed | ignored_skipped | ignored_duplicated); updated_at; uuid
Relationships: subscription; person. Include: none
Order: created_at. Where: status, uuid
Associations: deliveries -> Delivery
Actions: ignore POST …/events/{id}/ignore; redeliver POST …/events/{id}/redeliver (no payload)

## Organization
Endpoints: GET /webhooks/v2. Attributes: id
Associations: available_events; webhook_subscriptions

## WebhookSubscription
Endpoints: GET /webhook_subscriptions; …/{id}; POST /webhook_subscriptions; PATCH /webhook_subscriptions/{id}; DELETE /webhook_subscriptions/{id}
Attributes: active (boolean); application_id (string); authenticity_secret (string — HMAC key); created_at; id; name (string — the event name, e.g. `people.v2.events.person.created`); updated_at; url (string — your HTTPS endpoint)
Where: application_id
Associations: events -> Event
Actions: rotate_secret POST /webhook_subscriptions/{id}/rotate_secret (no payload; returns the subscription with a new authenticity_secret)
Create: POST /webhook_subscriptions — `{"data":{"type":"WebhookSubscription","attributes":{"name":"people.v2.events.person.updated","url":"https://example.com/hooks/pco","active":true}}}`
Update: PATCH /webhook_subscriptions/{id} — attrs: active
Delete: DELETE /webhook_subscriptions/{id}
Note: one subscription = one event name. Subscribe to several events with several POSTs.
