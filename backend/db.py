"""
Supabase client initialization.

If SUPABASE_URL and SUPABASE_KEY are set in the environment (or .env file),
a real Supabase client is returned.  Otherwise the module returns None and the
backend falls back gracefully to its in-memory store so the application still
works during local development without a Supabase project.
"""

import os
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_supabase_client():
    """Return a Supabase client or None if credentials are not configured."""
    global _client

    if _client is not None:
        return _client

    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip()

    if not url or not key:
        return None

    try:
        from supabase import create_client  # type: ignore

        _client = create_client(url, key)
        return _client
    except Exception as exc:
        print(f"[SUPABASE] Falha ao inicializar cliente: {exc}")
        return None
