"""Simple FTP honeypot service for Venus Trap."""

from __future__ import annotations

import logging
import socketserver
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
FTP_LOG_FILE = LOG_DIR / "ftp.log"

ftp_logger = logging.getLogger("ftp_logger")
ftp_logger.setLevel(logging.INFO)


def _configure_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(FTP_LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=2)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    if not ftp_logger.handlers:
        ftp_logger.addHandler(handler)


class FTPHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        client_ip, client_port = self.client_address
        ftp_logger.info("FTP client connected from %s:%s", client_ip, client_port)
        self.username = ""

        self._reply("220 Venus Trap FTP ready")

        while True:
            line = self.rfile.readline()
            if not line:
                break

            command_line = line.decode("utf-8", errors="ignore").strip()
            if not command_line:
                continue

            ftp_logger.info("FTP command from %s:%s | %s", client_ip, client_port, command_line)
            command, *args = command_line.split(" ", 1)
            argument = args[0] if args else ""

            command_upper = command.upper()

            if command_upper == "USER":
                self.username = argument
                self._reply("331 Username ok, need password")
            elif command_upper == "PASS":
                ftp_logger.info("FTP login attempt from %s | username=%s password=%s", client_ip, self.username, argument)
                self._reply("230 Login successful")
            elif command_upper == "SYST":
                self._reply("215 UNIX Type: L8")
            elif command_upper == "PWD":
                self._reply('257 "/" is current directory')
            elif command_upper == "CWD":
                self._reply("250 Directory changed")
            elif command_upper == "LIST":
                self._reply("150 Here comes the directory listing")
                self._reply("drwxr-xr-x 1 root root 4096 Jan 01 00:00 pub")
                self._reply("-rw-r--r-- 1 root root  128 Jan 01 00:00 readme.txt")
                self._reply("226 Directory send OK")
            elif command_upper == "RETR":
                self._reply("150 Opening BINARY mode data connection")
                self._reply("Fake content from honeypot")
                self._reply("226 Transfer complete")
            elif command_upper == "STOR":
                self._reply("150 Ok to send data")
                self._reply("226 File received")
            elif command_upper in {"TYPE", "PASV", "PORT"}:
                self._reply("200 Command okay")
            elif command_upper == "QUIT":
                self._reply("221 Goodbye")
                break
            else:
                self._reply("502 Command not implemented")

        ftp_logger.info("FTP client disconnected from %s:%s", client_ip, client_port)

    def _reply(self, message: str) -> None:
        self.wfile.write(f"{message}\r\n".encode("utf-8"))


class ThreadedFTPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


def run_server(host: str = "0.0.0.0", port: int = 2121) -> None:
    _configure_logging()
    with ThreadedFTPServer((host, port), FTPHandler) as server:
        ftp_logger.info("FTP honeypot started on %s:%s", host, port)
        server.serve_forever()


if __name__ == "__main__":
    run_server()
