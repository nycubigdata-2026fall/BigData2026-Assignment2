# Evaluation

The task, the output format and how submissions are scored. Run the commands below from the
folder that contains `assignment2/` (see the [main README](../README.md) for downloading).

| File | Content |
|---|---|
| `evaluate.py` | Checks the output format and computes the score |
| `examples/sample_output.csv` | An example output (week of 9/27, 4,785 users); your output must have exactly the same format |
| `examples/sample_truth.csv` | The correct answers for the same users |
| `test_input.csv` | The official test users (published on 10/28) |

## Task

For each user in `test_input.csv`, predict whether the user performs each of these 6
activities on any repository in the 7 days from 2026-11-11 16:00 UTC (11/12 00:00 Taiwan).
Output 0 or 1 for each:

| Column | Meaning |
|---|---|
| `open_pr` | Opens a new pull request |
| `open_issue` | Opens a new issue (not a PR) |
| `issue_comment` | Comments in the discussion thread of an issue or PR |
| `pr_review` | Submits a review on a PR (approve, request changes or comment) |
| `pr_review_comment` | Comments on specific lines of a PR's code diff |
| `push` | Pushes commits to a branch or tag |

`test_input.csv` (one `UserID` column, the GitHub user id) will be published here on
**10/28**: the cohort users with at least 5 activity records in the 90 days before 10/28
20:00 Taiwan time (the data of that day's release).

## Output format and evaluate.py

```
UserID,open_pr,open_issue,issue_comment,pr_review,pr_review_comment,push
989,1,0,0,0,0,1
2016,0,0,0,0,0,1
```

- `UserID` is the GitHub user id (`Users.github_user_id`).
- The header must be exactly as above, in the same order.
- Exactly one row for each given UserID: none missing, none extra, no duplicates.
- The 6 prediction columns may only contain 0 or 1, with no empty cells.

A format error stops the evaluation and the submission is not scored.

```bash
python assignment2/evaluation/evaluate.py --pred output.csv                                                # format check only
python assignment2/evaluation/evaluate.py --pred output.csv --input assignment2/evaluation/test_input.csv             # format check and the UserIDs match the test list
python assignment2/evaluation/evaluate.py --pred output.csv --truth assignment2/evaluation/examples/sample_truth.csv   # format check and score (example week)
```

## Scoring

```math
\text{Score} = \frac{\text{macro-F1} + \text{micro-F1}}{2}
```
