"""Dia 14 - 01 inspector stdio manual (JSON-RPC via subprocess)."""
import json
import subprocess
import sys

SERVER = [sys.executable, "dia14/server_demo.py"]


def rpc(proc, payload):
    assert proc.stdin and proc.stdout
    proc.stdin.write(json.dumps(payload) + "\n")
    proc.stdin.flush()
    return json.loads(proc.stdout.readline())


def main():
    proc = subprocess.Popen(
        SERVER,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    init = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "inspector-dia14", "version": "0.1"},
        },
    }
    print("-> initialize:", json.dumps(init))
    print("<- ", rpc(proc, init))

    notif = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    assert proc.stdin
    proc.stdin.write(json.dumps(notif) + "\n")
    proc.stdin.flush()
    print("-> notifications/initialized (sem id, sem resposta)")

    list_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    print("-> tools/list:", list_req)
    print("<- ", rpc(proc, list_req))

    call_req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "somar", "arguments": {"a": 40, "b": 2}},
    }
    print("-> tools/call somar:", call_req)
    print("<- ", rpc(proc, call_req))
    proc.terminate()


if __name__ == "__main__":
    main()
