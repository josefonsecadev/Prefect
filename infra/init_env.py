"""Cria segredos locais para uma instalação nova, sem mostrá-los no terminal."""
import argparse
from pathlib import Path
import secrets
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replace", action="store_true", help="Preservar .env anterior em .prefect e gerar um novo")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    target = root / ".env"
    if target.exists() and not args.replace:
        raise SystemExit(".env já existe; use --replace apenas para instalação nova")
    runtime = root / ".prefect" / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    if target.exists():
        backup = runtime / ("previous-env-" + secrets.token_hex(4))
        shutil.copy2(target, backup)
        backup.chmod(0o600)
    values = {}
    for line in (root / ".env.example").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            values[key] = secrets.token_hex(24) if value.startswith("change-me") else value
    # Chaves do backend local; os consumidores externos só recebem senha SQL.
    values["S3_ACCESS_KEY"] = values["RUSTFS_ACCESS_KEY"]
    values["S3_SECRET_KEY"] = values["RUSTFS_SECRET_KEY"]
    target.write_text("".join(f"{key}={value}\n" for key, value in values.items()), encoding="utf-8")
    target.chmod(0o600)
    print(".env local criado com segredos aleatórios; nenhum segredo impresso.")


if __name__ == "__main__":
    main()
