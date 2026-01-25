---
name: meta-docx
description: Generate meta_original.docx from main.docx using JSON extraction, translate *_en fields with fixed terminology, then render and delete the JSON.
---

# Meta DOCX Workflow

Use this skill when generating `meta_original.docx` from a `main.docx` in the `sample_news` style.

## Workflow

1) Extract JSON from `main.docx`:

```bash
python meta/extract_meta_request.py --source <path/to/main.docx> --json-out <path/to/meta_filled.json>
```

2) Translate only the `*_en` fields in the JSON. Do not change structure or any `*_zh` fields.

- Generate **title_en** and **overview_en** based on **summary_zh** (not a literal translation; concise and natural).
- Translate people labels (role_zh) using the mapping below.

3) Render the docx and delete the JSON:

```bash
python meta/render_meta.py --template templates/meta_template.docx --input <path/to/meta_filled.json> --output <path/to/meta_original.docx>
rm -f <path/to/meta_filled.json>
```

## Translation Reference (role_zh -> role_en)

- 慈濟志工: Tzu Chi volunteer
- 慈濟助學生: Tzu Chi's tuition aid recipient
- 慈濟照顧戶: Tzu Chi's aid recipient
- 慈青: Tzu Chi collegiate volunteer
- 醫療團隊志工: Tzu Chi medical volunteer
- 志工: Volunteer
- 白內障病患: Cataract patient
- 學生: Student
- 校長: Principal
- 民眾: Resident (use "Tzu Chi's aid recipient" if the person is receiving aid from Tzu Chi)
- 當地居民: Local resident
- 村長: Village chief
- 受災戶: Affected resident (use "Disaster survivor" if fatalities occurred)
- 受災民眾: Affected resident (use "Disaster survivor" if fatalities occurred)
- 受災居民: Affected resident (use "Disaster survivor" if fatalities occurred)
