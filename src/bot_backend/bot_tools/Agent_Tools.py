
from agents import function_tool, RunContextWrapper
from typing_extensions import Any
from pathlib import Path
import shutil, json
import socket, ssl, os


from dotenv import load_dotenv, find_dotenv, dotenv_values

load_dotenv(find_dotenv())

SERVER = os.getenv("SERVER")
NICK = os.getenv("NICK")
TOKEN = os.getenv("TOKEN")
PORT    = int(os.getenv("PORT", "6697"))
CHANNEL = os.getenv("CHANNEL", "").strip().lower()

def _send(sock, line: str) -> None:
    sock.sendall((line + "\r\n").encode("utf-8"))

@function_tool
def move_files(
    ctx: RunContextWrapper[Any],
    files: list[str],
    destination: str,
    do_copy: bool = True,
    overwrite: bool = False,
) -> str:
    normalized = [str(Path(p)) for p in files]
    seen, unique = set(), []
    for p in normalized:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    missing = [p for p in unique if not Path(p).is_file()]
    provided_count = len(files)
    unique_count = len(unique)
    valid = [p for p in unique if Path(p).is_file()]
    valid_count = len(valid)
    if not (provided_count == 20 and unique_count == 20 and valid_count == 20):
        return json.dumps({
            "noop": True,
            "reason": "Requires exactly 20 unique, existing files.",
            "provided_count": provided_count,
            "unique_count": unique_count,
            "valid_count": valid_count,
            "missing": missing,
        })
    dest = Path(destination)
    dest.mkdir(parents=True, exist_ok=True)
    op = shutil.copy2 if do_copy else shutil.move
    moved = []
    for path in valid:
        p = Path(path)
        target = dest / p.name
        if not overwrite:
            i = 1
            while target.exists():
                target = dest / f"{p.stem}-{i}{p.suffix}"
                i += 1
        op(str(p), str(target))
        moved.append(str(target))
    return json.dumps({
        "noop": False,
        "count": len(moved),
        "dest": str(dest),
        "moved": moved
    })

def twichchat_grabber():

    raw = socket.create_connection((SERVER, PORT), timeout=None)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED
    ctx.load_default_certs()
    sock = ctx.wrap_socket(raw, server_hostname=SERVER)

    _send(sock, f"PASS {TOKEN}")
    _send(sock, f"NICK {NICK}")
    _send(sock, "CAP REQ :twitch.tv/tags twitch.tv/commands twitch.tv/membership")
    _send(sock, f"JOIN #{CHANNEL}")

    joined, buf = False, ""
    try:
        while True:
            chunk = sock.recv(8192).decode("utf-8", errors="ignore")
            if not chunk:
                raise RuntimeError("Disconnected")
            buf += chunk

            while "\r\n" in buf:
                line, buf = buf.split("\r\n", 1)
                if not line:
                    continue

                if line.startswith("PING"):
                    _send(sock, line.replace("PING", "PONG", 1))
                    continue

                if not joined and (
                    " ROOMSTATE #" in line or " 366 " in line or f" JOIN #{CHANNEL}" in line
                ):
                    joined = True
                    continue

                if joined and " PRIVMSG " in line:
                    # stream messages out
                    yield line
                # ignore everything else
    finally:
        try:
            sock.close()
        except Exception:
            pass
