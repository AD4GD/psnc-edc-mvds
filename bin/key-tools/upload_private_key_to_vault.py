#!/usr/bin/env python3
"""Upload iShare private key PEM content to Hashicorp Vault KV v2 as field `content`."""

import argparse
import os
import sys

import hvac


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload a private key PEM file to Hashicorp Vault (KV v2)."
    )
    parser.add_argument(
        "--vault-url",
        default=os.getenv("VAULT_ADDR"),
        help="Vault URL (default: VAULT_ADDR env var)",
    )
    parser.add_argument(
        "--vault-token",
        default=os.getenv("VAULT_TOKEN"),
        help="Vault token (default: VAULT_TOKEN env var)",
    )
    parser.add_argument(
        "--private-key-file",
        default="ishare-private-key.pem",
        help="Path to private key PEM file",
    )
    parser.add_argument(
        "--secret-path",
        default="ishare-private-key",
        help="KV path under mount point, e.g. ishare-private-key",
    )
    parser.add_argument(
        "--mount-point",
        default="secret",
        help="KV mount point (default: secret)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.vault_url:
        print("ERROR: --vault-url is required or set VAULT_ADDR", file=sys.stderr)
        return 1
    if not args.vault_token:
        print("ERROR: --vault-token is required or set VAULT_TOKEN", file=sys.stderr)
        return 1

    if not os.path.isfile(args.private_key_file):
        print(f"ERROR: File not found: {args.private_key_file}", file=sys.stderr)
        return 1

    with open(args.private_key_file, "r", encoding="utf-8") as f:
        private_key_pem = f.read().strip()

    if "BEGIN PRIVATE KEY" not in private_key_pem:
        print(
            "ERROR: Provided file does not look like a PKCS#8 PEM private key",
            file=sys.stderr,
        )
        return 1

    client = hvac.Client(url=args.vault_url, token=args.vault_token)
    if not client.is_authenticated():
        print("ERROR: Vault authentication failed", file=sys.stderr)
        return 1

    try:
        client.secrets.kv.v2.create_or_update_secret(
            path=args.secret_path,
            mount_point=args.mount_point,
            secret={"content": private_key_pem},
        )
    except hvac.exceptions.InvalidPath as e:
        print(
            f"ERROR: Vault mount '{args.mount_point}' does not exist or is not KV v2.\n"
            f"Enable it first:\n\n"
            f"  curl -X POST -H 'X-Vault-Token: <token>' {args.vault_url}/v1/sys/mounts/{args.mount_point} \\\n"
            f"    -d '{{\"type\":\"kv\",\"options\":{{\"version\":\"2\"}}}}'\n",
            file=sys.stderr,
        )
        return 1

    print("Private key uploaded successfully")
    print(f"  Vault URL:    {args.vault_url}")
    print(f"  Mount point:  {args.mount_point}")
    print(f"  Secret path:  {args.secret_path}")
    print("  Field:        content")
    print("\nVerify:")
    print(
        f"vault kv get -mount={args.mount_point} -field=content {args.secret_path} | head -3"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
