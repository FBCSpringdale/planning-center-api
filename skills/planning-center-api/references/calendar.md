# Calendar API (calendar/v2)

Base URL: `https://api.planningcenteronline.com/calendar/v2`
Documented version: `2026-10-19` (beta at time of writing; latest stable `2026-06-22`; history: 2022-07-07, 2021-07-20, 2020-04-08, 2018-08-01). OAuth scope: `calendar`.
- 2026-06-22: booking and conflict endpoints redact event data for users lacking access — traversals may return `BookedEvent`, `BookedEventInstance`, `BookedEventTime` stubs instead of full Event/EventInstance/EventTime (applies to all earlier versions too).
- 2026-10-19 (beta): `calendar_instance` renamed `status` → `booking_status`; `status` now also accounts for the event request. Pin `X-PCO-API-Version: 2026-06-22` for stable behavior.
OpenAPI: `https://api.planningcenteronline.com/calendar/v2/open_api/2026-10-19`
Docs: `https://api.planningcenteronline.com/docs/apps/calendar/versions/2026-10-19/vertices/<snake_case_resource>`

Calendar is mostly read + resource management via API: events/instances/times/bookings/requests are read-only; you can create/update Resources, ResourceFolders, ResourceQuestions, Tags, TagGroups, ReportTemplates and EventConnections.

Conventions: see people.md. All collections paginate with `per_page` (1–100, default 25) and `offset`. All times are UTC.

Approval status codes: `A` approved, `P` pending, `R` rejected.

The big filter set on `/event_instances` and `/resource_bookings` (reused below as "status filters"): approved, approved_conflict, approved_pending, approved_pending_conflict, approved_pending_rejected, approved_pending_rejected_conflict, approved_rejected, approved_rejected_conflict, conflict, future, pending, pending_conflict, pending_rejected, pending_rejected_conflict, rejected, rejected_conflict. `/event_instances` additionally accepts: all, approver, approver_subscriber, event_request_approved, event_request_approved_pending, event_request_approved_pending_rejected, event_request_approved_rejected, event_request_pending, event_request_pending_rejected, event_request_rejected, lost, lost_due_to_blockout, manager, manager_approver, manager_approver_subscriber, manager_subscriber, not_pending_event_requests, owner, owner_approver, owner_approver_subscriber, owner_manager, owner_manager_approver, owner_manager_approver_subscriber, owner_manager_subscriber, owner_subscriber, shared, subscriber, unresolved. `/resource_bookings` additionally accepts: resources, rooms.

## Resource index (25)

Attachment, Calendar, Conflict, ContainingResource, Event, EventConnection, EventInstance, EventResourceAnswer, EventResourceRequest, EventTime, Feed, JobStatus, Organization, Person, ReportTemplate, RequiredApproval, Resource, ResourceApprovalGroup, ResourceBooking, ResourceFolder, ResourceQuestion, ResourceSuggestion, RoomSetup, Tag, TagGroup

## Relationship map

```
Organization
 ├─ calendars (Calendar) ── events (Event), approval_groups (ResourceApprovalGroup)
 ├─ events (Event) ── event_instances (EventInstance) ── event_times (EventTime), resource_bookings (ResourceBooking), tags
 │                 ├─ event_resource_requests (EventResourceRequest) ── resource, room_setup, answers (EventResourceAnswer), resource_bookings, created_by/updated_by (Person)
 │                 ├─ conflicts (Conflict) ── resource, winner (Event), resolved_by (Person)
 │                 ├─ attachments (Attachment), event_connections (EventConnection), feed (Feed), owner (Person), calendar, tags (Tag) ── tag_group (TagGroup)
 ├─ resources (Resource; kind Room|Resource) ── resource_bookings, event_resource_requests, conflicts, required_approvals (RequiredApproval), resource_approval_groups, resource_folder (ResourceFolder), resource_questions (ResourceQuestion), room_setups (RoomSetup) ── resource_suggestions (ResourceSuggestion), containing_resource
 ├─ resource_approval_groups (ResourceApprovalGroup) ── calendars, people, resources, required_approvals, event_resource_requests
 ├─ people (Person) ── event_resource_requests
 ├─ resource_bookings, event_instances, event_resource_requests, conflicts, attachments, feeds, job_statuses, report_templates, resource_folders, resource_questions, room_setups, tags, tag_groups
```

Person ids are shared with People.

---

## Attachment
A file or external link attached to an event (read-only).
Endpoints: GET /attachments; GET /events/{event_id}/attachments; …/{id}
Attributes: content_type (null for links); created_at; description; file_size (null for links); id; kind (file_upload | external_link); name; updated_at; url
Relationships: event -> Event. Include: event
Order/Where: content_type, created_at, description, file_size, kind, name, updated_at
Associations: event -> Event

## Calendar
A calendar belonging to the organization (read-only).
Endpoints: GET /calendars; …/{id}; GET /events/{e}/calendar; GET /resource_approval_groups/{rag}/calendars
Attributes: access; access_restricted (boolean); color (blue | aqua | teal | green | yellow | orange | pink | purple | magenta | indigo | *_bold variants); confirmable_event_count (only with ?fields); created_at; default (boolean); description; id; name; requires_approval (boolean); updated_at
Include: approval_groups. Order: name
Associations: approval_groups -> ResourceApprovalGroup; events -> Event

## Conflict
Two events with overlapping resource requests; `resolved_at` set when resolved. Read-only.
Endpoints: GET /conflicts [filter: future, resolved, unresolved]; GET /events/{e}/conflicts; GET /resources/{r}/conflicts; …/{id}
Attributes: created_at; id; note; resolved_at; updated_at
Relationships: resource -> Resource; resolved_by -> Person; winner -> Event. Include: resolved_by, resource, winner
Order: resolved_at
Associations: resolved_by; resource; winner

## ContainingResource
The record containing a RoomSetup (a Resource or the Organization). Endpoints: GET /room_setups/{id}/containing_resource

## Event
A calendar event (read-only).
Endpoints: GET /events [filter: future]; GET /events/{id}; GET /calendars/{c}/events; GET /tags/{t}/events; GET /tag_groups/{tg}/events
Attributes: approval_status (A | P | R); created_at; description (rich text); featured (boolean); id; image_url; link_only (boolean); name; percent_approved (integer); percent_rejected (integer); registration_url; summary (plain text); updated_at; visible_in_church_center (boolean)
Relationships: calendar -> Calendar; owner -> Person
Include: attachments, calendar, feed, owner, tags
Where: approval_status, created_at, featured, link_only, name, percent_approved, percent_rejected, updated_at, visible_in_church_center
Associations: attachments; calendar; conflicts; event_connections; event_instances [filter: future]; event_resource_requests; feed; owner; resource_bookings [filter: future]; tags
Reachable from: /events; /calendars/{c}/events; /tags/{t}/events; /tag_groups/{tg}/events; attachments/{id}/event; conflicts/{id}/winner; event_instances/{id}/event; event_resource_requests/{id}/event; event_times/{id}/event

## EventConnection
Connects a Calendar event to a record in another product.
Endpoints: GET /events/{event_id}/event_connections; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: connected_to_id; connected_to_name; connected_to_type (signup | group | event | service_type); connected_to_url; id; product_name (registrations | groups | check-ins | services); promoted (boolean, Groups only, only with ?fields)
Relationships: event -> Event. Where: connected_to_id, product_name, promoted
Create/Update attrs: connected_to_id, connected_to_name, connected_to_type, product_name, promoted

## EventInstance
One occurrence of an event (read-only). The practical "what's on the calendar" resource.
Endpoints: GET /event_instances [filter: status filters + extended set above]; GET /event_instances/{id}; GET /events/{e}/event_instances [filter: future]; GET /tags/{t}/event_instances
Attributes: all_day_event (boolean); church_center_url; compact_recurrence_description; created_at; description (only with ?fields); ends_at; id; image_url (only with ?fields); kind (standard | blockout, only with ?fields); location; name; published_ends_at; published_starts_at; recurrence; recurrence_description; starts_at; updated_at
Relationships: event -> Event. Include: event, event_times, resource_bookings, tags
Order: created_at, ends_at, starts_at, updated_at. Where: created_at, ends_at, kind, starts_at, updated_at
Associations: event; event_times -> EventTime; resource_bookings -> ResourceBooking [filter: future, resources, rooms]; tags -> Tag
Typical query: `GET /event_instances?filter=approved&where[starts_at][gte]=2026-11-01&where[starts_at][lt]=2026-12-01&include=event,event_times&order=starts_at`

## EventResourceAnswer
A reply to a ResourceQuestion in a request (read-only).
Endpoints: GET /event_resource_requests/{err}/answers; …/{id}
Attributes: answer (json); created_at; db_answer (only with ?fields); id; question (json snapshot); updated_at
Relationships: created_by, updated_by -> Person; resource_question; event_resource_request

## EventResourceRequest
A room/resource request tied to an event (read-only).
Endpoints: GET /event_resource_requests; GET /events/{e}/event_resource_requests; GET /resources/{r}/event_resource_requests; GET /people/{p}/event_resource_requests [filter: awaiting_response, future, not_in_conflict, not_overbooked, overbooked]; GET /resource_approval_groups/{rag}/event_resource_requests [same filters]; …/{id}
Attributes: approval_sent (boolean); approval_status (A | P | R); created_at; id; notes; quantity; updated_at; visible_on_kiosks (boolean)
Relationships: event; resource; event_resource_request; created_by; updated_by; room_setup. Include: created_by, event, resource, room_setup, updated_by
Where: approval_sent, approval_status, created_at, updated_at
Associations: answers -> EventResourceAnswer; created_by; event; resource_bookings [status filters]; resource; room_setup; updated_by

## EventTime
Start/end times for an event instance, incl. setup/teardown (read-only).
Endpoints: GET /event_instances/{ei}/event_times; …/{id}
Attributes: ends_at; id; name; starts_at; visible_on_kiosks (boolean); visible_on_widget_and_ical (boolean)
Relationships: event. Include: event. Order: ends_at, starts_at. Where: ends_at, name, starts_at, visible_on_kiosks, visible_on_widget_and_ical

## Feed
An imported feed (registrations, groups, ical, form). Read-only.
Endpoints: GET /feeds; …/{id}; GET /events/{e}/feed
Attributes: can_delete; default_church_center_visibility (hidden | published); deleting; feed_type (registrations | groups | ical | form); id; imported_at; name; prefix_event_names (only with ?fields); source_id; sync_campus_tags (only with ?fields)
Relationships: event_owner -> Person; default_calendar -> Calendar. Order: name. Where: feed_type, source_id

## JobStatus
Background job status. Endpoints: GET /job_statuses; …/{id}
Attributes: errors (json); id; message; retries; started_at; status

## Organization
Endpoints: GET /calendar/v2
Attributes: calendar_starts_on; date_format (%d/%m/%Y | %m/%d/%Y); id; name; onboarding (only with ?fields); time_zone; twenty_four_hour_time (boolean)
Associations (top-level collections): attachments; calendars; conflicts [filter: future, resolved, unresolved]; event_instances [status + extended filters]; event_resource_requests; events [filter: future]; feeds; job_statuses; people [filter: active, event_owners]; report_templates; resource_approval_groups; resource_bookings [status filters + resources, rooms]; resource_folders [filter: resources, rooms]; resource_questions; resources [filter: resources, rooms]; room_setups [filter: shared_room_setups]; tag_groups [filter: required]; tags [filter: individual]

## Person
People with access to Calendar (read-only).
Endpoints: GET /people [filter: active, event_owners]; …/{id}; GET /resource_approval_groups/{rag}/people
Attributes: avatar_url; can_edit_people; can_edit_resources; can_edit_rooms (booleans); child (boolean); contact_data (object: email_addresses, addresses, phone_numbers); created_at; event_administrator (only with ?fields); event_permissions_type; first_name; gender (M | F); has_access; has_full_access_to_any_calendar (only with ?fields); id; last_name; member_of_approval_groups (only with ?fields); middle_name; name; name_prefix; name_suffix; pending_request_count; people_permissions_type; permissions (integer); resolves_conflicts (boolean); resources_permissions_type; room_permissions_type; site_administrator; status (active | pending | inactive); updated_at
Include: organization. Order: created_at, first_name, last_name, resolves_conflicts, updated_at. Where: created_at, first_name, last_name, middle_name, updated_at
Associations: event_resource_requests [filter: awaiting_response, future, not_in_conflict, not_overbooked, overbooked]; organization

## ReportTemplate
Endpoints: GET /report_templates; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: body; created_at; description; id; title; updated_at
Create/Update attrs: body, description, title

## RequiredApproval
Link between a Resource and a ResourceApprovalGroup (read-only).
Endpoints: GET /resource_approval_groups/{rag}/required_approvals [filter: resources, rooms]; GET /resources/{r}/required_approvals; …/{id}
Attributes: id. Relationships: resource; resource_approval_group. Include: resource

## Resource
A room (kind Room) or resource (kind Resource).
Endpoints: GET /resources [filter: resources, rooms]; …/{id}; POST /resources; PATCH /resources/{id}; DELETE /resources/{id}
Attributes: created_at; description; expires_at; home_location; id; image; kind (Room | Resource); name; path_name (folder path, "/"-separated); quantity (integer); serial_number; updated_at
Relationships: conflicts, event_resource_requests, required_approvals, resource_approval_groups, resource_bookings, resource_questions, room_setups (to_many); resource_folder -> ResourceFolder
Include: resource_approval_groups, resource_folder*, resource_questions, room_setups
Order: created_at, expires_at, name, updated_at. Where: created_at, id, kind, name, path_name, serial_number, updated_at
Associations: conflicts; event_resource_requests; required_approvals; resource_approval_groups; resource_bookings [status filters]; resource_folder; resource_questions; room_setups
Reachable from: /resources; /resource_folders/{rf}/resources; /resource_approval_groups/{rag}/resources [filter: resources, rooms]; conflicts/{id}/resource; event_resource_requests/{id}/resource; resource_bookings/{id}/resource; required_approvals/{id}/resource; resource_suggestions/{id}/resource
Create: POST /resources — attrs: kind, description, expires_at, home_location, name, quantity, serial_number; rel: resource_folder
Update: PATCH /resources/{id} — same minus kind
Delete: DELETE /resources/{id}

## ResourceApprovalGroup
People whose approval is required to book attached rooms/resources (read-only).
Endpoints: GET /resource_approval_groups; …/{id}; GET /calendars/{c}/approval_groups; GET /resources/{r}/resource_approval_groups
Attributes: calendar_count, form_count, person_count, resource_count, room_count (integers, only with ?fields); created_at; id; name; updated_at
Include: calendars, people, resources. Order: created_at, name, updated_at. Where: created_at, id, name, updated_at
Associations: calendars; event_resource_requests [filter: awaiting_response, future, not_in_conflict, not_overbooked, overbooked]; people; required_approvals [filter: resources, rooms]; resources [filter: resources, rooms]

## ResourceBooking
A booking of a room/resource for an event instance (read-only).
Endpoints: GET /resource_bookings [status filters + resources, rooms]; …/{id}; GET /event_instances/{ei}/resource_bookings [filter: future, resources, rooms]; GET /events/{e}/resource_bookings [filter: future]; GET /resources/{r}/resource_bookings [status filters]; GET /event_resource_requests/{err}/resource_bookings [status filters]
Attributes: created_at; ends_at; id; quantity; starts_at; updated_at
Relationships: event; event_instance; resource. Include: event_resource_request, resource
Order/Where: created_at, ends_at, starts_at, updated_at
Associations: event_resource_request -> EventResourceRequest; resource -> Resource

## ResourceFolder
Folder containing rooms or resources.
Endpoints: GET /resource_folders [filter: resources, rooms]; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: ancestry; created_at; id; kind (Room | Resource); name; path_name; updated_at
Relationships: resources (to_many). Include: resources
Order: ancestry, created_at, name, updated_at. Where: ancestry, created_at, name, path_name, updated_at
Associations: resources -> Resource
Create attrs: kind, name. Update attrs: name

## ResourceQuestion
A question a requester must answer when booking a resource.
Endpoints: GET /resource_questions; GET /resources/{r}/resource_questions; …/{id}; POST /resources/{resource_id}/resource_questions; PATCH /resource_questions/{id}; DELETE /resource_questions/{id}
Attributes: choices (|-separated, for dropdown); created_at; description; id; kind (dropdown | paragraph | text | yesno | section_header); multiple_select (boolean); optional (boolean); position; question; updated_at
Relationships: resource. Where: created_at, kind, updated_at
Associations: resource -> Resource
Create/Update attrs: choices, description, kind, multiple_select, optional, position, question

## ResourceSuggestion
A resource + quantity suggested by a room setup (read-only).
Endpoints: GET /room_setups/{rs}/resource_suggestions; …/{id}
Attributes: created_at; id; quantity; updated_at. Relationships: resource; room_setup. Include: resource

## RoomSetup
A predefined room layout with diagram and suggested resources (read-only).
Endpoints: GET /room_setups [filter: shared_room_setups]; GET /resources/{r}/room_setups; GET /event_resource_requests/{err}/room_setup; …/{id}
Attributes: created_at; description; diagram (object: url, thumbnail); diagram_thumbnail_url; diagram_url; id; name; updated_at
Relationships: resource_suggestions (to_many); containing_resource. Include: containing_resource, resource_suggestions
Order/Where: created_at, name, updated_at
Associations: containing_resource -> ContainingResource; resource_suggestions -> ResourceSuggestion

## Tag
Organizational tag applied to events.
Endpoints: GET /tags [filter: individual]; …/{id}; GET /events/{e}/tags; GET /event_instances/{ei}/tags; GET /tag_groups/{tg}/tags; POST /tags; PATCH /tags/{id}; DELETE /tags/{id}
Attributes: church_center_category (boolean); color (hex); created_at; id; name; position (float); updated_at
Relationships: tag_group -> TagGroup; events, event_instances (to_many). Include: tag_group*
Order: name, position. Where: church_center_category, color, created_at, id, name, position, updated_at
Associations: event_instances; events; tag_group
Create/Update attrs: church_center_category, color, name, position; rel: tag_group

## TagGroup
Endpoints: GET /tag_groups [filter: required]; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: created_at; id; name; required (boolean — tags from this group must be applied when creating an event); updated_at
Relationships: events, tags (to_many); organization. Include: events, tags. Order: name. Where: created_at, name, updated_at
Associations: events -> Event; tags -> Tag
Create/Update attrs: name (required)
