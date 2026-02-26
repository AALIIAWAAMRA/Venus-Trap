"""Main launcher for Venus Trap honeypot services."""

from __future__ import annotations

import argparse
import threading

from binary_collection_server import run_server as run_binary_collector
from ftp import run_server as run_ftp
from ssh import main as run_ssh
from web import start_honeypot as run_http
from XMPP_server import run_server as run_xmpp


def start_service_thread(name: str, target, *args) -> threading.Thread:
    thread = threading.Thread(target=target, args=args, daemon=True, name=name)
    thread.start()
    print(f"[*] {name} started")
    return thread


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VENUS TRAP multi-service honeypot")

    parser.add_argument("-a", "--address", type=str, default="127.0.0.1")
    parser.add_argument("-u", "--username", type=str, default="hameid")
    parser.add_argument("-pw", "--password", type=str, default="123456")

    parser.add_argument("--ssh-port", type=int, default=2222)
    parser.add_argument("--http-port", type=int, default=8080)
    parser.add_argument("--ftp-port", type=int, default=2121)
    parser.add_argument("--xmpp-port", type=int, default=5222)
    parser.add_argument("--collector-port", type=int, default=9090)

    parser.add_argument("-s", "--ssh", action="store_true", help="Enable SSH honeypot")
    parser.add_argument("-w", "--http", action="store_true", help="Enable HTTP honeypot")
    parser.add_argument("-f", "--ftp", action="store_true", help="Enable FTP honeypot")
    parser.add_argument("-x", "--xmpp", action="store_true", help="Enable XMPP listener")
    parser.add_argument("-b", "--binary", action="store_true", help="Enable binary collection service")
    parser.add_argument("--all", action="store_true", help="Run all services")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    services_enabled = args.all or any([args.ssh, args.http, args.ftp, args.xmpp, args.binary])

    if not services_enabled:
        print("[-] No service selected. Use --all or one/more flags: --ssh --http --ftp --xmpp --binary")
        return

    threads = []

    if args.all or args.ssh:
        threads.append(start_service_thread("SSH Honeypot", run_ssh, args.address, args.ssh_port, args.username, args.password))

    if args.all or args.http:
        threads.append(start_service_thread("HTTP Honeypot", run_http, args.http_port, args.username, args.password))

    if args.all or args.ftp:
        threads.append(start_service_thread("FTP Honeypot", run_ftp, args.address, args.ftp_port))

    if args.all or args.xmpp:
        threads.append(start_service_thread("XMPP Telemetry", run_xmpp, args.address, args.xmpp_port))

    if args.all or args.binary:
        threads.append(start_service_thread("Binary Collection", run_binary_collector, args.address, args.collector_port))

    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\n[!] Shutdown requested. Exiting Venus Trap...")


if __name__ == "__main__":
    main()
