"""
Minimal mock ZEP Cloud REST API server for local development.
Handles all endpoints used by zep_cloud==3.13.0 client.
Entities are extracted from submitted text using the configured LLM.
"""

import json
import os
import uuid
import time
import threading
from datetime import datetime, timezone
from typing import Any

from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=True)

app = Flask(__name__)
CORS(app)

# In-memory store
_graphs: dict[str, dict] = {}           # graph_id -> {name, description, entity_types, text_chunks}
_episodes: dict[str, dict] = {}         # episode_uuid -> {content, processed, graph_id, ...}
_nodes: dict[str, list] = {}            # graph_id -> [node, ...]
_edges: dict[str, list] = {}            # graph_id -> [edge, ...]

_llm_client = OpenAI(
    api_key=os.environ.get("LLM_API_KEY", "mock"),
    base_url=os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1"),
)
_llm_model = os.environ.get("LLM_MODEL_NAME", "gpt-4o-mini")

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _extract_entities_from_text(graph_id: str, text: str) -> list[dict]:
    """Call LLM to extract persona entities from text."""
    try:
        resp = _llm_client.chat.completions.create(
            model=_llm_model,
            temperature=0.3,
            max_tokens=1500,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an entity extractor. Given text, extract 5-10 distinct people/personas "
                        "as JSON. Each person should have: name (string), summary (string describing them), "
                        "attributes (object with occupation, age_group, interests as strings). "
                        "Return ONLY a JSON array of objects, no markdown."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Extract personas from this text:\n\n{text[:3000]}",
                },
            ],
        )
        raw = resp.choices[0].message.content.strip()
        # Strip markdown code blocks if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
            raw = raw.rsplit("```", 1)[0].strip()
        entities = json.loads(raw)
        if not isinstance(entities, list):
            raise ValueError("not a list")
        return entities
    except Exception as e:
        print(f"[mock-zep] LLM entity extraction failed: {e}, using fallback personas")
        return _fallback_personas()

def _fallback_personas() -> list[dict]:
    return [
        {"name": "Alice Zhang", "summary": "Tech-savvy early adopter who follows crypto markets closely.", "attributes": {"occupation": "software engineer", "age_group": "25-35", "interests": "blockchain, DeFi, technology"}},
        {"name": "Bob Santos", "summary": "Retail investor cautious about volatility, holds long-term positions.", "attributes": {"occupation": "accountant", "age_group": "35-45", "interests": "value investing, crypto education"}},
        {"name": "Carol Kim", "summary": "Journalist covering fintech and decentralized finance narratives.", "attributes": {"occupation": "journalist", "age_group": "28-38", "interests": "fintech, regulation, crypto journalism"}},
        {"name": "David Patel", "summary": "Day trader focused on technical analysis and short-term trends.", "attributes": {"occupation": "trader", "age_group": "22-32", "interests": "technical analysis, market trends"}},
        {"name": "Eva Müller", "summary": "Academic researcher studying decentralized governance mechanisms.", "attributes": {"occupation": "researcher", "age_group": "30-40", "interests": "DAOs, governance, academic research"}},
        {"name": "Frank Li", "summary": "Skeptic of speculative assets, prefers traditional finance.", "attributes": {"occupation": "financial analyst", "age_group": "40-50", "interests": "traditional finance, risk management"}},
        {"name": "Grace Obi", "summary": "Community manager for a DeFi project, bullish on ecosystem growth.", "attributes": {"occupation": "community manager", "age_group": "24-34", "interests": "community building, DeFi, NFTs"}},
        {"name": "Henry Park", "summary": "Long-time crypto enthusiast who witnessed multiple market cycles.", "attributes": {"occupation": "entrepreneur", "age_group": "32-42", "interests": "Bitcoin, market cycles, startup"}},
    ]

def _build_nodes_for_graph(graph_id: str) -> list[dict]:
    """Extract or use fallback entities for a graph."""
    graph = _graphs.get(graph_id, {})
    all_text = "\n\n".join(graph.get("text_chunks", []))
    if len(all_text) > 100:
        entities = _extract_entities_from_text(graph_id, all_text)
    else:
        entities = _fallback_personas()

    nodes = []
    for ent in entities:
        name = ent.get("name", "Unknown Person")
        nodes.append({
            "uuid": str(uuid.uuid4()),
            "name": name,
            "labels": ["Entity", "Person"],
            "summary": ent.get("summary", f"A person named {name}."),
            "attributes": ent.get("attributes", {}),
            "created_at": _now(),
        })
    return nodes

# ── ZEP Cloud REST API mock endpoints ─────────────────────────────────────────

@app.route("/api/v2/graph/create", methods=["POST"])
def graph_create():
    body = request.get_json(silent=True) or {}
    graph_id = body.get("graph_id") or str(uuid.uuid4())
    _graphs[graph_id] = {
        "name": body.get("name", "mock-graph"),
        "description": body.get("description", ""),
        "entity_types": {},
        "text_chunks": [],
        "created_at": _now(),
    }
    _nodes[graph_id] = []
    _edges[graph_id] = []
    print(f"[mock-zep] graph/create graph_id={graph_id}")
    return jsonify({"graph_id": graph_id, "uuid": graph_id, "name": _graphs[graph_id]["name"], "created_at": _graphs[graph_id]["created_at"]})


@app.route("/api/v2/graph/<graph_id>", methods=["GET"])
def graph_get(graph_id: str):
    g = _graphs.get(graph_id, {"name": "mock", "description": "", "created_at": _now()})
    return jsonify({"graph_id": graph_id, "uuid": graph_id, "name": g.get("name", "mock"), "created_at": g.get("created_at", _now())})


@app.route("/api/v2/graph/<graph_id>", methods=["DELETE"])
def graph_delete(graph_id: str):
    _graphs.pop(graph_id, None)
    _nodes.pop(graph_id, None)
    _edges.pop(graph_id, None)
    print(f"[mock-zep] DELETE graph {graph_id}")
    return jsonify({"message": "Graph deleted"})


@app.route("/api/v2/graph/<graph_id>", methods=["PATCH"])
def graph_update(graph_id: str):
    return jsonify({"graph_id": graph_id})


@app.route("/api/v2/graph/list-all", methods=["GET"])
def graph_list():
    return jsonify([{"graph_id": k, "name": v.get("name", "mock")} for k, v in _graphs.items()])


# Entity types / ontology
@app.route("/api/v2/entity-types", methods=["GET"])
def entity_types_get():
    graph_id = request.args.get("graph_id")
    if graph_id and graph_id in _graphs:
        return jsonify({"entity_types": _graphs[graph_id].get("entity_types", {})})
    return jsonify({"entity_types": {}})


@app.route("/api/v2/entity-types", methods=["PUT"])
def entity_types_set():
    body = request.get_json(silent=True) or {}
    graph_ids = body.get("graph_ids") or []
    entities = body.get("entities") or {}
    for gid in graph_ids:
        if gid not in _graphs:
            _graphs[gid] = {"name": "mock", "entity_types": {}, "text_chunks": [], "created_at": _now()}
        _graphs[gid]["entity_types"] = entities
    print(f"[mock-zep] entity-types PUT graph_ids={graph_ids}")
    return jsonify({"message": "Entity types set"})


# Graph batch (add episodes)
@app.route("/api/v2/graph-batch", methods=["POST"])
def graph_batch():
    body = request.get_json(silent=True) or {}
    graph_id = body.get("graph_id")
    episodes_in = body.get("episodes") or []

    if graph_id not in _graphs:
        _graphs[graph_id] = {"name": "mock", "entity_types": {}, "text_chunks": [], "created_at": _now()}
        _nodes[graph_id] = []
        _edges[graph_id] = []

    result_episodes = []
    for ep_data in episodes_in:
        text = ep_data.get("data") or ep_data.get("content") or ""
        if text:
            _graphs[graph_id].setdefault("text_chunks", []).append(text)
        ep_uuid = str(uuid.uuid4())
        ep = {
            "uuid": ep_uuid,
            "content": text,
            "processed": True,   # immediately processed in mock
            "created_at": _now(),
            "source": "text",
        }
        _episodes[ep_uuid] = {**ep, "graph_id": graph_id}
        result_episodes.append(ep)

    # Trigger entity extraction in background once we have enough text
    all_text = "\n".join(_graphs[graph_id].get("text_chunks", []))
    if len(all_text) > 50 and not _nodes.get(graph_id):
        def _extract():
            _nodes[graph_id] = _build_nodes_for_graph(graph_id)
            print(f"[mock-zep] extracted {len(_nodes[graph_id])} entities for graph {graph_id}")
        threading.Thread(target=_extract, daemon=True).start()

    print(f"[mock-zep] graph-batch graph_id={graph_id} episodes={len(result_episodes)}")
    return jsonify(result_episodes)


# Episode get (processed status)
@app.route("/api/v2/graph/episodes/<ep_uuid>", methods=["GET"])
def episode_get(ep_uuid: str):
    ep = _episodes.get(ep_uuid, {})
    return jsonify({
        "uuid": ep_uuid,
        "content": ep.get("content", ""),
        "processed": True,
        "created_at": ep.get("created_at", _now()),
        "source": "text",
    })


@app.route("/api/v2/graph/episodes/<ep_uuid>/mentions", methods=["GET"])
def episode_mentions(ep_uuid: str):
    return jsonify({"mentions": []})


@app.route("/api/v2/graph/episodes/graph/<graph_id>", methods=["GET"])
def episodes_by_graph(graph_id: str):
    eps = [v for v in _episodes.values() if v.get("graph_id") == graph_id]
    return jsonify(eps)


# Node endpoints
@app.route("/api/v2/graph/node/graph/<graph_id>", methods=["GET", "POST"])
def nodes_by_graph(graph_id: str):
    # Wait up to 30s for async extraction to complete
    deadline = time.time() + 30
    while not _nodes.get(graph_id) and time.time() < deadline:
        time.sleep(0.5)

    if not _nodes.get(graph_id):
        _nodes[graph_id] = _build_nodes_for_graph(graph_id)

    nodes = _nodes.get(graph_id, [])
    # SDK sends POST with JSON body; GET uses query params
    body = request.get_json(silent=True) or {}
    limit = int(body.get("limit") or request.args.get("limit") or 100)
    cursor = body.get("uuid_cursor") or request.args.get("uuid_cursor")

    # Simple cursor pagination
    start = 0
    if cursor:
        for i, n in enumerate(nodes):
            if n["uuid"] == cursor:
                start = i + 1
                break
    page = nodes[start:start + limit]
    print(f"[mock-zep] nodes/graph/{graph_id} limit={limit} cursor={cursor} returning={len(page)}")
    return jsonify(page)


@app.route("/api/v2/graph/node/<node_uuid>", methods=["GET"])
def node_get(node_uuid: str):
    for nodes in _nodes.values():
        for n in nodes:
            if n["uuid"] == node_uuid:
                return jsonify(n)
    return jsonify({"uuid": node_uuid, "name": "unknown", "labels": ["Entity"], "summary": "", "attributes": {}, "created_at": _now()})


@app.route("/api/v2/graph/node/<node_uuid>/entity-edges", methods=["GET"])
def node_entity_edges(node_uuid: str):
    return jsonify([])


@app.route("/api/v2/graph/node/<node_uuid>/episodes", methods=["GET"])
def node_episodes(node_uuid: str):
    return jsonify([])


@app.route("/api/v2/graph/node/user/<user_id>", methods=["GET"])
def nodes_by_user(user_id: str):
    return jsonify([])


# Edge endpoints
@app.route("/api/v2/graph/edge/graph/<graph_id>", methods=["GET", "POST"])
def edges_by_graph(graph_id: str):
    return jsonify([])


@app.route("/api/v2/graph/edge/<edge_uuid>", methods=["GET"])
def edge_get(edge_uuid: str):
    return jsonify({"uuid": edge_uuid, "name": "", "fact": "", "created_at": _now()})


@app.route("/api/v2/graph/edge/<edge_uuid>", methods=["DELETE"])
def edge_delete(edge_uuid: str):
    return jsonify({"message": "Edge deleted"})


@app.route("/api/v2/graph/edge/user/<user_id>", methods=["GET"])
def edges_by_user(user_id: str):
    return jsonify([])


# Graph search
@app.route("/api/v2/graph/search", methods=["POST"])
def graph_search():
    return jsonify({"nodes": [], "edges": [], "episodes": []})


# Graph add-fact-triple
@app.route("/api/v2/graph/add-fact-triple", methods=["POST"])
def add_fact_triple():
    return jsonify({"uuid": str(uuid.uuid4()), "message": "Fact triple added"})


# Catch-all for any unmapped endpoint
@app.route("/api/v2/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def catchall(path: str):
    print(f"[mock-zep] UNHANDLED {request.method} /api/v2/{path}")
    return jsonify({"message": "ok", "uuid": str(uuid.uuid4()), "created_at": _now()}), 200


if __name__ == "__main__":
    port = int(os.environ.get("MOCK_ZEP_PORT", 9999))
    print(f"[mock-zep] Starting mock ZEP Cloud server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
