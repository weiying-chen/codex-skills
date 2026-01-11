---
name: translation
description: Translate Chinese to natural English in VOICEOVER (vo) or SUPER (sup) style, using consistent terminology rules and flexible mode selection.
---

# Translation

## Mode Selection
Accept mode tokens case-insensitively in either format:
- Single line: `$translation vo <text>` or `$translation sup <text>`
- Separate line: a line containing only `vo` or `sup` before the text
If no mode is provided, ask which mode to use.

## Shared Translation Rules
- Translate into smooth, natural, idiomatic English. Rewrite freely for clarity and flow.
- Output only the translated line(s); do not prepend labels like "VOICEOVER:" or "SUPER:" unless the user explicitly asks for them.
- Bias toward natural English over “faithful” structure: re-order, merge, or compress to avoid Chinese-to-English calques.
- Ignore/strip leading cue tags if present (e.g., `(NS)`, `(SOT)`); do not include them in the English output unless the user explicitly asks to keep them.
- Keep the timeline simple; only spell out a step-by-step sequence when it adds clarity.
- Avoid filler phrases like “allowed him to” / “made him able to” when a simpler verb works (“helped him feel safe,” “put him at ease”).
- Prefer active verbs and varied sentence openings; don’t default every line to the same cause→effect template.
- Prefer plain, everyday phrasing over clinical or abstract wording (e.g., “something got into his eyes,” “left his eyes irritated,” “made it hard to focus”).
- Avoid stiff constructions like “after contact with” / “came into contact with”; rewrite into everyday phrasing people actually use.
- Avoid clunky passive accident phrasing like “after he was splashed…”; prefer “dirty water got in his eyes,” “he got dirty water in his eyes,” or “dirty water splashed into his eyes.”
- Avoid awkward possessives in news copy (e.g., “the care team’s patience”); prefer “the staff were patient and caring” / “the medical team reassured him.”
- Avoid time-filler add-ons like “during his visit” or “as he sought care/treatment”; usually omit them, or use a plain verb only if needed (“went to the clinic,” “got checked out”).
- Avoid “is being …” phrasing unless it’s truly needed; prefer a clean active sentence.
- If age is included, avoid “At 12,”; prefer “12-year-old Maya …” / “Twelve-year-old Maya …” or fold it in later (“Maya, 12, …”) when it reads naturally.
- For body parts, prefer a possessive (e.g., “his eyes”) over “them/the eyes” when it reads clearer.
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
- Write a single, natural TV news voice-over line (one line; 1–2 short sentences is OK if it sounds more broadcast-natural).
- Prioritize broadcast fluency, spoken pacing, and “news copy” rhythm over literal completeness.
- Compress aggressively and summarize at a high level.
- Omit procedural or minor details.
- Default to clean, direct phrasing; avoid clunky cause-and-effect scaffolding unless it adds clarity.
- Prefer simple, spoken verbs like “went to the clinic,” “got checked out,” “saw a doctor,” or omit the medical-process framing entirely.
- Prefer people as the subject (“staff,” “doctors,” “volunteers,” “residents”) over abstract nouns doing actions (“the screening is being run…”).

## Examples (Generic)
Use these as pattern guides; rewrite freely.

### VO: Age phrasing
- Prefer: “A fall left 12-year-old Maya with a fractured wrist.”
- Prefer: “Maya, 12, fractured her wrist in a fall.”
 - Avoid: “At 12, Maya …”

### VO: Medical-process filler
- Prefer: “He went to the clinic to get his eyes checked.”
- Prefer: “Clinic staff reassured him and checked his eyes.”
- Avoid: “As he sought care/treatment …”
- Avoid: “During his visit …”

### VO: Avoid abstract possessives
- Prefer: “The staff were patient and reassuring.”
- Prefer: “The medical team reassured him.”
- Avoid: “The care team’s patience and love …”

### VO: Event copy (keep it human)
- Prefer: “Free eye screenings ran for two days, bringing in low-income residents hoping to see clearly again.”
- Prefer: “Staff guided patients through check-in, tests, and clear explanations.”
- Avoid: “A two-day free eye screening is being run with care at every step…”

### SUPER: Soundbite style
- Prefer: “I was really worried at first, but they were so kind—I felt safe right away.”
- Avoid: “The medical staff’s patience and love made me feel at ease during the consultation.”

### VO Quick Self-Check
- Read it aloud: it should sound like a single breath of news copy, not a literal rewrite.
- Watch for clunky patterns: “after contact with…,” “after he was splashed…,” “At 12,…,” “during his visit…,” “as he sought care/treatment…,” and abstract possessives like “the team’s patience…”
- Watch for bureaucratic phrasing like “is being run,” “with care at every step,” “every detail was not overlooked”; rewrite into plain spoken English.
- Favor concrete verbs + outcomes: “got dirty water in his eyes,” “left his eyes irritated,” “made it hard to focus,” “reassured him.”

## MODE: SUPER
- Write a short, natural interview soundbite.
- Favor spoken rhythm and emotional clarity.
- Keep it personal and conversational; omit explanatory details.
