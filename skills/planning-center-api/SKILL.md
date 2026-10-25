---
name: planning-center-api
description: Complete, agent-parsable reference for the Planning Center Online (PCO) REST API — all eleven products (People, Services, Groups, Check-Ins, Giving, Calendar, Registrations, Publishing, Webhooks, API, Current), every resource's attributes, relationships, includes, filters, create/update payloads and custom actions, plus auth (PAT/OAuth/PKCE/OIDC), JSON:API querying, pagination, rate limits, versioning, errors, file uploads and webhooks. Use this whenever a task touches Planning Center, PCO, planningcenteronline.com, Church Center data, or any PCO product by name (People/Services/Groups/Check-Ins/Giving/Calendar/Registrations/Publishing) — building integrations, n8n/Zapier-style workflows, syncs, reports, OAuth sign-in with a Planning Center account, webhook handlers, or answering "how do I get X out of Planning Center" — even if the user doesn't say "API". Read the per-product reference file before writing any endpoint, attribute, or payload.
---

# Planning Center API

Planning Center's own docs split each resource across a dozen tables and hide the parts that matter (which parent path to POST to, which attributes are assignable, what `filter=` accepts). This skill is a flattened, verified rewrite so you never guess an endpoint or field name. Everything below was extracted from https://api.planningcenteronline.com/docs on 2026-10-24.

## How to use this skill

1. Read the cross-cutting rules below (two minutes). They apply to every product.
2. Open `references/<product>.md` for the product you are touching and find the resource section. Each section is self-contained: endpoints, attributes with types/enums, relationships, `include` values, `order`/`where` fields, child associations with their `filter=` values, every parent path that reaches the resource, and the exact assignable attributes for create/update plus custom actions. Do not invent attributes or paths that are not listed.
3. For anything spanning products (the same person in Services and Giving, Calendar ↔ Registrations links, name collisions like "Event"), read `references/cross-product.md`. It also has copy-ready recipes.
4. For auth flows, error hints, dates, uploads and versioning in full detail, read `references/guides.md`. For webhook delivery/retry/signature rules, `references/webhooks.md`.
5. When calling the API from Python, use `scripts/pco_client.py` (PAT or OAuth, pagination, rate-limit backoff, JSON:API envelopes, file upload). It also works as a CLI for quick exploration.
6. When unsure what an endpoint supports at runtime, make one GET and read `meta`: `can_include`, `can_order_by`, `can_query_by`, `can_filter`, `total_count`. The API describes itself; trust `meta` over memory.

## Product map

| Product | Base path | Scope | Version documented | Resources | Reference | API writes? |
|---|---|---|---|---|---|---|
| People | `/people/v2` | `people` | 2026-10-05 | 67 | `references/people.md` | yes — people, contact info, households, custom fields, forms submissions, workflows, notes, lists (run/share) |
| Services | `/services/v2` | `services` | 2018-11-01 | 65 | `references/services.md` | yes — service types, plans, items, times, scheduling, songs, arrangements, keys, media, attachments, blockouts |
| Groups | `/groups/v2` | `groups` | 2023-07-10 | 17 | `references/groups.md` | partial — memberships, group update/actions, application approve/reject |
| Check-Ins | `/check-ins/v2` | `check_ins` | 2025-05-28 | 24 | `references/check-ins.md` | **read-only** |
| Giving | `/giving/v2` | `giving` | 2019-10-18 | 20 | `references/giving.md` | yes — batches, offline donations, refunds, funds, labels, pledges, in-kind, payment sources |
| Calendar | `/calendar/v2` | `calendar` | 2026-10-19 (beta; stable 2026-06-22) | 25 | `references/calendar.md` | partial — resources, folders, questions, tags, tag groups, report templates, event connections; events are read-only |
| Registrations | `/registrations/v2` | `registrations` | 2025-05-01 | 11 | `references/registrations.md` | **read-only** |
| Publishing | `/publishing/v2` | `publishing` | 2024-03-25 | 17 | `references/publishing.md` | yes — channels, episodes, times, resources, series, note templates |
| Webhooks | `/webhooks/v2` | none | 2022-10-20 | 5 | `references/webhooks.md` | yes — subscriptions, redeliver/ignore |
| API | `/api/v2` | `api` | 2026-09-24 | 7 | `references/api-and-current.md` | revoke PATs |
| Current | `/current/v2` | none | 2018-08-01 | 2 | `references/api-and-current.md` | read-only (`/me`) |

Base URL for everything: `https://api.planningcenteronline.com`. File uploads go to `https://upload.planningcenteronline.com/v2/files`. OAuth endpoints are `/oauth/authorize`, `/oauth/token`, `/oauth/revoke`, `/oauth/introspect`, `/oauth/userinfo`.

## Cross-cutting rules (condensed)

**Identity.** Every request runs as a user and inherits that user's permissions in each product. A `403` on a resource you can see in the UI usually means the token's user lacks the role, not that the endpoint is wrong. `GET /current/v2/me` identifies the caller with no scope. A person's `id` is identical across all products.

**Auth.** Single-church scripts: Personal Access Token via HTTP Basic (`-u app_id:secret`). Multi-church products: one OAuth 2.0 app in a dedicated free org; `Authorization: Bearer <token>`; access tokens live 2 h, refresh tokens 90 days; PKCE recommended/required for public clients; add `openid` scope for OIDC `id_token` + `/oauth/userinfo`. Always send a descriptive `User-Agent` (missing one can 403). Scopes are per product and space-separated.

**Versioning.** Each product versions independently. Send `X-PCO-API-Version: YYYY-MM-DD` to pin the version this skill documents (header overrides the app default; matching is "equal or earlier"). `LATEST` is for experiments only. The doc site shows the newest version, which can be newer than your app's default — if an attribute in these references is missing from a response, check the version first.

**JSON:API envelope.** Reads return `{data, included, links, meta}`. Writes send `{"data":{"type":"Person","attributes":{…},"relationships":{"team":{"data":{"type":"Team","id":"1"}}}}}`. Attributes never go top-level. Ids are strings in JSON. Relationship ids can often also be set via `<name>_id` attributes (listed per resource). Some creates accept nested `included` resources (Giving designations, People form submission values, People person with emails/phones).

**Querying.**
- `where[attr]=value` exact (case-insensitive); `where[attr]=Tim%25` prefix/suffix wildcard (`%` must be URL-encoded; not every attribute supports it); `where[attr][gt|gte|lt|lte]=value` ranges; `where[assoc][attr]=value` on included resources.
- `filter=name` enables the endpoint's named filters (comma-separated for several). These are listed as `[filter: …]` per association in the references.
- `include=a,b` and nested `include=households.people` (max two levels). `order=attr` or `-attr`.
- `fields[Type]=a,b` selects attributes and unlocks the ones marked "only with ?fields".
- `per_page` 1–100 (default 25), `offset`; follow `links.next`. `meta.total_count` is the full count. Offsets above 30,000 get a lower rate limit — prefer `where[updated_at][gte]` windows over deep paging.
- Date-only values on `date_time` attributes are interpreted in the organization's time zone and expanded to the whole day; pass full timestamps to be explicit. Responses are always UTC.

**Rate limits.** 100 requests / 20 s per user by default (75 when offset > 30,000); never hard-code. Read `X-PCO-API-Request-Rate-Limit`, `-Count`, `-Period`; on `429` wait `Retry-After` seconds. Only auto-retry idempotent requests.

**Errors.** 400 malformed, 401 bad credentials, 403 permission/scope/User-Agent, 404 bad id or hidden, 409 duplicate create race, 422 validation (body names each invalid attribute), 429 rate limit, 500/503 retry later. Auth error hints are animal names (PELICAN = missing scope, BABOON = expired token, CAPUCHIN = revoked, TRASH_PANDA = no access to that app, CHINCHILLA = unknown client) — full table in `references/guides.md`.

**Files.** `POST multipart/form-data file=@…` to `https://upload.planningcenteronline.com/v2/files` → `data[0].id` (UUID, expires) → set it as the string value of a file attribute (`Person.avatar`, Services `Attachment.file_upload_identifier`, Publishing `art`/`sermon_audio`).

**Paths.** Many resources are reachable from several parents (`Reachable from` in the references). Collection-level paths like `/people/v2/emails` list across the org; nested paths like `/people/v2/people/{id}/emails` scope to a parent and are usually where you POST. Member operations (`PATCH`/`DELETE`) work on any valid path to the record; the Services docs render odd canonical paths (e.g. `/songs/{id}/last_scheduled_item/...`) — use the natural parent path instead.

**Asynchronous operations.** Giving batch/batch-group commit and delete, Groups `duplicate`, Services plan `import` with `additional_target_ids` return immediately with an `updating`/job status; poll the record (or the returned status URL) before depending on the result.

**Read-only products.** Check-Ins and Registrations expose no create/update/delete. Calendar events/instances/bookings, Groups groups/events/group types, Publishing announcements, and all `Person` records outside People are read-only. Don't plan writes there; plan them in the source product or the UI.

## Quick resource index (where things live)

- Person, Email, PhoneNumber, Address, Household, HouseholdMembership, FieldDefinition/FieldDatum (custom fields), Tab, Form/FormSubmission, List/ListResult/Rule, Workflow/WorkflowCard/WorkflowStep, Note/NoteCategory, Campus, ServiceTime, MaritalStatus, MembershipType, BackgroundCheck, Message → `references/people.md`
- ServiceType, Plan, PlanTime, Item, ItemNote, PlanNote, Team, TeamPosition, PersonTeamPositionAssignment, PlanPerson (schedule assignment), Schedule (accept/decline), NeededPosition, Song, Arrangement, Key, Media, Attachment, Blockout, Folder, Series, Tag → `references/services.md`
- Group, GroupType, Membership, GroupApplication, Enrollment, Event (meeting), Attendance, RSVP, Resource (file/link), Tag → `references/groups.md`
- CheckIn, Event, EventPeriod, EventTime, Location, Station, Headcount, AttendanceType, Pass, Label, PersonEvent → `references/check-ins.md`
- Donation, Designation, Batch, BatchGroup, Fund, Refund, RecurringDonation, Pledge, PledgeCampaign, InKindDonation, PaymentMethod, PaymentSource, DonorSummary, Label → `references/giving.md`
- Event, EventInstance, EventTime, Resource (room/equipment), ResourceBooking, EventResourceRequest, Conflict, Calendar, Tag, TagGroup, Feed, RoomSetup → `references/calendar.md`
- Signup, Attendee, Registration, SelectionType, SignupTime, SignupLocation, Category → `references/registrations.md`
- Channel, Episode, EpisodeTime, EpisodeResource, Series, Speaker, Speakership, NoteTemplate, Announcement → `references/publishing.md`
- WebhookSubscription, AvailableEvent, Event (webhook), Delivery → `references/webhooks.md`
- OauthApplication, ConnectedApplication, PersonalAccessToken, `/current/v2/me` → `references/api-and-current.md`

## Working pattern for an agent

1. Confirm auth: `GET /current/v2/me?include=organization`. Note the person id and organization id/name/subdomain.
2. Confirm scope and permissions for the product: `GET /<product>/v2/me` (403 with PELICAN = scope missing; TRASH_PANDA = user has no access to that product).
3. Pin the version with `X-PCO-API-Version` matching the reference file.
4. Discover before writing: `GET` the collection with `per_page=1` and inspect `meta.can_query_by`, `meta.can_include`, `meta.can_filter`, `meta.can_order_by`; compare to the reference section.
5. Search before creating (People `where[search_name_or_email]`; Services `where[title]`; Giving `where[default]=true` for the fund) to avoid duplicates — there is no upsert.
6. Write with the exact assignable attributes listed; relationships as JSON:API linkage; check the 422 body for field-level errors.
7. For bulk reads, page with `per_page=100` and `where[updated_at][gte]=` windows; for change feeds, use webhooks (`references/webhooks.md`).
8. Report results with resource ids and `links.html` URLs so a human can open them in Planning Center.

## Gotchas worth knowing

- `Person.status` write: send `"inactive"` to deactivate, anything else reactivates; `inactivated_at` works the same with a timestamp/null.
- People `search_name_or_email_or_phone_number` is the broadest person search; `search_phone_number_e164` for normalized phones.
- Custom field checkbox values: POST one FieldDatum per checked option with the option *string* as `value`; uncheck by DELETE.
- Form submissions via API: option-field values must be the FormFieldOption **id**, not its label; the token user needs People Editor + form manage rights.
- Services `Plan` has no date attributes — dates come from `PlanTime` records; `sort_date` is derived. `Plan.items` are reordered with the `item_reorder` action, not by PATCHing `sequence`.
- Services `PlanPerson.status` accepts `C`/`U`/`D` or `Confirmed`/`Unconfirmed`/`Declined`; set `prepare_notification: true` to queue the scheduling email.
- Services `assign_tags` actions **replace** the whole tag set — send every tag you want to keep.
- Giving money is integer cents; fees are 0 or negative; online (Stripe) and recurring donations are read-only; API-created donations must live in a Batch; `?with_totals=true` adds totals to `meta`.
- Giving `Batch.commit` and Groups `duplicate` are asynchronous — poll.
- Check-Ins paths use a hyphen (`/check-ins/v2`) but the scope uses an underscore (`check_ins`).
- Calendar `EventInstance` is the per-occurrence record you want for "what's happening on date X"; `Event` is the series/container. Status filters (`approved`, `pending`, …) are `filter=` values, not attributes.
- Groups `Membership` is the writable join (role member/leader); `GroupApplication` approve/reject handles join requests; `Enrollment` is read-only status.
- Webhook `payload` is a JSON **string** inside JSON — parse twice. Verify `X-PCO-Webhooks-Authenticity` (HMAC-SHA256 of raw body with `authenticity_secret`). Respond 200 fast; 410 unsubscribes.
- The Calendar docs default to a beta version (2026-10-19); pin `2026-06-22` for stable behavior.
- `Organization` resources in each product list every top-level collection and its filters — a fast way to see what a product exposes.
