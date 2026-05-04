import sqlite3
import json
from config.settings import GST_DB_PATH

def db_conn():
    conn = sqlite3.connect(GST_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def db_init():
    """Create tables on first run."""
    with db_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS bills (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                month_key TEXT    NOT NULL,
                data_json TEXT    NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sales_overrides (
                month_key TEXT NOT NULL,
                day       INTEGER NOT NULL,
                data_json TEXT NOT NULL,
                PRIMARY KEY (month_key, day)
            );
            CREATE TABLE IF NOT EXISTS suppliers (
                name  TEXT PRIMARY KEY,
                gstin TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS hsn_entries (
                month_key TEXT    NOT NULL,
                data_json TEXT    NOT NULL
            );
            CREATE TABLE IF NOT EXISTS monthly_targets (
                month_key     TEXT PRIMARY KEY,
                target_amount REAL NOT NULL
            );
        """)

def db_load_bills(mk):
    with db_conn() as conn:
        rows = conn.execute("SELECT data_json FROM bills WHERE month_key=? ORDER BY id", (mk,)).fetchall()
    return [json.loads(r["data_json"]) for r in rows]

def db_save_bills(mk, bills_list):
    """Replace all bills for a month."""
    with db_conn() as conn:
        conn.execute("DELETE FROM bills WHERE month_key=?", (mk,))
        for b in bills_list:
            safe = {k: v for k, v in b.items() if not isinstance(v, bytes)}
            for fld in ("inv_date_obj",):
                if fld in safe and hasattr(safe[fld], "isoformat"):
                    safe[fld] = safe[fld].isoformat()
            conn.execute("INSERT INTO bills (month_key, data_json) VALUES (?,?)",
                         (mk, json.dumps(safe)))

def db_load_overrides(mk):
    with db_conn() as conn:
        rows = conn.execute("SELECT day, data_json FROM sales_overrides WHERE month_key=?", (mk,)).fetchall()
    return {r["day"]: json.loads(r["data_json"]) for r in rows}

def db_save_override(mk, day, data):
    with db_conn() as conn:
        conn.execute("INSERT OR REPLACE INTO sales_overrides (month_key, day, data_json) VALUES (?,?,?)",
                     (mk, day, json.dumps(data)))

def db_delete_overrides(mk):
    with db_conn() as conn:
        conn.execute("DELETE FROM sales_overrides WHERE month_key=?", (mk,))

def db_load_target(mk):
    """Return saved target_amount for month_key, or None."""
    with db_conn() as conn:
        row = conn.execute(
            "SELECT target_amount FROM monthly_targets WHERE month_key=?", (mk,)
        ).fetchone()
    return row["target_amount"] if row else None

def db_save_target(mk, amount):
    """Upsert a target_amount for month_key."""
    with db_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO monthly_targets (month_key, target_amount) VALUES (?,?)",
            (mk, amount)
        )

def db_load_suppliers():
    with db_conn() as conn:
        rows = conn.execute("SELECT name, gstin FROM suppliers").fetchall()
    return {r["name"]: r["gstin"] for r in rows}

def db_save_supplier(name, gstin):
    with db_conn() as conn:
        conn.execute("INSERT OR REPLACE INTO suppliers (name, gstin) VALUES (?,?)", (name, gstin))

def db_load_hsn(mk):
    """Load HSN entries for a month from DB. Returns list of dicts."""
    with db_conn() as conn:
        row = conn.execute(
            "SELECT data_json FROM hsn_entries WHERE month_key=?", (mk,)
        ).fetchone()
    return json.loads(row["data_json"]) if row else None

def db_save_hsn(mk, entries):
    """Persist HSN entries for a month."""
    with db_conn() as conn:
        conn.execute("DELETE FROM hsn_entries WHERE month_key=?", (mk,))
        conn.execute(
            "INSERT INTO hsn_entries (month_key, data_json) VALUES (?,?)",
            (mk, json.dumps(entries))
        )
