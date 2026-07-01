from backend.result_reconciler import reconcile_zero_summary_results


def test_keeps_mixed_failed_and_placeholders_from_passing():
    rows = [{"status": "failed"}, {"status": "error"}, {"status": None}]

    assert reconcile_zero_summary_results(rows) == ["failed", "failed", "failed"]


def test_promotes_when_failed_rows_account_for_whole_result_set():
    rows = [{"status": "failed"}, {"status": "failed"}]

    assert reconcile_zero_summary_results(rows) == ["passed", "passed"]


def test_promotes_when_no_error_placeholders_remain():
    rows = [{"status": "failed"}, {"status": "passed"}]

    assert reconcile_zero_summary_results(rows) == ["passed", "passed"]
