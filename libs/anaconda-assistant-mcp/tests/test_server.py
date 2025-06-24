from typing import Any
import pytest
from anaconda_assistant_mcp.server import search_packages


mock_query_all_response = [
    "conda-forge/osx-arm64::numpy==1.23.5=py310h5d7c261_0",
    "conda-forge/osx-arm64::numpy==1.23.5=py311ha92fb03_0",
]


@pytest.mark.asyncio
async def test_search_packages(monkeypatch):
    monkeypatch.setattr(
        "conda.api.SubdirData.query_all",
        lambda query, channels=None, subdirs=None: mock_query_all_response,
    )
    result = await search_packages("numpy")
    assert result == mock_query_all_response
