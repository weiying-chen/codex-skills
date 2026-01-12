---
name: translation
description: Translate Chinese to natural English in VOICEOVER (vo) or SUPER (sup) style, using consistent terminology rules.
---

# Translation

## Mode Selection
Accept mode tokens case-insensitively in either format:
- Single line: `$translation vo <text>` or `$translation sup <text>`
- Separate line: a line containing only `vo` or `sup` before the text
If no mode is provided, ask which mode to use.

## Shared Rules
- Translate into smooth, natural, idiomatic English; rewrite freely for clarity and flow.
- Output only the translated line(s); do not prepend labels like "VOICEOVER:" or "SUPER:" unless the user explicitly asks for them.
- Ignore/strip leading cue tags if present (e.g., `(NS)`, `(SOT)`), unless the user explicitly asks to keep them.
- Apply the terminology rules below consistently.

## Terminology Rules (Consistency)
- Translate "祝福金" as "cash relief" in disaster relief; otherwise "cash aid."
- Translate "物資卡" as "gift card(s)" when restricted to goods; otherwise "cash card(s)."
- Translate "會員" as "donating member(s)."
- Translate "精油" as "essential oil(s)."
- Translate "土耳其" as "Türkiye."
- Translate "補助金" as "financial aid" for non-government support; "subsidy" only for government programs.
- Translate "竹筒" as "bamboo bank(s)" only when highlighting spirit; otherwise "donation box" or "a small donation."
- Translate "證嚴上人" as "Venerable Master Cheng Yen."
- Translate branch names as “Tzu Chi's office in <city>.”
- Translate "口說好話，心想好意，身行好事" as "speak kind words, think kind thoughts, and do kind deeds."
- Translate "慈濟慈善基金會" as "Tzu Chi Foundation."
- Translate "原住民" as "indigenous."
- Translate "慈濟照顧戶" as "Tzu Chi's aid recipient."
- Translate "慈濟眼科中心" as "Tzu Chi Eye Center."
- Use "allow" instead of "let" when natural.
- Use "Bodhisattvas" (capitalized).
- Translate "食物銀行" as "food bank supplies."
- Translate "生活物資" as "supplies."
- Translate "地方家長" as "community leader."
- Translate "歲末祝福" as "Year-end Blessings Ceremony."
- Include "Sister" before the English name when the Chinese uses "修女."
- Translate "心態" as "attitude" unless it clearly means long-term mindset.
- Translate "姊妹們" as "the girls."
- Translate "弱勢族群" as "low-income residents" or "underserved residents" (pick the more natural fit for the line).

## MODE: VOICEOVER
Rewrite the Chinese as a single, natural English TV news voice-over line. Prioritize broadcast fluency and spoken pacing over literal translation. Compress aggressively, remove procedural details, and summarize the event at a high level. The result should sound like a polished news script, not a translation. If a detail does not advance the main action or emotional takeaway, omit it.

## MODE: SUPER
1. Rewrite the Chinese as a short, natural English interview soundbite. Prioritize spoken rhythm and emotional clarity over completeness. Simplify sentence structure, avoid formal phrasing, and let it sound like something a real person would say on camera. Omit details that feel explanatory rather than personal.
2. Do NOT wrap the entire output in quotation marks. Quotation marks may only be used if they appear naturally inside the dialogue itself.
3. Split that paragraph into subtitle lines, each under 55 characters, keeping all punctuation exactly as it appears in the translated paragraph.
