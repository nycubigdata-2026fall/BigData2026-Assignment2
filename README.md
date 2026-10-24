# BigData2026-Assignment2

Predict which of 6 GitHub activities each test user will perform during
**2026/11/12 00:00 – 11/19 00:00 (Taiwan time)**.

| Folder | What is in it |
|---|---|
| [`data/`](data/) | The data: GH Archive activity of a fixed group of 9,000 users as 8 relational tables (one Parquet file each). See [data/README.md](data/README.md). |
| [`evaluation/`](evaluation/) | The task, the output format, `evaluate.py`, the examples and, from 10/28, `test_input.csv`. See [evaluation/README.md](evaluation/README.md). |

## Download

```bash
git clone --depth 1 https://github.com/nycubigdata-2026fall/BigData2026-Assignment2.git assignment2
```

This creates the folder `assignment2/` inside the folder you run it from.

- The repository is **updated every day at 21:00 Taiwan time**; the last update is on
  11/11 at 21:00 (data up to 11/11 20:00).
- Every update **replaces** the previous version (force push): the repository always has
  exactly one commit, and **old versions are not kept**.

## Updating to the latest version

**Delete the old `assignment2` folder, then run the same `git clone` command again.**
Running it while the folder still exists fails with
`destination path 'assignment2' already exists`. Do not use `git pull`: the previous commit is
replaced every day, so `git pull` fails or asks you to merge.

| Risk | What to do |
|---|---|
| Updating deletes the whole folder | Keep your own files (code, notebooks, models, output.csv) **outside** `assignment2/`, and do not edit the files in it |
| Old versions are not kept | Copy `assignment2/data/` somewhere else before updating if you need that day's data |
| Row ids change | Keys such as `user_id` are row numbers and can be renumbered by any update; match users by `github_user_id` |
