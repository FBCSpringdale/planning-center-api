# Groups API (groups/v2)

Base URL: `https://api.planningcenteronline.com/groups/v2`
Documented version: `2023-07-10` (other: 2018-08-01). OAuth scope: `groups`.
2023-07-10 breaking changes: Membership lost its person attributes (use the `person` association); Membership lost color identifier (use `GroupType.color`); Group lost enrollment attributes (use the `enrollment` association).
OpenAPI: `https://api.planningcenteronline.com/groups/v2/open_api/2023-07-10`
Docs: `https://api.planningcenteronline.com/docs/apps/groups/versions/2023-07-10/vertices/<snake_case_resource>`

Conventions: see people.md. All collections paginate with `per_page` (1–100, default 25) and `offset`.

Groups is largely read-oriented via API: you can read everything, update a Group, create/update/delete Memberships, approve/reject GroupApplications, and run Group actions. Groups, GroupTypes, Events, Tags, Locations and Resources are created in the UI.

## Resource index (17)

Attendance, Campus, Enrollment, Event, EventNote, Group, GroupApplication, GroupType, Location, Membership, Organization, Owner, Person, RSVP, Resource, Tag, TagGroup

## Relationship map

```
Organization
 ├─ group_types (GroupType) ── groups (Group), events (Event), resources (Resource)
 ├─ groups (Group) ── memberships (Membership) ── person (Person)
 │                 ├─ events (Event) ── attendances (Attendance) ── person; rsvps (RSVP); notes (EventNote) ── owner (Owner); location
 │                 ├─ enrollment (Enrollment), applications (GroupApplication) ── person, group_type, location (Location), campuses (Campus), people (Person), resources (Resource), tags (Tag) ── tag_group (TagGroup), my_membership
 ├─ people (Person) ── groups, memberships, events
 ├─ events (Event), memberships (Membership), group_applications (GroupApplication), campuses (Campus), event_notes (EventNote), tag_groups (TagGroup) ── tags (Tag)
```

Person ids are shared with People.

---

## Attendance
A person's attendance at a specific event.
Endpoints: GET /events/{event_id}/attendances [filter: attended]; …/{id} (read-only)
Attributes: attended (boolean); id; role (string: member | leader | visitor | applicant — role at time of event)
Relationships: person -> Person; event -> Event. Include: person
Order: first_name, last_name, role. Where: role
Associations: person -> Person

## Campus
A campus as defined in Accounts (read-only).
Endpoints: GET /campuses; …/{id}; GET /groups/{group_id}/campuses
Attributes: id; name. Order: name. Where: id, name
Associations: groups -> Group

## Enrollment
Rules for when/how people may join a group and current status (read-only).
Endpoints: GET /groups/{group_id}/enrollment
Attributes: auto_closed (boolean); auto_closed_reason; date_limit (date string); date_limit_reached (boolean); id; member_limit (integer); member_limit_reached (boolean); status (open | closed | full | private); strategy (request_to_join | open_signup | closed)
Relationships: group -> Group

## Event
A single meeting of a group (physical or virtual). Read-only via API.
Endpoints: GET /events [filter: campus (requires campus_id), canceled, group (requires group_id), group_type (requires group_type_id), my_groups, not_canceled, upcoming]; GET /events/{id}; GET /groups/{group_id}/events [filter: canceled, not_canceled]; GET /group_types/{gt}/events [filter: canceled, not_canceled, upcoming]; GET /people/{person_id}/events [filter: canceled, not_canceled]
Attributes: attendance_requests_enabled (boolean); automated_reminder_enabled (boolean); canceled (boolean); canceled_at; description (HTML); ends_at; id; image (hash); location_type_preference (physical | virtual); multi_day (boolean); name; reminders_sent (boolean); reminders_sent_at; repeating (boolean); starts_at; virtual_location_url; visitors_count (integer)
Relationships: attendance_submitter -> Person; group -> Group; location -> Location; repeating_event -> RepeatingEvent
Include: group, location
Order: ends_at, name, starts_at. Where: ends_at, name, starts_at
Associations: attendances -> Attendance [filter: attended]; group; location; notes -> EventNote; rsvps -> RSVP

## EventNote
Leader notes for an event (read-only).
Endpoints: GET /events/{event_id}/notes; GET /event_notes; …/{id}
Attributes: body; id. Relationships: annotatable (polymorphic); owner -> Owner. Include: owner
Associations: owner -> Owner

## Group
A group of people that meet regularly.
Endpoints: GET /groups [filter: campus, enrollment, group, group_type, hidden, meeting_schedule, my_groups, people_database_searchable, published, tag]; GET /groups/{id}; PATCH /groups/{id}
Attributes: archived_at; can_create_conversation (boolean, only with ?fields); can_create_conversation_reason_code (chat_disabled | group_archived | non_member | leaders_only; only with ?fields); chat_enabled (boolean); contact_email; created_at; description (HTML); description_as_plain_text; direct_messages_enabled (boolean); events_listed (boolean); events_visibility (public | members); header_image (hash: thumbnail, medium, original); id; leaders_can_search_people_database (boolean); listed (boolean); location_type_preference (physical | virtual); members_are_confidential (boolean); memberships_count (integer, includes leaders, excludes requests); name; public_church_center_web_url; schedule (string); tag_ids (only with ?fields); virtual_location_url; widget_status (deprecated, only with ?fields)
Relationships: group_type -> GroupType; location -> Location
Include: enrollment, group_type*, location*
Order: chat_enabled, contact_email, created_at, enrollment_limit, listed, members_are_confidential, memberships_count, name
Where: archive_status (not_archived | only | include), name
Associations: applications -> GroupApplication; campuses -> Campus; enrollment -> Enrollment; events -> Event [filter: canceled, not_canceled]; group_type; location; memberships -> Membership; my_membership -> Membership; people -> Person; resources -> Resource [filter: leaders]; tags -> Tag
Reachable from: /groups (Organization); /group_types/{gt}/groups; /campuses/{campus_id}/groups; /people/{person_id}/groups; /groups/{g}/tags/{tag_id}/groups; events/{id}/group; group_applications/{id}/group; memberships/{id}/group
Actions:
- assign_campuses POST /groups/{id}/assign_campuses — type GroupAssignCampuses, attrs: campus_ids (array; replaces all). Permissions: administrator, group type manager, or leader. Returns no content.
- enable_chat POST /groups/{id}/enable_chat — type GroupEnableChat, attrs: confirm: true (required). Fails if members_are_confidential. Permissions: admins/group type managers; leaders if group type allows.
- disable_chat POST /groups/{id}/disable_chat — type GroupDisableChat, attrs: confirm: true.
- duplicate POST /groups/{id}/duplicate — type GroupDuplicate, attrs: fields (array, required; any of duplicate_members, duplicate_leaders, duplicate_event_defaults, duplicate_event_calendar, duplicate_resources, duplicate_basic_info, duplicate_church_center_settings, duplicate_chat_settings, duplicate_automations, notify_members, notify_leaders), name (optional, unique; default "<name> (Copy)"), group_type_id (optional). Background job → returns BatchStatusUrl with a `value` attribute to poll. Permissions: admins/group type managers.
Update: PATCH /groups/{id} — attrs: name, group_type_id, schedule, tag_ids; rels: group_type, location

## GroupApplication
A request to join a group.
Endpoints: GET /group_applications; GET /groups/{group_id}/applications; …/{id}
Attributes: applied_at; id; message; status (pending | approved | rejected)
Relationships: group -> Group; person -> Person. Include: group, person
Order: applied_at, status. Where: applied_at, status
Associations: group; person
Actions: approve POST /group_applications/{id}/approve — type GroupApplicationApproveAction, attrs: role (member default | leader; only admins/managers may create leaders); pending only; adds the person to the group. reject POST /group_applications/{id}/reject — no payload; pending only.

## GroupType
A category of groups (e.g. "Small Groups", "Classes"). Read-only.
Endpoints: GET /group_types [filter: church_center_visible, not_church_center_visible]; …/{id}
Attributes: church_center_map_visible (boolean); church_center_visible (boolean); color (hex); default_group_settings (JSON string); description; id; name; position (integer); public_church_center_web_url
Order: name, position. Where: id
Associations: events -> Event [filter: canceled, not_canceled, upcoming]; groups -> Group; resources -> Resource [filter: leaders]

## Location
A physical event location (read-only). Address precision depends on the caller's permissions.
Endpoints: GET /groups/{group_id}/location; GET /events/{event_id}/location
Attributes: display_preference (hidden | approximate | exact); full_formatted_address (may be approximate/null; Canadian postal codes obscured); id; latitude; longitude; name; radius (miles for approximate; 0 if exact; null if hidden); strategy (hidden | approximate | exact — effective for this request)
Relationships: group -> Group. Include: group

## Membership
The state of a Person in a Group. One active membership per person per group.
Endpoints: GET /memberships [filter: group (requires group_id, comma-separated), leader]; GET /groups/{group_id}/memberships; GET /groups/{group_id}/my_membership; GET /people/{person_id}/memberships; …/{id}; POST /groups/{group_id}/memberships; PATCH /memberships/{id}; DELETE /memberships/{id}
Attributes: id; joined_at; role (member | leader)
Relationships: group -> Group; person -> Person. Include: person*
Order: first_name, joined_at, last_name, role. Where: role
Associations: group; person
Create: POST /groups/{group_id}/memberships — attrs: joined_at, role; rel: person (`"relationships":{"person":{"data":{"type":"Person","id":"…"}}}`)
Update: PATCH /memberships/{id} — attrs: joined_at, role
Delete: DELETE /memberships/{id} (removes the person from the group)

## Organization
Endpoints: GET /groups/v2
Attributes: id; name; time_zone
Associations (top-level collections): campuses; event_notes; events [filters above]; group_applications; group_types [filter: church_center_visible, not_church_center_visible]; groups [filters above]; memberships [filter: group, leader]; people; tag_groups [filter: public]

## Owner
Owner/creator of an event note. Endpoints: GET /event_notes/{id}/owner
Attributes: avatar_url; first_name; id; last_name

## Person
A Planning Center user as seen by Groups (read-only).
Endpoints: GET /people; GET /people/{id}; GET /groups/{group_id}/people
Attributes: addresses (array); avatar_url; child (boolean, only with ?fields); created_at; email_addresses (array of {address, location, primary}); first_name; gender; id; last_name; permissions (administrator | group_type_manager | leader | member | no access); phone_numbers (array of {number, carrier, location, primary})
Order: first_name, last_name. Where: first_name, last_name
Associations: events -> Event [filter: canceled, not_canceled]; groups -> Group; memberships -> Membership
Reachable from: /people; /groups/{g}/people; attendances/{id}/person; group_applications/{id}/person; memberships/{id}/person

## RSVP
A person's RSVP for an event (read-only).
Endpoints: GET /events/{event_id}/rsvps; …/{id}
Attributes: id; response (awaiting_response | yes | no | maybe | not_sent)
Relationships: event; group; person. Order: response. Where: response

## Resource
A file or link shared with a group (read-only).
Endpoints: GET /groups/{group_id}/resources [filter: leaders]; GET /group_types/{gt}/resources [filter: leaders]; …/{id}
Attributes: description; id; last_updated; name; type (FileResource | LinkResource); visibility (leaders | members)
Relationships: created_by -> Person. Order: last_updated, name, pinned
Actions: download GET …/resources/{id}/download (returns a link for file resources); visit GET …/resources/{id}/visit (returns a link for link resources)

## Tag
Used to filter groups; organized into tag groups (read-only).
Endpoints: GET /tag_groups/{tag_group_id}/tags; GET /groups/{group_id}/tags; …/{id}
Attributes: id; name; position. Relationships: tag_group -> TagGroup. Order: name, position. Where: id, name
Associations: groups -> Group (/groups/{group_id}/tags/{tag_id}/groups)

## TagGroup
Endpoints: GET /tag_groups [filter: public]; …/{id} (read-only)
Attributes: display_publicly (boolean); id; multiple_options_enabled (boolean); name; position. Order: name, position. Where: name
Associations: tags -> Tag
