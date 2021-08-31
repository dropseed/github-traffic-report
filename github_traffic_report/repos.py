from .api import session


class Repo:
    def __init__(self, github_data):
        self.data = github_data
        self.full_name = self.data["full_name"]
        self.html_url = self.data["html_url"]
        self.avatar_url = self.data["owner"]["avatar_url"]
        self.private = self.data["private"]
        self.forks_count = self.data["forks_count"]
        self.stargazers_count = self.data["stargazers_count"]

        self.clones_data = {}
        self.paths_data = []
        self.referrers_data = []
        self.views_data = {}

    def __str__(self):
        return self.full_name

    def fetch_traffic_data(self):
        response = session.get(f"repos/{self.full_name}/traffic/clones")
        response.raise_for_status()
        self.clones_data = response.json()

        response = session.get(f"repos/{self.full_name}/traffic/views")
        response.raise_for_status()
        self.views_data = response.json()

        if self.views_data["count"]:
            response = session.get(f"repos/{self.full_name}/traffic/popular/paths")
            response.raise_for_status()
            self.paths_data = response.json()

            response = session.get(f"repos/{self.full_name}/traffic/popular/referrers")
            response.raise_for_status()
            self.referrers_data = response.json()
        else:
            self.paths_data = []
            self.referrers_data = []

    def print_traffic_data(self):
        print(f"Clones: {self.clones_data}")
        print(f"Paths: {self.paths_data}")
        print(f"Referrers: {self.referrers_data}")
        print(f"Views: {self.views_data}")

    def get_traffic_values(self, data, key, dates):
        values = []
        for date in dates:
            value = 0  # assume 0 (can be gaps in data)
            for v in data:
                if v["timestamp"].split("T")[0] == date:
                    value = v[key]
            values.append(value)
        return values

    def views_on_dates(self, dates):
        return self.get_traffic_values(self.views_data["views"], "count", dates)

    def unique_views_on_dates(self, dates):
        return self.get_traffic_values(self.views_data["views"], "uniques", dates)

    def clones_on_dates(self, dates):
        return self.get_traffic_values(self.clones_data["clones"], "count", dates)

    def unique_clones_on_dates(self, dates):
        return self.get_traffic_values(self.clones_data["clones"], "uniques", dates)
