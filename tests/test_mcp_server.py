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
    def __init__(self, recorder: list[dict], response: _DummyResponse | list[_DummyResponse]):
        self.recorder = recorder
        self.response = response
        self.is_closed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    async def aclose(self):
        self.is_closed = True

    async def request(self, method: str, url: str, **kwargs):
        self.recorder.append({'method': method, 'url': url, **kwargs})
        if isinstance(self.response, list):
            if not self.response:
                raise RuntimeError('No queued response left')
            return self.response.pop(0)
        return self.response


@pytest.mark.asyncio
async def test_request_uses_base_url_and_timeout(monkeypatch: pytest.MonkeyPatch):
    calls: list[dict] = []

    def _fake_client(*, timeout: float):
        assert timeout == 25.0
        return _DummyClient(calls, _DummyResponse({'ok': True}))

    monkeypatch.setenv('MIROFISH_API_URL', 'http://mirofish:5001')
    monkeypatch.setattr('mcp_server._CLIENT', None)
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

    monkeypatch.setattr('mcp_server._CLIENT', None)
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

    responses = [
        _DummyResponse({'ok': True}),  # get_project
        _DummyResponse({'ok': True}),  # get_run_status
        _DummyResponse({'data': {'simulation_id': 'sim-42'}}),  # get report by id
        _DummyResponse({'ok': True}),  # chat_with_report
    ]

    def _fake_client(*, timeout: float):
        return _DummyClient(calls, responses)

    monkeypatch.setattr('mcp_server._CLIENT', None)
    monkeypatch.setattr('mcp_server.httpx.AsyncClient', _fake_client)

    await mirofish_get_project('project-1')
    await mirofish_get_run_status('sim-9')
    await mirofish_chat_with_report('r1', 'hello', [])

    urls = [c['url'] for c in calls]
    assert urls[0].endswith('/api/graph/project/project-1')
    assert urls[1].endswith('/api/simulation/sim-9/run-status')
    assert urls[2].endswith('/api/report/r1')
    assert urls[3].endswith('/api/report/chat')
    assert calls[3]['json'] == {
        'simulation_id': 'sim-42',
        'message': 'hello',
        'chat_history': [],
    }


@pytest.mark.asyncio
async def test_chat_with_report_returns_error_when_simulation_id_missing(monkeypatch: pytest.MonkeyPatch):
    calls: list[dict] = []

    responses = [
        _DummyResponse({'data': {}}),
    ]

    def _fake_client(*, timeout: float):
        return _DummyClient(calls, responses)

    monkeypatch.setattr('mcp_server._CLIENT', None)
    monkeypatch.setattr('mcp_server.httpx.AsyncClient', _fake_client)

    raw = await mirofish_chat_with_report('r-missing', 'hello', [])
    payload = json.loads(raw)

    assert payload['success'] is False
    assert 'Could not resolve simulation_id' in payload['error']
    assert len(calls) == 1
    assert calls[0]['url'].endswith('/api/report/r-missing')
