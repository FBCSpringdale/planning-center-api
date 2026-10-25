# API product (api/v2) and Current API (current/v2)

Two small administrative APIs.

## API product — api/v2

Base URL: `https://api.planningcenteronline.com/api/v2`
Documented version: `2026-09-24` (history: 2025-09-30, 2019-02-13, 2018-08-01). OAuth scope: `api`.
2026-09-24 change: administrator visibility and revocation of personal access tokens.
OpenAPI: `https://api.planningcenteronline.com/api/v2/open_api/2026-09-24`

Purpose: introspect the organization's developer footprint — which OAuth apps are connected, their monthly active users, and personal access tokens.

```
Organization ── connected_applications (ConnectedApplication) ── people (ConnectedApplicationPerson)
             ├─ oauth_applications (OauthApplication) ── mau (OauthApplicationMau)
             └─ personal_access_tokens (PersonalAccessToken) ── person (Person)
```

### ConnectedApplication
Third-party OAuth apps users of this organization have authorized (read-only).
Endpoints: GET /connected_applications; …/{id}
Attributes: description; id; name; url
Associations: people -> ConnectedApplicationPerson

### ConnectedApplicationPerson
A person who connected an application.
Endpoints: GET /connected_applications/{ca}/people; …/{id}
Attributes: avatar_url; connected_at; first_name; id; last_name; scopes (array); site_administrator (boolean)
Where: site_administrator (boolean)

### OauthApplication
OAuth applications owned by this organization (read-only).
Endpoints: GET /oauth_applications; …/{id}
Attributes: description; id; name; url
Associations: mau -> OauthApplicationMau

### OauthApplicationMau
Monthly active users (any person issued a token that month). 24 months of history; nothing before mid-Feb 2019.
Endpoints: GET /oauth_applications/{oa}/mau; …/{id}
Attributes: count (integer); id; month (integer); year (integer)
Relationships: oauth_application

### Organization
Endpoints: GET /api/v2. Attributes: id
Associations: connected_applications; oauth_applications; personal_access_tokens [filter: accessible — not revoked]

### Person
Owner of a personal access token (read-only).
Endpoints: GET /personal_access_tokens/{pat}/person
Attributes: avatar_url; first_name; id; last_name

### PersonalAccessToken
Endpoints: GET /personal_access_tokens [filter: accessible]; …/{id}
Attributes: created_at; id; last_used_on (date, null if never used); name; revoked_at (null while usable)
Relationships: person -> Person. Include: person
Order: created_at, last_used_on, name, person, revoked_at
Associations: person -> Person
Actions: revoke POST /personal_access_tokens/{id}/revoke (no payload; organization administrators or the token's owner)

## Current API — current/v2

Base URL: `https://api.planningcenteronline.com/current/v2`
Version: `2018-08-01` (only version). **No OAuth scope required**; no permission rules are applied.
OpenAPI: `https://api.planningcenteronline.com/current/v2/open_api/2018-08-01`

Purpose: identify the authenticated user and organization without needing any product scope. `GET /current/v2/me` works for every OAuth app and PAT.

### Organization
Endpoints: GET /current/v2/people/{person_id}/organization; include `organization` on `/me`
Attributes: id; name; subdomain
Associations: people -> Person

### Person
Endpoints: GET /current/v2/me; GET /current/v2/people; …/{id}
Attributes: email; first_name; id; last_name
Include: organization
Associations: organization -> Organization

Example: `GET /current/v2/me?include=organization` → the caller's id/name/email plus `included[0]` = their Organization (id, name, subdomain). The person `id` is the same id used across all products.
