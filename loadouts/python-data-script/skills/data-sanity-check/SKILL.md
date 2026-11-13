---
name: data-sanity-check
description: Profile a dataset (CSV, Excel, Parquet, JSON) and flag quality problems before analysis. Use when the user shares a data file, asks "is this data OK?", or before producing figures someone will rely on.
---

# Data sanity check

Write a throwaway script `scripts/00_sanity_check.py` (PEP 723, polars) that reads the file and prints the checks below.
Do not modify the input file.

## Checks
1. **Shape:** row and column count. Does it match what the human expects (ask if they know)?
2. **Types:** each column's inferred type. Flag numbers stored as text (e.g. "1,234", "£12.50"), dates stored as text,
   and IDs inferred as numbers (leading zeros lost).
3. **Nulls:** null count and percentage per column. Flag columns over 5% null and "null-like" strings: `""`, `"N/A"`, `"null"`, `"-"`, `"0"` in date columns.
4. **Duplicates:** fully duplicated rows, and duplicates on the column that should be a unique key.
5. **Ranges:** min/max for numbers and dates. Flag negatives where impossible, dates in the future or before 1990, outliers beyond 3 IQR.
6. **Categories:** for text columns with fewer than 50 distinct values, list the values with counts. Flag near-duplicates
   (`"London"`, `"london"`, `"London "`).
7. **Dates:** check whether day-first or month-first parsing is ambiguous (all days ≤ 12?). Note time zone assumptions.
8. **Joins (if a second file is involved):** key overlap in both directions, and whether the join is one-to-one,
   one-to-many or many-to-many. Many-to-many is almost always a mistake.
9. **Totals:** if there is an amount column, print the grand total so the human can reconcile it with the source system.
10. **Personal data:** flag columns that look like names, emails, phone numbers or addresses.

## Report
```
Sanity check — <file> — <rows> rows × <cols> columns
Problems
- [High] customer_id inferred as integer — 214 IDs had leading zeros. Read as string.
- [Medium] order_date: 3.1% null; 12 dates in 2031.
Looks fine
- No duplicate rows; amounts total £48,210.55.
Questions for you
- Is order_date day-first? Every day value is ≤ 12, so it's ambiguous.
```
Lead with problems, keep "looks fine" to a line or two, and end with questions only the human can answer.
