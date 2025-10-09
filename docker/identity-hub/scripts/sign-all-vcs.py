#!/usr/bin/env python3
import json, time, base64, subprocess, tempfile
from pathlib import Path
import shutil
import sys

# --- resolve paths relative to this script, not CWD ---
SCRIPT_DIR = Path(__file__).resolve().parent
IH_DIR = SCRIPT_DIR.parent              # .../identity-hub
CERTS_DIR = IH_DIR / "certs"
CREDS_DIR = IH_DIR / "credentials"

ISSUER_DID = "did:web:dataspace-issuer"
SUBJECTS = [
    ("provider", "did:web:provider-ih%3A7093:bob"),
    ("consumer", "did:web:consumer-ih%3A7083:alice"),
    ("federated-catalog", "did:web:fc-ih%3A7103:piotr"),
]
KINDS = ["membership", "dataprocessor"]

PRIV_PEM = CERTS_DIR / "issuer_private.pem"

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def sign_with_openssl(payload_bytes: bytes) -> bytes:
    """Return Ed25519 signature using system openssl (expects PKCS#8 Ed25519 key)."""
    if not shutil.which("openssl"):
        raise RuntimeError("openssl not found in PATH")

    # Work around 'unable to determine file size for oneshot operation'
    with tempfile.NamedTemporaryFile(prefix="ed25519_payload_", delete=True) as tf:
        tf.write(payload_bytes)
        tf.flush()
        p = subprocess.run(
            ["openssl", "pkeyutl", "-sign", "-inkey", str(PRIV_PEM), "-rawin", "-in", tf.name],
            capture_output=True, text=False
        )
    if p.returncode != 0:
        stderr = (p.stderr or b"").decode(errors="replace").strip()
        raise RuntimeError(f"openssl pkeyutl failed (rc={p.returncode})\n{stderr}")
    return p.stdout

def make_jwt(vc, issuer, subject):
    header = {"alg": "EdDSA", "typ": "JWT", "kid": f"{issuer}#key-1"}
    now = int(time.time())
    claims = {"iss": issuer, "sub": subject, "aud": subject, "iat": now, "vc": vc}

    header_b64 = b64url(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = b64url(json.dumps(claims, separators=(",", ":")).encode())
    signing_input = f"{header_b64}.{payload_b64}".encode()

    signature = sign_with_openssl(signing_input)
    sig_b64 = b64url(signature)
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def update_credential(cred_path: Path, jwt: str):
    data = json.loads(cred_path.read_text(encoding="utf-8"))
    data["verifiableCredential"]["rawVc"] = jwt
    cred_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def main() -> int:
    if not PRIV_PEM.exists():
        print(f"Missing private key: {PRIV_PEM}", file=sys.stderr)
        return 1

    for folder, subject in SUBJECTS:
        for kind in KINDS:
            vc_path = CREDS_DIR / folder / f"{kind}_vc.json"
            cred_path = CREDS_DIR / folder / f"{kind}-credential.json"
            if not vc_path.exists() or not cred_path.exists():
                continue
            vc = json.loads(vc_path.read_text(encoding="utf-8"))
            token = make_jwt(vc, ISSUER_DID, subject)
            update_credential(cred_path, token)
            print(f"Signed {folder}/{kind}")
    print("✅ done")
    return 0

if __name__ == "__main__":
    sys.exit(main())
