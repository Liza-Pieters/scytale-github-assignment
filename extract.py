
#extract - python program communicate with gitHub se API & store data as JSON file
import os
import json
from pathlib import Path

import requests
from dotenv import load_dotenv


def fetch_pull_requests(max_pages=3):
    # load the variables & read token
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        raise ValueError("GITHUB_TOKEN is missing from .env")

    # api endpoint - API request
    url = "https://api.github.com/repos/home-assistant/core/pulls"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    params = {
        "state": "closed",
        "per_page": 100,
        "page": 1
    }

    pull_requests = []
    page_count = 0

    while url and page_count < max_pages:
        #send HTTP-request
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        # JSON --> Python-data
        page_data = response.json()
        pull_requests.extend(page_data)

        page_count += 1
        print(f"Page {page_count}: Retrieved {len(page_data)} PRs")

        # Get the next page URL from GitHub
        url = response.links.get("next", {}).get("url")
        params = None

    return pull_requests


# function to save raw data
def save_raw_data(pull_requests):
    output_path = Path("data/raw/pull_requests.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(pull_requests, file, indent=2)

    print(f"Successfully extracted {len(pull_requests)} pull requests.")
    print(f"Saved to: {output_path}")


# function to fetch PR
def fetch_pr_reviews(pr_number):
    # API endpoint for reviews of a specific PR
    url = (
        f"https://api.github.com/repos/"
        f"home-assistant/core/pulls/{pr_number}/reviews"
    )

    # load the variables & read token
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        raise ValueError("GITHUB_TOKEN is missing from .env")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    reviews = []

    while url:
        #send HTTP-request
        response = requests.get(
            url,
            headers=headers,
            params={"per_page": 100},
            timeout=30
        )

        response.raise_for_status()

        # JSON --> Python-data
        page_reviews = response.json()
        reviews.extend(page_reviews)

        # Get the next page URL from GitHub
        url = response.links.get("next", {}).get("url")

    return reviews


#store review data for specific PR - creates seperate JSON file for each PR
def save_pr_reviews(pr_number, reviews):
    output_path = Path(f"data/raw/reviews/{pr_number}.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(reviews, file, indent=2)

    print(f"Saved reviews for PR #{pr_number}")


#fetch and save reviews for all merged PRs
def fetch_all_pr_reviews(pull_requests):
    merged_prs = [
        pr for pr in pull_requests
        if pr.get("merged_at") is not None
    ]

    print(f"Fetching reviews for {len(merged_prs)} merged PRs...")

    failed_prs = []

    for index, pr in enumerate(merged_prs, start=1):
        pr_number = pr["number"]
        review_path = Path(f"data/raw/reviews/{pr_number}.json")

        # Skip PRs already extracted
        if review_path.exists():
            print(f"[{index}/{len(merged_prs)}] PR #{pr_number}: Already saved")
            continue

        try:
            reviews = fetch_pr_reviews(pr_number)
            save_pr_reviews(pr_number, reviews)

            print(
                f"[{index}/{len(merged_prs)}] "
                f"PR #{pr_number}: {len(reviews)} reviews"
            )

        except requests.RequestException as error:
            failed_prs.append(pr_number)
            print(f"Failed to fetch PR #{pr_number}: {error}")

    print(f"\nReview extraction completed.")
    print(f"Failed PRs: {len(failed_prs)}")

    if failed_prs:
        print(f"PR numbers requiring retry: {failed_prs}")



#fetch status checks for a PR commit
def fetch_pr_checks(pr):
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        raise ValueError("GITHUB_TOKEN is missing from .env")

    sha = pr["head"]["sha"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    url = (
        f"https://api.github.com/repos/"
        f"home-assistant/core/commits/{sha}/check-runs"
    )

    checks = []

    while url:
        response = requests.get(
            url,
            headers=headers,
            params={"per_page": 100},
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        checks.extend(data.get("check_runs", []))

        url = response.links.get("next", {}).get("url")

    return checks


#save status checks for a specific PR
def save_pr_checks(pr_number, checks):
    output_path = Path(f"data/raw/checks/{pr_number}.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(checks, file, indent=2)


#fetch and save checks for all merged PRs
def fetch_all_pr_checks(pull_requests):
    merged_prs = [
        pr for pr in pull_requests
        if pr.get("merged_at") is not None
    ]

    failed_prs = []

    for index, pr in enumerate(merged_prs, start=1):
        pr_number = pr["number"]
        check_path = Path(f"data/raw/checks/{pr_number}.json")

        if check_path.exists():
            continue

        try:
            checks = fetch_pr_checks(pr)
            save_pr_checks(pr_number, checks)

            print(
                f"[{index}/{len(merged_prs)}] "
                f"PR #{pr_number}: {len(checks)} checks"
            )

        except requests.RequestException as error:
            failed_prs.append(pr_number)
            print(f"Failed checks for PR #{pr_number}: {error}")

    print(f"Check extraction completed. Failed PRs: {len(failed_prs)}")

    if failed_prs:
        print(f"Failed PR numbers: {failed_prs}")


if __name__ == "__main__":
    pull_requests = fetch_pull_requests(max_pages=3)
    save_raw_data(pull_requests)
    fetch_all_pr_reviews(pull_requests)
    fetch_all_pr_checks(pull_requests)