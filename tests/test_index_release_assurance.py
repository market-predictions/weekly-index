from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.index_release_assurance import (
    build_release_assurance,
    validate_release_assurance,
    write_english_deferral_marker,
)


class IndexReleaseAssuranceTests(unittest.TestCase):
    def _report(self, root: Path, name: str, value: str) -> Path:
        headings = "\n".join(f"## {i}. Section {i}" for i in range(1, 18))
        body = (
            "# Weekly Indices Review 2026-05-18\n"
            + headings
            + "\n| Exposure | Proxy | Value EUR | Weight % |\n"
            + "|---|---|---:|---:|\n"
            + f"| S&P 500 | SPY | {value} | 25.11% |\n"
            + "| Cash | CASH | 15,566.74 | 14.01% |\n"
            + ("Evidence narrative. " * 80)
        )
        report = root / f"{name}.md"
        report.write_text(body, encoding="utf-8")
        report.with_name(f"{report.stem}_delivery.html").write_text(
            "<!doctype html><html><body>" + ("validated index delivery " * 100) + "</body></html>",
            encoding="utf-8",
        )
        report.with_suffix(".pdf").write_bytes(b"%PDF-" + b"0" * 2048)
        report.with_name(f"{report.stem}_equity_curve.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 256)
        return report

    def _fixture(self, root: Path, *, dutch_value: str = "27.902,30") -> tuple[Path, Path, Path]:
        close_date = "2026-05-18"
        token = "260518"
        output = root / "output_indices"
        (output / "pricing").mkdir(parents=True)
        (output / "runtime").mkdir(parents=True)
        (output / "run_manifests").mkdir(parents=True)

        en = self._report(output, f"weekly_indices_review_{token}", "27,902.30")
        nl = self._report(output, f"weekly_indices_review_nl_{token}", dutch_value)
        pricing = output / "pricing" / f"index_price_audit_{close_date}.json"
        portfolio = output / "index_portfolio_state.json"
        scorecard = output / "index_recommendation_scorecard.csv"
        ranking = output / f"index_candidate_ranking_{token}.json"
        coverage = output / f"index_discovery_coverage_{token}.json"
        runtime = output / "runtime" / f"index_report_state_{token}.json"
        valuation = output / "index_valuation_history.csv"

        pricing.write_text(
            json.dumps(
                {
                    "requested_close_date": close_date,
                    "positions": [
                        {
                            "benchmark_symbol": "^GSPC",
                            "primary_proxy": "SPY",
                            "benchmark_close": 7403.0,
                            "proxy_close": 738.65,
                            "benchmark_source": "yahoo_chart",
                            "proxy_source": "yahoo_chart",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        portfolio.write_text(json.dumps({"positions": [{"exposure_id": "us_large_cap"}]}), encoding="utf-8")
        scorecard.write_text("exposure_id,action\nus_large_cap,hold\n", encoding="utf-8")
        valuation.write_text("date,value\n2026-05-18,111116.08\n", encoding="utf-8")
        ranking.write_text(json.dumps({"report_token": token}), encoding="utf-8")
        coverage.write_text(json.dumps({"report_token": token}), encoding="utf-8")
        runtime.write_text(
            json.dumps(
                {
                    "report_token": token,
                    "report_date": close_date,
                    "source_files": {
                        "portfolio_state": str(portfolio),
                        "scorecard": str(scorecard),
                        "pricing_audit": str(pricing),
                        "candidate_ranking": str(ranking),
                        "discovery_coverage": str(coverage),
                    },
                }
            ),
            encoding="utf-8",
        )
        old_cwd = Path.cwd()
        try:
            import os
            os.chdir(root)
            write_english_deferral_marker(en.relative_to(root), close_date=close_date, token=token)
        finally:
            os.chdir(old_cwd)
        return en.relative_to(root), nl.relative_to(root), Path("output_indices/run_manifests") / f"index_release_assurance_{close_date}_{token}.json"

    def test_valid_bilingual_candidate_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            en, nl, assurance = self._fixture(root)
            old_cwd = Path.cwd()
            try:
                import os
                os.chdir(root)
                record = build_release_assurance(
                    source_sha="b" * 40,
                    github_run_id="123",
                    requested_close_date="2026-05-18",
                    report_token="260518",
                    english_report=en,
                    dutch_report=nl,
                    output=assurance,
                )
                self.assertEqual(record["decision"], "PASS")
                validate_release_assurance(
                    assurance,
                    expected_source_sha="b" * 40,
                    expected_close_date="2026-05-18",
                    expected_report_token="260518",
                )
            finally:
                os.chdir(old_cwd)

    def test_numeric_divergence_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            en, nl, assurance = self._fixture(root, dutch_value="99.999,99")
            old_cwd = Path.cwd()
            try:
                import os
                os.chdir(root)
                record = build_release_assurance(
                    source_sha="b" * 40,
                    github_run_id="123",
                    requested_close_date="2026-05-18",
                    report_token="260518",
                    english_report=en,
                    dutch_report=nl,
                    output=assurance,
                )
                self.assertEqual(record["decision"], "FAIL")
                self.assertIn("bilingual_table_numeric_parity", record["blockers"])
                with self.assertRaises(RuntimeError):
                    validate_release_assurance(assurance)
            finally:
                os.chdir(old_cwd)

    def test_missing_proxy_field_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            en, nl, assurance = self._fixture(root)
            pricing = root / "output_indices/pricing/index_price_audit_2026-05-18.json"
            payload = json.loads(pricing.read_text(encoding="utf-8"))
            payload["positions"][0].pop("proxy_close")
            pricing.write_text(json.dumps(payload), encoding="utf-8")
            old_cwd = Path.cwd()
            try:
                import os
                os.chdir(root)
                record = build_release_assurance(
                    source_sha="b" * 40,
                    github_run_id="123",
                    requested_close_date="2026-05-18",
                    report_token="260518",
                    english_report=en,
                    dutch_report=nl,
                    output=assurance,
                )
                self.assertEqual(record["decision"], "FAIL")
                self.assertIn("benchmark_proxy_separation", record["blockers"])
            finally:
                os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()
