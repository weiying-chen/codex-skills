---
name: translation
description: Translate Chinese to natural English in VOICEOVER (vo) or SUPER (sup) style, using consistent terminology rules.
---

# Translation

## Mode Selection
Accept mode tokens case-insensitively in either format:
- Single line: `$translation vo <text>` or `$translation sup <text>`
- Separate line: a line containing only `vo` or `sup` before the text
Sticky mode within the same chat:
- If the user omits the mode but has explicitly set `vo` or `sup` earlier in this chat, reuse the most recently set mode.
- Otherwise, if no mode is provided, choose the best fit:
- Use `vo` for third-person narration, news-style facts, and scene description.
- Use `sup` for first-person speech, quote-like lines, and anything that should read like an interview bite.
If it's genuinely ambiguous, ask which mode the user wants.

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

## MODE: VOICEOVER (vo)
1. Draft for meaning (capture the full intent).
2. Rewrite as original English TV news voice-over (spoken pacing; not literal).
3. Compress aggressively into a single line; keep only key facts and the emotional takeaway.
4. Final check: output only the line (no labels).

## MODE: SUPER (sup)
1. Draft for meaning.
2. Rewrite into a short, natural interview soundbite (spoken rhythm; not literal).
3. Split into subtitle lines (each under 55 characters), preserving punctuation exactly.
4. Final check: don’t wrap the whole output in quotation marks; output only the subtitle lines.
