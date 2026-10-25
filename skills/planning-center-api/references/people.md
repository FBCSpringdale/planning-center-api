# People API (people/v2)

Base URL: `https://api.planningcenteronline.com/people/v2`
Documented version: `2026-10-05` (send `X-PCO-API-Version: 2026-10-05` to pin). OAuth scope: `people`.
Version history (newest first): 2026-10-05, 2026-06-04, 2025-11-10, 2025-07-17, 2025-07-02, 2025-03-20, 2024-09-12, 2023-03-21, 2023-02-15, 2022-07-14, 2022-01-28, 2022-01-05, 2021-08-17, 2020-07-22, 2020-04-06, 2019-10-10, 2019-01-14, 2018-08-01.
Latest breaking change (2026-10-05): `Person.resource_permission_flags` replaced by `Person.selective_access`.
OpenAPI: `https://api.planningcenteronline.com/people/v2/open_api/2026-10-05`
Docs: `https://api.planningcenteronline.com/docs/apps/people/versions/2026-10-05/vertices/<snake_case_resource>`

People is the hub product: every other product's `Person` resource is a projection of a People `Person` with the same `id`. Contact info (emails, phone numbers, addresses), households, custom fields, forms, lists, workflows and notes all live here.

Conventions used below:
- `Endpoints` lists the canonical collection/member paths (list, read, create, update, delete). Paths are relative to the base URL.
- `Include` = valid `?include=` values. `*` = also assignable as a relationship on create/update.
- `Where` = `?where[attr]=value` attributes (types shown). `Order` = `?order=attr` (prefix `-` to reverse).
- `Associations` = child endpoints hanging off a member: `GET {member}/<suffix>`. `[filter: a, b]` = values accepted by `?filter=`.
- `Reachable from` = every parent path that returns this resource (how you traverse to it). Filters shown apply to that parent path.
- All collections paginate with `per_page` (1–100, default 25) and `offset`.
- "permissions: n/d" = not documented on the page; the acting user's People permission level still applies.

## Resource index (67)

Address, App, BackgroundCheck, BirthdayPeople, Campus, Carrier, Condition, ConnectedPerson, CustomSender, Email, FieldDatum, FieldDefinition, FieldOption, Form, FormCategory, FormField, FormFieldCondition, FormFieldOption, FormSubmission, FormSubmissionValue, Grade, Household, HouseholdMembership, InactiveReason, List, ListCategory, ListResult, ListShare, ListStar, MailchimpSyncStatus, MaritalStatus, MembershipType, Message, MessageGroup, NamePrefix, NameSuffix, Note, NoteCategory, NoteCategoryShare, NoteCategorySubscription, Organization, OrganizationStatistics, PeopleImport, PeopleImportConflict, PeopleImportHistory, Person, PersonApp, PersonMerger, PhoneNumber, PlatformNotification, Report, Rule, SchoolOption, ServiceTime, SocialProfile, SpamEmailAddress, Tab, Workflow, WorkflowAssigneeSummary, WorkflowAssigneeWorkflowSummary, WorkflowCard, WorkflowCardActivity, WorkflowCardNote, WorkflowCategory, WorkflowShare, WorkflowStep, WorkflowStepAssigneeSummary

## Relationship map (how the models connect)

```
Organization
 ├─ people (Person) ──┬─ emails (Email), phone_numbers (PhoneNumber), addresses (Address), social_profiles (SocialProfile)
 │                    ├─ household_memberships (HouseholdMembership) ── household (Household) ── people (Person)
 │                    ├─ field_data (FieldDatum) ── field_definition (FieldDefinition) ── tab (Tab); field_option (FieldOption)
 │                    ├─ notes (Note) ── category (NoteCategory) ── shares (NoteCategoryShare), subscriptions (NoteCategorySubscription)
 │                    ├─ workflow_cards (WorkflowCard) ── workflow (Workflow), current_step (WorkflowStep), activities, notes (WorkflowCardNote)
 │                    ├─ background_checks (BackgroundCheck)
 │                    ├─ person_apps (PersonApp) ── app (App)
 │                    ├─ messages (Message) ── message_group (MessageGroup)
 │                    ├─ primary_campus (Campus), school (SchoolOption), marital_status, name_prefix, name_suffix, inactive_reason
 │                    └─ connected_people (ConnectedPerson), platform_notifications, workflow_shares, workflow_assignee_workflow_summaries
 ├─ campuses (Campus) ── service_times (ServiceTime), lists (List)
 ├─ lists (List) ── rules (Rule) ── conditions (Condition); people (Person); list_results (ListResult); shares (ListShare); star (ListStar); category (ListCategory); mailchimp_sync_status
 ├─ forms (Form) ── fields (FormField) ── options (FormFieldOption), form_field_conditions (FormFieldCondition)
 │               └─ form_submissions (FormSubmission) ── form_submission_values (FormSubmissionValue), person (Person)
 ├─ workflows (Workflow) ── steps (WorkflowStep) ── assignee_summaries; cards (WorkflowCard); shares (WorkflowShare); category (WorkflowCategory)
 ├─ tabs (Tab) ── field_definitions (FieldDefinition) ── field_options (FieldOption)
 ├─ households (Household) ── household_memberships (HouseholdMembership)
 ├─ people_imports (PeopleImport) ── conflicts (PeopleImportConflict), histories (PeopleImportHistory)
 ├─ message_groups (MessageGroup) ── messages (Message), app (App), from (Person)
 └─ lookup tables: marital_statuses, membership_types, name_prefixes, name_suffixes, inactive_reasons, school_options, carriers, apps, form_categories, list_categories, note_categories, reports, spam_email_addresses, person_mergers, stats, birthday_people, workflow_assignee_summaries
```

Polymorphic relationships to know: `FieldDatum.customizable` (currently only Person), `FormField.fieldable` (FieldDefinition | NoteCategory | Workflow), `FormFieldOption.optionable`, `WorkflowCard.assignee` (a Person).

---

## Address
A physical and/or mailing address for a person.
Endpoints: GET /addresses; GET /addresses/{id}; POST /people/{person_id}/addresses; PATCH /addresses/{id}; DELETE /addresses/{id}
Attributes: city (string); country_code (string); country_name (string); created_at (date_time); id; location (string); primary (boolean); state (string); street_line_1 (string); street_line_2 (string); updated_at (date_time); zip (string)
Relationships: person -> Person (to_one)
Include: none
Order: city, country_code, created_at, location, primary, state, street_line_1, street_line_2, updated_at, zip
Where: city, country_code, location, primary (boolean), state, street_line_1, street_line_2, zip
Associations: none
Reachable from: /addresses (Organization); /people/{person_id}/addresses (Person)
Create: POST /people/{person_id}/addresses — attrs: city, state, zip, country_code, location, primary, street_line_1, street_line_2
Update: PATCH /addresses/{id} — same attrs
Delete: DELETE /addresses/{id}

## App
One of the Planning Center apps an organization can subscribe to (Services, Registrations, …).
Endpoints: GET /apps; GET /apps/{id} (read-only)
Attributes: id; name (string); url (string)
Order: name, url
Where: name, url
Reachable from: /apps (Organization); /people/{person_id}/apps (Person); /people/{person_id}/person_apps/{person_app_id}/app (PersonApp); /message_groups/{message_group_id}/app (MessageGroup)

## BackgroundCheck
Background checks for a Person.
Endpoints: GET /background_checks; GET /background_checks/{id}; POST /people/{person_id}/background_checks; PATCH /background_checks/{id}; DELETE /background_checks/{id}
Attributes: completed_at (date_time, null until a completed status; blank on create = now); current (boolean); expires_on (date, blank = org expiration policy); id; note (string); report_url (string, should require auth); status (string: awaiting_applicant | expired_invitation | report_processing | needs_review | complete_clear | complete_not_clear | canceled); status_updated_at (date_time)
Relationships: person -> Person (to_one); created_by -> Person (to_one)
Include: created_by*, person*
Order: expires_on, status_updated_at
Where: expires_on (date), status_updated_at (date_time)
Associations: created_by -> Person; person -> Person
Reachable from: /background_checks (Organization) [filter: awaiting_applicant, canceled, complete_clear, complete_not_clear, current, expired, expired_invitation, needs_review, not_expired, report_processing]; /people/{person_id}/background_checks (Person) [same filters]
Create: POST /people/{person_id}/background_checks — attrs: note, status, report_url, expires_on, completed_at
Update: PATCH /background_checks/{id} — attrs: note, status, report_url, expires_on
Delete: DELETE /background_checks/{id}

## BirthdayPeople
Upcoming birthdays. Capped at the first 15 people with a birthday in the next 30 days, ordered by birthday ascending.
Endpoints: GET /birthday_people (read-only; per_page still capped at 15 total)
Attributes: id
Reachable from: /birthday_people (Organization)

## Campus
A location belonging to an Organization.
Endpoints: GET /campuses; GET /campuses/{id}; POST /campuses; PATCH /campuses/{id}; DELETE /campuses/{id}
Attributes: church_center_enabled (boolean); city; contact_email_address; country; created_at; date_format (integer); description; geolocation_set_manually (boolean); id; latitude (float); longitude (float); name; phone_number; state; street; time_zone; time_zone_raw (only with ?fields); twenty_four_hour_time (boolean); updated_at; website; zip
Relationships: organization -> Organization (to_one)
Include: lists, service_times*
Order: created_at, name, updated_at
Where: created_at, id, updated_at
Associations: lists -> List; service_times -> ServiceTime
Reachable from: /campuses (Organization); /people/{person_id}/primary_campus (Person); /forms/{form_id}/campus (Form); /lists/{list_id}/campus (List)
Create: POST /campuses — attrs: latitude, longitude, description, street, city, state, zip, country, phone_number, website, twenty_four_hour_time, date_format, church_center_enabled, contact_email_address, time_zone, geolocation_set_manually, name — permissions: Organization Administrator
Update: PATCH /campuses/{id} — same attrs — permissions: Organization Administrator
Delete: DELETE /campuses/{id} — permissions: Organization Administrator

## Carrier
Phone carrier lookup values (for SMS).
Endpoints: GET /carriers; GET /carriers/{id} (read-only)
Attributes: id; international (boolean); name (string); value (string)
Order: international, name
Reachable from: /carriers (Organization)

## Condition
An individual criterion used by a List Rule.
Endpoints: GET /lists/{list_id}/rules/{rule_id}/conditions; GET …/conditions/{id} (read-only)
Attributes: application (string); comparison (string); created_at; definition_class (string); definition_identifier (string); description (string); id; settings (string); updated_at
Relationships: created_by -> Person (to_one)
Include: created_by
Order: application, comparison, created_at, definition_class, definition_identifier, description, settings, updated_at
Where: application, comparison, created_at, definition_class, definition_identifier, description, settings, updated_at
Associations: created_by -> Person
Reachable from: /lists/{list_id}/rules/{rule_id}/conditions (Rule)

## ConnectedPerson
An account from a different organization linked to an account in this organization.
Endpoints: GET /people/{person_id}/connected_people; GET …/connected_people/{id} (read-only)
Attributes: id; first_name; gender; given_name; last_name; middle_name; nickname; organization_id; organization_name
Relationships: organization -> Organization (to_one)
Reachable from: /people/{person_id}/connected_people (Person)

## CustomSender
A sender identity usable when sending emails. Creating or updating the email address starts verification.
Endpoints (inferred — the docs page renders truncated paths `/people/v2` and `/people/v2/{id}`; the collection name is `custom_senders`): GET /custom_senders; GET /custom_senders/{id}; POST /custom_senders
Attributes: created_at; email_address (string); expired (boolean); id; name (string); updated_at; verification_requested_at (date_time); verification_status (string); verified (boolean); verified_at (date_time)
Relationships: custom_sender_shares -> CustomSenderShare
Order: created_at, name, updated_at, verification_requested_at, verified_at
Associations: custom_sender_shares -> CustomSenderShare
Create: POST /custom_senders — assignable attributes are not listed on the page; `name` and `email_address` are the only non-derived attributes. Creating/updating the email address begins verification. Verify with a `GET` first (`meta.can_query_by`) before relying on this in production.

## Email
An email address and location.
Endpoints: GET /emails; GET /emails/{id}; POST /people/{person_id}/emails; PATCH /emails/{id}; DELETE /emails/{id}
Attributes: address (string); blocked (boolean); created_at; id; location (string); primary (boolean); updated_at; verified (boolean)
Relationships: person -> Person (to_one)
Order: address, created_at, location, primary, updated_at
Where: address, blocked, created_at, location, primary, updated_at
Associations: person -> Person
Reachable from: /emails (Organization); /people/{person_id}/emails (Person)
Create: POST /people/{person_id}/emails — attrs: address, location, primary
Update: PATCH /emails/{id} — attrs: address, location, primary
Delete: DELETE /emails/{id}

## FieldDatum
A single piece of data stored for a custom field (the value of a FieldDefinition for a Person).
Endpoints: GET /field_data; GET /field_data/{id}; POST /people/{person_id}/field_data; PATCH /field_data/{id}; DELETE /field_data/{id}
Attributes: created_at; file (string); file_content_type; file_name; file_size (integer); id; updated_at; value (string)
Relationships: field_definition -> FieldDefinition (to_one); customizable -> Customizable (to_one; currently only Person)
Include: field_definition*, field_option, tab
Order: created_at, file, file_content_type, file_name, file_size, updated_at, value
Where: created_at, field_definition_id (integer), file, file_content_type, file_name, file_size, updated_at, value
Associations: field_definition -> FieldDefinition; field_option -> FieldOption; person -> Person; tab -> Tab
Reachable from: /field_data (Organization); /people/{person_id}/field_data (Person)
Create: POST /people/{person_id}/field_data — attrs: value, field_definition_id. For checkbox fields POST the option string as `value`; a new FieldOption is created if none matches. Valid options: GET /field_definitions/{field_definition_id}/field_options.
Update: PATCH /field_data/{id} — attrs: value, field_definition_id
Delete: DELETE /field_data/{id}. Unchecking a checkbox = DELETE /people/{person_id}/field_data/{field_datum_id}.

## FieldDefinition
A custom field: name, data type, etc.
Endpoints: GET /field_definitions; GET /field_definitions/{id}; POST /tabs/{tab_id}/field_definitions; PATCH /field_definitions/{id}; DELETE /field_definitions/{id}
Attributes: config (string; number fields accept min/max keys); data_type (string); deleted_at (date_time); id; name (string); sequence (integer); slug (string); tab_id
Relationships: tab -> Tab (to_one)
Include: field_options, tab*
Order: config, data_type, deleted_at, name, sequence, slug, tab_id
Where: config, data_type, deleted_at, name, sequence, slug, tab_id
Associations: field_options -> FieldOption; tab -> Tab
Reachable from: /field_definitions (Organization) [filter: include_deleted]; /tabs/{tab_id}/field_definitions (Tab) [filter: with_deleted]; /field_data/{field_datum_id}/field_definition (FieldDatum)
Create: POST /tabs/{tab_id}/field_definitions — attrs: data_type, name, sequence, slug, config, deleted_at; rels: tab
Update: PATCH /field_definitions/{id} — same
Delete: DELETE /field_definitions/{id} (sets deleted_at)

## FieldOption
An option for a custom field of type "select" or "checkboxes".
Endpoints: GET /field_definitions/{field_definition_id}/field_options; …/{id}; POST …/field_options; PATCH …/field_options/{id}; DELETE …/field_options/{id}
Attributes: id; sequence (integer); value (string)
Relationships: field_definition -> FieldDefinition (to_one)
Order: sequence, value
Where: sequence, value
Reachable from: /field_definitions/{field_definition_id}/field_options (FieldDefinition); /field_data/{field_datum_id}/field_option (FieldDatum); /tabs/{tab_id}/field_options (Tab)
Create: POST /field_definitions/{field_definition_id}/field_options — attrs: value, sequence
Update: PATCH /field_definitions/{field_definition_id}/field_options/{id} — attrs: value, sequence
Delete: DELETE /field_definitions/{field_definition_id}/field_options/{id}

## Form
A custom form for people to fill out. Forms are read-only via API (create/update in the UI); submissions can be created.
Endpoints: GET /forms; GET /forms/{id}
Attributes: active (boolean); allow_submitting_for_household_members (boolean, only if feature enabled); archived (boolean); archived_at; can_manage (boolean); created_at; deleted_at; description; id; login_required (boolean); name; public_url; recently_viewed (boolean); send_submission_notification_to_submitter (boolean); submission_count (integer); updated_at
Relationships: campus -> Campus (to_one); form_category -> FormCategory (to_one)
Include: campus*, category
Order: active, archived_at, campus, category, created_at, deleted_at, description, name, recently_viewed, submission_count, updated_at
Where: active (boolean), id
Associations: campus -> Campus; category -> FormCategory; fields -> FormField; form_submissions -> FormSubmission
Reachable from: /forms (Organization) [filter: archived, closed, not_archived, open, recently_deleted, recently_viewed, unassigned, with_recoverable]; /forms/{form_id}/form_submissions/{form_submission_id}/form (FormSubmission)

## FormCategory
Endpoints: GET /form_categories; GET /form_categories/{id}; POST /form_categories; PATCH /form_categories/{id}; DELETE /form_categories/{id}
Attributes: created_at; id; name; updated_at
Order: created_at, name, updated_at
Where: created_at, name, updated_at
Reachable from: /form_categories (Organization); /forms/{form_id}/category (Form)
Create: POST /form_categories — attrs: name
Update: PATCH /form_categories/{id} — attrs: name
Delete: DELETE /form_categories/{id}

## FormField
A field in a custom form (read-only).
Endpoints: GET /forms/{form_id}/fields; GET /forms/{form_id}/fields/{id}
Attributes: created_at; description; field_type (string: string | text | checkboxes | dropdown | date | phone_number | address | birthday | gender | custom_field | note | workflow | heading | number | boolean | file | medical | workflow_checkbox | workflow_checkboxes | workflow_dropdown | marital_status | anniversary | grade | primary_campus | school | household); id; label; required (boolean); sequence (integer); settings (string); updated_at
Relationships: form -> Form (to_one); fieldable -> Fieldable (to_one, polymorphic: FieldDefinition | NoteCategory | Workflow); options -> FormFieldOption; form_field_conditions -> FormFieldCondition (to_many)
Include: form_field_conditions, options
Order: created_at, sequence, updated_at
Associations: form_field_conditions -> FormFieldCondition; options -> FormFieldOption
Reachable from: /forms/{form_id}/fields (Form); /forms/{form_id}/form_submissions/{form_submission_id}/form_fields (FormSubmission)

## FormFieldCondition
A rule that conditionally shows a form field based on the answer to a trigger field. A field has at most one condition. Match by `trigger_form_field_option` (option-based fields) or `trigger_form_field_option_value` (boolean custom fields); if neither is set the condition is met when the trigger has any answer. form_field and trigger_form_field must belong to the same form.
Endpoints: GET /forms/{form_id}/fields/{form_field_id}/form_field_conditions; …/{id}; POST …; PATCH …/{id}; DELETE …/{id}
Attributes: created_at; id; trigger_form_field_option_value (string); updated_at
Relationships: form_field -> FormField (to_one, shown field); trigger_form_field -> FormField (to_one, evaluated field); trigger_form_field_option -> FormFieldOption (to_one)
Order: created_at, updated_at
Where: created_at, updated_at
Reachable from: /forms/{form_id}/fields/{form_field_id}/form_field_conditions (FormField)
Create: POST /forms/{form_id}/fields/{form_field_id}/form_field_conditions — attrs: trigger_form_field_option_value; rels: form_field, trigger_form_field, trigger_form_field_option — permissions: manage the form
Update: PATCH /forms/{form_id}/fields/{field_id}/form_field_conditions/{id} — same — permissions: manage the form
Delete: DELETE …/form_field_conditions/{id} — permissions: manage the form

## FormFieldOption
An option on a custom form field (read-only).
Endpoints: GET /forms/{form_id}/fields/{field_id}/options; …/options/{id}
Attributes: created_at; id; label (string); sequence (integer); updated_at
Relationships: form_field -> FormField (to_one); optionable -> Optionable (to_one, polymorphic)
Order: created_at, sequence, updated_at
Reachable from: /forms/{form_id}/fields/{form_field_id}/options (FormField)

## FormSubmission
A completed entry submitted through a form. POST lets integrations record submissions captured outside Church Center (e.g. OCR'd paper forms).
Endpoints: GET /forms/{form_id}/form_submissions; …/{id}; POST /forms/{form_id}/form_submissions
Attributes: created_at; id; requires_verification (boolean, only with ?fields); selected_options_by_field (json, only with ?fields); updated_at; verified (boolean — true once the submitter confirms verification-required answers; auto-true when the submission creates a new person)
Relationships: person -> Person (to_one); form -> Form (to_one)
Include: form*, form_fields, form_submission_values*, person*
Order: created_at, person.first_name, person.last_name, updated_at
Where: created_at, updated_at
Associations: form -> Form; form_fields -> FormField; form_submission_values -> FormSubmissionValue; person -> Person
Reachable from: /forms/{form_id}/form_submissions (Form)
Create: POST /forms/{form_id}/form_submissions — permissions: token user needs overall People Editor or above AND manage rights on the form (Manager, or a manage FormShare).
  - Identify the submitter with either `person_id` (existing person) or `person_attributes` ({first_name, last_name, emails_attributes: [{location, address}]}); matching is by first name (or given name/nickname) + last name + email; no match = new person created.
  - Pass answers as `included` FormSubmissionValue resources, each with `form_field_id` and `value`. For option fields (checkboxes, dropdowns) `value` is the selected FormFieldOption **id**, not its label. Values for fields on other forms and blank values are silently discarded.
  - Side effects mirror a Church Center submission: subscriber notifications, optional submitter confirmation email, workflow card creation for workflow fields, and profile updates (contact info, birthdate, gender, household, custom fields). New person: updates apply immediately. Existing person with verification-required fields: a verification email is sent first; updates apply after the link is clicked.

## FormSubmissionValue
The answer to one field within a form submission. Supplied as included resources when creating a FormSubmission.
Endpoints: GET /forms/{form_id}/form_submissions/{form_submission_id}/form_submission_values; …/{id} (read-only; no standalone create)
Attributes: attachments (array); display_value (string); id
Relationships: form_field -> FormField (to_one); form_field_option -> FormFieldOption (to_one); form_submission -> FormSubmission (to_one)
Reachable from: /forms/{form_id}/form_submissions/{form_submission_id}/form_submission_values (FormSubmission)

## Grade
School grade lookup (key/value pairs); the same data is on `Organization.grades`.
Endpoints: GET /grades (read-only; the docs page renders a truncated path `/people/v2` — collection name inferred from the vertex name). The reliable alternative is `GET /people/v2` and read `data.attributes.grades`.
Attributes: id; key (integer); value (string)

## Household
Links people together and can have a primary contact. Add people via HouseholdMembership.
Endpoints: GET /households; GET /households/{id}; POST /households; PATCH /households/{id}; DELETE /households/{id}
Attributes: avatar (string, File UUID); created_at; id; member_count (integer); name; primary_contact_id; primary_contact_name; updated_at
Relationships: primary_contact -> Person (to_one); people -> Person (to_many)
Include: people*
Order: created_at, member_count, name, primary_contact_name, updated_at
Where: created_at, member_count, name, primary_contact_name, updated_at
Associations: household_memberships -> HouseholdMembership; people -> Person [filter: non_pending, without_deceased]
Reachable from: /households (Organization); /people/{person_id}/households (Person); /households/{household_id}/household_memberships/{household_membership_id}/household (HouseholdMembership); /people_imports/{people_import_id}/histories/{people_import_history_id}/household (PeopleImportHistory)
Create: POST /households — attrs: name, member_count, avatar, primary_contact_id; rels: people AND primary_contact (both must be specified)
Update: PATCH /households/{id} — attrs: name, member_count, avatar, primary_contact_id; rels: people
Delete: DELETE /households/{id}

## HouseholdMembership
Linking record between a Household and a Person.
Endpoints: GET /households/{household_id}/household_memberships; …/{id}; POST …; PATCH …/{id}; DELETE …/{id}
Attributes: household_role (string: adult | child_or_dependent | other_adult | parent_guardian); id; pending (boolean — unverified membership); person_name (string)
Relationships: person -> Person (to_one)
Include: household, person*
Order: pending, person_name
Where: pending (boolean), person_name
Associations: household -> Household; person -> Person
Reachable from: /households/{household_id}/household_memberships (Household); /people/{person_id}/household_memberships (Person)
Create: POST /households/{household_id}/household_memberships — attrs: pending, household_role; rels: person
Update: PATCH /households/{household_id}/household_memberships/{id} — same
Delete: DELETE /households/{household_id}/household_memberships/{id}

## InactiveReason
Why a member is no longer active.
Endpoints: GET /inactive_reasons; …/{id}; POST /inactive_reasons; PATCH /inactive_reasons/{id}; DELETE /inactive_reasons/{id}
Attributes: id; value (string)
Order: value. Where: value
Reachable from: /inactive_reasons (Organization); /people/{person_id}/inactive_reason (Person)
Create/Update attrs: value

## List
A tool for finding and grouping people using any criteria (saved query). Lists are built in the UI; the API can read, run, share, star and sync them.
Endpoints: GET /lists; GET /lists/{id}; PATCH /lists/{id}
Attributes: active_automations_count (integer); auto_generated_name (boolean); auto_refresh (boolean); auto_refresh_frequency (string); automations_active (boolean); automations_count (integer); batch_completed_at; created_at; description; has_inactive_results (boolean); id; include_inactive (boolean); invalid (boolean); name; name_or_description; paused_automations_count (integer); recently_viewed (boolean); refreshed_at; return_original_if_none (boolean); returns (string); starred (boolean); status (string); subset (string); total_people (integer); updated_at
Include: campus*, category, created_by, mailchimp_sync_status, people, rules, shares, updated_by
Order: active_automations_count, auto_refresh_frequency, automations_count, batch_completed_at, campus_id, campuses.name, created_at, list_categories.name, list_category_id, name, name_or_description, refreshed_at, starred, total_people, updated_at
Where: batch_completed_at, created_at, id, name, updated_at
Associations: campus -> Campus; category -> ListCategory; created_by -> Person; list_results -> ListResult; mailchimp_sync_status -> MailchimpSyncStatus; people -> Person; rules -> Rule; shares -> ListShare; star -> ListStar; updated_by -> Person
Reachable from: /lists (Organization) [filter: auto_refresh_enabled, can_manage, has_active_automations, mailchimp_connected, needs_attention, recently_viewed, starred, unassigned]; /campuses/{campus_id}/lists (Campus); /list_categories/{list_category_id}/lists (ListCategory)
Actions: `run` POST /lists/{list_id}/run (re-run the list to refresh results); `mailchimp_sync` POST /lists/{list_id}/mailchimp_sync (requires Mailchimp integration configured)
Update: PATCH /lists/{id} — rels: campus

## ListCategory
Endpoints: GET /list_categories; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: created_at; id; name; organization_id; updated_at
Include: lists. Order/Where: created_at, name, organization_id, updated_at
Associations: lists -> List
Reachable from: /list_categories (Organization); /lists/{list_id}/category (List)
Create/Update attrs: name

## ListResult
A row in a list's current results.
Endpoints: GET /lists/{list_id}/list_results; …/{id} (read-only)
Attributes: created_at; id; updated_at
Relationships: person -> Person (to_one); list -> List (to_one)
Include: person. Order: created_at, updated_at. Where: person_id (integer)
Associations: person -> Person
Reachable from: /lists/{list_id}/list_results (List)

## ListShare
Who has access to a list.
Endpoints: GET /lists/{list_id}/shares; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: created_at; group (string: No Access | Viewer | Editor | Manager); id; name; permission (string: view | manage)
Relationships: person -> Person (to_one). Include: person*
Order: created_at, group. Where: created_at, group, name, permission
Create: POST /lists/{list_id}/shares — attrs: permission, group, person_id; rels: person
Update: PATCH /lists/{list_id}/shares/{id} — attrs: permission, group
Delete: DELETE /lists/{list_id}/shares/{id}

## ListStar
Marks a list as starred for the current person.
Endpoints: GET /lists/{list_id}/star; POST /lists/{list_id}/star; DELETE /lists/{list_id}/star/{id}
Attributes: created_at; id

## MailchimpSyncStatus
Endpoints: GET /lists/{list_id}/mailchimp_sync_status; …/{id} (read-only)
Attributes: completed_at; error (string); id; progress (integer); segment_id (integer); status (string)

## MaritalStatus
Endpoints: GET /marital_statuses; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: id; value. Order: sequence, value. Where: value
Reachable from: /marital_statuses (Organization); /people/{person_id}/marital_status (Person)
Create/Update attrs: value

## MembershipType
Visitor, Regular Attender, Member, etc.
Endpoints: GET /membership_types; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: id; value. Order: sequence, value. Where: value
Reachable from: /membership_types (Organization)
Create/Update attrs: value
Note: `Person.membership` is a free string attribute, not a relationship to this table.

## Message
An individual email or SMS sent to a member. Every message has a parent MessageGroup. Read-only.
Endpoints: GET /messages; GET /messages/{id}
Attributes: app_name; bounced_at; created_at; delivery_status; file; from_address; from_name; id; kind (string: email | sms | church_center_message); message_type; read_at; reject_reason; rejection_notification_sent_at; sent_at; subject; to_addresses
Relationships: from -> Person; to -> Person; message_group -> MessageGroup
Include: message_group, to
Order: app_name, bounced_at, created_at, delivery_status, file, from_address, from_name, kind, reject_reason, rejection_notification_sent_at, sent_at, subject, to_addresses
Where: app_name, bounced_at, created_at, delivery_status, file, from_address, kind, reject_reason, rejection_notification_sent_at, sent_at, subject, to_addresses
Associations: message_group -> MessageGroup; to -> Person
Reachable from: /messages (Organization) [filter: created_after]; /people/{person_id}/messages (Person) [filter: created_after, received, sent, unread]; /message_groups/{message_group_id}/messages (MessageGroup)

## MessageGroup
Groups one or more emails/texts sent from a Planning Center app; records the sender and app. Read-only.
Endpoints: GET /message_groups; GET /message_groups/{id}
Attributes: contains_user_generated_content (boolean); created_at; from_address; id; message_count (integer); message_type; reply_to_address; reply_to_name; subject; system_message (boolean); transactional_message (boolean); uuid
Relationships: app -> App; from -> Person; messages -> Message (to_many)
Include: app, from, messages
Order/Where: contains_user_generated_content, created_at, from_address, message_count, message_type, reply_to_address, reply_to_name, subject, system_message, transactional_message, uuid
Associations: app -> App; from -> Person; messages -> Message
Reachable from: /message_groups (Organization); /people/{person_id}/message_groups (Person); /messages/{message_id}/message_group (Message)

## NamePrefix
Mr., Mrs., etc.
Endpoints: GET /name_prefixes; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: id; value. Order: value. Where: value
Reachable from: /name_prefixes (Organization); /people/{person_id}/name_prefix (Person)

## NameSuffix
Jr., Sr., III, etc.
Endpoints: GET /name_suffixes; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: id; value. Order: value. Where: value
Reachable from: /name_suffixes (Organization); /people/{person_id}/name_suffix (Person)

## Note
Text with a category attached to a person's profile.
Endpoints: GET /notes; GET /notes/{id}; POST /people/{person_id}/notes; PATCH /notes/{id}; DELETE /notes/{id}
Attributes: created_at; created_by_id; display_date (date_time); id; note (string); note_category_id; organization_id; person_id; updated_at
Relationships: note_category -> NoteCategory; organization -> Organization; person -> Person; created_by -> Person
Include: category, created_by*, person*
Order: created_at, display_date, id, note, note_category_id, updated_at
Where: created_at, note, note_category_id, updated_at
Associations: category -> NoteCategory; created_by -> Person; person -> Person
Reachable from: /notes (Organization); /people/{person_id}/notes (Person)
Create: POST /people/{person_id}/notes — attrs: note, created_at, updated_at, display_date, note_category_id; rels: created_by, person
Update: PATCH /notes/{id} — same
Delete: DELETE /notes/{id}

## NoteCategory
Endpoints: GET /note_categories; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: created_at; id; locked (boolean); name; organization_id; updated_at
Include: shares, subscribers, subscriptions
Order/Where: created_at, locked, name, organization_id, updated_at
Associations: shares -> NoteCategoryShare; subscribers -> Person; subscriptions -> NoteCategorySubscription
Reachable from: /note_categories (Organization) [filter: view_creatable]; /notes/{note_id}/category (Note)
Create/Update attrs: name. Delete: deleting a category deletes all its notes.

## NoteCategoryShare
Who can view notes in a category.
Endpoints: GET /note_categories/{note_category_id}/shares; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: group (string: No Access | Viewer | Editor | Manager); id; permission (string: view | view_create | manage); person_id
Relationships: person -> Person; note_category -> NoteCategory. Include: person*
Where: permission
Create/Update attrs: group, permission, person_id; rels: person

## NoteCategorySubscription
Endpoints: GET /note_category_subscriptions; …/{id} (read-only)
Attributes: created_at; id; updated_at
Relationships: person -> Person; note_category -> NoteCategory. Include: person
Order/Where: created_at, updated_at
Reachable from: /note_category_subscriptions (Organization); /note_categories/{note_category_id}/subscriptions (NoteCategory)

## Organization
A single church. Every other resource is scoped to it. The root collection endpoints listed under Associations are the top-level `/people/v2/<collection>` paths.
Endpoints: GET /people/v2 (the organization itself); GET /people/{person_id}/organization
Attributes: avatar_url; church_center_subdomain; contact_website; country_code; created_at; date_format (integer); grades (array); id; name; time_zone
Associations (top-level collections): addresses; apps; background_checks [filter: awaiting_applicant, canceled, complete_clear, complete_not_clear, current, expired, expired_invitation, needs_review, not_expired, report_processing]; birthday_people; campuses; carriers; emails; field_data; field_definitions [filter: include_deleted]; form_categories; forms [filter: archived, closed, not_archived, open, recently_deleted, recently_viewed, unassigned, with_recoverable]; households; inactive_reasons; list_categories; lists [filter: auto_refresh_enabled, can_manage, has_active_automations, mailchimp_connected, needs_attention, recently_viewed, starred, unassigned]; marital_statuses; membership_types; message_groups; messages [filter: created_after]; name_prefixes; name_suffixes; note_categories [filter: view_creatable]; note_category_subscriptions; notes; people [filter: admins, created_since, organization_admins]; people_imports; person_mergers; phone_numbers; reports; school_options; social_profiles; spam_email_addresses; stats -> OrganizationStatistics; tabs [filter: with_field_definitions]; workflow_assignee_summaries; workflows [filter: archived, has_my_cards, manage_cards_allowed, needs_attention, not_archived, only_deleted, recently_deleted, recently_viewed, unassigned, with_deleted, with_recoverable, with_steps]

## OrganizationStatistics
Endpoints: GET /stats (read-only). Attributes: id (statistics payload is returned in the attributes).

## PeopleImport
An ongoing or past CSV import.
Endpoints: GET /people_imports; …/{id} (read-only)
Attributes: attribs (string); created_at; id; processed_at; status (string: matching | processing_preview | previewing | processing_import | complete | undone | undoing); undone_at; updated_at
Relationships: created_by -> Person; undone_by -> Person
Where: status
Associations: conflicts -> PeopleImportConflict [filter: creates, creates_and_updates, errors, household_creates, household_updates, identical, ignored, not_ignored, updates]; histories -> PeopleImportHistory [filter: creates, household_creates, household_updates, identical, updates]
Reachable from: /people_imports (Organization)

## PeopleImportConflict
A change that will occur if the parent import completes.
Endpoints: GET /people_imports/{people_import_id}/conflicts; …/{id} (read-only)
Attributes: conflicting_changes (string); created_at; data (string); id; ignore (boolean); kind; message; name; updated_at
Where: kind, name

## PeopleImportHistory
A change that occurred when the parent import completed.
Endpoints: GET /people_imports/{people_import_id}/histories; …/{id} (read-only)
Attributes: conflicting_changes (hash); created_at; id; kind; name; updated_at
Relationships: household -> Household; person -> Person. Include: household, person
Where: name
Associations: household -> Household; person -> Person

## Person
One member or user of the application. Permissions determine how, if at all, they can use the app.
Endpoints: GET /people; GET /people/{id}; POST /people; PATCH /people/{id}; DELETE /people/{id}; GET /me (current user)
Attributes: accounting_administrator (boolean); anniversary (date); avatar (string, File UUID on write / URL on read); birthdate (date); can_create_forms (boolean); can_email_lists (boolean); child (boolean); created_at; demographic_avatar_url; directory_shared_info (json, only with ?fields); directory_status; first_name; gender; given_name; grade (integer); graduation_year (integer); id; inactivated_at (date_time — set an ISO 8601 time to deactivate, null to reactivate); last_name; login_identifier; medical_notes; membership (string); mfa_configured (boolean, only with ?fields, Organization Administrator only); middle_name; name; nickname; passed_background_check (boolean); people_permissions (string); remote_id (integer); school_type; selective_access (boolean); site_administrator (boolean); status (string — set "inactive" to deactivate now; any other value reactivates); stripe_account_identifier (only with ?fields); stripe_customer_identifier (only with ?fields); updated_at
Relationships: primary_campus -> PrimaryCampus/Campus (to_one); created_by -> Person (to_one)
Include: addresses*, emails*, field_data, households, inactive_reason*, marital_status*, name_prefix*, name_suffix*, organization, person_apps, phone_numbers*, platform_notifications, primary_campus*, school*, social_profiles*
Order: accounting_administrator, anniversary, birthdate, child, created_at, first_name, gender, given_name, grade, graduation_year, inactivated_at, last_name, membership, middle_name, nickname, people_permissions, remote_id, site_administrator, status, updated_at
Where: accounting_administrator (boolean), anniversary (date), birthdate (date), child (boolean), created_at, first_name, gender, given_name, grade (integer), graduation_year (integer), id, inactivated_at, last_name, medical_notes, membership, mfa_configured (Org Admin only), middle_name, nickname, people_permissions, primary_campus_id (integer), remote_id (integer), search_name, search_name_or_email, search_name_or_email_or_phone_number, search_phone_number, search_phone_number_e164, site_administrator (boolean), status, updated_at
Associations: addresses -> Address; apps -> App; background_checks -> BackgroundCheck [filter: see BackgroundCheck]; connected_people -> ConnectedPerson; emails -> Email; field_data -> FieldDatum; household_memberships -> HouseholdMembership; households -> Household; inactive_reason -> InactiveReason; marital_status -> MaritalStatus; message_groups -> MessageGroup; messages -> Message [filter: created_after, received, sent, unread]; name_prefix -> NamePrefix; name_suffix -> NameSuffix; notes -> Note; organization -> Organization; person_apps -> PersonApp; phone_numbers -> PhoneNumber; platform_notifications -> PlatformNotification; primary_campus -> Campus; school -> SchoolOption; social_profiles -> SocialProfile; workflow_assignee_workflow_summaries -> WorkflowAssigneeWorkflowSummary; workflow_cards -> WorkflowCard [filter: assigned]; workflow_shares -> WorkflowShare
Reachable from: /people (Organization) [filter: admins, created_since (defaults to last 24h; accepts `time` ISO 8601 param), organization_admins]; /households/{household_id}/people (Household) [filter: non_pending, without_deceased]; /lists/{list_id}/people (List); /workflows/{workflow_id}/shared_people (Workflow); /note_categories/{note_category_id}/subscribers (NoteCategory); plus to_one parents: emails/{id}/person, field_data/{id}/person, social_profiles/{id}/person, notes/{id}/person|created_by, background_checks/{id}/person|created_by, lists/{id}/created_by|updated_by, reports/{id}/created_by|updated_by, messages/{id}/to, message_groups/{id}/from, household_memberships/{id}/person, list_results/{id}/person, list_shares/{id}/person, note_category_shares/{id}/person, note_category_subscriptions/{id}/person, workflow_cards/{id}/assignee|person, workflow_shares/{id}/person, workflow_steps/{id}/default_assignee, workflow_step_assignee_summaries/{id}/person, form_submissions/{id}/person, people_import_histories/{id}/person, conditions/{id}/created_by
Create: POST /people — attrs: child, accounting_administrator, anniversary, birthdate, given_name, grade, graduation_year, middle_name, nickname, people_permissions, site_administrator, gender, inactivated_at, medical_notes, membership, stripe_customer_identifier, stripe_account_identifier, created_by_id, avatar, first_name, last_name, primary_campus_id, remote_id, status; rels (via include): addresses, emails, inactive_reason, marital_status, name_prefix, name_suffix, phone_numbers, primary_campus, school, social_profiles
Update: PATCH /people/{id} — same attrs except created_by_id
Delete: DELETE /people/{id}
Notes: search_name / search_name_or_email / search_name_or_email_or_phone_number are the practical "find a person" filters (e.g. `?where[search_name_or_email]=jane%20doe`). `where[primary_campus_id]` filters by campus. Deactivate with `{"data":{"attributes":{"status":"inactive"}}}`.

## PersonApp
The relationship between a Person and an App (which apps a person can access).
Endpoints: GET /people/{person_id}/person_apps; …/{id}; POST /people/{person_id}/person_apps
Attributes: allow_pco_login (boolean); id; people_permissions (string: no_access | viewer | editor)
Relationships: app -> App; person -> Person. Include: app*
Associations: app -> App
Create: POST /people/{person_id}/person_apps — attrs: app_id

## PersonMerger
History of profiles merged into other profiles (read-only).
Endpoints: GET /person_mergers; …/{id}
Attributes: created_at; id; person_to_keep_id; person_to_remove_id
Relationships: person_to_keep -> Person; person_to_remove -> Person
Order: created_at. Where: created_at, person_to_keep_id, person_to_remove_id
Reachable from: /person_mergers (Organization)

## PhoneNumber
A single telephone number and location.
Endpoints: GET /phone_numbers; …/{id}; POST /people/{person_id}/phone_numbers; PATCH /phone_numbers/{id}; DELETE /phone_numbers/{id}
Attributes: carrier; country_code; created_at; e164; formatted_number (only with ?fields); id; international; location; national; number; primary (boolean); updated_at; verified (boolean)
Relationships: person -> Person
Order: carrier, created_at, location, number, primary, updated_at
Where: carrier, created_at, location, number, primary, updated_at
Reachable from: /phone_numbers (Organization); /people/{person_id}/phone_numbers (Person)
Create: POST /people/{person_id}/phone_numbers — attrs: number, carrier, location, primary
Update: PATCH /phone_numbers/{id} — same
Delete: DELETE /phone_numbers/{id}

## PlatformNotification
Suite-wide notification shown at the top of each app until dismissed; scoped to a person. Read-only.
Endpoints: GET /people/{person_id}/platform_notifications; …/{id}
Attributes: html (string); id

## Report
Editable Liquid templates for presenting Lists.
Endpoints: GET /reports; …/{id}; POST /reports; PATCH /reports/{id}; DELETE /reports/{id}
Attributes: body (string); created_at; id; name; updated_at
Relationships: created_by -> Person; updated_by -> Person. Include: created_by, updated_by
Order/Where: body, created_at, name, updated_at
Associations: created_by -> Person; updated_by -> Person
Create/Update attrs: name, body

## Rule
Belongs to a List and groups Conditions (read-only).
Endpoints: GET /lists/{list_id}/rules; …/{id}
Attributes: created_at; id; subset (string); updated_at
Include: conditions. Order/Where: created_at, subset, updated_at
Associations: conditions -> Condition
Reachable from: /lists/{list_id}/rules (List)

## SchoolOption
A school name/type/grade range selectable for a person.
Endpoints: GET /school_options; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: beginning_grade; ending_grade; id; school_types (array); sequence (integer); value
Order/Where: beginning_grade, ending_grade, (school_types), sequence, value
Associations: promotes_to_school -> SchoolOption
Reachable from: /school_options (Organization); /people/{person_id}/school (Person); /school_options/{school_option_id}/promotes_to_school
Create/Update attrs: value, sequence, beginning_grade, ending_grade, school_types

## ServiceTime
A recurring service time on a Campus.
Endpoints: GET /campuses/{campus_id}/service_times; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: day (string: sunday | monday | tuesday | wednesday | thursday | friday | saturday); description; id; start_time (integer)
Relationships: organization -> Organization; campus -> Campus
Order: time
Create/Update attrs: start_time, day, description — permissions: Organization Administrator

## SocialProfile
A person's social media account.
Endpoints: GET /social_profiles; …/{id}; POST /people/{person_id}/social_profiles; PATCH /social_profiles/{id}; DELETE /social_profiles/{id}
Attributes: created_at; id; site (string); updated_at; url (string); verified (boolean)
Relationships: person -> Person. Include: person
Order/Where: created_at, site, updated_at, url, verified
Create/Update attrs: site, url, verified

## SpamEmailAddress
An email address marked as spam (read-only).
Endpoints: GET /spam_email_addresses; …/{id}
Attributes: address; created_at; id; updated_at

## Tab
A custom tab grouping field definitions.
Endpoints: GET /tabs; …/{id}; POST /tabs; PATCH /tabs/{id}; DELETE /tabs/{id}
Attributes: id; name; sequence (integer); slug
Relationships: field_definitions -> FieldDefinition (to_many); field_options -> FieldOption (to_many)
Include: field_definitions, field_options
Order/Where: name, sequence, slug
Associations: field_definitions -> FieldDefinition [filter: with_deleted]; field_options -> FieldOption
Reachable from: /tabs (Organization) [filter: with_field_definitions]; /field_data/{field_datum_id}/tab; /field_definitions/{field_definition_id}/tab
Create/Update attrs: name, sequence

## Workflow
A multi-step process that people move through as WorkflowCards.
Endpoints: GET /workflows; …/{id}; POST /workflows; PATCH /workflows/{id}; DELETE /workflows/{id}
Attributes: archived_at; campus_id; completed_card_count; created_at; deleted_at; id; my_due_soon_card_count (only with ?fields); my_overdue_card_count (only with ?fields); my_ready_card_count; name; recently_viewed (boolean); total_cards_count; total_overdue_card_count; total_ready_and_snoozed_card_count; total_ready_card_count; total_steps_count; total_unassigned_card_count; total_unassigned_steps_count; updated_at; workflow_category_id
Relationships: workflow_category -> WorkflowCategory; campus -> Campus
Include: category, shares, steps
Order: archived_at, campus_id, campus_name, created_at, deleted_at, my_ready_card_count, name, recently_viewed, total_overdue_card_count, total_ready_card_count, total_unassigned_card_count, updated_at, workflow_category_id, workflow_category_name
Where: archived_at, campus_id, created_at, deleted_at, id, name, updated_at, workflow_category_id
Associations: cards -> WorkflowCard; category -> WorkflowCategory; shared_people -> Person; shares -> WorkflowShare; steps -> WorkflowStep
Reachable from: /workflows (Organization) [filter: archived, has_my_cards, manage_cards_allowed, needs_attention, not_archived, only_deleted, recently_deleted, recently_viewed, unassigned, with_deleted, with_recoverable, with_steps]; /people/{person_id}/workflow_cards/{workflow_card_id}/workflow
Create: POST /workflows — attrs: name, campus_id, workflow_category_id
Update: PATCH /workflows/{id} — same
Delete: DELETE /workflows/{id}

## WorkflowAssigneeSummary
Aggregated card counts for an assignee across all visible workflows (read-only).
Endpoints: GET /workflow_assignee_summaries; …/{id}
Attributes: id; overdue_count; ready_count; snoozed_count
Relationships: person -> Person
Order: first_name, last_name, name, overdue_count, ready_count, snoozed_count

## WorkflowAssigneeWorkflowSummary
Per-workflow card counts for a specific assignee (read-only).
Endpoints: GET /people/{person_id}/workflow_assignee_workflow_summaries; …/{id}
Attributes: id; overdue_count; ready_count; snoozed_count; workflow_name
Relationships: workflow -> Workflow; person -> Person
Order: overdue_count, ready_count, snoozed_count, workflow_name

## WorkflowCard
A person's card inside a workflow. Note the asymmetric paths: create under the workflow, read/update/delete under the person.
Endpoints: GET /people/{person_id}/workflow_cards; GET /people/{person_id}/workflow_cards/{id}; GET /workflows/{workflow_id}/cards; POST /workflows/{workflow_id}/cards; PATCH /people/{person_id}/workflow_cards/{id}; DELETE /people/{person_id}/workflow_cards/{id}
Attributes: awaiting_automation (boolean); calculated_due_at; calculated_due_at_in_days_ago (integer); completed_at; created_at; flagged_for_notification_at; id; moved_to_step_at; overdue (boolean); pending_skip_evaluation (boolean); removed_at; snooze_until; stage (string); sticky_assignment (boolean); updated_at
Relationships: assignee -> Person (to_one); person -> Person; workflow -> Workflow; current_step -> WorkflowStep
Include: assignee*, current_step*, person*, workflow*
Order: completed_at, created_at, first_name, flagged_for_notification_at, last_name, moved_to_step_at, removed_at, stage, updated_at
Where: assignee_id (integer), overdue (boolean), stage
Associations: activities -> WorkflowCardActivity; assignee -> Person; current_step -> WorkflowStep; notes -> WorkflowCardNote; person -> Person; workflow -> Workflow
Reachable from: /people/{person_id}/workflow_cards (Person) [filter: assigned]; /workflows/{workflow_id}/cards (Workflow)
Actions (all POST /people/{person_id}/workflow_cards/{workflow_card_id}/<action>): go_back (previous step); promote (next step, completing current); skip_step (next step without completing); remove; restore; snooze (payload attrs: duration in days, e.g. 15; permissions: editor or assigned person); unsnooze; send_email (payload attrs: subject, note — emails the card's subject person)
Create: POST /workflows/{workflow_id}/cards — attrs: sticky_assignment, assignee_id, person_id
Update: PATCH /people/{person_id}/workflow_cards/{id} — same attrs
Delete: DELETE /people/{person_id}/workflow_cards/{id}

## WorkflowCardActivity
A record of an action performed on a card.
Endpoints: GET /people/{person_id}/workflow_cards/{workflow_card_id}/activities; …/{id}; DELETE …/activities/{id}
Attributes: attachments_meta (array); attachments_urls (array); automation_url; comment; content; content_is_html (boolean); created_at; form_submission_url; id; person_avatar_url; person_name; reassigned_to_avatar_url; reassigned_to_name; subject; type (string); updated_at
Relationships: person -> Person (null when performed by an integration); reassigned_to -> Person; workflow_card -> WorkflowCard; workflow_step -> WorkflowStep (only for type completion | skip | reversal | automation_success | automation_failure | manual_action_success | manual_action_failure)
Order: created_at, id, updated_at. Where: created_at, updated_at

## WorkflowCardNote
A note recorded on a workflow card.
Endpoints: GET /people/{person_id}/workflow_cards/{workflow_card_id}/notes; …/{id}; POST …/notes
Attributes: created_at; id; note; updated_at
Order/Where: created_at, updated_at
Create: POST …/notes — attrs: note, note_category_id (optional; also creates a matching profile Note in that category — that profile note is edited/deleted via /notes, not here)

## WorkflowCategory
Endpoints: GET /workflows/{workflow_id}/category; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: created_at; id; name; updated_at. Order/Where: created_at, name, updated_at
Create/Update attrs: name

## WorkflowShare
Who can access a workflow.
Endpoints: GET /workflows/{workflow_id}/shares; GET /people/{person_id}/workflow_shares; …/{id}; POST /workflows/{workflow_id}/shares; PATCH /people/{person_id}/workflow_shares/{id}; DELETE /people/{person_id}/workflow_shares/{id}
Attributes: group (string: No Access | Viewer | Editor | Manager); id; permission (string: view | manage_cards | manage); person_id
Relationships: person -> Person; workflow -> Workflow. Include: person*
Where: permission
Create: POST /workflows/{workflow_id}/shares — attrs: group, permission, person_id
Update: PATCH /people/{person_id}/workflow_shares/{id} — attrs: group, permission

## WorkflowStep
A step in a workflow.
Endpoints: GET /workflows/{workflow_id}/steps; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: action_type (string: assign | automate); auto_snooze_days (integer); auto_snooze_entry_hour (integer 17–23; requires auto_snooze_value, auto_snooze_interval and auto_snooze_wake_hour); auto_snooze_interval (string: day | week | month); auto_snooze_value (integer, positive); auto_snooze_wake_hour (integer 7–19, default 7); created_at; default_assignee_id; description; expected_response_time_in_days (integer); id; my_ready_card_count; name; sequence (integer); skip_conditions_enabled (boolean); total_ready_card_count; updated_at
Relationships: default_assignee -> Person; workflow -> Workflow. Include: default_assignee*
Order: created_at, name, sequence, updated_at. Where: created_at, name, updated_at
Associations: assignee_summaries -> WorkflowStepAssigneeSummary; default_assignee -> Person
Reachable from: /workflows/{workflow_id}/steps (Workflow); /people/{person_id}/workflow_cards/{workflow_card_id}/current_step (WorkflowCard)
Create/Update attrs: sequence, name, description, expected_response_time_in_days, default_assignee_id, auto_snooze_value, auto_snooze_interval, auto_snooze_wake_hour, auto_snooze_entry_hour, skip_conditions_enabled, action_type

## WorkflowStepAssigneeSummary
Ready and snoozed counts for an assignee on a step (read-only).
Endpoints: GET /workflows/{workflow_id}/steps/{workflow_step_id}/assignee_summaries; …/{id}
Attributes: id; ready_count; snoozed_count
Relationships: person -> Person; step -> Step. Include: person
