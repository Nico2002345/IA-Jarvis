import datetime
import ipaddress
import os

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

CERTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".certs")
CERT_PATH = os.path.join(CERTS_DIR, "cert.pem")
KEY_PATH = os.path.join(CERTS_DIR, "key.pem")


def _cert_covers_ip(ip: str) -> bool:
    if not (os.path.exists(CERT_PATH) and os.path.exists(KEY_PATH)):
        return False
    with open(CERT_PATH, "rb") as f:
        cert = x509.load_pem_x509_certificate(f.read())
    if cert.not_valid_after_utc <= datetime.datetime.now(datetime.timezone.utc):
        return False
    try:
        san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
        ips = {str(v) for v in san.get_values_for_type(x509.IPAddress)}
    except x509.ExtensionNotFound:
        ips = set()
    return ip in ips


def _generate_cert(ip: str):
    os.makedirs(CERTS_DIR, exist_ok=True)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "JARVIS Local")])
    alt_names = [
        x509.DNSName("localhost"),
        x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
    ]
    try:
        alt_names.append(x509.IPAddress(ipaddress.ip_address(ip)))
    except ValueError:
        pass
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(now + datetime.timedelta(days=3650))
        .add_extension(x509.SubjectAlternativeName(alt_names), critical=False)
        .sign(key, hashes.SHA256())
    )
    with open(KEY_PATH, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
    with open(CERT_PATH, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))


def ensure_cert(ip: str) -> tuple[str, str]:
    """Genera (si hace falta) un certificado autofirmado que cubra `ip` y devuelve (cert_path, key_path)."""
    if not _cert_covers_ip(ip):
        _generate_cert(ip)
    return CERT_PATH, KEY_PATH
