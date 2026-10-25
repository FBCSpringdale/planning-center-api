---
type: llm
focus: trace
weight: 1
---

The script resolves emails and phone numbers from the JSON:API `included` array via the person's relationships linkage (type+id), preferring records with primary=true, rather than assuming they are nested attributes.
