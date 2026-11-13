# Judge prompt template (one failure mode per judge)

You are checking one thing only: <failure mode, in the words from error analysis>.

Pass if: <concrete description of acceptable output>.
Fail if: <concrete description of the failure, with one real example>.

Input:
<input>

Output to check:
<output>

Answer with JSON only: {"pass": true or false, "reason": "<one sentence>"}

Before use: label at least 20 outputs by hand, run this judge on them and report agreement on passes and on fails
separately. Rewrite the pass and fail lines, not the labels, until the human accepts both numbers.
