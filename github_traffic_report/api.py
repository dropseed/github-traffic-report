from requests import Session
from urllib.parse import urljoin

from .logger import logger


class APISession(Session):
    def __init__(self, base_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = base_url
        self.params.update({"per_page": 100})

    def request(self, method, url, *args, **kwargs):
        next_url = urljoin(self.base_url, url)
        paginate = kwargs.pop("paginate", False)
        paginated_data = []

        while next_url:
            response = super().request(method, next_url, *args, **kwargs)
            logger.debug(f"{method} {response.status_code} {next_url}")

            data = response.json() if response.text else {}

            if data:
                if isinstance(paginate, str):
                    paginated_data += data.get(paginate, [])
                else:
                    paginated_data += data

            if paginate:
                next_url = response.links.get("next", {}).get("url", None)
            else:
                next_url = None

        # custom property for paginated, combined data
        response.paginated_data = paginated_data

        return response

    def set_token(self, token):
        self.headers.update({"Authorization": f"token {token}"})


session = APISession(base_url="https://api.github.com")
