# Schema

Source paths refer to the GitHub Events JSON (https://docs.github.com/en/rest/using-the-rest-api/github-event-types). All times are UTC.

**Keys:** every PK is the row index 0..n-1 (rows sorted by the row-time column) and every FK holds the row index of the referenced row. Row indices can change between daily releases; the original GitHub id of each row is in `github_<pk>` and never changes.

**Known only later:** `PullRequests.merged_at`, `PullRequests.merged_by_id`, `PullRequests.closed_at`, `Issues.closed_at`, `Issues.state_reason`, `PRReviews.dismissed_at`. These are filled in only after the row was created (marked "known only later" below); use their values only if they are earlier than t.

## Users (45,733 rows)

| column | type | key | source | description |
|---|---|---|---|---|
| `user_id` | int | PK | `derived (row number)` | Row index 0..n-1 in time order; FKs pointing here hold this index |
| `github_user_id` | int | GitHub id | `actor.id / payload.*.user.id` | Original GitHub id of the user; stable across releases |
| `login` | str |  | `actor.login / payload.*.user.login` | Username (latest seen; users can rename) |
| `is_bot` | bool |  | `derived` | login ends with [bot] |
| `is_cohort` | bool |  | `derived` | One of the fixed cohort users whose own activity is collected. Other users only appear because a cohort user's activity references them (e.g. the author of a PR a cohort user reviewed), so their activity is incomplete; task samples and the test list contain cohort users only |
| `first_seen_at` | time | row time | `derived` | Earliest event in the dataset that references this user |

## Repositories (109,376 rows)

| column | type | key | source | description |
|---|---|---|---|---|
| `repo_id` | int | PK | `derived (row number)` | Row index 0..n-1 in time order; FKs pointing here hold this index |
| `github_repo_id` | int | GitHub id | `repo.id` | Original GitHub id of the repository; stable across releases |
| `name` | str |  | `repo.name` | owner/repo |
| `owner_login` | str |  | `derived from repo.name` | Owner part of owner/repo |
| `org_id` | int |  | `org.id` | GitHub organization id; null for user-owned repos (not a row index) |
| `org_login` | str |  | `org.login` | Organization login |
| `first_seen_at` | time | row time | `derived` | Earliest event in the dataset on this repo |

## PullRequests (302,815 rows)

| column | type | key | source | description |
|---|---|---|---|---|
| `pr_id` | int | PK | `derived (row number)` | Row index 0..n-1 in time order; FKs pointing here hold this index |
| `github_pr_id` | int | GitHub id | `payload.pull_request.id` | Original GitHub id of the pull request; stable across releases |
| `repo_id` | int | FK → Repositories | `repo.id` | Target repository |
| `number` | int |  | `payload.pull_request.number` | PR number within the repo (#123) |
| `author_id` | int | FK → Users | `actor.id (action=opened) / payload.issue.user.id` | PR author; null if the PR was opened before the data window and nobody commented on it |
| `title` | str |  | `payload.issue.title (PR's issue object)` | PR title; only known if the PR has an IssueCommentEvent |
| `draft` | bool |  | `payload.issue.draft` | Draft PR (same availability as title) |
| `head_ref` | str |  | `payload.pull_request.head.ref` | Source branch |
| `base_ref` | str |  | `payload.pull_request.base.ref` | Target branch |
| `head_sha` | str |  | `payload.pull_request.head.sha` | Head commit when first seen |
| `base_sha` | str |  | `payload.pull_request.base.sha` | Base commit when first seen |
| `head_repo_id` | int |  | `payload.pull_request.head.repo.id` | GitHub id of the repo the branch lives in (a fork for external PRs); not an FK, not a row index |
| `is_cross_repo` | bool |  | `derived` | head_repo_id != repo_id, i.e. PR from a fork |
| `created_at` | time |  | `created_at (action=opened) / payload.issue.created_at` | When the PR was opened (may be before first_seen_at); null when the opening was never seen, e.g. a PR opened before the data window |
| `merged_at` | time | known only later | `created_at (action=merged)` | When it was merged |
| `merged_by_id` | int | FK → Users (row index), known only later | `actor.id (action=merged)` | Who merged it |
| `closed_at` | time | known only later | `created_at (action=closed or merged)` | When it was closed |
| `first_seen_at` | time | row time | `derived` | When the PR row appears in the data, so it is the row time: its earliest pull-request or review event; if author, title or opening time come from the PR conversation issue seen later, the time that issue was first seen. Comments on the PR conversation update the issue row (Issues.first_seen_at), not this |

## Issues (172,972 rows)

| column | type | key | source | description |
|---|---|---|---|---|
| `issue_id` | int | PK | `derived (row number)` | Row index 0..n-1 in time order; FKs pointing here hold this index |
| `github_issue_id` | int | GitHub id | `payload.issue.id` | Original GitHub id of the issue (on GitHub every PR is also an issue; those rows have is_pull_request=true); stable across releases |
| `repo_id` | int | FK → Repositories | `repo.id` | Repository |
| `number` | int |  | `payload.issue.number` | Issue number within the repo |
| `author_id` | int | FK → Users | `payload.issue.user.id` | Issue author |
| `is_pull_request` | bool |  | `payload.issue.pull_request` | This issue is the conversation of a PR |
| `pull_request_id` | int | FK → PullRequests | `derived (repo_id, number)` | The matching PR when is_pull_request and the PR is in PullRequests |
| `title` | str |  | `payload.issue.title` | Title, from the first event about the issue |
| `body` | str |  | `payload.issue.body` | Body text, truncated, from the first event about the issue |
| `labels` | str |  | `payload.issue.labels[].name` | Label names joined by |, from the first event about the issue (labels added later are not included) |
| `num_labels` | int |  | `derived` | Number of labels, from the first event about the issue |
| `assignee_id` | int | FK → Users | `payload.issue.assignee.id` | Assignee, from the first event about the issue (null if not set then, even when set later) |
| `milestone_title` | str |  | `payload.issue.milestone.title` | Milestone, from the first event about the issue (null if not set then, even when set later) |
| `issue_type` | str |  | `payload.issue.type.name` | Issue type (Bug / Feature / Task ...) if the org uses them, from the first event about the issue (null if not set then, even when set later) |
| `locked` | bool |  | `payload.issue.locked` | Conversation locked, from the first event about the issue (null if not set then, even when set later) |
| `created_via_app` | str |  | `payload.issue.performed_via_github_app.slug` | GitHub App that created it, if any |
| `created_at` | time |  | `payload.issue.created_at` | When the issue was opened (may be long before first_seen_at, even before the data window) |
| `closed_at` | time | known only later | `payload.issue.closed_at (latest seen)` | When it was closed; null if open at the end of the data |
| `state_reason` | str | known only later | `payload.issue.state_reason (latest seen)` | completed / not_planned / reopened / duplicate |
| `first_seen_at` | time | row time | `derived` | Earliest event in the dataset about this issue: the row exists in the data from this time on, so it is the row time |

## IssueComments (106,457 rows)

| column | type | key | source | description |
|---|---|---|---|---|
| `comment_id` | int | PK | `derived (row number)` | Row index 0..n-1 in time order; FKs pointing here hold this index |
| `github_comment_id` | int | GitHub id | `payload.comment.id` | Original GitHub id of the comment; stable across releases |
| `issue_id` | int | FK → Issues | `payload.issue.id` | Issue (or PR conversation) commented on |
| `repo_id` | int | FK → Repositories | `repo.id` | Repository |
| `author_id` | int | FK → Users | `payload.comment.user.id` | Commenter |
| `is_pull_request` | bool |  | `payload.issue.pull_request` | Comment is on a PR conversation |
| `body` | str |  | `payload.comment.body` | Comment text, truncated |
| `via_app` | str |  | `payload.comment.performed_via_github_app.slug` | GitHub App that posted it, if any |
| `created_at` | time | row time | `payload.comment.created_at` | When it was posted |
| `event_id` | str |  | `id` | GH Archive event id (provenance) |

## PRReviews (91,039 rows)

| column | type | key | source | description |
|---|---|---|---|---|
| `review_id` | int | PK | `derived (row number)` | Row index 0..n-1 in time order; FKs pointing here hold this index |
| `github_review_id` | int | GitHub id | `payload.review.id` | Original GitHub id of the review; stable across releases |
| `pr_id` | int | FK → PullRequests | `payload.pull_request.id` | Reviewed PR |
| `repo_id` | int | FK → Repositories | `repo.id` | Repository |
| `reviewer_id` | int | FK → Users | `payload.review.user.id` | Reviewer |
| `state` | str |  | `payload.review.state` | approved / commented / changes_requested (as submitted) |
| `body` | str |  | `payload.review.body` | Review summary text, truncated |
| `commit_id` | str |  | `payload.review.commit_id` | Commit the review was made on |
| `submitted_at` | time |  | `payload.review.submitted_at` | When the review was submitted (can be long before first_seen_at, even before the data window) |
| `dismissed_at` | time | known only later | `created_at (action=dismissed)` | When the review was dismissed |
| `first_seen_at` | time | row time | `derived` | Earliest event in the dataset about this review: the row exists in the data from this time on, so it is the row time |
| `event_id` | str |  | `id` | GH Archive event id (provenance) |

## PRReviewComments (66,670 rows)

| column | type | key | source | description |
|---|---|---|---|---|
| `comment_id` | int | PK | `derived (row number)` | Row index 0..n-1 in time order; FKs pointing here hold this index |
| `github_comment_id` | int | GitHub id | `payload.comment.id` | Original GitHub id of the review comment; stable across releases |
| `pr_id` | int | FK → PullRequests | `payload.pull_request.id` | PR the comment is on |
| `repo_id` | int | FK → Repositories | `repo.id` | Repository |
| `author_id` | int | FK → Users | `payload.comment.user.id` | Commenter |
| `pull_request_review_id` | int | FK → PRReviews | `payload.comment.pull_request_review_id` | Review this comment belongs to (null if not in PRReviews) |
| `in_reply_to_id` | int | FK → PRReviewComments | `payload.comment.in_reply_to_id` | Parent review comment in a thread (null if none / not in table) |
| `path` | str |  | `payload.comment.path` | File the comment is on |
| `file_extension` | str |  | `derived from path` | e.g. py, ts, md |
| `subject_type` | str |  | `payload.comment.subject_type` | line / file |
| `position` | int |  | `payload.comment.position` | Line index in the diff (null if outdated) |
| `original_position` | int |  | `payload.comment.original_position` | Line index in the original diff |
| `commit_id` | str |  | `payload.comment.commit_id` | Commit the comment refers to |
| `diff_hunk` | str |  | `payload.comment.diff_hunk` | Diff context, truncated |
| `body` | str |  | `payload.comment.body` | Comment text, truncated |
| `created_at` | time | row time | `payload.comment.created_at` | When it was posted |
| `event_id` | str |  | `id` | GH Archive event id (provenance) |

## Pushes (1,664,952 rows)

| column | type | key | source | description |
|---|---|---|---|---|
| `push_id` | int | PK | `derived (row number)` | Row index 0..n-1 in time order; FKs pointing here hold this index |
| `github_push_id` | int | GitHub id | `payload.push_id` | Original GitHub id of the push; stable across releases |
| `user_id` | int | FK → Users | `actor.id` | Pusher |
| `repo_id` | int | FK → Repositories | `payload.repository_id` | Repository |
| `ref` | str |  | `payload.ref` | Full ref, e.g. refs/heads/main |
| `ref_type` | str |  | `derived from ref` | branch / tag |
| `branch` | str |  | `derived from ref` | Ref name without refs/heads/ or refs/tags/ |
| `is_new_ref` | bool |  | `derived from payload.before` | payload.before is all zeros, i.e. the push created the branch/tag |
| `created_at` | time | row time | `created_at` | When the push happened |
| `event_id` | str |  | `id` | GH Archive event id (provenance) |
