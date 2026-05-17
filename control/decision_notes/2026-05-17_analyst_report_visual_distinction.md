# Decision Note — Analyst Report Visual Distinction

## Date
2026-05-17

## Decision
Weekly Index reports will use explicit visual mode separation between the Investor Report and the Analyst Report.

## Why
The current PDF structure contains an Investor Report followed by an Analyst Report, but the visual transition is too soft. Readers should immediately understand that the investor-facing section has ended and a deeper analyst section has started.

## Stable design direction
- Add a hard page break before the Analyst Report.
- Add a dedicated Analyst Report transition header.
- Use a distinct premium slate-blue analyst palette.
- Preferred Analyst primary header: `#2F4A66`.
- Preferred Analyst dark accent: `#24384D`.
- Preferred premium divider accent: `#C9A96A`.
- Preferred light analyst panel background: `#F4F6F8`.
- Keep white text on the analyst header for contrast.

## Output-contract implication
Investor Report and Analyst Report must not appear as one continuous undifferentiated document. The rendered PDF should make the report-mode boundary clear even when a reader skims quickly.
