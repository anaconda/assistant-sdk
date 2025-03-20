from typing import Optional, Dict, Any, Union

from anaconda_auth.client import BaseClient

from anaconda_assistant import __version__ as version
from anaconda_assistant.config import AssistantConfig


class APIClient(BaseClient):
    _user_agent = f"anaconda-assistant/{version}"

    def __init__(
        self,
        domain: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: Optional[str] = None,
        client_source: Optional[str] = None,
        ssl_verify: Optional[bool] = None,
        extra_headers: Optional[Union[str, dict]] = None,
    ):
        super().__init__(
            domain=domain,
            api_key=api_key,
            ssl_verify=ssl_verify,
            extra_headers=extra_headers,
        )

        kwargs: Dict[str, Any] = {}
        if api_version is not None:
            kwargs["api_version"] = api_version
        if client_source is not None:
            kwargs["client_source"] = client_source

        self._config = AssistantConfig(**kwargs)

        self.headers["X-Client-Source"] = self._config.client_source
        self.headers["X-Client-Version"] = version

    def urljoin(self, url: str) -> str:
        if url.startswith("http"):
            return url

        joined = f"{self._base_uri.strip('/')}/api/assistant/{self._config.api_version}/{url.lstrip('/')}"
        return joined
