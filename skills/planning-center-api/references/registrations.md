# Registrations API (registrations/v2)

Base URL: `https://api.planningcenteronline.com/registrations/v2`
Documented version: `2025-05-01` (the only version). OAuth scope: `registrations`.
OpenAPI: `https://api.planningcenteronline.com/registrations/v2/open_api/2025-05-01`
Docs: `https://api.planningcenteronline.com/docs/apps/registrations/versions/2025-05-01/vertices/<snake_case_resource>`

The Registrations API is **read-only** (no create/update/delete endpoints are documented). Visibility rules: organization admins see all signups and their attendees/registrations; signup managers see only signups they manage. Reading an individual Registration requires admin-level event permissions.

Conventions: see people.md. All collections paginate with `per_page` (1–100, default 25) and `offset`.

## Resource index (11)

Attendee, Campus, Category, EmergencyContact, Organization, Person, Registration, SelectionType, Signup, SignupLocation, SignupTime

## Relationship map

```
Organization
 ├─ signups (Signup) ── attendees (Attendee) ── person (Person), registration (Registration), selection_type (SelectionType), emergency_contact (EmergencyContact)
 │                   ├─ registrations (Registration) ── created_by (Person), registrant_contact (Person)
 │                   ├─ selection_types (SelectionType), signup_times (SignupTime), next_signup_time (SignupTime), signup_location (SignupLocation), campuses (Campus), categories (Category)
 ├─ attendees, registrations, people (Person), campuses, categories
```

Person ids are shared with People.

---

## Attendee
A person registered for a signup.
Endpoints: GET /attendees; GET /attendees/{id}; GET /signups/{signup_id}/attendees [filter: active, canceled, waitlist]
Attributes: active (boolean); canceled (boolean); complete (boolean, only with ?fields — all required items finished); created_at; id; name (only with ?fields); updated_at; waitlisted (boolean); waitlisted_at
Relationships: emergency_contact -> EmergencyContact; person -> Person; registration -> Registration; selection_type -> SelectionType
Include: emergency_contact, person, registration, selection_type
Order: created_at
Associations: emergency_contact; person; registration; selection_type

## Campus
Endpoints: GET /campuses; …/{id}; GET /signups/{signup_id}/campuses
Attributes: city; country; created_at; full_formatted_address; id; name; state; street; updated_at; zip

## Category
Labels that group signups.
Endpoints: GET /categories; …/{id}; GET /signups/{signup_id}/categories
Attributes: created_at; id; name; updated_at

## EmergencyContact
Endpoints: GET /attendees/{attendee_id}/emergency_contact
Attributes: id; name; phone_number

## Organization
Endpoints: GET /registrations/v2
Attributes: created_at; id; name; updated_at
Associations (top-level collections): attendees; campuses; categories; people; registrations; signups [filter: archived, unarchived]

## Person
Endpoints: GET /people; GET /people/{id}; GET /attendees/{a}/person; GET /registrations/{r}/created_by; GET /registrations/{r}/registrant_contact
Attributes: can_search (boolean); first_name; id; last_name; name

## Registration
A registration (checkout) that may cover several attendees. Money is in cents plus formatted strings.
Endpoints: GET /registrations; GET /registrations/{id}; GET /signups/{signup_id}/registrations; GET /attendees/{a}/registration
Attributes: created_at; id; total_cost (formatted, null if free); total_cost_cents; total_due (formatted); total_due_cents; total_paid (formatted); total_paid_cents; updated_at
Relationships: created_by -> Person; registrant_contact -> Person. Include: created_by, registrant_contact
Order: created_at, updated_at
Associations: created_by; registrant_contact

## SelectionType
Options a person chooses from when registering (ticket types).
Endpoints: GET /signups/{signup_id}/selection_types [filter: publicly_available]; GET /attendees/{a}/selection_type
Attributes: id; name; price_cents; maximum_capacity (null = unlimited); publicly_available (boolean); waitlist (boolean); created_at; updated_at; at_maximum_capacity (boolean, only with ?fields); available_capacity (only with ?fields); price_currency (only with ?fields); price_currency_symbol (only with ?fields); price_formatted (only with ?fields)

## Signup
An event people can register for.
Endpoints: GET /signups [filter: archived, unarchived]; GET /signups/{id}
Attributes: archived (boolean); at_maximum_capacity (boolean, only with ?fields); close_at; closed (boolean); created_at; description; id; logo_url; maximum_capacity (null = no signup-level limit); name; new_registration_url; open (boolean); open_at; updated_at
Relationships: campuses, categories, registrations, attendees, selection_types, signup_times (to_many); next_signup_time -> SignupTime; signup_location -> SignupLocation; organization
Include: campuses, categories, next_signup_time, selection_types, signup_location, signup_times
Order: created_at, updated_at. Where: id, name
Associations: attendees [filter: active, canceled, waitlist]; campuses; categories; next_signup_time; registrations; selection_types [filter: publicly_available]; signup_location; signup_times [filter: future, past]

## SignupLocation
Endpoints: GET /signups/{signup_id}/signup_location
Attributes: address_data (json, only with ?fields); created_at; formatted_address; full_formatted_address; id; latitude; location_type (address | coords | online); longitude; name; subpremise; updated_at; url

## SignupTime
Endpoints: GET /signups/{signup_id}/signup_times [filter: future, past]; GET /signups/{signup_id}/next_signup_time
Attributes: all_day (boolean); created_at; ends_at; id; starts_at; updated_at
