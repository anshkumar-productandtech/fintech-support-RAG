# Create the tables the web app uses for its rate limits. Safe to run more than once.
# Run it with:  python scripts/create_usage_tables.py
#
# usage_daily:   answers started on each UTC day, for DAILY_ANSWER_CAP.
# usage_visitor: questions per visitor per 10-minute window. ip_hash is
#                sha256(IP_HASH_SALT + ip); raw IPs are never stored.
# Row level security is on with no policies, like the chunks table, so Supabase's
# public API can't read or write them. The app connects as the table owner.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from answer import _connect  # noqa: E402

with _connect() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usage_daily (
            day     date PRIMARY KEY,
            answers int  NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usage_visitor (
            ip_hash      text        NOT NULL,
            window_start timestamptz NOT NULL,
            count        int         NOT NULL,
            PRIMARY KEY (ip_hash, window_start)
        )
    """)
    # For deleting old rows: window_start isn't the first column of the primary key.
    conn.execute(
        "CREATE INDEX IF NOT EXISTS usage_visitor_window_start ON usage_visitor (window_start)"
    )
    conn.execute("ALTER TABLE usage_daily ENABLE ROW LEVEL SECURITY")
    conn.execute("ALTER TABLE usage_visitor ENABLE ROW LEVEL SECURITY")

print("usage_daily and usage_visitor are ready (row level security on).")
