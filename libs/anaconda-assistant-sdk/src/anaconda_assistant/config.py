from anaconda_cli_base.config import AnacondaBaseSettings


class AssistantConfig(AnacondaBaseSettings, plugin_name="assistant"):
    domain: str = "assistant.anaconda.cloud"
    client_source: str = "anaconda-cli-prod"
    api_version: str = "v3"
