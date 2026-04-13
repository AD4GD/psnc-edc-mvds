"""add keycloak_id to participant

Revision ID: a1b2c3d4e5f6
Revises: b59521dc1cb9
Create Date: 2026-04-10 00:00:00.000000

Adds a nullable keycloak_id column (the Keycloak 'sub' UUID) to the participant
table so we can look up participants by their Keycloak identity without relying
on a custom token attribute/mapper.

The backfill section attempts to populate keycloak_id for existing rows by
matching participant.email against Keycloak users via the Admin REST API.
It is best-effort: rows that cannot be matched are left NULL and can be
populated later by logging in (the application sets keycloak_id on first use
if it is missing).
"""

from alembic import op
import sqlalchemy as sa
import os
import httpx


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "b59521dc1cb9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add the column (nullable so existing rows are not broken)
    op.add_column(
        "participant",
        sa.Column("keycloak_id", sa.String(255), nullable=True),
    )
    op.create_unique_constraint("uq_participant_keycloak_id", "participant", ["keycloak_id"])
    op.create_index("ix_participant_keycloak_id", "participant", ["keycloak_id"])

    # 2. Best-effort backfill via Keycloak Admin REST API
    _backfill_keycloak_ids()


def downgrade() -> None:
    op.drop_index("ix_participant_keycloak_id", table_name="participant")
    op.drop_constraint("uq_participant_keycloak_id", "participant", type_="unique")
    op.drop_column("participant", "keycloak_id")


# ---------------------------------------------------------------------------
# Backfill helpers
# ---------------------------------------------------------------------------

def _get_admin_token(base_url: str, realm: str, username: str, password: str) -> str:
    r = httpx.post(
        f"{base_url}/realms/master/protocol/openid-connect/token",
        data={
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": username,
            "password": password,
        },
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def _backfill_keycloak_ids() -> None:
    keycloak_url = os.getenv("KEYCLOAK_SERVER_URL", "").rstrip("/")
    realm = os.getenv("KEYCLOAK_REALM", "dataspace")
    admin_user = os.getenv("KEYCLOAK_ADMIN_USERNAME", "admin")
    admin_pass = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "")

    if not keycloak_url or not admin_pass:
        print(
            "[migration] KEYCLOAK_SERVER_URL or KEYCLOAK_ADMIN_PASSWORD not set – "
            "skipping keycloak_id backfill. Run manually or re-login users to populate."
        )
        return

    try:
        token = _get_admin_token(keycloak_url, realm, admin_user, admin_pass)
    except Exception as exc:
        print(f"[migration] Could not obtain Keycloak admin token – skipping backfill: {exc}")
        return

    headers = {"Authorization": f"Bearer {token}"}
    conn = op.get_bind()

    rows = conn.execute(
        sa.text("SELECT id, email FROM participant WHERE keycloak_id IS NULL")
    ).fetchall()

    updated = 0
    for row in rows:
        participant_id, email = row[0], row[1]
        try:
            r = httpx.get(
                f"{keycloak_url}/admin/realms/{realm}/users",
                params={"email": email, "exact": "true"},
                headers=headers,
                timeout=10,
            )
            r.raise_for_status()
            users = r.json()
            if users:
                kc_id = users[0]["id"]
                conn.execute(
                    sa.text("UPDATE participant SET keycloak_id = :kc_id WHERE id = :pid"),
                    {"kc_id": kc_id, "pid": str(participant_id)},
                )
                updated += 1
        except Exception as exc:
            print(f"[migration] Could not resolve keycloak_id for {email}: {exc}")

    print(f"[migration] keycloak_id backfill complete: {updated}/{len(rows)} participants updated.")
