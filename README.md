# github-traffic-report

Get a weekly emailed summary of traffic in your organization.

Uses the [GitHub API for repo traffic](https://docs.github.com/en/rest/reference/repos#traffic) (clones and page views), which has data for the last 14 days.

![GitHub traffic report weekly email screenshot](https://user-images.githubusercontent.com/649496/130651241-107288d1-e188-49b2-9240-a879238d9b1c.png)

## Use the GitHub Action

```yml
name: traffic-report
on:
  workflow_dispatch: {}
  schedule:
  - cron: 0 0 * * Mon  # Weekly

jobs:
  send:
    runs-on: ubuntu-latest
    steps:
    - uses: dropseed/github-traffic-report@v1
      with:
        # A token with access to the repos
        # (use secrets)
        github_token: ${{ secrets.TRAFFIC_REPORT_TOKEN }}

        # A repo search query to find repos for the report (public repos in this org by default)
        # For multiple queries, use a comma to separate them
        repo_query: "org:${{ github.repository.owner }} is:public"

        # Can be comma separated (just like an email "to" field)
        # (use secrets)
        to_email: "you@example.com"

        # SMTP settings for email sending
        # (use secrets)
        smtp_from: "reports@example.com"
        smtp_host: ""
        smtp_port: 587
        smtp_username: ""
        smtp_password: ""
```
