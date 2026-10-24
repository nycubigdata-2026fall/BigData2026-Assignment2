# Data

GH Archive activity of a fixed group of 9,000 users on any public GitHub repository, from
2025-12-01 00:00 UTC up to this release, as 8 relational tables. Updated every day at 21:00
Taiwan time (see the [main README](../README.md) for downloading and updating).

```
db/
  SCHEMA.md                            every column of every table, explained
  Users.parquet                        the 8 tables, one Parquet file each
  Repositories.parquet
  PullRequests.parquet
  Issues.parquet
  IssueComments.parquet
  PRReviews.parquet
  PRReviewComments.parquet
  Pushes.parquet
```

## `db/*.parquet`: the 8 tables

All activity of a fixed group of 9,000 users (the cohort) on any public GitHub repository,
from 2025-12-01 00:00 UTC up to this release. Users and repositories that the cohort's
activity refers to (for example the author of a PR a cohort user reviewed) are included as
well, so `Users` has more rows than the cohort. `Users.is_cohort` marks the cohort: only
their own activity is collected, so for any other user the tables hold only what cohort
users' events reveal about them.

| Table | One row is | Time column |
|---|---|---|
| `Users` | a GitHub user or bot | `first_seen_at` |
| `Repositories` | a repository | `first_seen_at` |
| `PullRequests` | a pull request | `first_seen_at` |
| `Issues` | an issue (PR conversations too, with `is_pull_request = true`) | `first_seen_at` |
| `IssueComments` | a comment in an issue or PR conversation | `created_at` |
| `PRReviews` | a submitted PR review (approve / comment / request changes) | `first_seen_at` |
| `PRReviewComments` | a comment on specific lines of a PR diff | `created_at` |
| `Pushes` | a push of commits to a branch or tag | `created_at` |

- **Keys.** Every table is sorted by its time column. The primary key (`user_id`,
  `repo_id`, `pr_id`, ...) is the row number 0, 1, 2, ... A foreign key holds the row number
  of the row it points to; for example `PullRequests.author_id = 5` means row 5 of `Users`.
  Row numbers can change between releases; the `github_<key>` column of each table
  (`github_user_id`, `github_repo_id`, ...) is the original GitHub id and never changes.
- **Times** are UTC, stored without a time zone (`datetime64[ns]`).
- **Row time of PRs, issues and reviews** is `first_seen_at`, when the row appears in the
  data, not `created_at` / `submitted_at`. An old issue enters the data only when someone
  acts on it, possibly long after it was opened; using `created_at` would let a model at
  time t see issues that only appear because of activity after t. A PR whose author or
  opening time is known only from its conversation issue appears when that issue does.
- **Issue attributes that can change** (`title`, `labels`, `assignee_id`, `milestone_title`,
  `issue_type`, `locked`) are taken from the first event about the issue, so they do not
  reveal changes made later.
- **Text columns** (`body`, `diff_hunk`, ...) are truncated.
- **Some columns become known only later**: `PullRequests.merged_at`, `PullRequests.merged_by_id`,
  `PullRequests.closed_at`, `Issues.closed_at`, `Issues.state_reason`, `PRReviews.dismissed_at`.
  They are filled in only after the row was created, so using them for a prediction at time t
  leaks the future: use their values only if they are earlier than t.

`db/SCHEMA.md` describes every column: type, whether it is a primary key, foreign key or
time column, which field of the GitHub event JSON it comes from, and what it means.

## Loading

```python
import pandas as pd
users = pd.read_parquet("assignment2/data/db/Users.parquet")
```

Every table is read the same way, e.g. `pd.read_parquet("assignment2/data/db/Pushes.parquet")`.
Join tables on their keys, for example `Pushes.user_id` = `Users.user_id`.

## Notes

1. **Use only data before t.** For a sample at time t, filter every table by its **time
   column** (the table above) before using it: `first_seen_at` for Users, Repositories,
   PullRequests, Issues and PRReviews, `created_at` for IssueComments, PRReviewComments and
   Pushes. For PRs, issues and reviews do **not** filter by `created_at` / `submitted_at`:
   those rows can appear in the data long after they were created.
2. Some columns become known only later; use their values only if they are earlier than t:
   PullRequests.merged_at, PullRequests.merged_by_id, PullRequests.closed_at, Issues.closed_at,
   Issues.state_reason, PRReviews.dismissed_at.
3. **Match users by `github_user_id`, not `user_id`.** Row numbers can change with every
   update. `UserID` in the test input and in your output is `github_user_id`.
4. **Only the 9,000 cohort users (`Users.is_cohort`) have complete activity.** Other users
   appear only through the cohort's events.
5. **There are no training, validation or test files.** Build your own samples from the
   tables and split them by time (train on older weeks, validate on newer ones). The answers
   of the official test are not in any file.
6. **Past data can change slightly** between releases: a PR or issue opened in a past week
   can enter the data later, when someone acts on it.
7. **Times are UTC** without a time zone (`datetime64[ns]`); 21:00 Taiwan = 13:00 UTC.
