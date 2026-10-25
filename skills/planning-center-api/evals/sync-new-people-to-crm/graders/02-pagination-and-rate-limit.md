---
type: llm
focus: trace
weight: 1
---

The script paginates (follows links.next or increments offset with per_page up to 100) and handles HTTP 429 by waiting the Retry-After value, and sets a User-Agent header.
