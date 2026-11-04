
import json
import csv
from pathlib import Path


def process_pull_requests():
    # read raw data
    input_path = Path("data/raw/pull_requests.json")

    with input_path.open("r", encoding="utf-8") as file:
        pull_requests = json.load(file)

    #fliter - MERGED PR
    merged_prs = [
        pr for pr in pull_requests
        if pr.get("merged_at") is not None
    ]

    processed_prs = []
    for pr in merged_prs:
        pr_number = pr["number"]
        review_path = Path(f"data/raw/reviews/{pr_number}.json")

        # read saved review data for this PR
        if review_path.exists():
            with review_path.open("r", encoding="utf-8") as file:
                reviews = json.load(file)

            cr_passed = check_code_review(reviews, pr["merged_at"])
        else:
            #missing review data cannot be treated as False
            cr_passed = None

        # Read saved status checks
        check_path = Path(f"data/raw/checks/{pr_number}.json")

        if check_path.exists():
            with check_path.open("r", encoding="utf-8") as file:
                checks = json.load(file)
        else:
            checks = []

        # Required checks at merge are not yet verified
        checks_passed = None

        processed_prs.append({
            "PR_NUMBER": pr_number,
            "PR_TITLE": pr["title"],
            "AUTHOR": pr["user"]["login"] if pr.get("user") else None,
            "MERGE_DATE": pr["merged_at"],
            "CR_Passed": cr_passed,
            "CHECKS_PASSED": checks_passed
        })

    #save processed data
    output_path = Path("data/processed/merged_prs.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(processed_prs, file, indent=2)

    print(f"Closed PRs retrieved: {len(pull_requests)}")
    print(f"Merged PRs found: {len(merged_prs)}")
    print(f"Saved to: {output_path}")

    return processed_prs


#check if at least 1 reviewer approved before merge
def check_code_review(reviews, merge_date):
    for review in reviews:
        if review.get("state") != "APPROVED":
            continue

        submitted_at = review.get("submitted_at")

        if submitted_at and submitted_at <= merge_date:
            return True

    return False


#inspect saved status checks
def inspect_pr_checks(pr_number):
    check_path = Path(f"data/raw/checks/{pr_number}.json")

    if not check_path.exists():
        return None

    with check_path.open("r", encoding="utf-8") as file:
        checks = json.load(file)

    results = {}

    for check in checks:
        conclusion = check.get("conclusion") or "pending"
        results[conclusion] = results.get(conclusion, 0) + 1

    return results



#check whether required commit checks completed successfully
def check_status_checks(checks, merge_date):
    if not checks:
        return None

    required_checks = [
        check for check in checks
        if check.get("name", "").endswith("/required")
    ]

    if not required_checks:
        return None

    for check in required_checks:
        completed_at = check.get("completed_at")
        conclusion = check.get("conclusion")

        if completed_at is None or completed_at > merge_date:
            return False

        if conclusion not in ("success", "neutral", "skipped"):
            return False

    return True



#export processed PR data to CSV
def export_csv(processed_prs):
    output_path = Path("output/github_pr_report.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    columns = [
        "PR_NUMBER",
        "PR_TITLE",
        "AUTHOR",
        "MERGE_DATE",
        "CR_Passed",
        "CHECKS_PASSED"
    ]

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(processed_prs)

    print(f"CSV saved to: {output_path}")


#test code review validation with raw data
if __name__ == "__main__":
    processed_prs = process_pull_requests()

    # Count review results for all merged PRs
    approved = sum(pr["CR_Passed"] is True for pr in processed_prs)
    not_approved = sum(pr["CR_Passed"] is False for pr in processed_prs)
    missing = sum(pr["CR_Passed"] is None for pr in processed_prs)

    print(f"CR_Passed True: {approved}")
    print(f"CR_Passed False: {not_approved}")
    print(f"Missing review data: {missing}")
    print("\nCheck results for PR #190312:")
    print(inspect_pr_checks(190312))

    # Read saved status checks
    # Required checks at merge are not yet verified
    export_csv(processed_prs)
