# Cross-product model map and recipes

## The one identity that spans everything: Person

A person's `id` is the same integer across every product. `people/v2/people/{id}`, `services/v2/people/{id}`, `giving/v2/people/{id}`, `check-ins/v2/people/{id}`, `groups/v2/people/{id}`, `calendar/v2/people/{id}` and `registrations/v2/people/{id}` are projections of one record, each exposing the attributes that product cares about:

| Product | What its Person adds | Writable there? |
|---|---|---|
| People | identity, contact info, household, custom fields, notes, workflows, permissions (`people_permissions`, `site_administrator`) | yes (source of truth) |
| Services | `plan_permissions`, `song_permissions`, `media_permissions`, scheduling preferences, blockouts, team positions, schedules | PATCH permissions only |
| Giving | `donor_number`, `permissions` (administrator/reviewer/counter/bookkeeper), donations, pledges, payment methods | PATCH donor_number only |
| Check-Ins | `check_in_count`, `last_checked_in_at`, `headcounter`, passes | no |
| Groups | `permissions` (administrator/group_type_manager/leader/member), groups, memberships | no |
| Calendar | calendar permissions, `resolves_conflicts`, `pending_request_count` | no |
| Registrations | `can_search`, attendees, registrations | no |
| Check-Ins `CheckIn.where[account_center_person_id]` and Giving `DonorSummary.id` also use this id. |

Create and edit people (names, emails, phones, addresses, birthdate, household) in **People** only. Other products read them. `GET /current/v2/me` returns the caller's id without any scope.

Campus is similar: People `Campus` is the source (`/people/v2/campuses`, created by Organization Administrators); Giving, Groups, Registrations and Check-Ins expose read-only Campus projections with the same ids.

## Links between products (ids stored in attributes)

- Services `Plan.linked_publishing_episode` ↔ Publishing `Episode.services_plan_remote_identifier` / `services_service_type_remote_identifier`; `Channel.services_service_type_remote_identifier`.
- Services `Attendance.check_ins_event_id` / `check_ins_event_period_id` ↔ Check-Ins `Event` / `EventPeriod` (Services–Check-Ins integration for volunteer attendance).
- Check-Ins `IntegrationLink.remote_gid` (`gid://<app>/<type>/<id>`) links a Check-Ins Event/Location to Services, Registrations, Groups records; `Event.integration_key`.
- Check-Ins `Event` filter `for_registrations` lists events backed by Registrations signups (2025-05-28 change).
- Calendar `EventConnection` links a Calendar event to `registrations` (signup), `groups` (group), `check-ins` (event), `services` (service_type) by `connected_to_id` + `product_name`.
- Calendar `Feed.feed_type` = registrations | groups | ical | form; `source_id` is the source record id.
- People `FormField.fieldable` (polymorphic) can be a Workflow or NoteCategory; `FormSubmission` creates `WorkflowCard`s for workflow fields.
- People `Message` / `MessageGroup` record emails/SMS sent by any product (`app_name`, `MessageGroup.app`).
- Giving `Fund.visibility` and `PledgeCampaign` surface on Church Center; Publishing `EpisodeResource.kind=giving_fund` links an episode to a Fund.
- Groups `Event` ↔ Calendar via feeds; Groups `Resource` (files/links) is separate from Calendar `Resource` (rooms/equipment) — same name, different concept.

## Name collisions to keep straight

| Name | People | Services | Groups | Calendar | Check-Ins | Giving | Publishing |
|---|---|---|---|---|---|---|---|
| Event | — | — | group meeting | calendar event | recurring check-in event | — | — |
| Attendance | — | volunteer attendance via Check-Ins | attendance at a group event | — | — | — | — |
| Tag/TagGroup | — | person/song/arrangement/media tags | group filter tags | event tags | — | — | — |
| Label | — | — | — | — | printable label | donation label | — |
| Note | profile note | ItemNote/PlanNote | EventNote | — | — | donation note | NoteTemplate |
| Resource | — | — | file/link for a group | room or equipment | — | — | EpisodeResource (link) |
| Series | — | plan series (artwork) | — | — | — | — | sermon series |
| Campus | source | — | projection | — | — | projection | AnnouncementsCampus |

## Recipes

### Find a person and everything about them
```
GET /people/v2/people?where[search_name_or_email]=jane%20doe&include=emails,phone_numbers,addresses,households,field_data
GET /people/v2/people/{id}/field_data?include=field_definition
GET /people/v2/people/{id}/notes?include=category
GET /people/v2/people/{id}/workflow_cards?include=workflow,current_step
GET /services/v2/people/{id}/schedules?filter=future&include=plan_times
GET /giving/v2/people/{id}/donations?include=designations&order=-received_at
GET /groups/v2/people/{id}/memberships
GET /groups/v2/people/{id}/groups
GET /check-ins/v2/people/{id}/check_ins?order=-created_at
```

### Create a person with contact info in one call
```json
POST /people/v2/people?include=emails,phone_numbers
{"data":{"type":"Person","attributes":{"first_name":"Jane","last_name":"Doe","birthdate":"1990-04-01","status":"active"}},
 "included":[{"type":"Email","attributes":{"address":"jane@example.com","location":"Home","primary":true}},
             {"type":"PhoneNumber","attributes":{"number":"5551234567","location":"Mobile","primary":true}}]}
```
(Or POST the person, then `POST /people/v2/people/{id}/emails` and `/phone_numbers`.) Dedupe first with `where[search_name_or_email]`.

### Record a custom field value
```
GET /people/v2/field_definitions?where[slug]=membership_class_date   → id, data_type, tab
POST /people/v2/people/{id}/field_data {"data":{"attributes":{"field_definition_id":"123","value":"2026-10-25"}}}
```
Checkbox fields: POST the option string as `value`; remove by deleting the FieldDatum.

### Walk a Services plan
```
GET /services/v2/service_types                                     → pick service_type_id
GET /services/v2/service_types/{st}/plans?filter=future&order=sort_date&per_page=5&include=plan_times
GET /services/v2/service_types/{st}/plans/{plan}/items?include=song,arrangement,key
GET /services/v2/service_types/{st}/plans/{plan}/team_members?include=person,team
```
Create a plan: `POST …/plans {"data":{"attributes":{"title":"Sunday"}}}` then `POST …/plans/{id}/plan_times {"data":{"attributes":{"starts_at":"…Z","ends_at":"…Z","time_type":"service"}}}`, then items. Or `POST /service_types/{st}/create_plans` with `template` to clone.

### Schedule a volunteer and request confirmation
```
POST /services/v2/service_types/{st}/plans/{plan}/team_members
{"data":{"attributes":{"person_id":"123","team_id":"45","team_position_name":"Vocals","status":"U","prepare_notification":true}}}
```
The person then accepts/declines via `POST /services/v2/people/{p}/schedules/{s}/accept|decline`.

### Who is scheduled this Sunday (all teams)
```
GET /services/v2/service_types/{st}/plans?filter=future&per_page=1&order=sort_date
GET /services/v2/service_types/{st}/plans/{plan}/team_members?filter=confirmed&include=person&per_page=100
```

### Record an offline gift (see giving.md "Core workflow")
Batch → donations with included Designations → commit → poll.

### Add someone to a group
```
POST /groups/v2/groups/{group_id}/memberships {"data":{"attributes":{"role":"member"},"relationships":{"person":{"data":{"type":"Person","id":"123"}}}}}
```

### Attendance report for a Check-Ins event
```
GET /check-ins/v2/events?where[name]=Kids%20Church
GET /check-ins/v2/events/{e}/event_periods?order=-starts_at&per_page=4&fields[EventPeriod]=starts_at,regular_count,guest_count,volunteer_count,unique_total_count
GET /check-ins/v2/events/{e}/event_periods/{ep}/check_ins?filter=attendee&include=person,locations&per_page=100
```

### Upcoming Church Center calendar
```
GET /calendar/v2/event_instances?filter=approved&where[starts_at][gte]=2026-11-01&where[starts_at][lt]=2026-12-01&include=event,event_times&order=starts_at&per_page=100
```
Filter to published events client-side via `included` Event `visible_in_church_center`.

### Keep a cache fresh
Poll `?where[updated_at][gte]=<last sync ISO time>&order=updated_at&per_page=100` per resource, or subscribe to `<app>.v2.events.<resource>.created|updated|destroyed` webhooks. Deleted records do not appear in updated_at polling — use `destroyed` webhooks, or People's `/people/v2/person_mergers` for merges.

### Sync a People List to an external system
```
GET /people/v2/lists?where[name]=Newsletter
POST /people/v2/lists/{id}/run            (refresh results)
GET /people/v2/lists/{id}/people?per_page=100&include=emails
```
