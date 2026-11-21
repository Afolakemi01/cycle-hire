# cycle-hire

A Python pipeline that validates a cycle-hire export and produces a per-station summary of hire counts and average ride length, to support decisions on where to add bikes.

## What it does

1. Reads `data/hires.csv`
2. Cleans and validates each row against seven data-quality rules
3. Writes accepted hires into a per-station summary
4. Writes every rejected row, with its reason, for correction at source
5. Logs a warning for each rejected row and a final count of rows read, accepted and rejected

## Data-quality rules

Fields are stripped of surrounding spaces, then checked in this order. A row is rejected on the first rule it fails.

| Rule | Reason |
|---|---|
| `hire_id` is not blank | `missing hire_id` |
| `hire_id` has not already been accepted | `duplicate hire_id` |
| `station` is not blank | `missing station` |
| `hire_date` is a valid `YYYY-MM-DD` date | `bad hire_date` |
| `duration_minutes` is a whole number | `duration not a whole number` |
| Duration is between 1 and 1440 minutes | `duration out of range` |
| `rider_type` is `member` or `casual` | `bad rider_type` |

## Outputs

`output/station_summary.csv`

| station | hires | total_minutes | average_minutes |
|---|---|---|---|
| Deansgate | 3 | 94 | 31.3 |
| Oxford Road | 3 | 98 | 32.7 |
| Piccadilly Gardens | 2 | 45 | 22.5 |
| Salford Quays | 2 | 1465 | 732.5 |

`output/rejected_hires.csv`: the original columns plus `reason` (12 of 22 rows in the sample data).

## Finding

The Salford Quays average is skewed by a single 24-hour hire (H1017), which is likely an undocked bike. Excluding it, the average is 25.0 minutes. The hire passes the current rules, so it is reported rather than removed. Whether 24-hour hires should count is a business decision.

## Project structure

```
cycle-hire/
├── cycle_hire/      # pipeline and validation code
├── data/            # input CSV
├── output/          # generated files
├── tests/           # pytest tests
└── pyproject.toml
```

## Setup and run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m cycle_hire.pipeline
```

## Tests and linting

```bash
pytest
ruff check .
```

## Possible improvements

- Flag unusually long hires automatically in the summary
- Read input and output paths from configuration instead of hard-coding them
