#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import binascii
import contextlib
import json
import os
import re
from typing import Any, AsyncIterator

import httpx
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

mcp = FastMCP("MiroFish")

# H5 (Python): module-level client w/ connection pooling instead of per-call AsyncClient.
# Set during startup via FastMCP lifespan; falls back to lazy init for stdio mode.
_CLIENT: httpx.AsyncClient | None = None

# H4 (Python): per-file decode size cap (50 MB matches MiroFish backend upload limit).
MAX_FILE_BYTES = 50 * 1024 * 1024
# Total multipart payload cap (sum of all files) to bound memory pressure.
MAX_TOTAL_UPLOAD_BYTES = 100 * 1024 * 1024


def _base_url() -> str:
    return os.getenv("MIROFISH_API_URL", "http://mirofish:5001").rstrip("/")


def _get_client() -> httpx.AsyncClient:
    global _CLIENT
    if _CLIENT is None or _CLIENT.is_closed:
        _CLIENT = httpx.AsyncClient(timeout=25.0)
    return _CLIENT


def _sanitize_error(message: str) -> str:
    # H7: URL-anchored only — KHÔNG match bare word "mirofish" (would redact
    # legitimate user content mentioning the product name).
    redacted = re.sub(r"https?://[^\s\"'<>]+", "[url]", message)
    redacted = re.sub(r"https?://mirofish(?:-mcp)?(?::\d+)?", "[mirofish-internal]", redacted)
    return redacted


async def _request(method: str, path: str, *, json_body: dict[str, Any] | None = None,
                   params: dict[str, Any] | None = None,
                   files: list[tuple[str, tuple[str, bytes, str]]] | None = None,
                   data: dict[str, Any] | None = None,
                   idempotency_key: str | None = None,
                   language: str | None = None) -> str:
    url = f"{_base_url()}{path}"
    client = _get_client()
    try:
        headers: dict[str, str] = {}
        if idempotency_key:
            headers["X-Idempotency-Key"] = idempotency_key
        # Locale propagation: MiroFish locale.get_locale() reads Accept-Language
        # (default zh). Without forwarding caller's preferred language, every
        # report comes back in Chinese regardless of workflow `report_language`.
        if language:
            headers["Accept-Language"] = language
        resp = await client.request(
            method,
            url,
            json=json_body,
            params=params,
            files=files,
            data=data,
            headers=headers or None,
        )
        resp.raise_for_status()
        return json.dumps(resp.json(), ensure_ascii=False)
    except httpx.HTTPStatusError as exc:
        # Surface backend error body when JSON-parseable — gives caller actionable detail.
        body_snippet = ""
        with contextlib.suppress(Exception):
            body_snippet = exc.response.text[:500]
        return json.dumps({
            "success": False,
            "error": _sanitize_error(f"HTTP {exc.response.status_code}: {body_snippet or str(exc)}"),
        }, ensure_ascii=False)
    except httpx.HTTPError as exc:
        return json.dumps({"success": False, "error": _sanitize_error(str(exc))}, ensure_ascii=False)


def _validate_id_arg(name: str, value: str) -> str | None:
    """L4: enforce at-least-one-of validation. Returns error message or None."""
    if not value:
        return f"{name} is required"
    return None


@mcp.tool
async def mirofish_generate_ontology(simulation_requirement: str, project_name: str = "",
                                     additional_context: str = "",
                                     files: list[dict[str, str]] | None = None) -> str:
    """Generate ontology from requirement text and base64-encoded source files (PDF/MD/TXT).

    Args:
        simulation_requirement: Required — description of the simulation scenario.
        project_name: Optional project label.
        additional_context: Optional context paragraph.
        files: Required — list of {filename, content_base64}. At least one file with valid
               base64 content is mandatory (MiroFish backend rejects empty uploads).
    """
    # H6: validate non-empty files BEFORE calling Flask (which returns opaque 400).
    if not files:
        return json.dumps({
            "success": False,
            "error": "files parameter is required — supply at least one {filename, content_base64} entry",
        }, ensure_ascii=False)

    file_parts: list[tuple[str, tuple[str, bytes, str]]] = []
    total_bytes = 0
    for idx, f in enumerate(files):
        filename = f.get("filename", "").strip() or f"input-{idx}.txt"
        content_base64 = f.get("content_base64", "")
        if not content_base64:
            return json.dumps({
                "success": False,
                "error": f"files[{idx}] ({filename}): content_base64 is empty",
            }, ensure_ascii=False)
        # H4: propagate decode errors instead of silent fallback to b"".
        try:
            payload = base64.b64decode(content_base64, validate=True)
        except (binascii.Error, ValueError) as exc:
            return json.dumps({
                "success": False,
                "error": f"files[{idx}] ({filename}): invalid base64 — {exc}",
            }, ensure_ascii=False)
        # H4: enforce per-file + total size limits.
        if len(payload) > MAX_FILE_BYTES:
            return json.dumps({
                "success": False,
                "error": f"files[{idx}] ({filename}): exceeds {MAX_FILE_BYTES // (1024 * 1024)} MB limit",
            }, ensure_ascii=False)
        total_bytes += len(payload)
        if total_bytes > MAX_TOTAL_UPLOAD_BYTES:
            return json.dumps({
                "success": False,
                "error": f"total upload size exceeds {MAX_TOTAL_UPLOAD_BYTES // (1024 * 1024)} MB limit",
            }, ensure_ascii=False)
        file_parts.append(("files", (filename, payload, "application/octet-stream")))

    form_data = {
        "simulation_requirement": simulation_requirement,
        "project_name": project_name,
        "additional_context": additional_context,
    }
    return await _request("POST", "/api/graph/ontology/generate", files=file_parts, data=form_data)


@mcp.tool
async def mirofish_build_graph(project_id: str, graph_name: str = "", chunk_size: int = 1000, chunk_overlap: int = 100, idempotency_key: str = "") -> str:
    return await _request("POST", "/api/graph/build", json_body={"project_id": project_id, "graph_name": graph_name, "chunk_size": chunk_size, "chunk_overlap": chunk_overlap}, idempotency_key=idempotency_key or None)


@mcp.tool
async def mirofish_get_task_status(task_id: str) -> str:
    return await _request("GET", f"/api/graph/task/{task_id}")


@mcp.tool
async def mirofish_get_project(project_id: str) -> str:
    return await _request("GET", f"/api/graph/project/{project_id}")


@mcp.tool
async def mirofish_create_simulation(project_id: str, name: str = "", idempotency_key: str = "") -> str:
    return await _request("POST", "/api/simulation/create", json_body={"project_id": project_id, "name": name}, idempotency_key=idempotency_key or None)


@mcp.tool
async def mirofish_prepare_simulation(simulation_id: str, idempotency_key: str = "") -> str:
    return await _request("POST", "/api/simulation/prepare", json_body={"simulation_id": simulation_id}, idempotency_key=idempotency_key or None)


@mcp.tool
async def mirofish_get_prepare_status(task_id: str = "", simulation_id: str = "") -> str:
    # L4: require at least one identifier — otherwise the proxy bills for a no-op call.
    if not task_id and not simulation_id:
        return json.dumps({
            "success": False,
            "error": "at least one of task_id or simulation_id is required",
        }, ensure_ascii=False)
    payload: dict[str, str] = {}
    if task_id:
        payload["task_id"] = task_id
    if simulation_id:
        payload["simulation_id"] = simulation_id
    return await _request("POST", "/api/simulation/prepare/status", json_body=payload)


@mcp.tool
async def mirofish_start_simulation(simulation_id: str, platform: str = "", max_rounds: int = 0, idempotency_key: str = "") -> str:
    # P4: forward optional platform + max_rounds when caller sets them; otherwise
    # let Flask use the LLM-generated config defaults.
    body: dict[str, Any] = {"simulation_id": simulation_id}
    if platform:
        body["platform"] = platform
    if max_rounds and max_rounds > 0:
        body["max_rounds"] = max_rounds
    return await _request("POST", "/api/simulation/start", json_body=body, idempotency_key=idempotency_key or None)


@mcp.tool
async def mirofish_get_run_status(simulation_id: str) -> str:
    return await _request("GET", f"/api/simulation/{simulation_id}/run-status")


@mcp.tool
async def mirofish_stop_simulation(simulation_id: str) -> str:
    return await _request("POST", "/api/simulation/stop", json_body={"simulation_id": simulation_id})


@mcp.tool
async def mirofish_get_simulation_timeline(simulation_id: str) -> str:
    return await _request("GET", f"/api/simulation/{simulation_id}/timeline")


@mcp.tool
async def mirofish_get_simulation_posts(simulation_id: str) -> str:
    return await _request("GET", f"/api/simulation/{simulation_id}/posts")


@mcp.tool
async def mirofish_get_simulation_comments(simulation_id: str) -> str:
    return await _request("GET", f"/api/simulation/{simulation_id}/comments")


@mcp.tool
async def mirofish_generate_report(simulation_id: str, language: str = "", idempotency_key: str = "") -> str:
    return await _request(
        "POST",
        "/api/report/generate",
        json_body={"simulation_id": simulation_id},
        idempotency_key=idempotency_key or None,
        language=language or None,
    )


@mcp.tool
async def mirofish_get_report_generate_status(task_id: str = "", simulation_id: str = "") -> str:
    # L4: require at least one identifier.
    if not task_id and not simulation_id:
        return json.dumps({
            "success": False,
            "error": "at least one of task_id or simulation_id is required",
        }, ensure_ascii=False)
    payload: dict[str, str] = {}
    if task_id:
        payload["task_id"] = task_id
    if simulation_id:
        payload["simulation_id"] = simulation_id
    return await _request("POST", "/api/report/generate/status", json_body=payload)


@mcp.tool
async def mirofish_get_report(report_id: str) -> str:
    return await _request("GET", f"/api/report/{report_id}")


@mcp.tool
async def mirofish_get_report_by_simulation(simulation_id: str) -> str:
    return await _request("GET", f"/api/report/by-simulation/{simulation_id}")


@mcp.tool
async def mirofish_chat_with_report(report_id: str, message: str, conversation_history: list[dict[str, Any]] | None = None) -> str:
    return await _request("POST", "/api/report/chat", json_body={
        "report_id": report_id,
        "message": message,
        "conversation_history": conversation_history or [],
    })


@mcp.custom_route("/invoke", methods=["POST"])
async def _invoke_handler(request: Request) -> JSONResponse:
    """Stateless JSON-RPC handler for internal service calls (no session required)."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    method = body.get("method")
    params = body.get("params", {})

    if method == "tools/list":
        tools = await mcp.list_tools()
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "tools": [
                    {"name": t.name, "description": t.description, "inputSchema": t.parameters}
                    for t in tools
                ]
            }
        })
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments") or {}
        if not tool_name:
            return JSONResponse({"error": "Missing params.name"}, status_code=400)
        try:
            result = await mcp.call_tool(tool_name, arguments)
            # FastMCP returns ToolResult — extract content text
            content = []
            if hasattr(result, "content"):
                for item in result.content:
                    if hasattr(item, "text"):
                        content.append({"type": "text", "text": item.text})
                    else:
                        content.append({"type": "text", "text": str(item)})
            elif isinstance(result, list):
                for item in result:
                    if hasattr(item, "text"):
                        content.append({"type": "text", "text": item.text})
                    else:
                        content.append({"type": "text", "text": str(item)})
            else:
                content = [{"type": "text", "text": str(result)}]
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {"content": content}
            })
        except Exception as e:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {"code": -32000, "message": str(e)}
            }, status_code=200)
    else:
        return JSONResponse({"error": f"Unsupported method: {method}"}, status_code=400)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio")
    parser.add_argument("--port", type=int, default=8901)
    args = parser.parse_args()
    mcp.run(transport=args.transport, port=args.port)
