# Bilingual Weekly Index Architecture

## Purpose

Add a Dutch companion report to the Weekly Index product without creating a second investment model.

The bilingual model must preserve the validated English baseline and add a language/rendering layer on top of the same data, state, pricing, and report-token contract.

---

## 1. Decision framework

The investment decision framework remains shared across both languages.

Both reports must use the same decisions for:
- regime classification
- portfolio actions
- long-side opportunity board
- defensive / inverse opportunity readiness
- capital re-underwriting
- current holdings and cash
- portfolio value and contribution
- continuity input

The Dutch report may rephrase the conclusions, but it must not reinterpret the model or introduce different investment decisions.

---

## 2. Input / state contract

The English and Dutch reports must consume the same authoritative artifacts:

- requested close date
- report token
- `output_indices/index_portfolio_state.json`
- `output_indices/index_valuation_history.csv`
- `output_indices/index_recommendation_scorecard.csv`
- pricing audit for the requested close date
- candidate ranking artifact for the report token
- discovery coverage artifact for the report token
- macro / research / alternative-duel / short-radar artifacts

Required invariant:

```text
EN report token == NL report token == requested close date token
EN pricing basis == NL pricing basis
EN portfolio value == NL portfolio value
EN positions == NL positions
```

The Dutch report must never run a separate pricing pass or separate ranking model.

---

## 3. Output contract

The Dutch report must preserve:

- Investor Report first
- Analyst Report second
- visible Part II / Analyst Report transition
- Section 7: equity curve plus Tradable Proxy Performance
- Section 15: holdings/cash only
- TradingView ticker links in tables
- embedded equity curve image
- print-safe chart labels
- inline list markers
- premium executive visual language

The Dutch report must localize:

- report date / weekday / month names
- section labels
- table headers
- recurring finance terminology
- summary blocks and action language

The Dutch report must avoid:

- English weekday/month leakage
- literal machine translations
- raw internal artifact labels
- process-language leakage
- different numbers from the English report

---

## 4. Operational runbook

Recommended implementation order:

1. Add Dutch terminology control file.
2. Add Dutch output rules.
3. Generate Dutch markdown from the same canonical report/state artifacts.
4. Add numeric parity validator.
5. Add section parity validator.
6. Add Dutch date-localization validator.
7. Add Dutch terminology validator.
8. Render Dutch PDF using the same layout logic.
9. Extend delivery manifest to list EN and NL assets.
10. Send EN and NL together only if both validate.

Failure rule:

```text
If either EN or NL fails validation, do not send the bilingual package.
```

---

## Initial file-path proposal

Potential future files:

- `control/NL_TERMINOLOGY.md`
- `control/BILINGUAL_OUTPUT_RULES.md`
- `tools/generate_index_nl_report.py`
- `tools/validate_index_bilingual_numeric_parity.py`
- `tools/validate_index_bilingual_section_parity.py`
- `tools/validate_index_nl_language_contract.py`
- `send_index_report_bilingual.py`

Output paths:

- English: `output_indices/weekly_indices_review_YYMMDD.md`
- Dutch: `output_indices/weekly_indices_review_nl_YYMMDD.md`
- English PDF: `output_indices/weekly_indices_review_YYMMDD.pdf`
- Dutch PDF: `output_indices/weekly_indices_review_nl_YYMMDD.pdf`

---

## Authority rule

The English report and machine artifacts are the initial source of truth for numbers and decisions. The Dutch report is a localized companion view. It may improve readability and terminology, but it may not change the investment state.
