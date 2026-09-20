# financeqa-answer-check

I read the 64 conceptual questions in FinanceQA's test.csv and recomputed the gold answers that looked off, using only the numbers in each question.
Six gold answers come out different (rows 86, 98, 100, 103, 110, 146) and one question can't be answered as worded (112). Row 142's answer has debt issuance reducing financing cash flow.
For the 84 questions that need a 10-K I did not check the finance, only a few places where an answer and the last line of its own reasoning disagree. Row 64's last expression works out to 10.92%, not the 11.31% it states. Row 78 carries the reasoning for a different question, and row 18's reasoning ends at 9.66% where the answer field says 9.56%. This part is not a complete list.

    python3 check.py            # downloads test.csv from Hugging Face
    python3 check.py test.csv   # or use a local copy

`output.txt` is what it printed on 2026-09-19. Rows are 0-based, header excluded. Standard library only.
