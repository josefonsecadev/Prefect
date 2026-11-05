"""Prepara TLS e hash SQL localmente, somente na instalação ou troca de senha."""
import hashlib
import os
from pathlib import Path
import re
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def main():
    root = Path(__file__).resolve().parents[1]
    load_dotenv(root / '.env')
    user = os.environ.get('TRINO_USER', 'analista')
    password = os.environ.get('TRINO_PASSWORD', '')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', user) or not password or password.startswith('change-me'):
        raise RuntimeError('Configure TRINO_USER e TRINO_PASSWORD no .env')
    folder = root / '.prefect/runtime/trino'
    folder.mkdir(parents=True, exist_ok=True)
    salt = os.urandom(16)
    # O autenticador de arquivos do Trino 484 verifica PBKDF2WithHmacSHA1.
    digest = hashlib.pbkdf2_hmac('sha1', password.encode(), salt, 210000, dklen=32)
    target = folder / 'password.db'
    target.write_text(f'{user}:210000:{salt.hex()}:{digest.hex()}\n', encoding='utf-8')
    target.chmod(0o600)
    target = folder / 'server.pem'
    if not target.exists():
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'localhost')])
        now = datetime.now(timezone.utc)
        cert = (x509.CertificateBuilder().subject_name(subject).issuer_name(subject)
                .public_key(key.public_key()).serial_number(x509.random_serial_number())
                .not_valid_before(now - timedelta(minutes=5)).not_valid_after(now + timedelta(days=365))
                .add_extension(x509.SubjectAlternativeName([
                    x509.DNSName('localhost'), x509.DNSName('trino')]), critical=False)
                .sign(key, hashes.SHA256()))
        target.write_bytes(key.private_bytes(serialization.Encoding.PEM,
                           serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
                           + cert.public_bytes(serialization.Encoding.PEM))
        target.chmod(0o600)
    print('TLS local preservado/preparado e hash SQL atualizado; nenhum segredo impresso.')


if __name__ == '__main__':
    main()
