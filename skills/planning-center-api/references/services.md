# Services API (services/v2)

Base URL: `https://api.planningcenteronline.com/services/v2`
Documented version: `2018-11-01` (only other version: 2018-08-01). OAuth scope: `services`.
2018-11-01 change: `/people` respects the "Can view people not on My Teams" permission.
OpenAPI: `https://api.planningcenteronline.com/services/v2/open_api/2018-11-01`
Docs: `https://api.planningcenteronline.com/docs/apps/services/versions/2018-11-01/vertices/<snake_case_resource>`

Services is worship/service planning: Folders → ServiceTypes → Plans → Items (songs, media, headers) and PlanTimes; Teams/TeamPositions → PlanPeople (scheduling); Songs → Arrangements → Keys; Media; Attachments everywhere.

Conventions: see people.md (Endpoints, Include `*` = assignable, Where, Order, Associations `[filter: …]`, Reachable from). All collections paginate with `per_page` (1–100, default 25) and `offset`.

Path note: the Services docs render member operations (PATCH/DELETE) under whichever parent path is listed first alphabetically, which produces odd-looking canonical paths like `/songs/{song_id}/last_scheduled_item/{item_id}/item_notes/{id}`. Any parent path that reaches the resource works for member operations; this file shows the natural path (usually `/service_types/{service_type_id}/plans/{plan_id}/...`).

Permission vocabulary (Person.plan_permissions / song_permissions / media_permissions): Archived, Scheduled Viewer, Viewer, Scheduler, Editor, Administrator.

## Resource index (65)

Arrangement, ArrangementSections, Attachment, AttachmentActivity, AttachmentType, AttachmentTypeGroup, Attendance, AvailableSignup, Blockout, BlockoutDate, BlockoutException, BlockoutScheduleConflict, Chat, Contributor, CustomSlide, Email, EmailTemplate, EmailTemplateRenderedResponse, Folder, FolderPath, Item, ItemAssignment, ItemNote, ItemNoteCategory, ItemTime, Key, Live, LiveController, Media, MediaSchedule, NeededPosition, Organization, Person, PersonTeamPositionAssignment, Plan, PlanImportMetadata, PlanNote, PlanNoteCategory, PlanPerson, PlanPersonTime, PlanTemplate, PlanTime, PublicView, ReportTemplate, Schedule, ScheduledPerson, SchedulingPreference, Series, ServiceType, ServiceTypePath, SignupSheet, SignupSheetMetadata, SkippedAttachment, Song, SongSchedule, SongbookStatus, SplitTeamRehearsalAssignment, Tag, TagGroup, Team, TeamLeader, TeamPosition, TextSetting, TimePreferenceOption, Zoom

## Relationship map

```
Organization
 ├─ folders (Folder) ── folders (Folder), service_types (ServiceType)
 ├─ service_types (ServiceType)
 │    ├─ plans (Plan) ── items (Item) ── song, arrangement, key, media, attachments, item_notes, item_times, item_assignments, custom_slides
 │    │               ├─ plan_times (PlanTime) ── split_team_rehearsal_assignments
 │    │               ├─ team_members (PlanPerson) ── person, team, plan_times, declined_plan_times, plan_person_times
 │    │               ├─ needed_positions (NeededPosition) ── team, time
 │    │               ├─ notes (PlanNote) ── plan_note_category; attachments; all_attachments; attendances; contributors; my_schedules (Schedule); live (Live); series; next_plan; previous_plan; signup_teams
 │    ├─ plan_templates (PlanTemplate) ── items, notes, team_members
 │    ├─ teams (Team) ── team_positions (TeamPosition) ── person_team_position_assignments (PersonTeamPositionAssignment) ── person, time_preference_options
 │    │                 ├─ team_leaders (TeamLeader), people (Person), service_types
 │    ├─ plan_times, plan_person_times, item_note_categories, plan_note_categories, live_controllers, time_preference_options, public_view, attachments, unscoped_plans
 ├─ people (Person) ── schedules (Schedule), plan_people (PlanPerson), blockouts (Blockout) ── blockout_dates, blockout_exceptions
 │                  ├─ person_team_position_assignments, team_leaders, available_signups (AvailableSignup) ── signup_sheets (SignupSheet) ── scheduled_people, signup_sheet_metadata
 │                  └─ emails, tags, text_settings, scheduling_preferences
 ├─ songs (Song) ── arrangements (Arrangement) ── keys (Key) ── attachments; sections (ArrangementSections); attachments; tags
 │               ├─ attachments, song_schedules (SongSchedule), tags, last_scheduled_item (Item), unscoped_arrangements
 ├─ media (Media) ── attachments (Attachment) ── zooms (Zoom); media_schedules; tags
 ├─ series (Series) ── plans
 ├─ tag_groups (TagGroup) ── tags (Tag), folder
 ├─ email_templates (EmailTemplate), attachment_types (AttachmentType), report_templates (ReportTemplate), chat (Chat)
```

Person ids are shared with People (`/people/v2/people/{id}` == `/services/v2/people/{id}`).

---

## Arrangement
A version of a song (chord chart, lyrics, keys, sequence).
Endpoints: GET /songs/{song_id}/arrangements; …/{id}; POST /songs/{song_id}/arrangements; PATCH …/{id}; DELETE …/{id}
Attributes: archived_at; bpm (float); chord_chart (string — standard or ChordPro); chord_chart_chord_color (integer); chord_chart_columns (integer); chord_chart_font; chord_chart_font_size (integer: 10 11 12 13 14 15 16 18 20 22 24 26 28 32 36 42 48); chord_chart_key; created_at; has_chord_chart (boolean); has_chords (boolean); id; length (integer, seconds); lyrics; lyrics_enabled (boolean); meter (string: 2/2 2/4 3/2 3/4 4/2 4/4 5/4 6/4 3/8 6/8 7/4 7/8 9/8 12/4 12/8); name; notes; number_chart_enabled (boolean); numeral_chart_enabled (boolean); print_margin (0.0in | 0.25in | 0.5in | 0.75in | 1.0in); print_orientation (Portrait | Landscape); print_page_size (Widescreen (16x9) | Fullscreen (4x3) | A4 | Letter | Legal | 11x17); sequence (array of section labels e.g. "Verse 1", "Chorus 1"); sequence_full (array); sequence_short (array); updated_at
Relationships: updated_by -> Person; created_by -> Person; song -> Song
Include: keys, sections
Associations: attachments -> Attachment; keys -> Key; sections -> ArrangementSections; tags -> Tag
Reachable from: /songs/{song_id}/arrangements (Song); /songs/{song_id}/unscoped_arrangements (Song, includes archived); /service_types/{st}/plans/{plan}/items/{item_id}/arrangement (Item)
Actions: archive POST /songs/{song_id}/arrangements/{id}/archive; unarchive POST …/unarchive (use the unscoped_arrangements path to find archived ones); assign_tags POST …/assign_tags — body `{"data":{"type":"TagAssignment","attributes":{},"relationships":{"tags":{"data":[{"type":"Tag","id":"1"}]}}}}` replaces ALL tags (send full set), returns 204
Create/Update attrs: bpm, chord_chart, chord_chart_chord_color, chord_chart_columns, chord_chart_font, chord_chart_font_size, chord_chart_key, length, lyrics_enabled, meter, name, notes, number_chart_enabled, numeral_chart_enabled, print_margin, print_orientation, print_page_size, sequence

## ArrangementSections
Sections derived from an arrangement's chord chart (read-only).
Endpoints: GET /songs/{song_id}/arrangements/{arrangement_id}/sections; …/{id}
Attributes: id; sections (array of {label, lyrics, breaks_at})

## Attachment
A file stored on Planning Center or linked from elsewhere. Attachable to Plan, Item, Song, Arrangement, Key, Media, ServiceType.
Endpoints: list under any parent below; POST under a parent (e.g. /songs/{song_id}/arrangements/{arrangement_id}/attachments, /service_types/{st}/plans/{plan}/attachments, /media/{media_id}/attachments); PATCH /attachments/{id} via any parent path; DELETE via any parent path
Attributes: allow_mp3_download (boolean); attachable_type; content; content_type; created_at; deleted_at; display_name; downloadable (boolean); file_size (integer); file_upload_identifier (string — Planning Center File UUID, required only when creating a file attachment, only with ?fields); filename; filetype; has_preview (boolean); id; import_to_item_details (boolean); licenses_purchased; licenses_remaining; licenses_used; linked_url; page_order; pco_type; remote_link; streamable (boolean); thumbnail_url; transposable (boolean); updated_at; url; web_streamable (boolean)
Relationships: attachable (polymorphic to_one); attachment_types -> AttachmentType (to_many); created_by, updated_by, administrator -> Person
Include: zooms
Order: attachable_type, created_at, deleted_at, filename, filetype, size
Where: administrator_id (integer), attachable_type, licenses_purchased (integer)
Associations: zooms -> Zoom
Reachable from: /songs/{song_id}/attachments; /songs/{song_id}/arrangements/{arrangement_id}/attachments; /songs/{song_id}/arrangements/{arrangement_id}/keys/{key_id}/attachments; /service_types/{st}/attachments; /service_types/{st}/plans/{plan}/attachments; /service_types/{st}/plans/{plan}/all_attachments [filter: attachable_type, extensions]; /service_types/{st}/plans/{plan}/items/{item}/attachments | selected_attachment | selected_background; /media/{media_id}/attachments
Actions: open POST {attachment}/open → AttachmentActivity with `attachment_url` (the downloadable file URL); preview POST {attachment}/preview → reduced-resolution URL (404 if has_preview is false)
Create: POST under a parent — attrs: attachment_type_ids, content, file_upload_identifier (UUID from upload.planningcenteronline.com), filename, import_to_item_details, remote_link, page_order
Update: PATCH — same attrs. Delete: DELETE.

## AttachmentActivity
Returned from the Attachment `open`/`preview` actions.
Attributes: activity_type; attachment_url; date (date); id. Relationships: attachment -> Attachment

## AttachmentType
Groups files so access can be limited; an attachment type can be linked to a team position.
Endpoints: GET /attachment_types; …/{id} (read-only)
Attributes: aliases; built_in (boolean); capoed_chord_charts (boolean); chord_charts (boolean); exclusions; id; lyrics (boolean); name; number_charts (boolean); numeral_charts (boolean)
Relationships: attachment_type_group -> AttachmentTypeGroup. Order: name

## AttachmentTypeGroup
Attributes: id; name; readonly (boolean). Order: name. Read-only.

## Attendance
Check-in attendance for a scheduled person (read-only).
Endpoints: GET /service_types/{st}/plans/{plan}/attendances; …/{id}
Attributes: check_ins_event_id; check_ins_event_period_id; checked_in_at; id
Relationships: plan_time -> PlanTime; plan_person -> PlanPerson

## AvailableSignup
Signups available to a person (read-only).
Endpoints: GET /people/{person_id}/available_signups [filter: current_organization]; …/{id}
Attributes: id; organization_name; planning_center_url; service_type_name; signups_available (boolean)
Relationships: organization, person, service_type. Include: signup_sheets
Associations: signup_sheets -> SignupSheet

## Blockout
A blockout date range with optional recurrence.
Endpoints: GET /people/{person_id}/blockouts [filter: future, past]; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: created_at; description; ends_at; group_identifier; id; organization_name; reason; repeat_frequency (no_repeat | every_1 … every_8); repeat_interval (exact_day_of_month | week_of_month_1 | week_of_month_2 | week_of_month_3 | week_of_month_4 | week_of_month_last); repeat_period (daily | weekly | monthly | yearly); repeat_until (date); settings; share (boolean); starts_at; time_zone; updated_at
Relationships: person -> Person; organization -> Organization
Where: group_identifier
Associations: blockout_dates -> BlockoutDate; blockout_exceptions -> BlockoutException
Create/Update attrs: reason, repeat_frequency, repeat_interval, repeat_period, share, repeat_until, starts_at, ends_at

## BlockoutDate
The concrete dates generated by a blockout/recurrence, generated up to a year ahead (read-only).
Endpoints: GET /people/{person_id}/blockouts/{blockout_id}/blockout_dates; …/{id}
Attributes: ends_at (wall clock); ends_at_utc; group_identifier; id; reason; share (boolean); starts_at (wall clock); starts_at_utc; time_zone
Relationships: person -> Person; blockout -> Blockout

## BlockoutException
A single date excluded from a blockout's generated dates.
Endpoints: GET /people/{person_id}/blockouts/{blockout_id}/blockout_exceptions; …/{id}; POST …/blockout_exceptions
Attributes: created_at; date (date); id; updated_at
Create attrs: date

## BlockoutScheduleConflict
A schedule that conflicts with a blockout (read-only, returned in context).
Attributes: id; can_accept_partial; dates; organization_name; person_avatar; person_name; position_display_times; service_type_name; short_dates; sort_date; status; team_name; team_position_name
Relationships: organization, person, plan, plan_person, service_type

## Chat
Chat context for the current user (read-only). Endpoints: GET /chat
Attributes (all only with ?fields): group_identifiers (array); my_teams (array); payload; people (array); plans (array); teams (array); teams_i_lead (array); id

## Contributor
A person who contributed to a plan (read-only).
Endpoints: GET /service_types/{st}/plans/{plan}/contributors; …/{id}
Attributes: contributable_action; contributable_category; contributable_type; created_at; full_name; id; photo_thumbnail_url; updated_at
Relationships: plan -> Plan; person -> Person. Order: created_at, updated_at

## CustomSlide
Text for display on a screen, attached to an item.
Endpoints: GET /service_types/{st}/plans/{plan}/items/{item_id}/custom_slides; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: body; enabled (boolean); id; label; order (integer)
Relationships: item -> Item; attachment -> Attachment
Create/Update attrs: body, enabled, label, order

## Email
A person's email as seen by Services (read-only here; edit in People).
Endpoints: GET /people/{person_id}/emails; …/{id}
Attributes: address; id; primary (boolean)

## EmailTemplate
Endpoints: GET /email_templates; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: created_at; html_body; id; kind; subject; updated_at
Relationships: template_owner -> Organization
Actions: render POST /email_templates/{id}/render — body `{"data":{"attributes":{"format":"html"|"text"},"relationships":{"person":{"data":{"type":"Person","id":"…"}}}}}` → EmailTemplateRenderedResponse
Create attrs: html_body, subject, kind. Update attrs: html_body, subject

## EmailTemplateRenderedResponse
Result of EmailTemplate render. Attributes: body; id; subject. Relationships: person; email_template

## Folder
Container for Service Types or other Folders.
Endpoints: GET /folders; …/{id}; POST /folders; PATCH /folders/{id}; DELETE /folders/{id}
Attributes: container; created_at; id; name; updated_at
Relationships: ancestors -> Folder; parent -> Folder; campus -> Campus
Include: service_types. Order: name. Where: parent_id (integer)
Associations: folders -> Folder; service_types -> ServiceType
Reachable from: /folders (Organization); /folders/{folder_id}/folders; /tag_groups/{tag_group_id}/folder
Create/Update attrs: name, parent_id, campus_id

## FolderPath
The folder path of a folder (read-only). Attributes: id; path (array)

## Item
An item in a plan (song, media, header, or generic item).
Endpoints: GET /service_types/{st}/plans/{plan}/items; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: created_at; custom_arrangement_sequence (array of section labels); custom_arrangement_sequence_full (array); custom_arrangement_sequence_short (array); description; html_details; id; item_type (string: song | header | media | item — settable only on create and only `header` can be passed; song items come from song_id, media items from attaching video media); key_name; length (integer, seconds); sequence (integer); service_position (pre | post | during); title; updated_at
Relationships: plan -> Plan; song -> Song; arrangement -> Arrangement; key -> Key; selected_layout -> Layout; selected_background -> Attachment
Include: arrangement*, item_assignments, item_notes, item_times, key*, media*, selected_attachment*, song*
Associations: arrangement; attachments; custom_slides; item_assignments; item_notes; item_times; key; media; selected_attachment; selected_background; song
Reachable from: /service_types/{st}/plans/{plan}/items (Plan); /service_types/{st}/plan_templates/{tpl}/items (PlanTemplate); /series/{series_id}/plans/{plan}/live/{live_id}/items (Live); /songs/{song_id}/last_scheduled_item (Song; requires `service_type` query param)
Create: POST …/items — attrs: arrangement_id, custom_arrangement_sequence, description, html_details, key_id, length, selected_layout_id, service_position, song_id, title, item_type, sequence
Update: PATCH …/items/{id} — same minus item_type, sequence (reorder via Plan `item_reorder` action)
Delete: DELETE …/items/{id}

## ItemAssignment
Assignment of a person or position to a plan item.
Endpoints: GET …/items/{item_id}/item_assignments; …/{id}; POST; DELETE …/{id}
Attributes: assignable_type (Person | TeamPosition); id
Relationships: plan; item; assignable (Person | TeamPosition)
Create attrs: assignable_type, assignable_id

## ItemNote
A plan item note in a category. Category is set only on create (delete + recreate to change it).
Endpoints: GET …/items/{item_id}/item_notes; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: category_name; content; created_at; id; updated_at
Relationships: item_note_category -> ItemNoteCategory (required on create); item -> Item. Include: item_note_category*
Create attrs: content, item_note_category_id. Update attrs: content

## ItemNoteCategory
Category of item notes for a Service Type (read-only).
Endpoints: GET /service_types/{st}/item_note_categories; …/{id}
Attributes: created_at; deleted_at; frequently_used (boolean); id; name; sequence; updated_at

## ItemTime
Timing of an item within a plan time (read-only).
Endpoints: GET …/items/{item_id}/item_times; …/{id}
Attributes: exclude (boolean); id; length; length_offset; live_end_at; live_start_at
Relationships: item; plan_time; plan
Reachable from: items/{item_id}/item_times; live/{live_id}/current_item_time | next_item_time

## Key
A pitch center for an arrangement.
Endpoints: GET /songs/{song_id}/arrangements/{arrangement_id}/keys; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: alternate_keys (array of {name, key}); created_at; ending_key (Ab A A# Bb B C C# Db D D# Eb E F F# Gb G G#, minor adds "m"); ending_minor (boolean); id; name; starting_key (same enum); starting_minor (boolean); updated_at
Relationships: arrangement -> Arrangement. Order: created_at, updated_at
Associations: attachments -> Attachment
Create/Update attrs: alternate_keys, ending_key, name, starting_key

## Live
Services LIVE state for a plan.
Endpoints: GET /service_types/{st}/plans/{plan}/live; …/{id}; (POST/PATCH/DELETE documented but with no attributes)
Attributes: can_chat; can_control; can_control_video_feed; can_take_control (booleans); chat_room_channel; dates; id; live_channel; series_title; title
Include: controller, current_item_time, items, next_item_time, service_type
Associations: controller -> Person; current_item_time -> ItemTime; items -> Item; next_item_time -> ItemTime; service_type -> ServiceType; watchable_plans -> Plan
Actions: go_to_next_item POST …/live/{id}/go_to_next_item; go_to_previous_item POST …/go_to_previous_item; toggle_control POST …/toggle_control

## LiveController
A person allowed to control LIVE without the usual permissions (read-only).
Endpoints: GET /service_types/{st}/live_controllers; …/{id}
Attributes: created_at; full_name; id; photo_thumbnail_url; updated_at. Relationships: person. Order: created_at, updated_at

## Media
A piece of media (video, audio, image, document…).
Endpoints: GET /media [filter: archived, not_archived, audio, background_audio, background_image, background_video, countdown, curriculum, document, drama, image, powerpoint, song_video, video]; …/{id}; POST /media; PATCH /media/{id}; DELETE /media/{id}
Attributes: created_at; creator_name; id; image_url; length; media_type (audio | background_audio | background_image | background_video | countdown | curriculum | document | drama | image | powerpoint | song_video | video); media_type_name; preview_content_type; preview_file_name; preview_file_size; preview_updated_at; preview_url; themes; thumbnail_content_type; thumbnail_file_name; thumbnail_file_size; thumbnail_updated_at; thumbnail_url; title; updated_at
Include: attachments. Order: created_at, title, updated_at. Where: creator_name, id, themes, title
Associations: attachments -> Attachment; media_schedules -> MediaSchedule; tags -> Tag
Reachable from: /media (Organization); …/items/{item_id}/media (Item)
Actions: archive POST /media/{id}/archive (optional `time` ISO 8601 attribute to schedule; type MediaArchive); unarchive POST /media/{id}/unarchive; assign_tags POST /media/{id}/assign_tags (TagAssignment, replaces all tags, 204)
Create/Update attrs: media_type, title, creator_name, themes

## MediaSchedule
Where a media item is scheduled (read-only).
Endpoints: GET /media/{media_id}/media_schedules; …/{id}
Attributes: id; plan_dates; plan_short_dates; plan_sort_date; service_type_name. Relationships: plan; service_type

## NeededPosition
Unfilled positions needed for a team in a plan.
Endpoints: GET /service_types/{st}/plans/{plan}/needed_positions; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: id; quantity (integer); scheduled_to; team_position_name
Relationships: team -> Team; plan -> Plan; time -> PlanTime; time_preference_option -> TimePreferenceOption. Include: team*, time*
Associations: team -> Team; time -> PlanTime
Create attrs: quantity, time_id, time_preference_option_id (+ team via relationship/include). Update attrs: quantity

## Organization
Account-level settings. Endpoints: GET /services/v2
Attributes: allow_mp3_download; beta; calendar_starts_on_sunday; ccli; ccli_auto_reporting_enabled; ccli_connected; ccli_reporting_enabled; created_at; date_format (US | EU); extra_file_storage_allowed; file_storage_exceeded; file_storage_extra_charges; file_storage_extra_enabled; file_storage_size; file_storage_size_used; id; legacy_id; music_stand_enabled; name; owner_name; people_allowed; people_remaining; projector_enabled; rehearsal_mix_enabled; rehearsal_pack_connected; required_to_set_download_permission (editor | administrator | site_administrator); secret; time_zone; twenty_four_hour_time; updated_at
Associations (top-level collections): attachment_types; chat; email_templates; folders; media [filters above]; people; report_templates [filter: matrix, people, plans, without_defaults]; series; plans; service_types [filter: no_parent]; songs; tag_groups [filter: arrangement, media, person, song]; teams [filter: editable, service_types]

## Person
An individual in Services (same id as People).
Endpoints: GET /people; GET /people/{id}; PATCH /people/{id}; GET /me
Attributes: access_media_attachments; access_plan_attachments; access_song_attachments (booleans); anniversary (date); archived (boolean); archived_at; assigned_to_rehearsal_team (boolean); birthdate (date); can_edit_all_people; can_search; can_view_all_people (booleans); created_at; facebook_id (deprecated); first_name; full_name; given_name; ical_code; id; last_name; legacy_id (v1 id); logged_in_at; max_permissions; max_plan_permissions; me_tab; media_permissions (Scheduled Viewer | Viewer | Editor | Administrator); media_tab; middle_name; name_prefix; name_suffix; nickname; notes; onboardings (array); passed_background_check (boolean); people_tab; permissions (deprecated → plan_permissions); person_permissions (only with ?fields); photo_thumbnail_url; photo_url; plan_permissions (Archived | Scheduled Viewer | Viewer | Scheduler | Editor | Administrator); plans_tab; praise_charts_enabled; preferred_app; preferred_max_plans_per_day; preferred_max_plans_per_month; profile_name (only with ?fields); signature (only with ?fields); site_administrator; song_permissions (Scheduled Viewer | Viewer | Editor | Administrator); songs_tab; status; updated_at
Relationships: created_by, updated_by -> Person; current_folder -> Folder
Include: emails, tags, team_leaders
Order: created_at, first_name, last_name, updated_at. Where: assigned_to_rehearsal_team (boolean), legacy_id
Associations: available_signups [filter: current_organization]; blockouts [filter: future, past]; emails; person_team_position_assignments [filter: not_archived, not_deleted]; plan_people -> PlanPerson; schedules -> Schedule [filter: after, all, before, future, not_across_organizations, past, with_declined]; scheduling_preferences; tags; team_leaders [filter: not_archived, not_deleted]; text_settings
Reachable from: /people (Organization); /teams/{team_id}/people; /people/{person_id}/team_leaders/{tl}/people; plan_people/{id}/person; schedules/{id}/respond_to; person_team_position_assignments/{id}/person; live/{id}/controller
Actions: assign_tags POST /people/{id}/assign_tags (TagAssignment, replaces all, 204); collapse_service_types / expand_service_types POST /people/{id}/collapse_service_types | expand_service_types (body type CollapseServiceTypes/ExpandServiceTypes with service_type relationship list; 204)
Update: PATCH /people/{id} — attrs: preferred_app, onboardings, access_media_attachments, access_plan_attachments, access_song_attachments, current_folder_id, media_permissions, permissions, person_permissions, plan_permissions, song_permissions
No create/delete here — people are created in People.

## PersonTeamPositionAssignment
A person's assignment to a position within a team (team membership).
Endpoints: GET /service_types/{st}/team_positions/{tp}/person_team_position_assignments; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: created_at; id; preferred_weeks (array, used when schedule_preference = "Choose Weeks", e.g. ['1','3','5']); schedule_preference (Unavailable | Every week | Every other week | Every 3rd week | Every 4th week | Every 5th week | Every 6th week | Once a quarter | Once a month | Twice a month | Three times a month | Choose Weeks); updated_at
Relationships: person -> Person; team_position -> TeamPosition; time_preference_options -> TimePreferenceOption (to_many). Include: person*, team_position*
Order: first_name, last_name
Associations: person -> Person; team_position -> TeamPosition
Reachable from: /people/{person_id}/person_team_position_assignments [filter: not_archived, not_deleted]; /teams/{team_id}/person_team_position_assignments; /service_types/{st}/team_positions/{tp}/person_team_position_assignments [filter: time_preference_options — pass `time_preference_option_ids[]`; id "none" = people with no preferred times]
Create attrs: schedule_preference, preferred_weeks, time_preference_option_ids, person_id. Update attrs: schedule_preference, preferred_weeks, time_preference_option_ids

## Plan
A single plan (a service) within a Service Type.
Endpoints: GET /service_types/{st}/plans [filter: after, before, future, no_dates, past]; …/{id}; POST; PATCH …/{id}; DELETE …/{id}; GET /service_types/{st}/unscoped_plans [filter: deleted]
Attributes: can_view_order (boolean); created_at; dates (string, all service-time dates); files_expire_at (15 days after last service time); id; items_count; last_time_at; multi_day (boolean); needed_positions_count; other_time_count; permissions (current user's perms on the ServiceType); plan_notes_count; plan_people_count; planning_center_url; prefers_order_view; public (boolean); public_by_schedule (boolean); rehearsable; rehearsal_time_count; reminders_disabled (boolean); series_title; service_time_count; short_dates; sort_date (first service time; falls back to rehearsal, other, then now); title; total_length (seconds, excludes pre/post items); updated_at
Relationships: service_type -> ServiceType; previous_plan, next_plan -> Plan; series -> Series; created_by, updated_by -> Person; linked_publishing_episode; attachment_types (to_many)
Include: contributors, my_schedules, plan_times, series*
Order: created_at, sort_date, title, updated_at. Where: created_at, id, series_title, title, updated_at
Associations: all_attachments [filter: attachable_type, extensions]; attachments; attendances; contributors; items; live; my_schedules -> Schedule; needed_positions; next_plan; notes -> PlanNote [filter: team]; plan_times; previous_plan; series; signup_teams -> Team; team_members -> PlanPerson [filter: confirmed, not_archived, not_declined, not_deleted]
Reachable from: /service_types/{st}/plans (ServiceType); /series/{series_id}/plans (Series); /people/{person_id}/plan_people/{pp}/plan; plans/{id}/next_plan | previous_plan; live/{id}/watchable_plans
Actions:
- import POST /service_types/{st}/plans/{id}/import — attrs: source_id (Plan or PlanTemplate id), additional_target_ids (array, async), copy_items, copy_people, copy_notes (booleans, default false), team_ids (array; nil = all teams when copy_people). Permissions: scheduler on target; source Plan needs viewer, source PlanTemplate needs scheduler; schedulers copy people only for teams they lead; copy_items/copy_notes need editor. Returns PlanImportMetadata.
- item_reorder POST …/plans/{id}/item_reorder — body `{"data":{"type":"PlanItemReorder","attributes":{"sequence":["item_id",…]}}}` → 204
- autoschedule POST …/plans/{id}/autoschedule — body type "Autoschedule" with `team` relationship → PlanPersonAutoschedule collection
Create: POST /service_types/{st}/plans — attrs: title, public, series_id, series_title; rels: series
Update: PATCH …/plans/{id} — attrs: title, public, series_id, series_title, reminders_disabled
Delete: DELETE …/plans/{id}
Note: dates come from PlanTimes, not Plan attributes; create the plan, then POST plan_times.

## PlanImportMetadata
Result of Plan/PlanTemplate import. Attributes: any_plan_people_missing_background_check (boolean); id

## PlanNote
A note on a plan, in a category.
Endpoints: GET /service_types/{st}/plans/{plan}/notes [filter: team]; …/{id}; POST; PATCH …/{id}; DELETE …/{id} (also under plan_templates/{tpl}/notes)
Attributes: category_name; content; created_at; id; updated_at
Relationships: created_by -> Person; plan_note_category -> PlanNoteCategory (required); teams. Include: plan_note_category*
Order/Where: created_at, updated_at
Create/Update attrs: content; rel: plan_note_category

## PlanNoteCategory
Plan note categories for a Service Type (read-only).
Endpoints: GET /service_types/{st}/plan_note_categories; …/{id}
Attributes: created_at; deleted_at; id; name; sequence; updated_at

## PlanPerson
A person scheduled within a plan (the schedule request / assignment).
Endpoints: GET /service_types/{st}/plans/{plan}/team_members [filter: confirmed, not_archived, not_declined, not_deleted]; GET /people/{person_id}/plan_people; …/{id}; POST /service_types/{st}/plans/{plan}/team_members; PATCH /people/{person_id}/plan_people/{id}; DELETE /people/{person_id}/plan_people/{id}
Attributes: can_accept_partial (boolean); created_at; decline_reason; id; name; notes; notification_changed_at; notification_changed_by_name; notification_prepared_at; notification_read_at; notification_sender_name; notification_sent_at; photo_thumbnail; prepare_notification (boolean); scheduled_by_is_eligible_for_responds_to (only with ?fields); scheduled_by_name (only with ?fields); status (C | U | D | Confirmed | Unconfirmed | Declined); status_updated_at; team_position_name; updated_at
Relationships: person; plan; scheduled_by -> Person; service_type; team; responds_to -> Person; times, service_times -> PlanTime (to_many); time_preference_options (to_many)
Include: declined_plan_times*, person*, plan*, team*
Where: team_id (integer)
Associations: declined_plan_times -> PlanTime; person; plan; plan_person_times -> PlanPersonTime; plan_times -> PlanTime; team
Create: POST …/team_members — attrs: person_id, team_id, status, decline_reason, notes, team_position_name, responds_to_id, prepare_notification, notification_prepared_at
Update: PATCH /people/{person_id}/plan_people/{id} — same attrs
Delete: DELETE /people/{person_id}/plan_people/{id}
Note: creating with `status: "U"` and `prepare_notification: true` queues a schedule request email; the person accepts/declines via Schedule actions.

## PlanPersonTime
Per-time status for a split-team assignment (read-only).
Endpoints: GET /people/{person_id}/plan_people/{pp}/plan_person_times; GET /service_types/{st}/plan_person_times
Attributes: created_at; id; status; updated_at. Relationships: plan_time; plan; plan_person. Order: updated_at

## PlanTemplate
Endpoints: GET /service_types/{st}/plan_templates; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: can_view_order; created_at; id; item_count; multi_day; name; note_count; prefers_order_view; rehearsable; team_count; updated_at
Relationships: service_type; created_by; updated_by
Order: created_at, item_count, name, note_count, team_count, updated_at
Associations: items -> Item; notes -> PlanNote; team_members -> PlanPerson [filter: confirmed, not_archived, not_declined, not_deleted]
Actions: import POST …/plan_templates/{id}/import (same payload/permissions as Plan import; source_id may be a Plan or PlanTemplate); item_reorder POST …/plan_templates/{id}/item_reorder (PlanItemReorder)
Create/Update attrs: name

## PlanTime
A time (service, rehearsal, other) in a plan.
Endpoints: GET /service_types/{st}/plans/{plan}/plan_times; GET /service_types/{st}/plan_times [filter: future, named, not_deleted, past]; …/{id}; POST /service_types/{st}/plans/{plan}/plan_times; PATCH /service_types/{st}/plan_times/{id}; DELETE /service_types/{st}/plan_times/{id}
Attributes: created_at; ends_at; id; live_ends_at; live_starts_at; name; recorded (boolean); scheduled_team_ids (array, only with ?fields); starts_at; team_reminders (array of {team_id: days 0–7}); time_type (rehearsal | service | other); updated_at
Relationships: assigned_teams -> Team (to_many); assigned_positions -> TeamPosition (to_many)
Include: split_team_rehearsal_assignments. Order: starts_at. Where: time_type
Associations: split_team_rehearsal_assignments -> SplitTeamRehearsalAssignment
Reachable from: plans/{plan}/plan_times; service_types/{st}/plan_times; plan_people/{pp}/plan_times | declined_plan_times; schedules/{s}/plan_times | declined_plan_times; needed_positions/{np}/time
Create/Update attrs: starts_at, ends_at, name, time_type, team_reminders

## PublicView
Options for a public plan page (read-only). Endpoints: GET /service_types/{st}/public_view
Attributes (booleans): amazon; headers; item_descriptions; item_lengths; itunes; media_items; regular_items; series_and_plan_titles; series_artwork; service_times; song_items; spotify; vimeo; youtube; id

## ReportTemplate
Endpoints: GET /report_templates [filter: matrix, people, plans, without_defaults]; …/{id} (read-only)
Attributes: body; default (boolean); id; title; type (ReportMatrix | ReportPeople | ReportPlan)

## Schedule
A PlanPerson as seen in a user's schedule (with display data); used to accept/decline.
Endpoints: GET /people/{person_id}/schedules [filter: after (ISO date), all, before (ISO date), future, not_across_organizations, past, with_declined]; …/{id}; GET /service_types/{st}/plans/{plan}/my_schedules
Attributes: can_accept_partial; can_accept_partial_one_time; can_rehearse; dates; decline_reason; id; organization_name; organization_time_zone; organization_twenty_four_hour_time; person_name; plan_visible (boolean); plan_visible_to_me (boolean); position_display_times; reschedule_declines; responds_to_name; service_type_name; short_dates; sort_date; status; team_name; team_position_name
Relationships: person; service_type; organization; plan_person -> PlanPerson; plan; team; responds_to_person -> Person; times -> PlanTime (to_many)
Include: plan_times. Order: starts_at. Where: plan_id (integer)
Associations: declined_plan_times -> PlanTime; plan_times -> PlanTime; respond_to -> Person; team -> Team
Actions:
- accept POST /people/{person_id}/schedules/{id}/accept — empty JSON body accepts all times. To accept some and decline others: `{"data":{"type":"ScheduleAccept","attributes":{"reason":"…"},"relationships":{"declined_plan_times":{"data":[{"type":"PlanTime","id":"…"}]}}}}`. If every time is declined it falls through to decline (optional replacement_id, replacement_confirmed).
- decline POST /people/{person_id}/schedules/{id}/decline — `{"data":{"type":"ScheduleDecline","attributes":{"reason":"…"},"relationships":null}}`; optional attrs replacement_id (account_center_id) and replacement_confirmed (true skips confirmation) when the team reschedules declines with replacements.

## ScheduledPerson
A person already scheduled to a signup sheet (read-only).
Endpoints: GET /people/{person_id}/available_signups/{as}/signup_sheets/{ss}/scheduled_people; …/{id}
Attributes: full_name; id; status; thumbnail. Relationships: person; signup_sheet

## SchedulingPreference
Household member scheduling preference (read-only).
Endpoints: GET /people/{person_id}/scheduling_preferences; …/{id}
Attributes: id; preference. Relationships: household_member -> Person

## Series
Groups plans with related messages (across service types). A series is not created until artwork is added to a plan; Plan.series_title covers series without artwork.
Endpoints: GET /series; …/{id} (read-only)
Attributes: artwork_content_type; artwork_file_name; artwork_file_size; artwork_for_dashboard; artwork_for_mobile; artwork_for_plan; artwork_original; created_at; has_artwork (boolean); id; title; updated_at
Order: created_at. Where: title
Associations: plans -> Plan
Reachable from: /series (Organization); /service_types/{st}/plans/{plan}/series

## ServiceType
A container for plans (e.g. "Sunday Morning").
Endpoints: GET /service_types [filter: no_parent]; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: archived_at; attachment_types_enabled (boolean); background_check_permissions; comment_permissions (deprecated); created_at; custom_item_types (array of {name, color}; colors #e8f6df #e0f7ff #e6e2fd #ffe0e8 #ffedd1 #cfcfcf #eaebeb #ffffff); deleted_at; frequency; id; last_plan_from; name; permissions; scheduled_publish (boolean); sequence; standard_item_types (array of {name: Header|Song|Media, color}); updated_at
Relationships: parent -> Folder
Include: time_preference_options. Order: name, sequence. Where: id, name, parent_id (integer)
Associations: attachments; item_note_categories; live_controllers; plan_note_categories; plan_person_times; plan_templates; plan_times [filter: future, named, not_deleted, past]; plans [filter: after, before, future, no_dates, past]; public_view; team_positions; teams; time_preference_options; unscoped_plans [filter: deleted]
Reachable from: /service_types (Organization); /folders/{folder_id}/service_types; /teams/{team_id}/service_types; live/{id}/service_type
Actions: create_plans POST /service_types/{id}/create_plans — attrs: count (integer, max 12, default 1), copy_items, copy_people, copy_notes (booleans), team_ids (array), as_template (boolean), base_date (ISO 8601 date); relationships: plan (source for times/items/people/notes) and/or template (source for items/people/notes, takes precedence over plan)
Create/Update attrs: attachment_types_enabled, background_check_permissions, custom_item_types, frequency, last_plan_from, name, scheduled_publish, sequence, standard_item_types; rel: parent_id

## ServiceTypePath
Folder path of a Service Type (read-only). Attributes: id; path (array)

## SignupSheet
A position a person can sign up for.
Endpoints: GET /people/{person_id}/available_signups/{as}/signup_sheets; …/{id}
Attributes: display_times; group_key; id; plan_title; position_name; sort_date; sort_index; team_name; title
Relationships: plan; team_position; team. Include: scheduled_people, signup_sheet_metadata
Associations: scheduled_people -> ScheduledPerson; signup_sheet_metadata -> SignupSheetMetadata
Actions: accept POST …/signup_sheets/{id}/accept (no payload)

## SignupSheetMetadata
Collection-only. Attributes: conflicts (hash); ends_at; id; starts_at; time_name; time_type. Relationships: plan_time

## SkippedAttachment
Attributes: id; skipped (boolean). Relationships: person; attachment

## Song
Endpoints: GET /songs; …/{id}; POST /songs; PATCH /songs/{id}; DELETE /songs/{id}
Attributes: admin; author; ccli_number (integer); copyright; created_at; hidden (boolean); id; last_scheduled_at; last_scheduled_short_dates; notes; themes; title (passing a CCLI number on create lets Services fetch metadata); updated_at
Order: created_at, last_scheduled_at, title, updated_at. Where: author, ccli_number (integer), hidden (boolean), themes, title
Associations: arrangements; attachments; last_scheduled_item -> Item (requires `service_type` query param); song_schedules -> SongSchedule [filter: after, before, most_recent, most_recent_with_upcoming, three_most_recent]; tags; unscoped_arrangements
Reachable from: /songs (Organization); …/items/{item_id}/song
Actions: assign_tags POST /songs/{id}/assign_tags (TagAssignment, replaces all tags, 204)
Create/Update attrs: title, admin, author, copyright, ccli_number, hidden, themes

## SongSchedule
Upcoming/past schedules for a song (read-only).
Endpoints: GET /songs/{song_id}/song_schedules [filter: after, before (ISO dates), most_recent (requires `amount`), most_recent_with_upcoming (requires `amount`), three_most_recent]; …/{id}
Attributes: arrangement_name; id; key_name; plan_dates; plan_sort_date; plan_visible (boolean); service_type_name
Relationships: arrangement; key; plan; service_type; item. Order: plan_sort_date

## SongbookStatus
Status of an in-progress songbook generation. Attributes: id; status; status_code; status_token; url (set when FINISHED)

## SplitTeamRehearsalAssignment
Maps a split team to time preference options for rehearsal/other times.
Endpoints: GET /service_types/{st}/plan_times/{pt}/split_team_rehearsal_assignments; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: id; schedule_special_service_times (boolean)
Relationships: team -> Team; time_preference_options -> TimePreferenceOption (to_many). Include: none
Associations: team -> Team
Create/Update attrs: schedule_special_service_times

## Tag
A tag in a tag group (read-only; assign via *_tags actions).
Endpoints: GET /tag_groups/{tag_group_id}/tags; …/{id}
Attributes: id; name. Relationships: tag_group -> TagGroup
Reachable from: tag_groups/{id}/tags; songs/{id}/tags; songs/{id}/arrangements/{id}/tags; media/{id}/tags; people/{id}/tags; service_types/{st}/team_positions/{tp}/tags

## TagGroup
Endpoints: GET /tag_groups [filter: arrangement, media, person, song]; …/{id} (read-only)
Attributes: allow_multiple_selections (boolean); id; name; required (boolean); service_type_folder_name; tags_for (person | song | arrangement | media)
Relationships: folder -> Folder; tags -> Tag (to_many); organization. Include: folder, tags. Where: name, tags_for
Associations: folder -> Folder; tags -> Tag

## Team
A team within a Service Type.
Endpoints: GET /teams [filter: editable, service_types]; GET /service_types/{st}/teams; …/{id}; POST /service_types/{st}/teams
Attributes: archived_at; assigned_directly (boolean); created_at; default_prepare_notifications (boolean); default_status; deleted_at; direct_messages_enabled (boolean); id; last_plan_from; name; rehearsal_team (boolean); schedule_to (plan | time — "time" = split team); secure_team (boolean); sequence; stage_color; stage_variant; updated_at; viewers_see (integer)
Relationships: service_type; default_responds_to -> Person (id 0 = "All Team Leaders"); service_types (to_many)
Include: people, person_team_position_assignments, service_types*, team_leaders, team_positions
Order: created_at, name, updated_at. Where: id, name
Associations: people -> Person; person_team_position_assignments; service_types; team_leaders -> TeamLeader; team_positions -> TeamPosition
Reachable from: /teams; /service_types/{st}/teams; plans/{plan}/signup_teams; plan_people/{pp}/team; schedules/{s}/team; needed_positions/{np}/team; team_leaders/{tl}/team; team_positions/{tp}/team; split_team_rehearsal_assignments/{id}/team
Create: POST /service_types/{st}/teams — attrs: name, archived_at, assigned_directly, deleted_at, rehearsal_team, secure_team, schedule_to, stage_color, stage_variant, service_type_ids; rels: service_types
(No update/delete documented.)

## TeamLeader
A leader of a team (read-only).
Endpoints: GET /teams/{team_id}/team_leaders; GET /people/{person_id}/team_leaders [filter: not_archived, not_deleted]; …/{id}
Attributes: id; send_responses_for_accepts; send_responses_for_blockouts; send_responses_for_declines (booleans)
Relationships: person; team. Include: people, team. Order: first_name, last_name
Associations: people -> Person; team -> Team

## TeamPosition
A position within a team (read-only via API).
Endpoints: GET /service_types/{st}/team_positions; GET /teams/{team_id}/team_positions; …/{id}
Attributes: id; name; negative_tag_groups (array); sequence; tag_groups (array); tags (array)
Relationships: team -> Team; attachment_types (to_many); tags (to_many). Include: tags, team. Order: name
Associations: person_team_position_assignments [filter: time_preference_options]; tags; team

## TextSetting
A person's SMS settings.
Endpoints: GET /people/{person_id}/text_settings; …/{id}; PATCH …/{id}
Attributes: carrier; display_number; general_emails_enabled; id; normalized_number; reminders_enabled; scheduling_replies_enabled; scheduling_requests_enabled
Update attrs: general_emails_enabled, reminders_enabled, scheduling_replies_enabled, scheduling_requests_enabled

## TimePreferenceOption
A service time a person prefers to be scheduled to (read-only).
Endpoints: GET /service_types/{st}/time_preference_options; …/{id}
Attributes: created_at; day_of_week (integer); description; id; minute_of_day (0–2359); sort_index; starts_at; time_type; updated_at
Order: day_of_week, hour_of_day

## Zoom
Zoom level for an attachment on a device.
Endpoints: GET /media/{media_id}/attachments/{attachment_id}/zooms (or any attachment parent path); …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: aspect_ratio (float, 3 dp); id; x_offset (float, % of width); y_offset (float, % of height); zoom_level (float 1.0–5.0)
Relationships: person; attachable; attachment
Create attrs: zoom_level, x_offset, y_offset, aspect_ratio. Update attrs: zoom_level, x_offset, y_offset
