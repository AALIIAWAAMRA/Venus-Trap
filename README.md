# VENUS TRAP

**VENUS TRAP** is a multi-service honeypot lab that combines:
- High-interaction style behavior (interactive fake SSH shell).
- Low-interaction deception services (HTTP login trap, FTP trap, XMPP-like telemetry listener).
- A binary collection backend to store suspicious uploaded samples.

---

## Architecture

The project includes these modules:

- `ssh.py` → SSH honeypot with credential and command logging.
- `web.py` → HTTP login honeypot (Flask).
- `ftp.py` → FTP honeypot command listener.
- `XMPP_server.py` → XMPP-like bot-chat telemetry capture.
- `binary_collection_server.py` → sample upload and hash/metadata storage.
- `venus_trap.py` → unified launcher to run one service or all services together.
- `exploit.py` → simulator that sends traffic to all services for testing.

---

## Main workflow logic

1. Attacker/bot connects to one of the exposed honeypot services.
2. Service accepts and logs behavior (credentials, commands, stanzas, requests).
3. Suspicious file can be submitted to binary collector endpoint.
4. Collector stores sample + hashes + metadata for investigation.
5. Logs are rotated under `logs/` for incident analysis.

---

## Image gallery placeholders

> The sections below reserve **8 images** exactly as requested.

### 1) Architecture + Main Logic
![Architecture and main logic](docs/images/01-architecture-main-logic.png)

### 2) Action (runtime behavior)
![Action screenshot](docs/images/02-action.png)

### 3) Source Code (part 1)
![Source code screenshot 1](docs/images/03-source-code-1.png)

### 4) Source Code (part 2)
![Source code screenshot 2](docs/images/04-source-code-2.png)

### 5) Logs
![Logs screenshot](docs/images/05-logs.png)

### 6) Web Honeypot (login page)
![Web honeypot screenshot 1](docs/images/06-web-honeypot-login.png)

### 7) Web Honeypot (submitted credentials)
![Web honeypot screenshot 2](docs/images/07-web-honeypot-submit.png)

### 8) Web Honeypot (additional flow)
![Web honeypot screenshot 3](docs/images/08-web-honeypot-extra.png)

---

## Quick start

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run all services together
```bash
python venus_trap.py --all -a 127.0.0.1 -u hameid -pw 123456
```

Default ports:
- SSH: `2222`
- HTTP: `8080`
- FTP: `2121`
- XMPP: `5222`
- Binary collector: `9090`

### Run simulator traffic
```bash
python exploit.py --host 127.0.0.1 --http-port 8080 --ftp-port 2121 --xmpp-port 5222 --collector-port 9090
```

---

## Binary collection API

### POST `/submit`
Upload a file with multipart form-data key `sample`.

Optional fields:
- `reported_by`

Returns:
- Stored metadata including `sha256`, `md5`, `size`, `source_ip`, and filename.

---

## Logs and artifacts

- `logs/ssh.log` → SSH auth/session events
- `logs/cmd_ssh.log` → SSH shell commands
- `logs/web.log` → HTTP credential posts
- `logs/ftp.log` → FTP client commands
- `logs/xmpp.log` → XMPP-like stanzas
- `logs/binary_collection.log` → binary submission events
- `artifacts/binaries/` → stored sample files by SHA-256
- `artifacts/binaries/metadata.jsonl` → one JSON metadata record per line

---

## Legal notice

Use this project **only** for authorized lab/testing environments. Do not deploy this on public networks without explicit permission and proper controls.
