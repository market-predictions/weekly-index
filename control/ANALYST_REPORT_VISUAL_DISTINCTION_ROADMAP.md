# Analyst Report Visual Distinction Roadmap

## Current issue
The Weekly Index PDF contains an Investor Report followed by an Analyst Report, but the visual transition is too soft. Readers should immediately understand that the Investor Report has ended and the Analyst Report has started.

## Recommended change
Add a clear visual boundary between the two report modes.

## Design direction
Use a distinct premium Analyst Report palette that harmonizes with the existing executive report style but is clearly different from the Investor Report.

Recommended Analyst palette:
- Primary analyst header: `#2F4A66` deep slate blue
- Dark analyst accent: `#24384D`
- Premium divider accent: `#C9A96A`
- Light analyst panel background: `#F4F6F8`
- Header text: `#FFFFFF`

## Implementation roadmap
1. Add a hard page break before the Analyst Report in PDF output.
2. Add a dedicated Analyst Report transition header.
3. Use the slate-blue Analyst palette for the Analyst header and section-number badges.
4. Keep the gold divider accent for continuity with the premium brand language.
5. Add a persistent `Analyst Report` visual cue on analyst pages.
6. Add render validation so the Analyst Report boundary cannot silently disappear.

## Output-contract decision
Investor Report and Analyst Report must not appear as one continuous undifferentiated document. The transition must be visible even when a reader skims the PDF.
