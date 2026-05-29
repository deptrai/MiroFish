from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcp_server import (
    _request,
    mirofish_chat_with_report,
    mirofish_generate_ontology,
    mirofish_get_project,
    mirofish_get_run_status,
)


class _DummyResponse:
    def __init__(self, payload: dict, ok: bool = True):
        self._payload = payload
        self._ok = ok

    def raise_for_status(self) -> None:
        if not self._ok:
            raise RuntimeError('boom')

    def json(self) -> dict:
        return self._payload


class _DummyClient:
    def __init__(self, recorder: list[dict], response: _DummyResponse):
        self.recorder = recorder
        self.response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    async def request(self, method: str, url: str, **kwargs):
        self.recorder.append({'method': method, 'url': url, **kwargs})
        return self.response


@pytest.mark.asyncio
async def test_request_uses_base_url_and_timeout(monkeypatch: pytest.MonkeyPatch):
    calls: list[dict] = []

    def _fake_client(*, timeout: float):
        assert timeout == 25.0
        return _DummyClient(calls, _DummyResponse({'ok': True}))

    monkeypatch.setenv('MIROFISH_API_URL', 'http://mirofish:5001')
    monkeypatch.setattr('mcp_server.httpx.AsyncClient', _fake_client)

    raw = await _request('GET', '/api/graph/project/p1')
    data = json.loads(raw)

    assert data['ok'] is True
    assert calls[0]['url'] == 'http://mirofish:5001/api/graph/project/p1'


@pytest.mark.asyncio
async def test_generate_ontology_builds_multipart(monkeypatch: pytest.MonkeyPatch):
    calls: list[dict] = []

    def _fake_client(*, timeout: float):
        return _DummyClient(calls, _DummyResponse({'project_id': 'p-1'}))

    monkeypatch.setattr('mcp_server.httpx.AsyncClient', _fake_client)

    payload = await mirofish_generate_ontology(
        simulation_requirement='Need ontology',
        project_name='demo',
        additional_context='ctx',
        files=[{'filename': 'spec.txt', 'content_base64': 'aGVsbG8='}],
    )
    data = json.loads(payload)

    assert data['project_id'] == 'p-1'
    assert calls[0]['method'] == 'POST'
    assert calls[0]['url'].endswith('/api/graph/ontology/generate')
    assert calls[0]['data']['project_name'] == 'demo'
    assert calls[0]['files'][0][0] == 'files'
    assert calls[0]['files'][0][1][0] == 'spec.txt'


@pytest.mark.asyncio
async def test_endpoint_mappings(monkeypatch: pytest.MonkeyPatch):
    calls: list[dict] = []

    def _fake_client(*, timeout: float):
        return _DummyClient(calls, _DummyResponse({'ok': True}))

    monkeypatch.setattr('mcp_server.httpx.AsyncClient', _fake_client)

    await mirofish_get_project('project-1')
    await mirofish_get_run_status('sim-9')
    await mirofish_chat_with_report('r1', 'hello', [])

    urls = [c['url'] for c in calls]
    assert urls[0].endswith('/api/graph/project/project-1')
    assert urls[1].endswith('/api/simulation/sim-9/run-status')
    assert urls[2].endswith('/api/report/chat')
