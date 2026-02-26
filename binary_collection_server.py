"""Binary collection service for Venus Trap.

Accepts malware sample uploads and stores metadata for later analysis.
"""

from __future__ import annotations

import hashlib
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict

from flask import Flask, jsonify, request

LOG_DIR = Path("logs")
ARTIFACT_DIR = Path("artifacts") / "binaries"
METADATA_FILE = ARTIFACT_DIR / "metadata.jsonl"


collector_logger = logging.getLogger("binary_collector")
collector_logger.setLevel(logging.INFO)


def _configure_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(LOG_DIR / "binary_collection.log", maxBytes=5 * 1024 * 1024, backupCount=2)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    if not collector_logger.handlers:
        collector_logger.addHandler(handler)


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _md5(content: bytes) -> str:
    return hashlib.md5(content).hexdigest()


def _build_metadata(filename: str, content: bytes, source_ip: str, reported_by: str) -> Dict[str, str | int]:
    return {
        "filename": filename,
        "size": len(content),
        "sha256": _sha256(content),
        "md5": _md5(content),
        "source_ip": source_ip,
        "reported_by": reported_by,
    }


def create_app() -> Flask:
    _configure_logging()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    app = Flask(__name__)

    @app.get("/health")
    def health() -> tuple[dict[str, str], int]:
        return {"status": "ok", "service": "binary-collection"}, 200

    @app.post("/submit")
    def submit_binary():
        sample = request.files.get("sample")
        if sample is None or sample.filename == "":
            return jsonify({"error": "missing file field: sample"}), 400

        content = sample.read()
        if not content:
            return jsonify({"error": "empty file"}), 400

        source_ip = request.headers.get("X-Source-IP", request.remote_addr or "unknown")
        reported_by = request.form.get("reported_by", "unknown")

        metadata = _build_metadata(sample.filename, content, source_ip, reported_by)

        sample_path = ARTIFACT_DIR / metadata["sha256"]
        sample_path.write_bytes(content)

        with METADATA_FILE.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(metadata) + "\n")

        collector_logger.info(
            "Sample received | file=%s size=%s sha256=%s source_ip=%s reported_by=%s",
            metadata["filename"],
            metadata["size"],
            metadata["sha256"],
            metadata["source_ip"],
            metadata["reported_by"],
        )

        return jsonify({"message": "sample stored", "metadata": metadata}), 201

    return app


def run_server(host: str = "0.0.0.0", port: int = 9090) -> None:
    app = create_app()
    collector_logger.info("Binary collection service started on %s:%s", host, port)
    app.run(host=host, port=port)


if __name__ == "__main__":
    run_server()
