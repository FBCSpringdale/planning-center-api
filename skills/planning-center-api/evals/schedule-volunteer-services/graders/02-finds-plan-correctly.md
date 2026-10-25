---
type: llm
focus: trace
weight: 1
---

The answer locates next Sunday's plan via GET /services/v2/service_types/{id}/plans with filter=future (and/or sort_date ordering) rather than inventing a date attribute on Plan, and notes that plan dates live on PlanTime.
