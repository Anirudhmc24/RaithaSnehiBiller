import sqlite3
import datetime
from config.settings import DB_PATH

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create tables, auto-migrate old DBs, seed sample data."""
    conn = get_conn()
    c    = conn.cursor()

    # ── Inventory ──────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            qr_code     TEXT    UNIQUE,
            name        TEXT    NOT NULL,
            hsn_code    TEXT    NOT NULL,
            section     TEXT    NOT NULL,
            row_no      TEXT    NOT NULL,
            slot        TEXT    NOT NULL,
            unit        TEXT    DEFAULT 'Kg',
            quantity    REAL    DEFAULT 0,
            mrp         REAL    NOT NULL,
            cost_price  REAL    DEFAULT 0,
            gst_rate    REAL    DEFAULT 0.05
        )
    """)
    # Auto-migrate
    existing = [r[1] for r in c.execute("PRAGMA table_info(inventory)")]
    if "gst_rate" not in existing:
        c.execute("ALTER TABLE inventory ADD COLUMN gst_rate REAL DEFAULT 0.05")
    if "qr_code" not in existing:
        c.execute("ALTER TABLE inventory ADD COLUMN qr_code TEXT")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_inv_qr ON inventory(qr_code) WHERE qr_code IS NOT NULL")

    # ── Invoices ───────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no      TEXT    UNIQUE NOT NULL,
            customer_name   TEXT,
            customer_phone  TEXT,
            customer_gstin  TEXT,
            invoice_date    TEXT    NOT NULL,
            taxable_value   REAL,
            cgst_amount     REAL,
            sgst_amount     REAL,
            total_amount    REAL
        )
    """)

    # ── Invoice Line Items ─────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS invoice_items (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no      TEXT    NOT NULL,
            product_id      INTEGER NOT NULL,
            product_name    TEXT,
            hsn_code        TEXT,
            quantity        REAL,
            unit            TEXT,
            unit_price      REAL,
            gst_rate        REAL,
            taxable_value   REAL,
            cgst_amount     REAL,
            sgst_amount     REAL,
            line_total      REAL,
            FOREIGN KEY (invoice_no) REFERENCES invoices(invoice_no)
        )
    """)
    existing_ii = [r[1] for r in c.execute("PRAGMA table_info(invoice_items)")]
    if "gst_rate" not in existing_ii:
        c.execute("ALTER TABLE invoice_items ADD COLUMN gst_rate REAL DEFAULT 0.05")

    # ── QR Code Registry ────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS qr_registry (
            qr_code         TEXT    PRIMARY KEY,
            product_id      INTEGER,
            product_name    TEXT,
            first_scanned   TEXT,
            scan_count      INTEGER DEFAULT 1,
            FOREIGN KEY (product_id) REFERENCES inventory(id)
        )
    """)

    # Seed sample products
    c.execute("SELECT COUNT(*) FROM inventory")
    if c.fetchone()[0] == 0:
        samples = [
            ("8901030870925","Urea (46% N)",          "31021010","Chemical Section","Row 1","AA","Bag",500, 380, 300,0.05),
            ("8901030870932","DAP (Diammonium Phos)", "31053000","Chemical Section","Row 1","AB","Bag",150,1350,1100,0.05),
            ("8901030870949","MOP (Muriate of Pot)",  "31042010","Chemical Section","Row 2","AA","Bag",200, 900, 750,0.05),
            ("8901030870956","NPK 10:26:26",          "31059010","Chemical Section","Row 2","AB","Bag",180,1200, 980,0.05),
            ("8901030870963","Gypsum",                "25201000","Mineral Section", "Row 3","BA","Bag",300, 250, 180,0.05),
            ("8901030870970","Zinc Sulphate",         "28330300","Micro-Nutrient",  "Row 3","BB","Kg",  85,  85,  65,0.18),
            ("8901030870987","Boron (Borax)",         "28402000","Micro-Nutrient",  "Row 4","CA","Kg", 120, 120,  95,0.18),
            ("8901030870994","Ferrous Sulphate",      "28332910","Micro-Nutrient",  "Row 4","CB","Kg",  60,  60,  45,0.18),
            ("8901030871007","Organic Compost",       "31010010","Organic Section", "Row 5","DA","Bag",350, 350, 250,0.00),
            ("8901030871014","Neem Cake",             "31010090","Organic Section", "Row 5","DB","Kg",  40,  40,  28,0.00),
            ("8901030871021","Potassium Nitrate",     "31043000","Chemical Section","Row 6","EA","Kg",  95,  95,  75,0.05),
            ("8901030871038","Calcium Nitrate",       "31023000","Chemical Section","Row 6","EB","Kg",  70,  70,  55,0.05),
            ("8901030871045","Chlorpyrifos 20% EC",   "38081091","Pesticide Section","Row 7","FA","Litre",45,450,350,0.12),
            ("8901030871052","Imidacloprid 17.8% SL", "38081099","Pesticide Section","Row 7","FB","Litre",60,600,480,0.12),
        ]
        c.executemany("""
            INSERT INTO inventory
                (qr_code,name,hsn_code,section,row_no,slot,unit,quantity,mrp,cost_price,gst_rate)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, samples)
        now = datetime.datetime.now().isoformat()
        for s in samples:
            c.execute("""
                INSERT OR IGNORE INTO qr_registry
                    (qr_code,product_id,product_name,first_scanned,scan_count)
                SELECT ?,id,name,?,1 FROM inventory WHERE qr_code=?
            """, (s[0], now, s[0]))

    conn.commit()
    conn.close()

def lookup_barcode(qr_code: str):
    qr_code = qr_code.strip()
    conn    = get_conn()
    prod    = conn.execute(
        "SELECT * FROM inventory WHERE qr_code=?", (qr_code,)
    ).fetchone()
    conn.close()
    if prod:
        return dict(prod), False
    return None, True

def register_barcode_scan(qr_code: str, product_id: int, product_name: str):
    conn = get_conn()
    now  = datetime.datetime.now().isoformat()
    existing = conn.execute(
        "SELECT qr_code FROM qr_registry WHERE qr_code=?", (qr_code,)
    ).fetchone()
    if existing:
        conn.execute(
            "UPDATE qr_registry SET scan_count=scan_count+1 WHERE qr_code=?",
            (qr_code,)
        )
    else:
        conn.execute("""
            INSERT INTO qr_registry (qr_code,product_id,product_name,first_scanned,scan_count)
            VALUES (?,?,?,?,1)
        """, (qr_code, product_id, product_name, now))
    conn.commit()
    conn.close()

def generate_invoice_no():
    conn   = get_conn()
    now    = datetime.datetime.now()
    prefix = f"SLV-{now.strftime('%Y%m')}-"
    row    = conn.execute(
        "SELECT invoice_no FROM invoices WHERE invoice_no LIKE ? ORDER BY id DESC LIMIT 1",
        (prefix + "%",)
    ).fetchone()
    conn.close()
    seq = int(row["invoice_no"].split("-")[-1]) + 1 if row else 1
    return f"{prefix}{seq:04d}"
