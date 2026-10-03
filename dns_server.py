import json
import socket
import sys

from dnslib import A, DNSRecord, RR

CONFIG_PATH = sys.argv[1] if len(sys.argv) > 1 else "config.json"

with open(CONFIG_PATH) as f:
    config = json.load(f)

UPSTREAM = config["upstream"]
LISTEN = config.get("listen", "0.0.0.0")
PORT = config.get("port", 53)
REWRITES = {name.lower().rstrip("."): ip for name, ip in config.get("rewrites", {}).items()}


def normalize(qname):
    return str(qname).lower().rstrip(".")


def forward(data):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(5)
        sock.sendto(data, (UPSTREAM, 53))
        try:
            return sock.recvfrom(4096)[0]
        except socket.timeout:
            return None


def handle(data):
    request = DNSRecord.parse(data)
    qname = normalize(request.q.qname)
    if qname in REWRITES and request.q.qtype == 1:  # A record
        reply = request.reply()
        reply.add_answer(RR(request.q.qname, 1, rdata=A(REWRITES[qname]), ttl=60))
        return reply.pack()
    return forward(data)


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((LISTEN, PORT))
        print(f"Listening on {LISTEN}:{PORT} udp, forwarding to {UPSTREAM}")
        while True:
            data, addr = sock.recvfrom(4096)
            try:
                response = handle(data)
            except Exception as exc:
                print(f"Error handling query: {exc}")
                continue
            if response:
                sock.sendto(response, addr)


if __name__ == "__main__":
    main()
