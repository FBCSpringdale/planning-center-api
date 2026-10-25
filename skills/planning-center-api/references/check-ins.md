# Check-Ins API (check-ins/v2)

Base URL: `https://api.planningcenteronline.com/check-ins/v2` (note the hyphen in the product path).
Documented version: `2025-05-28` (history: 2024-11-07, 2024-09-03, 2023-04-05, 2019-07-17, 2018-08-01). OAuth scope: `check_ins` (underscore in the scope, hyphen in the URL).
2025-05-28 change: querying `event` by registration event id now targets the new Registrations integration.
OpenAPI: `https://api.planningcenteronline.com/check-ins/v2/open_api/2025-05-28`
Docs: `https://api.planningcenteronline.com/docs/apps/check-ins/versions/2025-05-28/vertices/<snake_case_resource>`

The Check-Ins API is **read-only** as documented: every resource exposes list/read only (no POST/PATCH/DELETE pages). Use it for attendance reporting, rosters, headcounts, and security codes. Check-ins themselves are created at stations/apps.

Conventions: see people.md. All collections paginate with `per_page` (1–100, default 25) and `offset`.

The standard check-in filter set, reused on every `check_ins` association: `attendee` (regular + guest), `checked_out`, `not_checked_out`, `first_time` (person's first check-in for the event), `guest`, `regular`, `volunteer`, `one_time_guest` (no person record), `not_one_time_guest`.

## Resource index (24)

AttendanceType, CheckIn, CheckInGroup, CheckInTime, Event, EventLabel, EventPeriod, EventTime, Headcount, IntegrationLink, Label, Location, LocationEventPeriod, LocationEventTime, LocationLabel, Option, Organization, Pass, Person, PersonEvent, PreCheck, RosterListPerson, Station, Theme

## Relationship map

```
Organization
 ├─ events (Event) ── event_periods (EventPeriod, one per session/week) ── event_times (EventTime) ── check_ins, headcounts, location_event_times
 │                 ├─ locations (Location, tree via parent/locations) ── options, location_labels, location_event_periods, location_event_times
 │                 ├─ attendance_types (AttendanceType) ── headcounts (Headcount)
 │                 ├─ event_labels (EventLabel) ── label; person_events (PersonEvent); integration_links; current_event_times; check_ins
 ├─ check_ins (CheckIn) ── person, event, event_period, event_times, locations, options, check_in_times (CheckInTime), check_in_group (CheckInGroup), checked_in_at (Station), checked_in_by / checked_out_by (Person)
 ├─ people (Person) ── check_ins, passes (Pass), person_events (PersonEvent)
 ├─ stations (Station) ── check_in_groups, checked_in_at_check_ins, event, location, print_station, theme (Theme)
 ├─ labels (Label) ── event_labels, location_labels
 ├─ headcounts, event_times, options, passes, themes, integration_links
```

Person ids are shared with People.

---

## AttendanceType
An attendee type tracked by headcount rather than individual check-in.
Endpoints: GET /events/{event_id}/attendance_types; …/{id}
Attributes: color; created_at; id; limit (integer); name; updated_at
Relationships: event -> Event. Include: event. Where: id, name
Associations: event -> Event; headcounts -> Headcount

## CheckIn
An attendance record. `checked_out_at` present once checked out.
Endpoints: GET /check_ins [filter: standard set]; GET /check_ins/{id}; also under events, event_periods, event_times, locations, location_event_periods, location_event_times, people, stations (all with standard filters), options, check_in_groups
Attributes: checked_out_at; confirmed_at; created_at; emergency_contact_name; emergency_contact_phone_number; first_name; id; kind (string); last_name; medical_notes; number (integer); one_time_guest (boolean); security_code; updated_at
Relationships: event_period -> EventPeriod; person -> Person
Include: check_in_times, checked_in_at, checked_in_by, checked_out_by, event, event_period, event_times, locations, options, person
Order: checked_out_at, created_at, first_name, last_name, number, updated_at
Where: account_center_person_id (integer — the People person id), created_at, security_code, updated_at
Associations: check_in_group -> CheckInGroup; check_in_times -> CheckInTime; checked_in_at -> Station; checked_in_by -> Person; checked_out_by -> Person; event -> Event; event_period -> EventPeriod; event_times -> EventTime; locations -> Location; options -> Option; person -> Person
Reachable from: /check_ins; /events/{e}/check_ins; /events/{e}/event_periods/{ep}/check_ins; /event_times/{et}/check_ins; /people/{p}/check_ins; /stations/{s}/checked_in_at_check_ins; /stations/{s}/check_in_groups/{g}/check_ins; /options/{o}/check_ins; location_event_periods/{id}/check_ins; location_event_times/{id}/check_ins; person_events/{id}/first_check_in | last_check_in

## CheckInGroup
Check-ins made together (same "checked in by" person); unit of label printing.
Endpoints: GET /stations/{station_id}/check_in_groups [filter: canceled, printed, ready, skipped]; …/{id}; GET /check_ins/{id}/check_in_group
Attributes: check_ins_count; created_at; id; name_labels_count; print_status (ready | printed | canceled | skipped); security_labels_count; updated_at
Relationships: check_ins -> CheckIn (to_many); event_period -> EventPeriod; print_station -> Station. Include: check_ins, event_period, print_station. Where: none (filter by status with `?filter=` on the station path)
Associations: check_ins -> CheckIn; event_period -> EventPeriod; print_station -> Station

## CheckInTime
Links an EventTime and a Location to a CheckIn.
Endpoints: GET /check_ins/{check_in_id}/check_in_times; …/{id}
Attributes: alerts (array); has_validated (boolean); id; kind; services_integrated (boolean)
Relationships: event_time; location; check_in; pre_check -> PreCheck

## Event
A recurring event people attend; each recurrence is an EventPeriod with EventTimes.
Endpoints: GET /events [filter: archived, for_campus, for_headcounts, for_registrations, not_archived]; …/{id}
Attributes: app_source (only with ?fields); archived_at; created_at; enable_services_integration (boolean); frequency; id; integration_key; location_times_enabled (boolean); name; pre_select_enabled (boolean); updated_at
Relationships: campuses -> Campus (to_many). Include: attendance_types
Order: created_at, name. Where: id, name
Associations: attendance_types; check_ins [standard filters]; current_event_times -> EventTime; event_labels -> EventLabel; event_periods -> EventPeriod; integration_links -> IntegrationLink; locations -> Location [filter: locations, root]; person_events -> PersonEvent
Reachable from: /events; check_ins/{id}/event; event_periods/{id}/event; event_times/{id}/event; stations/{id}/event; locations/{id}/event; attendance_types/{id}/event; event_labels/{id}/event; person_events/{id}/event

## EventLabel
How many copies of a label to print for an event and for whom.
Endpoints: GET /events/{event_id}/event_labels; GET /labels/{label_id}/event_labels; …/{id}
Attributes: created_at; for_guest; for_regular; for_volunteer (booleans); id; quantity; updated_at
Include: event, label. Associations: event; label

## EventPeriod
A recurrence ("session") of an event — one per week for weekly events.
Endpoints: GET /events/{event_id}/event_periods; …/{id}
Attributes: created_at; ends_at; guest_count; id; note; regular_count; starts_at; unique_guest_count, unique_regular_count, unique_total_count, unique_volunteer_count (integers, only with ?fields — deduplicated people); updated_at; volunteer_count
Relationships: event -> Event. Include: event, event_times
Order: starts_at. Where: ends_at, starts_at
Associations: check_ins [standard filters]; event; event_times -> EventTime [filter: available]; location_event_periods -> LocationEventPeriod

## EventTime
A time someone may check in; copied from session to session.
Endpoints: GET /event_times; GET /events/{e}/current_event_times; GET /events/{e}/event_periods/{ep}/event_times [filter: available]; …/{id}
Attributes: created_at; day_of_week; guest_count; hides_at; hour; id; minute; name; regular_count; shows_at; starts_at; total_count; updated_at; volunteer_count
Relationships: event; event_period. Include: event, event_period, headcounts
Order: shows_at, starts_at. Where: created_at, updated_at
Associations: available_locations -> Location; check_ins [standard filters]; event; event_period; headcounts -> Headcount; location_event_times -> LocationEventTime

## Headcount
A tally for an event time + attendance type. Absent = possibly zero.
Endpoints: GET /headcounts; GET /event_times/{et}/headcounts; GET /events/{e}/attendance_types/{at}/headcounts; …/{id}
Attributes: created_at; id; total (integer); updated_at
Relationships: event_time; attendance_type. Include: attendance_type, event_time
Order: created_at, total, updated_at. Where: created_at, updated_at

## IntegrationLink
Links a resource from another product (Services, Registrations, Groups…) to a Check-Ins resource.
Endpoints: GET /integration_links; GET /events/{e}/integration_links; GET …/locations/{l}/integration_links; …/{id}
Attributes: id; remote_app; remote_gid (gid://<app>/<type>/<id>); remote_id; remote_type; sync_future_assignment_types (boolean)
Relationships: local -> the linked Check-Ins resource (Event or Location). Where: remote_gid

## Label
A printable label. `prints_for`: "Person" = name label, "Group" = security label.
Endpoints: GET /labels; …/{id}
Attributes: created_at; id; name; prints_for (Person | Group); roll; updated_at; xml
Relationships: event_labels (to_many); location_labels (to_many)
Associations: event_labels -> EventLabel; location_labels -> LocationLabel

## Location
A check-in location for an event. kind "Folder" cannot be checked into but contains other locations.
Endpoints: GET /events/{event_id}/locations [filter: locations, root]; …/{id}; GET …/locations/{id}/locations (children); GET …/locations/{id}/parent
Attributes: age_max_in_months; age_min_in_months; age_on (date); age_range_by; attendees_per_volunteer; child_or_adult; created_at; effective_date (date); gender; grade_max; grade_min; id; kind; max_occupancy; milestone; min_volunteers; name; opened (boolean); position; questions; updated_at
Relationships: parent -> Location. Include: event, locations, options, parent
Order: kind, name, position
Associations: check_ins [standard filters]; event; integration_links; location_event_periods; location_event_times; location_labels; locations (children); options; parent
Reachable from: /events/{e}/locations; /event_times/{et}/available_locations; check_ins/{id}/locations; stations/{id}/location; location_event_periods/{id}/location; location_event_times/{id}/location; location_labels/{id}/location

## LocationEventPeriod
Check-in counts for a location during an event period.
Endpoints: GET …/event_periods/{ep}/location_event_periods; GET …/locations/{l}/location_event_periods; …/{id}
Attributes: created_at; guest_count; id; regular_count; updated_at; volunteer_count
Relationships: check_ins (to_many); event_period; location. Include: event_period, location
Associations: check_ins [standard filters]; event_period; location

## LocationEventTime
Check-in counts for a location at an event time (occupancy).
Endpoints: GET /event_times/{et}/location_event_times; GET …/locations/{l}/location_event_times; …/{id}
Attributes: created_at; guest_count; id; regular_count; updated_at; volunteer_count
Relationships: event_time; location; check_ins (to_many). Include: event_time, location. Where: created_at, updated_at
Associations: check_ins [standard filters]; event_time; location

## LocationLabel
Label print rules for a location.
Endpoints: GET /labels/{label_id}/location_labels; GET …/locations/{l}/location_labels; …/{id}
Attributes: created_at; for_guest; for_regular; for_volunteer; id; quantity; updated_at. Include: label, location

## Option
An option an attendee may select when checking in (may carry extra labels).
Endpoints: GET /options; GET /check_ins/{c}/options; GET …/locations/{l}/options; …/{id}
Attributes: body; created_at; id; quantity; updated_at
Relationships: label -> Label. Include: label
Associations: check_ins -> CheckIn; label -> Label

## Organization
Endpoints: GET /check-ins/v2
Attributes: avatar_url; created_at; daily_check_ins (integer); date_format_pattern; id; name; time_zone; updated_at
Associations (top-level collections): check_ins [standard filters]; event_times; events [filter: archived, for_campus, for_headcounts, for_registrations, not_archived]; headcounts; integration_links; labels; options; passes; people; stations; themes

## Pass
Barcode/mobile pass for quick lookup of a person.
Endpoints: GET /passes; GET /people/{person_id}/passes; …/{id}
Attributes: code; created_at; id; kind (barcode | pkpass — pkpass creates a mobile pass and emails the person); updated_at
Relationships: person -> Person. Include: person. Where: code
Associations: person -> Person

## Person
An attendee, volunteer, or administrator. May be absent for deleted people or "Visitor – Label Only" check-ins.
Endpoints: GET /people; GET /people/{id}
Attributes: addresses (array); avatar_url; birthdate; check_in_count; child (boolean); created_at; demographic_avatar_url; email_addresses (array); first_name; gender; grade; headcounter (boolean); id; ignore_filters (boolean); last_checked_in_at; last_name; medical_notes; middle_name; name; name_prefix; name_suffix; passed_background_check; permission; phone_numbers (array); top_permission; updated_at
Include: organization
Order: check_in_count, first_name, last_checked_in_at, last_name. Where: headcounter, ignore_filters, permission, search_name
Associations: check_ins [standard filters]; organization; passes -> Pass; person_events -> PersonEvent
Reachable from: /people; check_ins/{id}/person | checked_in_by | checked_out_by; passes/{id}/person; person_events/{id}/person

## PersonEvent
A person's attendance count for an event.
Endpoints: GET /events/{event_id}/person_events; GET /people/{person_id}/person_events; …/{id}
Attributes: check_in_count; created_at; id; updated_at
Relationships: event; first_check_in -> CheckIn; last_check_in -> CheckIn; person. Include: event, first_check_in, last_check_in, person
Associations: event; first_check_in; last_check_in; person

## PreCheck
Pre-check record referenced by CheckInTime (attributes: id only).

## RosterListPerson
A roster row (read-only). Attributes: birthdate; demographic_avatar_url; first_name; gender; grade; id; ignore_filters; last_name; medical_notes; name

## Station
A check-in device, optionally tied to a printer.
Endpoints: GET /stations; …/{id}
Attributes: id; check_in_count (only with ?fields); closes_at (only with ?fields); created_at; input_type (scanner | keypad); input_type_options (all_input_types | only_keypad | only_scanner); mode (integer); name; next_shows_at (only with ?fields); online (boolean, only with ?fields); open_for_check_in (boolean, only with ?fields); seconds_until_closes_at (integer, only with ?fields); seconds_until_next_shows_at (integer, only with ?fields); timeout_seconds; updated_at
Relationships: event; location; print_station -> Station; theme -> Theme. Include: event, location, print_station, theme
Associations: check_in_groups -> CheckInGroup [filter: canceled, printed, ready, skipped]; checked_in_at_check_ins -> CheckIn [standard filters]; event; location; print_station; theme

## Theme
Custom style for stations. Endpoints: GET /themes; …/{id}; GET /stations/{id}/theme
Attributes: background_color; color; created_at; id; image; image_thumbnail; mode; name; text_color; updated_at
