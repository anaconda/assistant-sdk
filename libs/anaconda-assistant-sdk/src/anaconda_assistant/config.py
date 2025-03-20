from typing import Optional
from anaconda_cli_base.config import AnacondaBaseSettings


class AssistantConfig(AnacondaBaseSettings, plugin_name="assistant"):
    client_source: str = "anaconda-cli-prod"
    api_version: str = "v3"
    accepted_terms: Optional[bool] = None
    data_collection: Optional[bool] = None
