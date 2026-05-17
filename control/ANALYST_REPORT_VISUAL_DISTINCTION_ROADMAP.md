# Analyst Report Visual Distinction Baseline

## Status
Frozen as the current Weekly Index design baseline after PDF review on 2026-05-17.

## Decision
The Weekly Index report uses explicit visual mode separation between the Investor Report and Analyst Report.

The Investor Report keeps the warm executive investor identity. The Analyst Report uses a distinct petrol-teal institutional analyst identity.

## Final Analyst palette
- Primary analyst header and section badges: `#0F5B5C` deep petrol-teal
- Dark analyst accent / text accent: `#0B4446`
- Premium divider accent: `#C9A96A`
- Analyst panel background: `#F5F8F8`
- Analyst table header background: `#E4EEEE`
- Nested analyst cards: `#FFFFFF`
- Nested analyst card border: `#D6E1E1`
- Even analyst table rows: `#F7FBFB`
- Header text: `#FFFFFF`

## Render behavior
1. Force a hard page break before the Analyst Report.
2. Add a dedicated Analyst Report transition header.
3. Show `PART II` above `Analyst Report`.
4. Keep the gold divider accent for continuity with the premium brand language.
5. Use petrol-teal section-number badges and section-label color throughout Analyst pages.
6. Keep Section 10 position cards white inside the subtle cool-grey Analyst panel; do not give Section 10 a separate blue card tint.
7. Validate rendered output so the Analyst Report boundary cannot silently disappear.

## Output-contract decision
Investor Report and Analyst Report must not appear as one continuous undifferentiated document. The transition must be visible even when a reader skims the PDF.

## Regression guard
The workflow validator `tools/validate_index_analyst_visual_distinction.py` must continue to require the petrol-teal Analyst identity marker `#0F5B5C`.
