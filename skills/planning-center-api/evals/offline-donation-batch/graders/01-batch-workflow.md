---
type: llm
focus: trace
weight: 1
---

The code creates a Batch, posts donations under /giving/v2/batches/{batch_id}/donations, and commits with POST /giving/v2/batches/{batch_id}/commit, polling for status committed (handling the asynchronous "updating" state).
