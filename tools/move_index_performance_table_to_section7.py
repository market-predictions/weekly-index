import re
from pathlib import Path

out = Path('output_indices')
report_re = re.compile(r'^weekly_indices_review_(\d{6})(?:_(\d{2}))?\.md$')
hits = []
for path in out.glob('weekly_indices_review_*.md'):
    match = report_re.match(path.name)
    if match:
        hits.append((match.group(1), int(match.group(2) or '0'), path))
if not hits:
    raise SystemExit('no canonical weekly index report found')
hits.sort(key=lambda row: (row[0], row[1]))
report = hits[-1][2]
text = report.read_text(encoding='utf-8')
marker = '### Tradable Proxy Performance'
chart = '`EQUITY_CURVE_CHART_PLACEHOLDER`'
sec8 = '\n## 8.'
sec15 = '\n## 15.'
sec16 = '\n## 16.'

if marker not in text:
    raise SystemExit('performance table missing')

s7 = text.index('\n## 7.')
s8 = text.index(sec8, s7)
s15 = text.index(sec15)
s16 = text.index(sec16, s15)

section7 = text[s7:s8]
section15 = text[s15:s16]

if marker in section7:
    print(f'INDEX_SECTION7_PERFORMANCE_OK | report={report.name} | already_moved=yes')
    raise SystemExit(0)

if marker not in section15:
    raise SystemExit('performance table not in section 7 or 15')

m = section15.index(marker)
block = section15[m:].strip()
section15_clean = section15[:m].rstrip() + '\n\n'

if chart not in section7:
    raise SystemExit('equity curve placeholder missing in section 7')

c = section7.index(chart) + len(chart)
section7_new = section7[:c].rstrip() + '\n\n' + block + '\n' + section7[c:].rstrip() + '\n'
text_new = text[:s7] + section7_new + text[s8:s15] + section15_clean + text[s16:]
report.write_text(text_new.rstrip() + '\n', encoding='utf-8')
print(f'INDEX_SECTION7_PERFORMANCE_OK | report={report.name} | moved=yes')
