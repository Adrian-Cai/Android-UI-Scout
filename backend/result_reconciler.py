from __future__ import annotations

from collections.abc import Iterable
from typing import Literal, TypedDict

ResultStatus = Literal["passed", "failed", "error"]


class ResultRow(TypedDict, total=False):
    status: str | None


def reconcile_zero_summary_results(rows: Iterable[ResultRow]) -> list[ResultStatus]:
    """Reconcile result rows when an execution reports a zero-count summary.

    Some executions can have failed rows while unfinished rows are still stored as
    ``error`` or ``NULL`` placeholders.  Counting only finished rows makes that
    mixed state look like every finished row failed, which previously allowed the
    zero-summary success path to promote all rows to ``passed``.  Only promote
    failed rows when failures account for the whole result set or when there are
    no error/NULL placeholders left to clean up.
    """

    statuses = [row.get("status") for row in rows]
    db_total = len(statuses)
    db_failed = sum(status == "failed" for status in statuses)
    db_error = sum(status in ("error", None) for status in statuses)

    all_rows_failed = db_total > 0 and db_total == db_failed
    no_error_placeholders = db_error == 0
    should_promote_failures = db_failed > 0 and (all_rows_failed or no_error_placeholders)

    reconciled: list[ResultStatus] = []
    for status in statuses:
        if status == "passed":
            reconciled.append("passed")
        elif status == "failed":
            reconciled.append("passed" if should_promote_failures else "failed")
        elif status in ("error", None):
            reconciled.append("failed" if db_failed > 0 and not should_promote_failures else "passed")
        else:
            reconciled.append("error")
    return reconciled
