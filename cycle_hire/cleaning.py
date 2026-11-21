import csv
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s, %(levelname)s, %(message)s"
)

logger = logging.getLogger(__name__)


def strip_and_check_hire_id(record):
    cleaned = {key: value.strip() for key, value in record.items()}

    if cleaned["hire_id"] == "":
        return (record, "missing hire_id")

    return (cleaned, None)


def check_duplicates(record, seen):
    if record["hire_id"] in seen:
        return (record, "duplicate hire_id")

    return (record, None)


def check_station(record):
    if record["station"] == "":
        return (record, "missing station")

    return (record, None)


def check_date_and_duration(record):
    try:
        hire_date = datetime.strptime(record["hire_date"], "%Y-%m-%d").date()
    except ValueError:
        return (record, "bad hire_date")

    try:
        duration_minutes = int(record["duration_minutes"])
    except ValueError:
        return (record, "duration not a whole number")

    if duration_minutes < 1 or duration_minutes > 1440:
        return (record, "duration out of range")

    cleaned = {
        "hire_id": record["hire_id"],
        "hire_date": hire_date,
        "station": record["station"].title(),
        "duration_minutes": duration_minutes,
        "rider_type": record["rider_type"],
    }

    return (cleaned, None)


def check_rider_type(record):
    riders = ["member", "casual"]

    rider_type = record["rider_type"].lower()
    if rider_type not in riders:
        return (record, "bad rider_type")

    record["rider_type"] = rider_type
    return (record, None)


def validate_row(row, seen):
    record, reason = strip_and_check_hire_id(row)
    if reason is not None:
        return (row, reason)

    record, reason = check_duplicates(record, seen)
    if reason is not None:
        return (record, reason)

    record, reason = check_station(record)
    if reason is not None:
        return (record, reason)

    record, reason = check_date_and_duration(record)
    if reason is not None:
        return (record, reason)

    record, reason = check_rider_type(record)
    if reason is not None:
        return (record, reason)

    seen.add(record["hire_id"])
    return (record, None)


def station_summary(valid_rows):
    summary = {}

    for row in valid_rows:
        station = row["station"]
        duration = row["duration_minutes"]

        if station not in summary:
            summary[station] = {"hires": 0, "total_minutes": 0}

        summary[station]["hires"] += 1
        summary[station]["total_minutes"] += duration

    for station, values in summary.items():
        average = values["total_minutes"] / values["hires"]
        values["average_minutes"] = round(average, 1)

    return summary


def read_files(path, seen):
    rows_in = 0
    rows_rejected = 0
    cleaned_rows = 0

    rejects = []
    cleaned = []

    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows_in += 1
            record, reason = validate_row(row, seen)

            if reason is not None:
                rejected_row = {**row, "reason": reason}
                rejects.append(rejected_row)
                rows_rejected += 1
                logger.warning("Rejected hire_id %s: %s", row["hire_id"], reason)

            else:
                cleaned.append(record)
                cleaned_rows += 1

    assert rows_in == rows_rejected + cleaned_rows, (
        f"assertion failed: rows do not match: rows_in:{rows_in}, rejected_rows:{rows_rejected}, cleaned_rows{cleaned_rows}"
    )
    return cleaned, rejects, rows_in, rows_rejected, cleaned_rows


def write_summary(summary, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["station", "hires", "total_minutes", "average_minutes"]
        summary_writter = csv.DictWriter(f, fieldnames=fieldnames)
        summary_writter.writeheader()

        for station in sorted(summary):
            values = summary[station]
            summary_writter.writerow({"station": station, **values})

    return len(summary)


def write_rejects(rejects, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "hire_id",
            "hire_date",
            "station",
            "duration_minutes",
            "rider_type",
            "reason",
        ]
        reject_writter = csv.DictWriter(f, fieldnames=fieldnames)
        reject_writter.writeheader()
        reject_writter.writerows(rejects)
    return len(rejects)


def main():
    logger.info("run started")
    seen = set()

    cleaned, rejects, rows_in, rows_rejected, cleaned_rows = read_files(
        "data/hires.csv", seen
    )
    logger.info("extracting summary")
    summary = station_summary(cleaned)

    number_of_hires = write_summary(summary, "output/station_summary.csv")
    logger.info("wrote %s rows to output/station_summary.csv", number_of_hires)

    number_of_rejects = write_rejects(rejects, "output/rejected_hires.csv")
    logger.info("wrote %s rows to output/rejected_hires.csv", number_of_rejects)

    logger.info(
        "read %s rows, accepted %s rows, rejected %s rows",
        rows_in,
        cleaned_rows,
        rows_rejected,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("run failed")
        raise
