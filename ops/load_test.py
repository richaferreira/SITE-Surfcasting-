#!/usr/bin/env python3
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import math
from time import perf_counter
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(0, min(len(ordered) - 1, math.ceil((pct / 100) * len(ordered)) - 1))
    return ordered[rank]


def request_once(url: str, timeout: float) -> tuple[bool, float, int]:
    started = perf_counter()
    status = 0
    try:
        request = Request(url, headers={"User-Agent": "srl-load-smoke/1.0"})
        with urlopen(request, timeout=timeout) as response:
            status = int(response.status)
            response.read(256)
        ok = 200 <= status < 400
    except HTTPError as exc:
        status = int(exc.code)
        ok = False
    except (URLError, TimeoutError, OSError):
        ok = False
    elapsed_ms = (perf_counter() - started) * 1000
    return ok, elapsed_ms, status


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke de carga HTTP sem dependências externas.")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--requests", type=int, default=200)
    parser.add_argument("--concurrency", type=int, default=20)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--p95-ms", type=float, default=1200.0)
    parser.add_argument("--max-error-rate", type=float, default=0.01)
    args = parser.parse_args()

    paths = args.path or ["/health/live", "/api/v1/beaches"]
    targets = [args.base_url.rstrip("/") + (path if path.startswith("/") else "/" + path) for path in paths]
    total = max(1, args.requests)
    concurrency = max(1, min(args.concurrency, total))

    latencies: list[float] = []
    failures: list[dict[str, object]] = []
    started = perf_counter()

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {
            pool.submit(request_once, targets[index % len(targets)], args.timeout): targets[index % len(targets)]
            for index in range(total)
        }
        for future in as_completed(futures):
            target = futures[future]
            ok, latency_ms, status = future.result()
            latencies.append(latency_ms)
            if not ok:
                failures.append({"url": target, "status": status, "latency_ms": round(latency_ms, 2)})

    elapsed = perf_counter() - started
    error_rate = len(failures) / total
    result = {
        "requests": total,
        "concurrency": concurrency,
        "duration_seconds": round(elapsed, 3),
        "throughput_rps": round(total / elapsed, 2) if elapsed else total,
        "errors": len(failures),
        "error_rate": round(error_rate, 4),
        "latency_ms": {
            "p50": round(percentile(latencies, 50), 2),
            "p95": round(percentile(latencies, 95), 2),
            "max": round(max(latencies, default=0.0), 2),
        },
        "targets": targets,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if failures[:5]:
        print("Amostra de falhas:", json.dumps(failures[:5], ensure_ascii=False))

    if error_rate > args.max_error_rate:
        print(f"ERRO: taxa de falhas {error_rate:.2%} acima do limite {args.max_error_rate:.2%}")
        return 2
    p95 = percentile(latencies, 95)
    if p95 > args.p95_ms:
        print(f"ERRO: p95 {p95:.2f} ms acima do limite {args.p95_ms:.2f} ms")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
