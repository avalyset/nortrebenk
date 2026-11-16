#!/usr/bin/env python3
"""Mellomtjener for agentkjøringer (NTB-0006).

Står på det interne Docker-nettet til agenten og på et nett med rute ut. Videresender bare forespørsler med sti under
/v1/ til https://api.anthropic.com, med strømming. Nøkkelen leses fra miljøvariabelen NTB_UPSTREAM_KEY og settes som
x-api-key; innkommende x-api-key og authorization fjernes. Forespørsler der verktøylista har et tjenersideverktøy for
nettsøk eller netthenting (typenavn som begynner med web_search_ eller web_fetch_), avvises med 400.

Loggen (NTB_LOGG, standard /logg/mellomtjener.log) har én linje per forespørsel: UTC-tid, metode, sti, status og
om forespørselen ble avvist. Innhold og hoder logges aldri.

    NTB_UPSTREAM_KEY=... python3 mellomtjener.py   # lytter på 0.0.0.0:8080
"""
import gzip
import http.client
import http.server
import json
import os
import socketserver
import ssl
import threading
import time
import zlib

OPPSTRØMS = "api.anthropic.com"
PORT = int(os.environ.get("NTB_PORT", "8080"))
LOGG = os.environ.get("NTB_LOGG", "/logg/mellomtjener.log")
NETTVERKTØY = ("web_search_", "web_fetch_")
FJERN_INN = {"host", "x-api-key", "authorization", "content-length", "connection", "proxy-connection",
             "keep-alive", "transfer-encoding", "upgrade", "te"}
FJERN_UT = {"transfer-encoding", "connection", "keep-alive", "content-length"}
_lås = threading.Lock()


def logg(metode, sti, status, avvist):
    linje = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\t{metode}\t{sti.split('?')[0]}\t{status}\t{avvist}\n"
    with _lås, open(LOGG, "a", encoding="utf-8") as f:
        f.write(linje)


def nettverktøy(kropp, koding):
    """Returnerer typenavnet på første nettverktøy i verktøylista, ellers None."""
    if not kropp:
        return None
    try:
        if koding == "gzip":
            kropp = gzip.decompress(kropp)
        elif koding == "deflate":
            kropp = zlib.decompress(kropp)
        data = json.loads(kropp)
    except Exception:  # noqa: BLE001
        return None
    for v in data.get("tools") or []:
        t = v.get("type", "") if isinstance(v, dict) else ""
        if t.startswith(NETTVERKTØY):
            return t
    return None


class Behandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):  # ingen standardlogg (den kan ta med forespørselslinjen)
        pass

    def _svar(self, status, melding, avvist):
        kropp = json.dumps({"type": "error", "error": {"type": "invalid_request_error", "message": melding}}).encode()
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(kropp)))
        self.end_headers()
        self.wfile.write(kropp)
        logg(self.command, self.path, status, avvist)

    def _videresend(self):
        if not self.path.startswith("/v1/"):
            return self._svar(403, "nortrebenk: bare /v1/ videresendes", "ja: sti")
        lengde = int(self.headers.get("content-length") or 0)
        kropp = self.rfile.read(lengde) if lengde else b""
        t = nettverktøy(kropp, (self.headers.get("content-encoding") or "").lower())
        if t:
            return self._svar(400, f"nortrebenk: tjenersideverktøyet {t} er ikke tillatt", f"ja: {t}")
        hoder = {k: v for k, v in self.headers.items() if k.lower() not in FJERN_INN}
        hoder["x-api-key"] = os.environ["NTB_UPSTREAM_KEY"]
        hoder["host"] = OPPSTRØMS
        if kropp:
            hoder["content-length"] = str(len(kropp))
        k = http.client.HTTPSConnection(OPPSTRØMS, 443, timeout=900, context=ssl.create_default_context())
        try:
            k.request(self.command, self.path, body=kropp or None, headers=hoder)
            r = k.getresponse()
            self.send_response(r.status)
            for n, v in r.getheaders():
                if n.lower() not in FJERN_UT:
                    self.send_header(n, v)
            self.send_header("transfer-encoding", "chunked")
            self.end_headers()
            while True:
                bit = r.read1(65536)
                if not bit:
                    break
                self.wfile.write(f"{len(bit):x}\r\n".encode() + bit + b"\r\n")
                self.wfile.flush()
            self.wfile.write(b"0\r\n\r\n")
            logg(self.command, self.path, r.status, "nei")
        except Exception as e:  # noqa: BLE001
            logg(self.command, self.path, 502, f"nei: oppstrømsfeil {type(e).__name__}")
            try:
                self._svar(502, "nortrebenk: oppstrømsfeil", "nei")
            except Exception:  # noqa: BLE001
                pass
        finally:
            k.close()

    do_POST = do_GET = do_PUT = do_DELETE = do_PATCH = _videresend

    def do_HEAD(self):
        self._svar(403, "nortrebenk: HEAD videresendes ikke", "ja: metode")


class Tjener(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


if __name__ == "__main__":
    if not os.environ.get("NTB_UPSTREAM_KEY"):
        raise SystemExit("NTB_UPSTREAM_KEY mangler")
    os.makedirs(os.path.dirname(LOGG), exist_ok=True)
    Tjener(("0.0.0.0", PORT), Behandler).serve_forever()
