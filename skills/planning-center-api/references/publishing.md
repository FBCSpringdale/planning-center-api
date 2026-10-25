# Publishing API (publishing/v2)

Base URL: `https://api.planningcenteronline.com/publishing/v2`
Documented version: `2024-03-25` (first public version; also 2018-08-01). OAuth scope: `publishing`.
OpenAPI: `https://api.planningcenteronline.com/publishing/v2/open_api/2024-03-25`
Docs: `https://api.planningcenteronline.com/docs/apps/publishing/versions/2024-03-25/vertices/<snake_case_resource>`

Publishing manages sermon Channels → Episodes (with EpisodeTimes for live schedule, EpisodeResources for links, Speakerships for speakers, NoteTemplate for sermon notes), Series, Speakers, and Church Center Announcements.

Image/audio attributes (`art`, `podcast_art`, `sermon_audio`) are set by passing an upload UUID from `https://upload.planningcenteronline.com/v2/files` (see guides) or a `signed_identifier` from an existing File.

Conventions: see people.md. All collections paginate with `per_page` (1–100, default 25) and `offset`.

## Resource index (17)

Announcement, AnnouncementCategory, AnnouncementsAnnouncementCategory, AnnouncementsCampus, Channel, ChannelDefaultEpisodeResource, ChannelDefaultTime, ChannelNextTime, Episode, EpisodeResource, EpisodeStatistics, EpisodeTime, NoteTemplate, Organization, Series, Speaker, Speakership

## Relationship map

```
Organization
 ├─ channels (Channel) ── episodes (Episode) ── episode_times (EpisodeTime), episode_resources (EpisodeResource), speakerships (Speakership) ── speaker (Speaker), note_template (NoteTemplate), series (Series), channel
 │                     ├─ series (Series), current_episode (Episode), channel_default_times (ChannelDefaultTime), channel_default_episode_resources, next_times (ChannelNextTime), statistics (EpisodeStatistics)
 ├─ episodes, series, speakers (Speaker)
 ├─ announcements (Announcement) ── announcements_announcement_categories ── announcement_category (AnnouncementCategory); announcements_campuses (AnnouncementsCampus) ── campus
 └─ announcement_categories
```

Services link: `Episode.services_plan_remote_identifier` / `services_service_type_remote_identifier` and `Channel.services_service_type_remote_identifier` hold Services Plan / ServiceType ids. Services `Plan.linked_publishing_episode` points back.

---

## Announcement
Church Center announcement (read-only).
Endpoints: GET /announcements [filter: active, active_and_scheduled, archived, inactive]; …/{id}
Attributes: archived (boolean); attach_linked_resource_image_job_id; church_center_url; featured (boolean); hide_at; id; image (hash); link; link_resource_id; link_type; show_at; status; summary; title
Relationships: announcements_announcement_categories (to_many); announcements_campuses (to_many); organization
Include: announcements_announcement_categories, announcements_campuses
Order: featured, show_at, status, title. Where: title
Associations: announcements_announcement_categories -> AnnouncementsAnnouncementCategory; announcements_campuses -> AnnouncementsCampus

## AnnouncementCategory
Endpoints: GET /announcement_categories; …/{id} (read-only). Attributes: id; name. Order: name

## AnnouncementsAnnouncementCategory
Join between Announcement and AnnouncementCategory (read-only).
Endpoints: GET /announcements/{a}/announcements_announcement_categories; …/{id}; …/{id}/announcement_category
Attributes: id. Relationships: announcement_category. Include: announcement_category

## AnnouncementsCampus
Join between Announcement and Campus (read-only).
Endpoints: GET /announcements/{a}/announcements_campuses; …/{id}
Attributes: id. Relationships: campus -> Campus

## Channel
A collection of sermons.
Endpoints: GET /channels [filter: archived, not_archived, podcast_enabled, published]; …/{id}; POST /channels; PATCH /channels/{id}; DELETE /channels/{id}
Attributes: activate_episode_minutes_before (integer); archived (boolean); art (hash, set via upload UUID or signed_identifier); can_enable_chat (boolean); church_center_url; created_at; default_video_duration (integer); default_video_embed_code; default_video_url; description; enable_audio; enable_on_demand_video; enable_watch_live (booleans); general_chat_enabled; group_chat_enabled (booleans); id; name; podcast_art (hash); podcast_feed_url; podcast_settings (hash); position (integer); published (boolean); sermon_notes_enabled (boolean); services_service_type_remote_identifier; updated_at; url
Relationships: channel_default_episode_resources, channel_default_times, episodes, next_times, series (to_many); current_episode -> Episode; statistics
Include: channel_default_episode_resources*, channel_default_times*, current_episode
Order: name, position
Associations: channel_default_episode_resources; channel_default_times; current_episode -> Episode; episodes -> Episode [filter: connected_to_services, not_connected_to_services, not_published, published, published_to_library]; next_times -> ChannelNextTime; series -> Series; statistics -> EpisodeStatistics
Reachable from: /channels; episodes/{id}/channel; series/{id}/channel
Create/Update attrs: art, podcast_art, podcast_settings, activate_episode_minutes_before, default_video_embed_code, description, url, default_video_duration, default_video_url, enable_audio, enable_on_demand_video, enable_watch_live, general_chat_enabled, group_chat_enabled, name, position, archived, published, sermon_notes_enabled; rels: channel_default_episode_resources, channel_default_times

## ChannelDefaultEpisodeResource
Default resources (links) new episodes get (read-only).
Endpoints: GET /channels/{channel_id}/channel_default_episode_resources; …/{id}
Attributes: featured (boolean); icon; id; kind (giving_fund | people_form | generic_url | services_public_page); position; title; type; url

## ChannelDefaultTime
Default weekly live times for a channel.
Endpoints: GET /channels/{channel_id}/channel_default_times; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: day_of_week (0 = Sunday); frequency (weekly); hour; id; minute; position
Order: position
Create/Update attrs: day_of_week, hour, minute, frequency, position

## ChannelNextTime
Next computed default time (read-only). Endpoints: GET /channels/{channel_id}/next_times; …/{id}
Attributes: id; starts_at

## Episode
A sermon/episode in a channel.
Endpoints: GET /episodes [filter: connected_to_services, not_connected_to_services, not_published_live, published_live, published_on_church_center]; GET /episodes/{id}; GET /channels/{c}/episodes [filter: connected_to_services, not_connected_to_services, not_published, published, published_to_library]; GET /channels/{c}/current_episode; POST /episodes; PATCH /episodes/{id}; DELETE /episodes/{id}
Attributes: art (hash); church_center_url; created_at; description; id; library_audio_url; library_streaming_service (vimeo | youtube | livestream_com | resi | facebook | boxcast); library_video_embed_code; library_video_thumbnail_url; library_video_url; needs_library_audio_or_video_url; needs_notes_template; needs_video_url (booleans); page_actions (array); published_live_at; published_to_library_at; sermon_audio (hash); services_plan_remote_identifier; services_service_type_remote_identifier; stream_type (channel_default_livestream | livestream | prerecorded); streaming_service (same enum); title; updated_at; video_embed_code; video_thumbnail_url; video_url
Relationships: series -> Series. Include: channel*, episode_resources*, episode_times*, series*, speakerships*
Order: published_live_at, published_to_library_at, stream_type, title
Where: series_id (integer), services_plan_remote_identifier, services_service_type_remote_identifier
Associations: channel; episode_resources; episode_times; note_template -> NoteTemplate; series; speakerships
Actions: generate_download_url POST /episodes/{id}/generate_download_url (empty body) → signed download URL for sermon_audio
Create/Update attrs: art, series_id, title, description, sermon_audio, stream_type, video_url, published_to_library_at, library_audio_url, library_video_url; rels: channel, episode_resources, episode_times, series, speakerships

## EpisodeResource
A link/resource shown with an episode.
Endpoints: GET /episodes/{episode_id}/episode_resources; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: featured (boolean); icon; id; kind (giving_fund | people_form | generic_url | services_public_page); position; title; type; url
Order: position
Create/Update attrs: featured, icon, position, title, type, url

## EpisodeStatistics
Viewership stats per episode (read-only).
Endpoints: GET /channels/{channel_id}/statistics; …/{id}
Attributes: id; library_watch_count; live_watch_count; published_live_at; published_to_library_at; times (array of watch_count per EpisodeTime); title

## EpisodeTime
Live schedule times for an episode.
Endpoints: GET /episodes/{episode_id}/episode_times; …/{id}; POST; PATCH …/{id}; DELETE …/{id}
Attributes: caveats (array); current_state (upcoming | active | over); current_timestamp (float); ends_at; id; starts_at; streaming_service (vimeo | youtube | livestream_com | resi | facebook | boxcast); video_embed_code; video_url
Order: starts_at
Create/Update attrs: starts_at, video_embed_code, video_url

## NoteTemplate
Sermon notes template for an episode.
Endpoints: GET /episodes/{episode_id}/note_template; …/{id}; PATCH …/{id}
Attributes: auto_create_free_form_notes (boolean); enabled (boolean); id; published_at; template (string)
Update attrs: enabled, template, auto_create_free_form_notes

## Organization
Endpoints: GET /publishing/v2
Attributes: downloads_used (only with ?fields); id; name; subdomain
Associations (top-level collections): announcement_categories; announcements [filter: active, active_and_scheduled, archived, inactive]; channels [filter: archived, not_archived, podcast_enabled, published]; episodes [filters above]; series [filter: not_published, published, published_on_church_center]; speakers

## Series
A sermon series within a channel.
Endpoints: GET /series [filter: not_published, published, published_on_church_center]; …/{id}; GET /channels/{c}/series; GET /episodes/{e}/series; POST /series; PATCH /series/{id}; DELETE /series/{id}
Attributes: art (hash); church_center_url; created_at; description; ended_at; episodes_count; id; published (boolean); started_at; title; updated_at
Relationships: channel -> Channel. Include: channel
Order: ended_at, episodes_count, started_at, title. Where: id
Associations: channel -> Channel
Create/Update attrs: art, description, published, title

## Speaker
Endpoints: GET /speakers; …/{id}; GET /episodes/{e}/speakerships/{s}/speaker (read-only)
Attributes: avatar_url; episodes_count; first_name; formatted_name; id; last_name; name_prefix; name_suffix; speaker_type
Order: first_name

## Speakership
Links a Speaker to an Episode.
Endpoints: GET /episodes/{episode_id}/speakerships; …/{id}; PATCH …/{id}; DELETE …/{id} (create by including speakerships when creating/updating the Episode)
Attributes: id. Relationships: speaker -> Speaker (set via relationship data, not a speaker_id attribute). Include: speaker*
Associations: speaker -> Speaker
Update: PATCH …/speakerships/{id} — rel: speaker
