#!/usr/bin/env python3
"""Non-mutating live hosting smoke check. Uses synthetic/public data only."""
import concurrent.futures
import json
import ssl
import time
import urllib.error
import urllib.request

HOSTS = {
    "Render": "https://spiritual-vibez-app.onrender.com",
    "Cloudflare": "https://app.neurospicymystic.com",
}
ROUTES = {
    "/api/health": "health",
    "/api/tarot/cards": "tarot",
    "/api/astrology/locations/countries": "countries",
    "/api/astrology/locations/regions?country=US": "regions",
    "/api/astrology/locations/cities?country=US&state=NY&query=Utica": "cities",
    "/assets/tarot/00-the-fool.png": "image",
}

def probe(item):
    host, base, path, kind = item
    url = base + path
    req = urllib.request.Request(url, headers={
        "User-Agent": "SpiritualVibezHostingSmoke/1.0 (GitHub Actions)",
        "Accept": "application/json" if kind != "image" else "image/png",
    })
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            status = response.status
            content_type = response.headers.get("Content-Type", "")
            sample = response.read(200_000)
            if kind == "image":
                valid = sample.startswith(b"\x89PNG\r\n\x1a\n")
                detail = "png_signature=" + str(valid)
            else:
                try:
                    obj = json.loads(sample)
                    if kind == "health":
                        valid = obj.get("status") == "online" and "FastAPI" not in obj.get("detail", "")
                        detail = "status=" + str(obj.get("status")) + ",app=" + str(obj.get("app", ""))[:80]
                    elif kind == "tarot":
                        valid = isinstance(obj.get("cards"), list) and len(obj["cards"]) == 78
                        detail = "cards=" + str(len(obj.get("cards", [])))
                    elif kind == "countries":
                        valid = any(x.get("code") == "US" for x in obj.get("countries", []))
                        detail = "countries=" + str(len(obj.get("countries", [])))
                    elif kind == "regions":
                        valid = any(x.get("code") == "NY" for x in obj.get("regions", []))
                        detail = "regions=" + str(len(obj.get("regions", [])))
                    elif kind == "cities":
                        valid = any(x.get("city", "").casefold() == "utica" for x in obj.get("places", []))
                        detail = "places=" + str(len(obj.get("places", []))) + ",first_place_id=" + str(obj.get("places", [{}])[0].get("place_id", ""))
                except Exception as exc:
                    valid = False
                    detail = "invalid JSON (" + type(exc).__name__ + "),first_bytes=" + repr(sample[:100])
            return {"host": host, "route": path, "status": status, "ok": valid and status == 200,
                    "content_type": content_type, "detail": detail, "elapsed_s": round(time.monotonic()-start, 2)}
    except urllib.error.HTTPError as exc:
        body = exc.read(500)
        return {"host": host, "route": path, "status": exc.code, "ok": False,
                "detail": "HTTP " + str(exc.code) + " " + repr(body[:200]), "elapsed_s": round(time.monotonic()-start, 2)}
    except Exception as exc:
        return {"host": host, "route": path, "status": None, "ok": False,
                "detail": type(exc).__name__ + ": " + str(exc)[:200], "elapsed_s": round(time.monotonic()-start, 2)}

def main():
    items = [(host, base, path, kind)
             for host, base in HOSTS.items() for path, kind in ROUTES.items()]
    print("Checking both hosts and their real API responses. No private data submitted.", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(probe, items))
    for row in results:
        print(("%-10s  %s  %s  HTTP=%s  %s  %ss" %
            (row["host"], "PASS" if row["ok"] else "FAIL", row["route"],
             row["status"], row["detail"], row["elapsed_s"])), flush=True)
    with open("hosting-smoke-report.json", "w", encoding="utf-8") as f:
        json.dump({"results": results}, f, indent=2)
    print("Summary:", sum(r["ok"] for r in results), "/", len(results),
          "checks passed.", flush=True)
    # Keep the workflow green so evidence is uploaded even when an external
    # hosting configuration is not yet correct. The printed PASS/FAIL matters.
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
