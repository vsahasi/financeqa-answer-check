"""Recompute a few FinanceQA gold answers from the numbers in their own questions.

Usage: python3 check.py [path/to/test.csv]
Without a path it downloads FinanceQA/test.csv from the Hugging Face dataset.
Rows are 0-based positions in test.csv, header excluded.
"""
import csv, io, sys, urllib.request
from collections import defaultdict

URL = "https://huggingface.co/datasets/AfterQuery/FinanceQA/resolve/main/FinanceQA/test.csv"

csv.field_size_limit(10**9)
if len(sys.argv) > 1:
    text = open(sys.argv[1], encoding="utf-8", newline="").read()
else:
    text = urllib.request.urlopen(URL).read().decode("utf-8")
rows = list(csv.DictReader(io.StringIO(text)))
print(f"{len(rows)} rows\n")


def show(i, recomputed, note):
    r = rows[i]
    print(f"row {i}: {r['question'].strip()[:110]}...")
    print(f"  gold answer : {r['answer'].strip()[:90]}")
    print(f"  recomputed  : {recomputed}")
    print(f"  note        : {note}\n")


# 86: $75 in 7 years at 9%
show(86, f"${75 / 1.09 ** 7:.2f}", "75 / 1.09^7")

# 98: WACC 9%, after-tax debt 5%, D/E 0.6. The reasoning gets E/V = 0.625 and then divides by 0.675.
d_v = 0.6 / 1.6
show(98, f"{(0.09 - d_v * 0.05) / (1 - d_v):.2%}", "(9% - 0.375 * 5%) / 0.625")

# 100: same deal as row 99 (EV +60, debt +30, cash -30), but the question asks about equity value.
show(100, f"{60 - 30 - 30}M change",
     "equity = EV - debt + cash, with debt up 30 and cash down 30 as the reasoning assumes; the reasoning text is row 99's, word for word")

# 103: 800 purchase, 400 debt, all 400 paid down, no cash left, exit at 300 * 5.
moic = (300 * 5) / 400
show(103, f"{moic:.2f}x MOIC, {moic ** 0.2 - 1:.0%} IRR",
     "the reasoning still subtracts the 400 of debt the question says was paid down, and adds 100 of cash the question never mentions")

# 110: revenue 120, costs 90 (half fixed), volume +15%
profit = 120 * 1.15 - (45 + 45 * 1.15)
show(110, f"${profit - 30:.2f} million increase", "the reasoning also ends at 11.25; only the answer field says 11.5")

# 112: price doubles from $25, $12 cost, 15% overhead
show(112, "cannot be computed", "the question never says how many mugs are sold; the reasoning multiplies by 15")

# 146: $300 loan at 6% interest, 12% of principal repaid, 10% tax
ni = (600 - 300 - 150 - 300 * 0.06) * 0.9
show(146, f"net income {ni:.1f}, cash up {ni + 300 - 36:.1f}",
     "same steps as the reasoning, but it charges 12% interest (36) where the question says 6% (18)")

# 142: wording
show(142, "issuing debt raises cash flow from financing by $300", "answer text says it 'reduces' it")

# The next three are 10-K questions. I only evaluated the last expression of their reasoning.

# 64: Costco ROA. The reasoning's last line is (7367 + 211.8283272) / 69412.5 = 11.31%.
show(64, f"{(7367 + 211.8283272) / 69412.5:.2%}", "that expression is not 11.31%")

# 18: Costco WACC. The last line says the expression equals 9.66%; the answer field says 9.56%.
e, d = 418_856, 11_414.85
show(18, f"{0.0966 * e / (d + e) + 0.06 * d / (d + e):.2%}",
     "the expression on the last line works out to the answer field, not to the 9.66% written after it")

# 78: inventory turnover question whose reasoning is about membership counts.
show(78, f"{222_358 / ((18_647 + 16_651) / 2):.1f}x",
     "merchandise costs over average inventory; the attached reasoning never mentions inventory")

dupes = defaultdict(list)
for i, r in enumerate(rows):
    dupes[r["chain_of_thought"].strip()].append(i)
print("rows sharing identical reasoning text:", [v for v in dupes.values() if len(v) > 1])
