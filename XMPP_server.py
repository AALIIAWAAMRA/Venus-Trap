"""A lightweight XMPP-like telemetry listener for Venus Trap.

This is intentionally minimal and designed to capture attacker chat-like bot traffic.
"""

from __future__ import annotations

import logging
import socketserver
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "xmpp.log"

xmpp_logger = logging.getLogger("xmpp_logger")
xmpp_logger.setLevel(logging.INFO)


def _configure_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=2)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    if not xmpp_logger.handlers:
        xmpp_logger.addHandler(handler)


class XMPPRequestHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        client_ip, client_port = self.client_address
        xmpp_logger.info("XMPP client connected from %s:%s", client_ip, client_port)

        self.wfile.write(b"<stream:stream from='venus-trap' id='1'>\n")

        while True:
            line = self.rfile.readline()
            if not line:
                break

            payload = line.decode("utf-8", errors="ignore").strip()
            if not payload:
                continue

            xmpp_logger.info("stanza from %s:%s | %s", client_ip, client_port, payload)

            if "</stream:stream>" in payload:
                self.wfile.write(b"</stream:stream>\n")
                break

            self.wfile.write(b"<message from='venus-trap'>received</message>\n")

        xmpp_logger.info("XMPP client disconnected from %s:%s", client_ip, client_port)


class ThreadedXMPPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


def run_server(host: str = "0.0.0.0", port: int = 5222) -> None:
    _configure_logging()
    with ThreadedXMPPServer((host, port), XMPPRequestHandler) as server:
        xmpp_logger.info("XMPP telemetry server started on %s:%s", host, port)
        server.serve_forever()


if __name__ == "__main__":
    run_server()
