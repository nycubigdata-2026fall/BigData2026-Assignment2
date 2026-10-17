import argparse
import os
import sys

import pandas as pd

USER_COL = "UserID"
EVENT_COLS = ["open_pr", "open_issue", "issue_comment", "pr_review", "pr_review_comment", "push"]
OUTPUT_COLUMNS = [USER_COL] + EVENT_COLS


class FormatError(Exception):
    pass


def read_predictions(path, expected_users=None):
    try:
        df = pd.read_csv(path, dtype=str)
    except Exception as e:
        raise FormatError(f"cannot read {path} as CSV: {e}")
    if list(df.columns) != OUTPUT_COLUMNS:
        raise FormatError(f"header must be exactly {','.join(OUTPUT_COLUMNS)}; got {','.join(df.columns)}")
    if not len(df):
        raise FormatError("no prediction rows")
    if df.isna().any().any():
        raise FormatError("empty cells are not allowed")
    for col in df.columns:
        if not df[col].str.fullmatch(r"\d+").all():
            raise FormatError(f"column {col} must contain only non-negative integers")
    df = df.astype("int64")
    bad = ~df[EVENT_COLS].isin([0, 1])
    if bad.any().any():
        raise FormatError(f"prediction columns must be 0 or 1 (found other values in "
                          f"{', '.join(c for c in EVENT_COLS if bad[c].any())})")
    if df[USER_COL].duplicated().any():
        raise FormatError(f"duplicate UserIDs: {df[USER_COL][df[USER_COL].duplicated()].head().tolist()}")
    if expected_users is not None:
        got, want = set(df[USER_COL]), set(expected_users)
        if got != want:
            raise FormatError(f"UserIDs differ from the requested list: {len(want - got)} missing, "
                              f"{len(got - want)} unexpected")
    return df


def _counts(pred, truth):
    p = pred.set_index(USER_COL).loc[truth[USER_COL], EVENT_COLS].to_numpy()
    t = truth[EVENT_COLS].to_numpy()
    return ((p == 1) & (t == 1)).sum(0), ((p == 1) & (t == 0)).sum(0), ((p == 0) & (t == 1)).sum(0)


def _f1(tp, fp, fn):
    return 2 * tp / (2 * tp + fp + fn) if tp + fp + fn else 1.0


def f1_per_event(pred, truth):
    return [float(_f1(*c)) for c in zip(*_counts(pred, truth))]


def scores(pred, truth):
    tp, fp, fn = _counts(pred, truth)
    macro = sum(_f1(*c) for c in zip(tp, fp, fn)) / len(EVENT_COLS)
    micro = _f1(tp.sum(), fp.sum(), fn.sum())
    return {"macro_f1": float(macro), "micro_f1": float(micro), "score": float((macro + micro) / 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", required=True, help="your output CSV")
    ap.add_argument("--input", help="test input CSV (one UserID column): check the UserIDs match")
    ap.add_argument("--truth", help="answer CSV, same format as the output: check the UserIDs and score")
    args = ap.parse_args()
    expected = None
    if args.truth:
        truth = pd.read_csv(args.truth)
        expected = truth[USER_COL].tolist()
    elif args.input:
        expected = pd.read_csv(args.input)[USER_COL].tolist()
    try:
        pred = read_predictions(args.pred, expected)
    except FormatError as e:
        print(f"Format check: ERROR - {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Format check: no errors ({len(pred)} users)")
    if args.truth:
        s = scores(pred, truth)
        print(f"macro-F1: {100 * s['macro_f1']:.2f}%")
        print(f"micro-F1: {100 * s['micro_f1']:.2f}%")
        print(f"Score:    {100 * s['score']:.2f}%")
        if "sample_truth" in os.path.basename(args.truth):
            print("Note: these scores are computed with the example answers in sample_truth.csv "
                  "(week of 9/27); they are not your final score on the official test.")


if __name__ == "__main__":
    main()
