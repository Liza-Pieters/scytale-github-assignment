
from pathlib import Path
from transform import process_pull_requests, export_csv


def main():
    raw_data = Path("data/raw/pull_requests.json")

    if not raw_data.exists():
        raise FileNotFoundError(
            "Raw PR data is missing. Run extract.py first."
        )

    print("Processing saved GitHub pull requests...")

    processed_prs = process_pull_requests()
    export_csv(processed_prs)

    print(f"Completed: {len(processed_prs)} merged PRs processed.")


if __name__ == "__main__":
    main()
