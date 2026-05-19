# Weekly Index Review — Bilingual Output Rules

## Purpose

This file defines the bilingual output contract for the Weekly Index Review.

The bilingual system must produce an English report and a Dutch companion report from the same state, pricing, ranking, research and portfolio artifacts.

The Dutch report is a localized companion view, not a second investment model.

---

## Non-negotiable invariants

For every bilingual run:

```text
EN requested close date == NL requested close date
EN report token == NL report token
EN pricing basis == NL pricing basis
EN portfolio value == NL portfolio value
EN cash value == NL cash value
EN holdings == NL holdings
EN tickers == NL tickers
EN position sizes == NL position sizes
EN recommendation decisions == NL recommendation decisions
```

If any invariant fails, the bilingual package must not be sent.

---

## File naming contract

English markdown:

```text
output_indices/weekly_indices_review_YYMMDD.md
```

Dutch markdown:

```text
output_indices/weekly_indices_review_nl_YYMMDD.md
```

English PDF:

```text
output_indices/weekly_indices_review_YYMMDD.pdf
```

Dutch PDF:

```text
output_indices/weekly_indices_review_nl_YYMMDD.pdf
```

English delivery HTML:

```text
output_indices/weekly_indices_review_YYMMDD_delivery.html
```

Dutch delivery HTML:

```text
output_indices/weekly_indices_review_nl_YYMMDD_delivery.html
```

The Dutch filename must use the same token as the English filename.

---

## Report structure parity

The Dutch report must preserve the same section order as the English report:

1. Samenvatting
2. Portefeuille-acties in één oogopslag
3. Wereldwijd regimedashboard
4. Indexkansenbord
5. Belangrijkste risico’s / ontkrachters
6. Kernconclusie
7. Vermogenscurve en portefeuilleontwikkeling
8. Regionale en stijlallocatiekaart
9. Tweede-orde-effectenkaart
10. Beoordeling huidige posities
11. Beste nieuwe indexkansen
12. Portefeuillerotatieplan
13. Definitieve actietabel
14. Positiewijzigingen in deze run
15. Huidige portefeuilleposities en cash
16. Continuïteitsinvoer voor de volgende run
17. Disclaimer

The Dutch report must preserve:
- Investor Report first
- Analyst Report second
- `DEEL II / Analistenrapport` transition
- Section 7: equity curve plus Tradable Proxy Performance
- Section 15: holdings/cash only

---

## Numeric parity

The following must match exactly or within deterministic formatting tolerance:

- portfolio value
- cash
- market values
- weights
- shares
- proxy prices
- 1w / 1m / 3m / since-entry returns
- P/L EUR
- contribution percentages
- candidate scores
- scorecard values

Dutch formatting may use Dutch labels, but numeric values must not change.

Preferred numeric style:

```text
EUR 111,116.08
25.11%
+4.01%
```

Do not localize decimals to commas unless every validator and table parser supports it. Initial bilingual implementation should preserve English-style decimal points for numeric parity and easier validation.

---

## Date localization

Dutch report dates must use Dutch weekday and month names.

Correct:

```text
maandag 18 mei 2026
```

Incorrect:

```text
Monday, 18 May 2026
```

No English weekday/month names may appear in the Dutch report title, hero block, or summary.

---

## Terminology authority

Use:

```text
control/NL_TERMINOLOGY.md
```

as the terminology source for Dutch output.

The Dutch report must avoid:
- raw internal artifact terms
- workflow language
- literal machine translations
- mixed English/Dutch financial phrases where a better Dutch term exists

Tickers, index names and ETF symbols stay unchanged.

---

## Layout and rendering parity

The Dutch report must reuse the validated English layout system:

- same Investor/Analyst visual split
- same petrol-teal Analyst identity
- same chart embedding
- same table styling
- same inline-list marker rendering
- same TradingView ticker links
- same print-safe equity chart labels

The Dutch version may need slightly shorter wording where long Dutch text risks overflow.

If the Dutch text causes visual overflow, shorten the Dutch copy rather than weakening the layout.

---

## Validation requirements before bilingual delivery

A bilingual send must pass:

1. English report validators.
2. Dutch markdown structure validator.
3. EN/NL section parity validator.
4. EN/NL numeric parity validator.
5. Dutch date-localization validator.
6. Dutch terminology validator.
7. Dutch render-polish validator.
8. Dutch ticker-link validator.
9. Bilingual delivery-manifest validator.

Failure rule:

```text
If either language fails, do not send the bilingual package.
```

---

## Delivery contract

The delivery manifest must list both English and Dutch assets:

- English markdown
- Dutch markdown
- English PDF
- Dutch PDF
- English delivery HTML
- Dutch delivery HTML
- equity curve image if attached or embedded

Do not claim bilingual delivery succeeded without workflow manifest or send receipt evidence.

---

## Implementation sequence

Recommended sequence:

1. Generate Dutch markdown from the English/state artifacts.
2. Validate Dutch section headings and date localization.
3. Validate numeric parity against English.
4. Render Dutch HTML/PDF.
5. Validate render and ticker links.
6. Extend delivery to attach EN + NL outputs.
7. Extend run manifest to include bilingual asset list.

Do not start with email delivery. First prove markdown and render parity.
