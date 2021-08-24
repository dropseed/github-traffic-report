import base64

# import plotly
# import plotly.graph_objects as go
import click


class Table:
    def __init__(self):
        self.headers = []
        self.rows = []
        self.subheader = ""

    @property
    def all_rows(self):
        return [self.headers] + self.rows

    def print(self):
        col_sizes = [0 for _ in self.headers]
        for row in self.all_rows:
            for col_index, col_value in enumerate(row):
                col_sizes[col_index] = max(col_sizes[col_index], len(col_value))

        for i, header in enumerate(self.headers):
            if i == 0:
                click.secho(header.ljust(col_sizes[i]), bold=True, nl=False)
            else:
                click.secho(header.rjust(col_sizes[i]), bold=True, nl=False)

            click.echo(" ", nl=False)  # space between cols

        click.echo()

        for row in self.rows:
            for i, cell in enumerate(row):
                icon = ""
                if hasattr(cell, "change"):
                    if cell.increased:
                        icon = click.style(" ↑", fg="green")
                    elif cell.decreased:
                        icon = click.style(" ↓", fg="red")
                    elif cell.unchanged:
                        icon = "  "
                if i == 0:
                    # Left-align the first column
                    click.secho(
                        str(cell).ljust(col_sizes[i] - len(icon)) + icon, nl=False
                    )
                else:
                    # Right-align the rest
                    # TODO something not right here still
                    click.secho(
                        str(cell).rjust(col_sizes[i] - len(icon)) + icon, nl=False
                    )

                click.echo(" ", nl=False)  # space between cols

            click.echo()


class Cell:
    INCREASE = "increase"
    DECREASE = "decrease"
    UNCHANGED = "unchanged"

    def __init__(self, value, change=None, url=None):
        self.value = value
        self.change = change
        self.url = url

    def __str__(self):
        return str(self.value)

    def __len__(self):
        return len(self.value)

    # Make truncate work in templates
    def __getitem__(self, item):
        return self.value[item]

    @property
    def increased(self):
        return self.change == Cell.INCREASE

    @property
    def decreased(self):
        return self.change == Cell.DECREASE

    @property
    def unchanged(self):
        return self.change == Cell.UNCHANGED


class Chart:
    def __init__(self):
        fig = go.Figure()
        fig.update_xaxes(showgrid=False, tickformat="%a %m/%d")
        fig.update_yaxes(showgrid=False, title="Views")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20),
        )
        self.fig = fig

    def to_base64(self, width=800, height=400):
        png = plotly.io.to_image(self.fig, format="png", width=width, height=height)
        return base64.b64encode(png).decode("ascii")
