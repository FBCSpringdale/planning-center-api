---
tags: [planning-center-api]
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We use Planning Center at our church. I have a PAT in PCO_APP_ID / PCO_SECRET. Write a Python script that pulls every person created or updated in the last 7 days with their primary email and mobile phone and writes them to new_people.csv, handling pagination and rate limits properly. Only active people.
