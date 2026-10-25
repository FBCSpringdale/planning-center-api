# Planning Center API — Cross-cutting guides (full detail)

Source: https://api.planningcenteronline.com/docs/overview/* (Getting Started, Authentication, Rate Limiting, JSON-API, Dates & Times, File Uploads, Libraries, Errors, Versioning, Webhooks, Add-ons). This file holds the complete rules; SKILL.md holds the condensed version.

## 1. Accounts and permissions

- Every request is made on behalf of a user; the integration acts with that user's permission levels in each product. When a user's access changes, the API access changes with it.
- Single church, your own account: use a **Personal Access Token** (PAT) on a user in that organization.
- Product/service for many churches: create a separate free Planning Center organization for your company (https://accounts.planningcenteronline.com), create **one** OAuth application there, and reuse it for every church. Since March 22, 2023 only Organization Administrators can create OAuth applications, and all Organization Administrators manage them.
- Developer account (apps, PATs, webhooks, API Explorer): https://api.planningcenteronline.com/oauth/applications
- Breaking changes are announced on the API News mailing list (http://eepurl.com/jempmE). Bug reports: https://github.com/planningcenter/developers/

## 2. Authentication

### Personal Access Token
HTTP Basic auth with `client_id` as username and `secret` as password on every request. Server-side only; never from a browser; never share; may not be used across multiple churches.
```
curl -u CLIENT_ID:SECRET https://api.planningcenteronline.com/people/v2/people
```
Create at https://api.planningcenteronline.com/personal_access_tokens. Tokens found publicly are disabled automatically.

### OAuth 2.0 (authorization code)
Authorization URL: `https://api.planningcenteronline.com/oauth/authorize`
Token URL: `https://api.planningcenteronline.com/oauth/token`
1. Redirect: `https://api.planningcenteronline.com/oauth/authorize?client_id=CLIENT_ID&redirect_uri=https://example.com/auth/complete&response_type=code&scope=people` (scope = space-separated list).
2. Planning Center redirects back with `?code=`.
3. `POST https://api.planningcenteronline.com/oauth/token` with `grant_type=authorization_code`, `code`, `client_id`, `client_secret`, `redirect_uri` (form fields or JSON).
4. Response: `{"access_token","token_type":"bearer","expires_in":7200,"refresh_token","scope","created_at"}`.
5. Use `Authorization: Bearer ACCESS_TOKEN`.
- Access tokens expire after **2 hours**. Refresh tokens are honored for **90 days** after the associated access token was issued; if your app doesn't refresh for 90 days the user must re-authorize.
- Refresh: `POST /oauth/token` JSON `{"client_id","client_secret","refresh_token","grant_type":"refresh_token"}` → new access_token + new refresh_token (store the new refresh token).
- Revoke: `POST /oauth/revoke` form `token`, `token_type_hint=access_token|refresh_token`, `client_id`, `client_secret` → 200 with empty JSON even if already revoked. Revoking a refresh token also invalidates its access token.
- Introspect: `POST /oauth/introspect` form `token`, `client_id`, `client_secret` → `{"active":true,"scope","client_id","token_type":"Bearer","exp","iat"}` or `{"active":false}`.

### Scopes
| Product | Scope |
|---|---|
| API | `api` |
| Calendar | `calendar` |
| Check-Ins | `check_ins` |
| Giving | `giving` |
| Groups | `groups` |
| Home | `home` |
| People | `people` |
| Publishing | `publishing` |
| Registrations | `registrations` |
| Services | `services` |
Webhooks endpoints require no scope. `openid` is an additional scope for OIDC.

### Current user
`GET /<product>/v2/me` requires that product's scope and applies that product's permissions. `GET /current/v2/me` works for every OAuth app with no scope and no permission rules.

### PKCE
Supported for confidential and public apps; recommended for confidential, required for public apps. Generate `code_verifier` (43–128 unreserved chars), derive `code_challenge` = BASE64URL(SHA256(verifier)), add `code_challenge` and `code_challenge_method=S256` to the authorize URL, then send `code_verifier` with the token request. Recommended setup: confidential app + server-side token exchange + PKCE.

### OpenID Connect
Add scope `openid` (can combine with product scopes). Token response also carries `id_token` (JWT, expires after 1 hour) with claims: iss, sub (person id), aud, name, email, organization_id, organization_name, nonce, exp, iat. Discovery: `https://api.planningcenteronline.com/.well-known/openid-configuration`. Recommended extra params: `state` (CSRF), `prompt=select_account` (or `login`), `nonce`. Userinfo: `GET /oauth/userinfo` with the bearer token → `{sub,name,email,organization_id,organization_name}`. Sample apps: Flask+Python, Sinatra+Ruby (incl. client-side PKCE demo), Slim+PHP under github.com/planningcenter.

### User-Agent
Required on all requests. Use something identifying, e.g. `My Planning Center App (https://pcapp.example.com/contact)` or `PCO Demo (me@pcodemo.example.com)`. Missing/poor User-Agent can return `403 Forbidden`.

## 3. Rate limiting

- Default **100 requests per 20 seconds per authenticated user**. Requests with `offset` > 30,000 are limited to **75 per 20 seconds**. Endpoints can have their own limits; limits can change without notice — never hard-code them.
- Headers on every response: `X-PCO-API-Request-Rate-Limit` (max in period), `X-PCO-API-Request-Rate-Period` (e.g. `20 seconds`), `X-PCO-API-Request-Rate-Count` (used so far), and on 429 `Retry-After` (seconds).
- 429 body: `{"errors":[{"code":"429","detail":"Rate limit exceeded: 118 of 100 requests per 20 seconds"}]}`.
- Client pattern: read the headers; on 429 sleep `Retry-After` (default 1s) and retry (idempotent requests only — don't blindly replay POSTs); proactively slow down when count ≥ 80% of limit; cap retries (e.g. 5).

## 4. JSON:API format

- Conforms to JSON:API 1.0. Collections: `{"data":[{type,id,attributes,relationships,links}, …], "included":[…], "links":{…}, "meta":{…}}`. Single: `{"data":{…}}`.
- Writes use the same envelope: `{"data":{"type":"Person","attributes":{…},"relationships":{…}}}`. `type` may usually be omitted; attributes go under `attributes`, never top-level.
- `meta.total_count` and `meta.count` are returned on collections; `meta.can_include`, `meta.can_order_by`, `meta.can_query_by`, `meta.can_filter`, `meta.parent` describe what the endpoint supports — a live self-description you can read when unsure.
- `links.self`, `links.next`, `links.prev` on collections; resource `links` include `self`, `html` (web UI URL) and one URL per association.

### Filtering
- `where[attr]=value` — case-insensitive equality. `where[attr]=Tim%25` (URL-encoded `%` at start/end) does prefix/suffix matching (not on every attribute).
- Operators for dates/numbers: `where[attr][gt|gte|lt|lte]=value`; combine for ranges.
- Filter on included resources: `?include=emails&where[emails][address]=tim@example.com`.
- Which attributes are queryable: the **Query By / Where** list per resource (reference files) or `meta.can_query_by`.
- `filter=name` enables an endpoint's named filters (e.g. `/people/v2/people/13/messages?filter=received`); listed per association as "Filter By" in the reference files; multiple filters comma-separated.
- `search_*` pseudo-attributes (e.g. People `where[search_name_or_email]=`) are the full-text search entry points.
- `fields[Type]=a,b` (sparse fieldsets) also unlocks attributes marked "only with ?fields" (e.g. `fields[Person]=mfa_configured`).

### Includes
- `include=emails,phone_numbers` returns related resources in `included`; relationships appear as `{type,id}` linkage.
- Nested includes with dot notation, max **two levels**: `include=households.people`.
- Allowed values: `meta.can_include` or the Include list per resource.

### Ordering and pagination
- `order=attr`, descending with `-attr`; some endpoints allow related-attr sorts (e.g. `person.last_name`).
- `per_page` 1–100 (default 25), `offset` integer. Follow `links.next` until absent, or loop `offset += per_page` while `offset < meta.total_count`.

## 5. Dates and times

- ISO 8601. Dates `YYYY-MM-DD`; date-times `YYYY-MM-DDTHH:MM:SSZ`. Responses are always UTC.
- Querying a `date_time` attribute with a **date value** is interpreted in the **organization's time zone** and expanded to the day span: for a Pacific org `where[created_at]=2018-02-22` means `2018-02-22T08:00:00Z <= created_at <= 2018-02-23T07:59:59.999999Z`; `[gt]` means after that day ends; `[gte]` from the day start; `[lt]` before the day start; `[lte]` through the day end.
- Pass a full date-time (with `Z` or offset) to opt out: `where[created_at][gte]=2018-02-22T00:00:00-05:00&where[created_at][lt]=2018-02-23T00:00:00-05:00`.
- Operator table: `=` on day; `[gt]` after; `[gte]` on or after; `[lt]` before; `[lte]` on or before.

## 6. File uploads

`POST https://upload.planningcenteronline.com/v2/files` as `multipart/form-data` with a `file` field, authenticated like any API call:
```
curl -u CLIENT_ID:SECRET -X POST -F 'file=@/path/to/file.png' https://upload.planningcenteronline.com/v2/files
```
Response: `{"data":[{"type":"File","id":"us1-16207df7-…","attributes":{"source_ip","md5","content_type","file_size","name","expires_at"}}]}`. The `id` is the file UUID; it expires (`expires_at`), so attach promptly. Pass the UUID as the string value of any file attribute, e.g. `PATCH /people/v2/people/1` `{"data":{"attributes":{"avatar":"us1-16207df7-…"}}}`. Used by: People `Person.avatar`, `Household.avatar`; Services `Attachment.file_upload_identifier`; Publishing `art`, `podcast_art`, `sermon_audio`.

## 7. Errors

| Status | Meaning |
|---|---|
| 400 | Bad Request — malformed request (also `unsupported_version_error` for versions < 2018-08-01) |
| 401 | Unauthorized — bad token/secret |
| 403 | Forbidden — no access to the resource, insufficient role to create, missing scope, or bad User-Agent |
| 404 | Not Found — bad URL or id (also returned instead of 403 for some hidden resources) |
| 409 | Conflict — uniqueness race from simultaneous creates; send one create per resource |
| 422 | Validation Error — body lists each invalid attribute (there may be several) |
| 429 | Too Many Requests — see rate limiting |
| 500 | Internal Server Error — retry later |
| 503 | Service Unavailable — maintenance |

Error body: `{"errors":[{"status":"422","title":"…","detail":"…","code":"…","source":{"parameter":"…"}}]}` (shape follows JSON:API errors).

Error hints (appear in error payloads for auth problems): BLACKBIRD unsupported `kind` param; CHINCHILLA client application not found/invalid; FLAMINGO authenticated user doesn't exist; LEMMING authenticated organization doesn't exist; PELICAN token lacks required scope; BABOON access token expired (before March 2025 also revoked); CAPUCHIN access token revoked; TRASH_PANDA person has no access to the requested application; WEASEL signature scope invalid for path; ANTEATER missing authorization header (signature auth); BLUE_JAY authorization header malformed; MOCKINGBIRD invalid token (signature auth).

## 8. Versioning

- Per-application default version is set in the developer account; override per request with `X-PCO-API-Version: YYYY-MM-DD`. Header wins over app default.
- Matching is "equal to or less than": with versions 2018-08-01, 2018-08-10, 2018-08-17 available, header `2018-08-14` resolves to `2018-08-10`.
- `X-PCO-API-Version: LATEST` = always tomorrow's date; expect breaking changes; not for production.
- Versions before 2018-08-01 → 400 `unsupported_version_error`.
- Each product versions independently (see the version header line in each reference file). The docs site shows the newest version by default, which may be newer than your app's pinned default — pin explicitly to the version you built against.

## 9. Libraries

Planning Center maintains `pco_api` for Ruby (https://github.com/planningcenter/pco_api_ruby). Everything else is plain HTTP + JSON; community client libraries exist for most languages (search "planningcenter api <language>").

## 10. Webhooks

See webhooks.md for the full guide and the webhooks/v2 resources.

## 11. Add-ons

Add-ons are OAuth applications with React-based UI components rendered inside Planning Center products (e.g. the Clearstream add-on). Building one starts by contacting Planning Center. Docs: https://api.planningcenteronline.com/docs/overview/add-ons (Process, Terminology, Building Your First Add-On, Add-ons CLI, Insertion Points, Component Library, API Reference, OAuth, Guidelines, Upgrading Your Add-On — the upgrade page covers support timelines for `@remote-ui` and `component_version: "5"`). Out of scope for ordinary API integrations.
