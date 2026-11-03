"""Janela de processamento chamada por um agendador externo ao Prefect."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import threading
import time


ROOT = Path(__file__).resolve().parents[1]


def compose(*args, capture=False, check=True):
    return subprocess.run(["docker", "compose", "--profile", "processing", *args],
                          cwd=ROOT, check=check, text=True,
                          stdout=subprocess.PIPE if capture else None)


def sample_memory(stop, path):
    with path.open("a", encoding="utf-8") as handle:
        while not stop.is_set():
            result = compose("stats", "--no-stream", "--format", "json", capture=True, check=False)
            handle.write(json.dumps({"time": time.time(), "stats": result.stdout,
                                     "exit_code": result.returncode}) + "\n")
            handle.flush()
            stop.wait(5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, required=True)
    args = parser.parse_args()
    runtime = ROOT / ".prefect" / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    lock = runtime / "batch.lock"
    try:
        descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise SystemExit("Batch já está em execução ou deixou trava após interrupção; verificar runs antes de recuperar")
    with os.fdopen(descriptor, "w") as handle:
        handle.write(str(os.getpid()))
    stop = threading.Event()
    monitor = None
    started = False
    try:
        running = compose("ps", "--services", "--status", "running", capture=True).stdout.splitlines()
        if {"prefect-server", "prefect-worker"} & set(running):
            raise RuntimeError("Prefect já está ligado; esta janela não assume serviços iniciados por outro processo")
        if not {"trino", "rustfs", "polaris", "polaris-db"}.issubset(running):
            raise RuntimeError("Inicie a base e o Trino antes do batch")
        monitor = threading.Thread(target=sample_memory, args=(stop, runtime / "memory.jsonl"), daemon=True)
        monitor.start()
        started = True
        compose("up", "-d", "--no-deps", "--wait", "--wait-timeout", "180", "prefect-server")
        compose("up", "-d", "--no-deps", "prefect-worker")
        # Execução síncrona: o desligamento depende da saída, nunca de um horário fixo.
        compose("exec", "-T", "prefect-worker", "python", "-m", "infra.daily_flows", "--year", str(args.year))
    finally:
        try:
            if started:
                check = compose("exec", "-T", "prefect-worker", "python", "-m", "infra.daily_flows", "--check-idle", check=False)
                if check.returncode == 0:
                    compose("stop", "-t", "60", "prefect-worker")
                    compose("stop", "-t", "60", "prefect-server")
                else:
                    raise RuntimeError("Prefect mantido ligado: não foi possível comprovar ausência de runs ativos")
        finally:
            stop.set()
            if monitor:
                monitor.join(timeout=10)
            lock.unlink()


if __name__ == "__main__":
    main()
