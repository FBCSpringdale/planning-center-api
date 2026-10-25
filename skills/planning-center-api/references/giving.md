# Giving API (giving/v2)

Base URL: `https://api.planningcenteronline.com/giving/v2`
Documented version: `2019-10-18` (other: 2018-08-01). OAuth scope: `giving`.
2019-10-18 breaking changes: Batch/BatchGroup destroy and commit are asynchronous — they return the record with status `updating`; poll until done.
OpenAPI: `https://api.planningcenteronline.com/giving/v2/open_api/2019-10-18`
Docs: `https://api.planningcenteronline.com/docs/apps/giving/versions/2019-10-18/vertices/<snake_case_resource>`

Money is always integer cents (`amount_cents`) plus a currency code. Fees are 0 or negative. Online (Stripe) donations and recurring donations are read-only; the API writes offline/batch donations, funds, labels, pledges, in-kind donations, payment sources and notes.

Conventions: see people.md. All collections paginate with `per_page` (1–100, default 25) and `offset`.

## Resource index (20)

Batch, BatchGroup, Campus, Designation, DesignationRefund, Donation, DonorSummary, Fund, InKindDonation, Label, Note, Organization, PaymentMethod, PaymentSource, Person, Pledge, PledgeCampaign, RecurringDonation, RecurringDonationDesignation, Refund

## Relationship map

```
Organization
 ├─ batch_groups (BatchGroup) ── batches (Batch) ── donations (Donation), owner (Person), batch_group
 ├─ donations (Donation) ── designations (Designation) ── fund (Fund); labels (Label); note (Note); refund (Refund) ── designation_refunds (DesignationRefund) ── designation, fund
 │                       └─ person, campus (Campus), payment_source (PaymentSource), batch, recurring_donation
 ├─ people (Person) ── donations, batches, batch_groups, in_kind_donations, payment_methods (PaymentMethod) ── recurring_donations, pledges (Pledge) ── pledge_campaign, primary_campus, recurring_donations
 ├─ recurring_donations (RecurringDonation) ── designations (RecurringDonationDesignation) ── fund; payment_method
 ├─ pledge_campaigns (PledgeCampaign) ── fund, pledges (Pledge)
 ├─ funds (Fund), labels (Label), campuses (Campus), payment_sources (PaymentSource), in_kind_donations (InKindDonation), donor_summaries (DonorSummary)
```

Person ids are shared with People.

## Core workflow: record offline donations

1. `POST /batches` `{"data":{"attributes":{"description":"Sunday 2026-10-25"}}}` → Batch (status in_progress).
2. `POST /batches/{batch_id}/donations` with included designations:
```json
{"data":{"type":"Donation","attributes":{"payment_method":"check","payment_check_number":1234,"received_at":"2026-10-25T15:00:00Z"},
  "relationships":{"person":{"data":{"type":"Person","id":"123"}}}},
 "included":[{"type":"Designation","attributes":{"amount_cents":10000},"relationships":{"fund":{"data":{"type":"Fund","id":"1"}}}}]}
```
3. `POST /batches/{batch_id}/commit` (no body) → status `updating` → poll `GET /batches/{batch_id}` until `committed`.
Donations added to an already-committed batch are committed automatically. A batch cannot be committed with zero donations.

---

## Batch
A collection of Donations. API-created donations must belong to a batch. Uncommitted-batch donations are hidden from donor histories/statements.
Endpoints: GET /batches [filter: committed, in_progress]; GET /batches/{id}; POST /batches; PATCH /batches/{id}; DELETE /batches/{id}
Attributes: committed_at (null while in_progress/updating); created_at; description (shown as "Untitled batch" if blank); donations_count (integer, only with ?fields); id; status (in_progress | updating | committed); total_cents; total_currency; updated_at
Relationships: batch_group -> BatchGroup. Include: batch_group*, owner
Order: committed_at, updated_at. Where: committed_at, updated_at
Associations: batch_group -> BatchGroup; donations -> Donation; owner -> Person
Reachable from: /batches; /batch_groups/{bg}/batches [filter: committed, in_progress]; /people/{person_id}/batches [filter: committed, in_progress]
Actions: commit POST /batches/{id}/commit — no body; async (status → updating → committed); 422 if it cannot be committed
Create/Update attrs: description; rel: batch_group. Delete is async (returns status updating).

## BatchGroup
Optional grouping of batches. Committing a group commits all its batches and donations.
Endpoints: GET /batch_groups [filter: committed, in_progress]; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: committed (boolean); created_at; description ("Untitled group" if blank); id; status (uncommitted | updating | committed); total_cents; total_currency; updated_at
Relationships: owner -> Person; batches -> Batch (to_many). Include: owner
Order: updated_at. Where: description, updated_at
Associations: batches -> Batch [filter: committed, in_progress]; owner -> Person
Actions: commit POST /batch_groups/{id}/commit — no body; async
Create/Update attrs: description

## Campus
A location of the organization (managed in Accounts/People). Read-only here.
Endpoints: GET /campuses; …/{id}
Attributes: address (object); id; name
Associations: donations -> Donation
Reachable from: /campuses; donations/{id}/campus; in_kind_donations/{id}/campus; people/{id}/primary_campus

## Designation
How much of a Donation goes to a Fund. Supplied as `included` resources when creating/updating a Donation.
Endpoints: GET /donations/{donation_id}/designations; …/{id}
Attributes: amount_cents (integer, required); amount_currency; fee_cents (0 or negative, proportional share); id
Relationships: fund -> Fund. Include: fund*
Associations: fund -> Fund

## DesignationRefund
Links a Refund with a Designation.
Endpoints: GET /donations/{donation_id}/refund/designation_refunds; …/{id}
Attributes: amount_cents; amount_currency; fee_cents; id
Relationships: designation -> Designation; fund -> Fund. Include: designation
Associations: designation -> Designation

## Donation
A gift given at a point in time. Add `?with_totals=true` on collection endpoints to get `meta.received_total_amount_cents` and `meta.currency` (respects `where`, ignores pagination, unavailable when filtering by fund_id).
Endpoints: GET /donations [filter: succeeded]; GET /donations/{id}; POST /batches/{batch_id}/donations; PATCH /donations/{id}; DELETE /donations/{id}
Attributes: id; amount_cents (sum of designations); amount_currency; completed_at (null for uncommitted batch donations); created_at; fee_cents (0 or negative); fee_covered (boolean, Stripe only); fee_currency; memo (only when enabled for specific funds); payment_brand (card brand or bank name; null for cash); payment_channel (api | sms | mobile_app | web | admin | other); payment_check_dated_at (date); payment_check_number (integer); payment_last4 (may be padded with *); payment_method (ach | cash | check | card — required); payment_method_sub (credit | debit | prepaid | unknown; null for non-card); payment_status (pending | succeeded | failed); received_at (defaults to now on API create); refundable (boolean — via API; may be false even if refundable in UI); refunded (boolean); updated_at
Relationships: batch -> Batch; campus -> Campus; person -> Person; payment_source -> PaymentSource; labels -> Label (to_many); recurring_donation -> RecurringDonation
Include: designations*, labels*, note, refund
Order: completed_at, created_at, received_at, updated_at. Where: completed_at, created_at, payment_method, received_at, updated_at
Associations: campus; designations -> Designation; labels -> Label; note -> Note; refund -> Refund
Reachable from: /donations [filter: succeeded]; /batches/{b}/donations; /campuses/{c}/donations; /payment_sources/{ps}/donations; /people/{p}/donations
Actions:
- issue_refund POST /donations/{id}/issue_refund — batch donations only; optional attrs: refunded_at (date, recommended); 422 if not refundable or not in a batch
- mark_failed POST /donations/{id}/mark_failed — required attrs: reason (string, audit trail); failed donations stay in history but are excluded from statements/totals; 422 if already failed, refunded, or Stripe online
Create: POST /batches/{batch_id}/donations — attrs: payment_method (required), payment_method_sub, payment_last4, payment_brand, payment_check_number, payment_check_dated_at, fee_cents, received_at; rels: person, payment_source, campus, labels; included designations (at least one, each with amount_cents + fund relationship)
Update: PATCH /donations/{id} — same attrs plus person_id, payment_source_id, campus_id; labels relationship replaces the set (null or {} removes all; omit to leave intact); included designations with ids update those, without ids replace all. Non-batch (online) donations: only labels can be updated.
Delete: DELETE /donations/{id}

## DonorSummary
Collection-only per-donor totals over a date range (default last 30 days).
Endpoints: GET /donor_summaries [filter: has_joint_giver]
Attributes: id (= person id); donation_count (includes refunded/failed); donor_number (if visible); first_donated (lifetime); name; total_received_donation_amount_cents; total_received_donation_amount_currency
Relationships: joint_giver -> Person; organization. Include: joint_giver
Order: donation_count, first_donated, name, total_received_donation_amount_cents. Where: campus_id, person_id, received_at (use gte/lte for the range)

## Fund
Intent of a donation. Every org has a default fund (usually "General"): `?where[default]=true`.
Endpoints: GET /funds; …/{id}; POST /funds; PATCH /funds/{id}; DELETE /funds/{id}
Attributes: color (hex); created_at; default (boolean); deletable (boolean); description (≤255 chars); id; ledger_code; name (unique, required); slug; updated_at; visibility (everywhere | admin_only | nowhere | hidden — required)
Where: default (boolean), id, name, visibility
Reachable from: /funds; designations/{id}/fund; in_kind_donations/{id}/fund; pledge_campaigns/{id}/fund; recurring_donation_designations/{id}/fund
Create/Update attrs: name, ledger_code, description, visibility

## InKindDonation
A non-cash gift (goods, services, stock). API creation does not send acknowledgment emails.
Endpoints: GET /in_kind_donations; GET /people/{person_id}/in_kind_donations; …/{id}; POST /in_kind_donations; PATCH …/{id}; DELETE …/{id}
Attributes: acknowledgment_last_sent_at (auto); created_at; description (required); exchange_details; fair_market_value_cents (> 0, ≤ 21,000,000); fair_market_value_currency; id; received_on (date, required); updated_at; valuation_details (≤255)
Relationships: fund -> Fund (required); person -> Person (required); campus -> Campus (defaults to donor's primary campus; explicit value or null overrides). Include: campus*, fund*, person*
Order: created_at, received_on, updated_at. Where: campus_id, created_at, fund_id, received_on, updated_at
Associations: campus; fund; person
Create/Update attrs: description, exchange_details, fair_market_value_cents, fair_market_value_currency, received_on, valuation_details; rels: fund, campus, person

## Label
Admin-only categorization for donations.
Endpoints: GET /labels; GET /donations/{d}/labels; …/{id}; POST /labels; PATCH /labels/{id}; DELETE /labels/{id}
Attributes: id; slug (lowercase letters, numbers, dashes; auto-formatted). Where: slug
Create/Update attrs: slug

## Note
Single internal note per donation (admins/bookkeepers only).
Endpoints: GET /donations/{donation_id}/note; POST /donations/{donation_id}/note (overwrites an existing note)
Attributes: body; id
Create attrs: body

## Organization
Endpoints: GET /giving/v2
Attributes: id; name; text2give_enabled (boolean); time_zone
Associations (top-level collections): batch_groups [filter: committed, in_progress]; batches [filter: committed, in_progress]; campuses; donations [filter: succeeded]; donor_summaries [filter: has_joint_giver]; funds; in_kind_donations; labels; payment_sources; people [filter: has_donated]; pledge_campaigns; recurring_donations

## PaymentMethod
A donor's stored card/bank account (informational only; cannot create charges).
Endpoints: GET /people/{person_id}/payment_methods; …/{id}
Attributes: brand; created_at; expiration (cards, MM/YYYY); id; last4 (may be padded with *); method_subtype (credit | debit | prepaid | unknown | checking | savings); method_type (card | us_bank_account | au_becs_debit); updated_at; verified (bank accounts)
Relationships: person; recurring_donations (to_many)
Associations: recurring_donations -> RecurringDonation

## PaymentSource
The platform a donation came from ("Planning Center" built-in; external like Square/Pushpay can be added).
Endpoints: GET /payment_sources; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: created_at; id; name (unique, required); status (active | archived); updated_at
Associations: donations -> Donation
Create/Update attrs: name, status, payment_source_type

## Person
A People person as seen by Giving.
Endpoints: GET /people [filter: has_donated]; GET /people/{id}; PATCH /people/{id}
Attributes: addresses (array); donor_number (integer); email_addresses (array); first_donated_at; first_name; id; last_name; permissions (administrator | reviewer | counter | bookkeeper); phone_numbers (array)
Relationships: primary_campus -> Campus. Where: first_name, last_name
Associations: batch_groups [filter: committed, in_progress]; batches [filter: committed, in_progress]; donations; in_kind_donations; payment_methods; pledges; primary_campus; recurring_donations
Reachable from: /people; batches/{id}/owner; batch_groups/{id}/owner; donor_summaries/{id}/joint_giver; in_kind_donations/{id}/person; pledges/{id}/joint_giver
Update: PATCH /people/{id} — attrs: donor_number

## Pledge
A person's pledge toward a PledgeCampaign.
Endpoints: GET /people/{person_id}/pledges; GET /pledge_campaigns/{pc}/pledges; …/{id}; POST /people/{person_id}/pledges; PATCH /people/{person_id}/pledges/{id}; DELETE …/{id}
Attributes: amount_cents; amount_currency; created_at; donated_total_cents; id; joint_giver_amount_cents; joint_giver_donated_total_cents; updated_at
Relationships: person; pledge_campaign. Include: joint_giver, pledge_campaign*
Order/Where: created_at, updated_at
Associations: joint_giver -> Person; pledge_campaign -> PledgeCampaign
Create attrs: amount_cents, person_id, pledge_campaign_id; rel: pledge_campaign. Update attrs: amount_cents

## PledgeCampaign
Endpoints: GET /pledge_campaigns; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: created_at; description; ends_at; goal_cents; goal_currency; id; name; received_total_from_pledges_cents; received_total_outside_of_pledges_cents; show_goal_in_church_center (boolean); starts_at; updated_at
Relationships: fund -> Fund. Include: fund*
Order: ends_at, starts_at. Where: ends_at, fund_id, starts_at
Associations: fund; pledges -> Pledge
Create/Update attrs: name, description, starts_at, ends_at, goal_cents, show_goal_in_church_center, fund_id; rel: fund

## RecurringDonation
A scheduled repeating donation (read-only).
Endpoints: GET /recurring_donations; GET /people/{person_id}/recurring_donations; GET /people/{p}/payment_methods/{pm}/recurring_donations; …/{id}
Attributes: amount_cents; amount_currency; created_at; id; last_donation_received_at; next_occurrence; release_hold_at (for temporary_hold); schedule (JSON, "repeatable" gem structure); status (active | indefinite_hold | temporary_hold); updated_at
Relationships: person. Include: designations. Where: fund_id, status
Associations: payment_method -> PaymentMethod; designations -> RecurringDonationDesignation

## RecurringDonationDesignation
Fund split for a recurring donation (read-only).
Endpoints: GET /recurring_donations/{rd}/designations; …/{id}
Attributes: amount_cents; amount_currency; id. Relationships: fund. Include: fund

## Refund
Refund info for a donation (read-only; create via Donation issue_refund).
Endpoints: GET /donations/{donation_id}/refund; …/{id}
Attributes: amount_cents; amount_currency; created_at; fee_cents (Stripe fee returned); fee_currency; id; refunded_at; updated_at
Relationships: donation; designation_refunds (to_many). Include: designation_refunds
Associations: designation_refunds -> DesignationRefund
