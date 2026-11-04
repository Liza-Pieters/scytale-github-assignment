# Agentic AI Prompt — JIRA Integration

## Objective

Extend the existing GitHub pull request data pipeline to support JIRA ticket extraction using the JIRA REST API.

The AI agent should reproduce the existing project's Extract → Transform → Report workflow while introducing reusable components for multiple API integrations.

## Agent Instructions

You are a Python data engineer working with an existing GitHub integration.

1. **Inspect the existing project**
   - Read `extract.py`, `transform.py`, `main.py`, and `requirements.txt`.
   - Identify reusable functionality such as authentication, pagination, JSON storage, data transformation, and CSV export.
   - Preserve the existing GitHub integration and its outputs.

2. **Design a reusable architecture**
   - Introduce an abstract `BaseExtractor` class with shared methods for API requests, pagination, and saving raw data.
   - Create `GitHubExtractor` and `JiraExtractor` implementations.
   - Keep integration-specific transformations separate.
   - Reuse common CSV export functionality where appropriate.

3. **Implement JIRA extraction**
   - Authenticate using JIRA API credentials supplied through environment variables.
   - Retrieve tickets from a configurable JIRA project using the REST API.
   - Handle pagination, API errors, rate limits, and missing fields.
   - Save the raw response under `data/raw/jira/`.

4. **Transform JIRA tickets**
   - Extract ticket key, summary, status, assignee, reporter, created date, updated date, and resolution date.
   - Handle missing assignees and unresolved tickets.
   - Save processed data under `data/processed/jira/`.

5. **Generate reports**
   - Export a CSV report to `output/jira_ticket_report.csv`.
   - Preserve the existing GitHub report at `output/github_pr_report.csv`.

6. **Add tests and documentation**
   - Create unit tests using mocked API responses.
   - Verify pagination, authentication handling, missing fields, and CSV output.
   - Update the README with instructions for both integrations.
   - Never expose credentials in source code or generated files.

## Expected Deliverables

- Reusable Python classes supporting GitHub and JIRA.
- Working JIRA API extraction and transformation.
- Separate JSON extracts and CSV reports.
- Automated tests for both integrations.
- Updated documentation.

## Success Criteria

The existing GitHub pipeline must continue to work, and the JIRA pipeline must independently generate a ticket report using configurable credentials.

The agent must report any unimplemented functionality or unverified assumptions rather than claiming completion.