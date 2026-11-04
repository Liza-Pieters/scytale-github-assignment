
from transform import check_code_review, check_status_checks


def test_approved_review_before_merge():
    reviews = [
        {
            "state": "APPROVED",
            "submitted_at": "2026-10-01T10:00:00Z"
        }
    ]

    assert check_code_review(
        reviews, "2026-10-02T10:00:00Z"
    ) is True


def test_review_after_merge():
    reviews = [
        {
            "state": "APPROVED",
            "submitted_at": "2026-10-03T10:00:00Z"
        }
    ]

    assert check_code_review(
        reviews, "2026-10-02T10:00:00Z"
    ) is False


def test_required_check_success():
    checks = [
        {
            "name": "codecov/patch/required",
            "conclusion": "success",
            "completed_at": "2026-10-01T10:00:00Z"
        }
    ]

    assert check_status_checks(
        checks, "2026-10-02T10:00:00Z"
    ) is True


def test_required_check_failure():
    checks = [
        {
            "name": "codecov/patch/required",
            "conclusion": "failure",
            "completed_at": "2026-10-01T10:00:00Z"
        }
    ]

    assert check_status_checks(
        checks, "2026-10-02T10:00:00Z"
    ) is False


def test_no_identifiable_required_checks():
    checks = [
        {
            "name": "optional-check",
            "conclusion": "success",
            "completed_at": "2026-10-01T10:00:00Z"
        }
    ]

    assert check_status_checks(
        checks, "2026-10-02T10:00:00Z"
    ) is None
