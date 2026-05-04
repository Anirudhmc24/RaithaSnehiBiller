import sqlite3
from config.settings import DB_PATH

def get_master_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def db_master_init():
    """Create and seed the master database of fertilizers and pesticides."""
    with get_master_conn() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS master_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                hsn_code TEXT NOT NULL,
                gst_rate REAL NOT NULL,
                category TEXT NOT NULL
            )
        """)
        
        # Check if empty, then seed
        c.execute("SELECT COUNT(*) FROM master_products")
        if c.fetchone()[0] == 0:
            samples = [
                # Fertilizers (5%)
                ("Urea (46% N)", "31021010", 0.05, "Fertilizer"),
                ("DAP (Diammonium Phosphate)", "31053000", 0.05, "Fertilizer"),
                ("MOP (Muriate of Potash)", "31042010", 0.05, "Fertilizer"),
                ("NPK 10:26:26", "31059010", 0.05, "Fertilizer"),
                ("NPK 19:19:19", "31051000", 0.05, "Fertilizer"),
                ("NPK 20:20:0:13", "31052000", 0.05, "Fertilizer"),
                ("Single Super Phosphate (SSP)", "31031000", 0.05, "Fertilizer"),
                ("Calcium Nitrate", "31023000", 0.05, "Fertilizer"),
                ("Potassium Nitrate", "31043000", 0.05, "Fertilizer"),
                ("Ammonium Sulphate", "31022100", 0.05, "Fertilizer"),
                
                # Micronutrients (18%)
                ("Zinc Sulphate", "28330300", 0.18, "Micronutrient"),
                ("Boron (Borax)", "28402000", 0.18, "Micronutrient"),
                ("Ferrous Sulphate", "28332910", 0.18, "Micronutrient"),
                ("Magnesium Sulphate", "28332100", 0.18, "Micronutrient"),
                ("Copper Sulphate", "28332500", 0.18, "Micronutrient"),
                
                # Pesticides/Insecticides (12% or 18% depending on formulation, usually 18% for speciality)
                ("Chlorpyrifos 20% EC", "38081091", 0.12, "Pesticide"),
                ("Imidacloprid 17.8% SL", "38081099", 0.12, "Pesticide"),
                ("Cypermethrin 25% EC", "38081019", 0.12, "Pesticide"),
                ("Monocrotophos 36% SL", "38081099", 0.12, "Pesticide"),
                ("Profenofos 50% EC", "38081099", 0.18, "Pesticide"),
                ("Mancozeb 75% WP", "38089290", 0.18, "Fungicide"),
                ("Carbendazim 50% WP", "38089290", 0.18, "Fungicide"),
                ("Hexaconazole 5% EC", "38089290", 0.18, "Fungicide"),
                ("Glyphosate 41% SL", "38089390", 0.18, "Herbicide"),
                ("Paraquat Dichloride 24% SL", "38089390", 0.18, "Herbicide"),
                ("Pretilachlor 50% EC", "38089390", 0.18, "Herbicide"),
                ("Pendimethalin 30% EC", "38089390", 0.18, "Herbicide"),
                # Rallis India Insecticides (12% or 18%)
                ("Rallis Taffy", "38081099", 0.18, "Pesticide"),
                ("Rallis Tatamida", "38081099", 0.18, "Pesticide"),
                ("Rallis Zygant", "38081099", 0.18, "Pesticide"),
                ("Rallis Asataf (Acephate)", "38081099", 0.18, "Pesticide"),
                ("Rallis Applaud (Buprofezin)", "38081099", 0.18, "Pesticide"),
                ("Rallis Nagata (Ethion + Cypermethrin)", "38081099", 0.18, "Pesticide"),
                
                # Rallis India Fungicides (18%)
                ("Rallis Copper Oxy Chloride", "38089290", 0.18, "Fungicide"),
                ("Rallis Metalaxyl", "38089290", 0.18, "Fungicide"),
                ("Rallis Kresoxim-methyl", "38089290", 0.18, "Fungicide"),
                ("Rallis Tebuconazole", "38089290", 0.18, "Fungicide"),

                # Rallis India Herbicides (18%)
                ("Rallis Metribuzin", "38089390", 0.18, "Herbicide"),
                
                # Rallis India Plant Growth Nutrients (18%)
                ("TATA Bahaar", "31059090", 0.18, "Plant Growth Nutrient"),
                ("Rallis Surplus", "31059090", 0.18, "Plant Growth Nutrient"),
                ("Rallis Aquafert", "31059090", 0.18, "Plant Growth Nutrient"),
                ("Rallis NAYAZINC", "28330300", 0.18, "Micronutrient"),

                # Organic / Exempt (0%)
                ("Organic Compost", "31010010", 0.00, "Organic"),
                ("Neem Cake", "31010090", 0.00, "Organic"),
                ("Vermicompost", "31010099", 0.00, "Organic"),
                ("Castor Cake", "31010099", 0.00, "Organic"),
                ("Groundnut Cake", "31010099", 0.00, "Organic")
            ]
            
            c.executemany("""
                INSERT OR IGNORE INTO master_products (name, hsn_code, gst_rate, category)
                VALUES (?, ?, ?, ?)
            """, samples)
        conn.commit()

def search_master_products(query: str):
    """Return a list of matching master products for autocomplete."""
    with get_master_conn() as conn:
        rows = conn.execute("""
            SELECT name, hsn_code, gst_rate, category 
            FROM master_products 
            WHERE name LIKE ? 
            ORDER BY name 
            LIMIT 50
        """, (f"%{query}%",)).fetchall()
    return [dict(r) for r in rows]

def get_all_master_products():
    with get_master_conn() as conn:
        rows = conn.execute("""
            SELECT name, hsn_code, gst_rate, category 
            FROM master_products 
            ORDER BY name
        """).fetchall()
    return [dict(r) for r in rows]
