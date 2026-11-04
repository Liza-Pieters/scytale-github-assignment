# Scytale Junior Data Engineer Home Assignment

A Python data pipeline that extracts merged pull requests from the `home-assistant/core` GitHub repository, processes code reviews and status checks, and generates a CSV report.

## Project Structure

```text
scytale-github-assignment/
├── ai_utils/
│   ├── prompts.md
│   └── jira_agent_prompt.md
├── tests/
│   └── test_transform.py
├── extract.py
├── transform.py
├── main.py
├── requirements.txt
└── README.md
```

The pipeline generates the following directories locally:

- `data/raw/` — Raw GitHub API responses in JSON format.
- `data/processed/` — Transformed pull request data.
- `output/` — Final CSV report.

These generated directories are excluded from Git.

## Setup

Requires Python 3.12 or a compatible Python 3 version.

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GITHUB_TOKEN=your_github_personal_access_token
```

Do not commit your token or `.env` file to GitHub.

## Running the Pipeline

First, extract data from the GitHub API:

```bash
python extract.py
```

This retrieves closed pull requests, filters merged pull requests, and saves their review and check-run data locally.

Then generate the processed JSON and CSV report:

```bash
python main.py
```

The final report is saved to:

`output/github_pr_report.csv`

## Report Columns

| Column | Description |
|---|---|
| `PR_NUMBER` | GitHub pull request number |
| `PR_TITLE` | Pull request title |
| `AUTHOR` | GitHub username of the PR author |
| `MERGE_DATE` | Timestamp when the PR was merged |
| `CR_Passed` | Whether at least one reviewer approved before the merge |
| `CHECKS_PASSED` | Result of the available required-check heuristic |

## Status Check Limitations

GitHub check runs do not, by themselves, establish which checks were required by branch protection rules at the historical merge time.

This implementation identifies candidate required checks using names ending in `/required`.

- `True`: All identified candidate checks completed successfully, neutrally, or were skipped before the merge.
- `False`: At least one identified candidate check failed or did not complete before the merge.
- Empty: No candidate required checks were identified, or check data was unavailable.

These results are an approximation and should not be interpreted as a complete historical verification of GitHub branch protection requirements.

The current extraction is limited to the configured pull request pages and does not represent the repository's complete history.

## Tests

Run the automated tests with:

```bash
python -m pytest
```

The tests cover code review and status check transformation logic.

## AI Resources and Optional Bonus

The `ai_utils/` directory documents AI assistance used during development.

`ai_utils/jira_agent_prompt.md` contains an agentic AI prompt for extending the project to JIRA ticket extraction, including reusable object-oriented components.

The JIRA integration is a proposed extension and is not implemented in the current pipeline.
