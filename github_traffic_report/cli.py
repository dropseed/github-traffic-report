import datetime

import click
import jinja2

# import plotly.graph_objects as go

from .email import send_email
from .api import session
from .output import Table, Cell, Chart
from .repos import Repo

from .logger import logger


@click.group()
def cli():
    pass


@cli.command()
@click.argument("repo_query")
@click.option("--to", envvar="REPORT_TO", required=True)
@click.option("--smtp-from", envvar="REPORT_SMTP_FROM", required=True)
@click.option("--smtp-host", envvar="REPORT_SMTP_HOST", required=True)
@click.option("--smtp-port", envvar="REPORT_SMTP_PORT", default=587)
@click.option("--smtp-username", envvar="REPORT_SMTP_USERNAME", required=True)
@click.option("--smtp-password", envvar="REPORT_SMTP_PASSWORD", required=True)
@click.option("--token", envvar="GITHUB_TOKEN", required=True)
@click.option("--debug", is_flag=True)
def send(
    repo_query,
    to,
    smtp_from,
    smtp_host,
    smtp_port,
    smtp_username,
    smtp_password,
    token,
    debug,
):
    if not debug:
        logger.disabled = True

    session.set_token(token)

    repo_results = []

    for query in repo_query.split(","):
        response = session.get(
            "https://api.github.com/search/repositories",
            params={"q": query, "sort": "stars", "order": "desc"},
            paginate="items",
        )
        response.raise_for_status()
        repo_results += response.paginated_data

    print(f"Found {len(repo_results)} repos to report on")

    repos = [Repo(data) for data in repo_results]
    for repo in repos:
        print(repo)
        repo.fetch_traffic_data()

    # includes today, since the GitHub API does too
    last_14_days = [
        (datetime.datetime.now() - datetime.timedelta(days=x)).date()
        for x in range(0, 14)
    ]
    last_14_days_iso = [x.isoformat() for x in last_14_days]
    print("Last 14 days", last_14_days_iso)
    last_7_days = last_14_days_iso[-7:]
    previous_7_days = last_14_days_iso[:-7]

    repos_by_views = sorted(
        repos, key=lambda r: sum(r.unique_views_on_dates(last_7_days)), reverse=True
    )
    # Remove any that don't have data
    repos_by_views = [
        x
        for x in repos_by_views
        if any(x.unique_views_on_dates(last_14_days_iso))
        or any(x.unique_clones_on_dates(last_14_days_iso))
    ]

    table = Table()
    table.headers = ["Repo", "Visitors (views)", "Cloners (clones)"]
    table.subheader = "Last 7 days"

    for repo in repos_by_views:
        unique_views_this_week = sum(repo.unique_views_on_dates(last_7_days))
        unique_clones_this_week = sum(repo.unique_clones_on_dates(last_7_days))

        unique_views_last_week = sum(repo.unique_views_on_dates(previous_7_days))
        unique_clones_last_week = sum(repo.unique_clones_on_dates(previous_7_days))

        if not unique_views_this_week and not unique_clones_this_week:
            # Don't need to show inactive rows on the table
            continue

        if unique_views_this_week > unique_views_last_week:
            views_change = Cell.INCREASE
        elif unique_views_this_week < unique_views_last_week:
            views_change = Cell.DECREASE
        else:
            views_change = Cell.UNCHANGED

        if unique_clones_this_week > unique_clones_last_week:
            clones_change = Cell.INCREASE
        elif unique_clones_this_week < unique_clones_last_week:
            clones_change = Cell.DECREASE
        else:
            clones_change = Cell.UNCHANGED

        views_this_week = sum(repo.views_on_dates(last_7_days))
        clones_this_week = sum(repo.clones_on_dates(last_7_days))

        table.rows.append(
            [
                Cell(repo.full_name, None, url=repo.html_url),
                Cell(
                    f"{unique_views_this_week} ({views_this_week})",
                    views_change,
                ),
                Cell(
                    f"{unique_clones_this_week} ({clones_this_week})",
                    clones_change,
                ),
            ]
        )

    table.print()

    repo_reports = []
    for repo in repos_by_views:
        repo_has_data = False
        paths_table = Table()
        paths_table.headers = ["Path", "Unique visitors", "Views"]
        paths_table.subheader = "Last 14 days"
        for path_data in repo.paths_data:
            paths_table.rows.append(
                [
                    Cell(
                        path_data["title"], url="https://github.com" + path_data["path"]
                    ),
                    str(path_data["uniques"]),
                    str(path_data["count"]),
                ]
            )
            if path_data["uniques"] > 0:
                repo_has_data = True

        referrers_table = Table()
        referrers_table.headers = ["Referrer", "Unique visitors", "Views"]
        referrers_table.subheader = "Last 14 days"
        for referrer_data in repo.referrers_data:
            referrers_table.rows.append(
                [
                    Cell(
                        referrer_data["referrer"],
                        url=f"https://github.com/{repo.full_name}/graphs/traffic?referrer={referrer_data['referrer']}#top-domains",
                    ),
                    str(referrer_data["uniques"]),
                    str(referrer_data["count"]),
                ]
            )
            if referrer_data["uniques"] > 0:
                repo_has_data = True

        # repo_chart = Chart()
        # repo_chart.fig.add_trace(
        #     go.Scatter(
        #         x=last_14_days_iso,
        #         y=repo.views_on_dates(last_14_days_iso),
        #         name="Views",
        #     ),
        # )
        # repo_chart.fig.add_trace(
        #     go.Scatter(
        #         x=last_14_days_iso,
        #         y=repo.clones_on_dates(last_14_days_iso),
        #         name="Clones",
        #     ),
        # )

        if repo_has_data:
            repo_reports.append(
                {
                    "repo": repo,
                    # "chart": repo_chart.to_base64(height=200),
                    "paths_table": paths_table,
                    "referrers_table": referrers_table,
                }
            )

    # aggregate_chart = Chart()
    # for repo in repos_by_views:
    #     aggregate_chart.fig.add_trace(
    #         go.Scatter(
    #             x=last_14_days_iso,
    #             y=repo.views_on_dates(last_14_days_iso),
    #             name=repo.full_name,
    #         ),
    #     )

    start_date = last_14_days[-1]
    end_date = last_14_days[0]

    env = jinja2.Environment(
        loader=jinja2.PackageLoader("github_traffic_report"),
        autoescape=jinja2.select_autoescape(),
    )
    template = env.get_template("report.html")
    output = template.render(
        start_date=start_date,
        end_date=end_date,
        repo_reports=repo_reports,
        # aggregate_chart=aggregate_chart.to_base64(),
        aggregate_table=table,
    )

    if debug:
        with open("report.html", "w+") as f:
            f.write(output)

    send_email(
        subject=f"GitHub traffic report for {start_date.strftime('%b %d')} to {end_date.strftime('%b %d')}",
        html=output,
        to_email=to,
        from_email=smtp_from,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_username=smtp_username,
        smtp_password=smtp_password,
    )
