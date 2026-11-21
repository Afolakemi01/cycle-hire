from cycle_hire.cleaning import check_date_and_duration, validate_row


def test_validate_row_passes_a_good_row():
    seen = set()
    record = {
        "hire_id": "H1001",
        "hire_date": "2026-11-02",
        "station": "Piccadilly Gardens",
        "duration_minutes": "18",
        "rider_type": "casual",
    }

    record, reason = validate_row(record, seen)
    assert reason is None


def test_negative_duration_is_rejected():
    record = {
        "hire_id": "H1001",
        "hire_date": "2026-11-02",
        "station": "Piccadilly Gardens",
        "duration_minutes": "-5",
        "rider_type": "casual",
    }

    record, reason = check_date_and_duration(record)
    assert reason == "duration out of range"


def test_bad_date_is_rejected():
    record = {
        "hire_id": "H1001",
        "hire_date": "2026-13-32",
        "station": "Piccadilly Gardens",
        "duration_minutes": "18",
        "rider_type": "casual",
    }
    record, reason = check_date_and_duration(record)
    assert reason == "bad hire_date"
