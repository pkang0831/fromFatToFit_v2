#!/usr/bin/env python3
"""
Create (or repair) a QA user with email + password in Supabase Auth,
and ensure a matching public.user_profiles row.

Run from repo root or backend (loads backend/.env):

  cd backend && source venv/bin/activate
  set -a && source .env && set +a
  QA_EMAIL='you@example.com' QA_PASSWORD='your-secure-password' \\
    python ../scripts/supabase_create_qa_email_user.py

Requires in environment:
  SUPABASE_URL
  SUPABASE_SERVICE_KEY   (service role — never commit)

Do not commit passwords. Rotate QA_PASSWORD if it was ever shared.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Load backend/.env if present
try:
    from dotenv import load_dotenv

    root = Path(__file__).resolve().parent.parent
    load_dotenv(root / "backend" / ".env")
    load_dotenv(root / "backend" / ".env.local")
except ImportError:
    pass

from supabase import create_client


def main() -> int:
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
    email = (os.environ.get("QA_EMAIL") or os.environ.get("E2E_EMAIL") or "").strip()
    password = os.environ.get("QA_PASSWORD") or os.environ.get("E2E_PASSWORD") or ""

    if not url or not key:
        print("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY.", file=sys.stderr)
        return 1
    if not email or not password:
        print("Missing QA_EMAIL and QA_PASSWORD (or E2E_EMAIL / E2E_PASSWORD).", file=sys.stderr)
        return 1

    client = create_client(url, key)
    user_id: str | None = None

    try:
        res = client.auth.admin.create_user(
            {
                "email": email,
                "password": password,
                "email_confirm": True,
            }
        )
        if res.user:
            user_id = res.user.id
        print(f"Auth: created user id={user_id}")
    except Exception as e:  # noqa: BLE001 — surface API errors to operator
        err = str(e).lower()
        if any(x in err for x in ("already", "registered", "exists", "duplicate")):
            print("Auth: user already exists; signing in to resolve id…")
            try:
                sign = client.auth.sign_in_with_password(
                    {"email": email, "password": password}
                )
                if sign.user:
                    user_id = sign.user.id
                print(f"Auth: ok, user id={user_id}")
            except Exception as e2:  # noqa: BLE001
                print(
                    "Could not create or sign in. Fix password in Supabase Dashboard "
                    "or use a new QA_EMAIL.",
                    file=sys.stderr,
                )
                print(e2, file=sys.stderr)
                return 1
        else:
            print(e, file=sys.stderr)
            return 1

    if not user_id:
        print("Could not determine user id.", file=sys.stderr)
        return 1

    now = datetime.now(timezone.utc).isoformat()
    row = {
        "user_id": user_id,
        "email": email,
        "premium_status": False,
        "onboarding_completed": False,
        "created_at": now,
    }

    try:
        existing = (
            client.table("user_profiles")
            .select("id")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if existing.data:
            client.table("user_profiles").update({"email": email}).eq("user_id", user_id).execute()
            print("Profiles: updated email on existing row.")
        else:
            client.table("user_profiles").insert(row).execute()
            print("Profiles: inserted user_profiles row.")
    except Exception as e:  # noqa: BLE001
        print("Profiles: failed (run docs/sql/SUPABASE_QA_USER_PROFILE.sql if columns differ):", e, file=sys.stderr)
        return 1

    print("Done. Use NEXT_PUBLIC_ENABLE_EMAIL_LOGIN=true and log in at /login.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
