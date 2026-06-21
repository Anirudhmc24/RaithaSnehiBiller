package com.example.raithasnehibiller.data

import android.content.ContentValues
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Date
import java.util.Locale

class DatabaseHelper(context: Context) : SQLiteOpenHelper(context, DATABASE_NAME, null, DATABASE_VERSION) {

    companion object {
        private const val DATABASE_NAME = "raitha_snehi_offline.db"
        private const val DATABASE_VERSION = 1

        // Tables
        const val TABLE_INVENTORY = "inventory"
        const val TABLE_INVOICES = "invoices"
        const val TABLE_INVOICE_ITEMS = "invoice_items"

        // Common Column
        const val KEY_ID = "id"

        // Inventory Columns
        const val KEY_QR_CODE = "qr_code"
        const val KEY_NAME = "name"
        const val KEY_HSN_CODE = "hsn_code"
        const val KEY_LOCATION_PATH = "location_path"
        const val KEY_UNIT = "unit"
        const val KEY_QUANTITY = "quantity"
        const val KEY_MRP = "mrp"
        const val KEY_COST_PRICE = "cost_price"
        const val KEY_GST_RATE = "gst_rate"

        // Invoices Columns
        const val KEY_INVOICE_NO = "invoice_no"
        const val KEY_CUST_NAME = "customer_name"
        const val KEY_DATE = "invoice_date"
        const val KEY_TAXABLE = "taxable_value"
        const val KEY_CGST = "cgst_amount"
        const val KEY_SGST = "sgst_amount"
        const val KEY_TOTAL = "total_amount"

        // Invoice Items Columns
        const val KEY_PRODUCT_ID = "product_id"
        const val KEY_PRODUCT_NAME = "product_name"
        const val KEY_UNIT_PRICE = "unit_price"
        const val KEY_LINE_TOTAL = "line_total"
    }

    override fun onCreate(db: SQLiteDatabase) {
        // Create Inventory Table
        val createInventoryTable = ("CREATE TABLE " + TABLE_INVENTORY + "("
                + KEY_ID + " INTEGER PRIMARY KEY AUTOINCREMENT,"
                + KEY_QR_CODE + " TEXT UNIQUE,"
                + KEY_NAME + " TEXT NOT NULL,"
                + KEY_HSN_CODE + " TEXT NOT NULL,"
                + KEY_LOCATION_PATH + " TEXT,"
                + KEY_UNIT + " TEXT DEFAULT 'Kg',"
                + KEY_QUANTITY + " REAL DEFAULT 0.0,"
                + KEY_MRP + " REAL NOT NULL,"
                + KEY_COST_PRICE + " REAL DEFAULT 0.0,"
                + KEY_GST_RATE + " REAL DEFAULT 0.05" + ")")
        db.execSQL(createInventoryTable)

        // Create Invoices Table
        val createInvoicesTable = ("CREATE TABLE " + TABLE_INVOICES + "("
                + KEY_ID + " INTEGER PRIMARY KEY AUTOINCREMENT,"
                + KEY_INVOICE_NO + " TEXT UNIQUE NOT NULL,"
                + KEY_CUST_NAME + " TEXT DEFAULT 'Cash Customer',"
                + KEY_DATE + " TEXT NOT NULL,"
                + KEY_TAXABLE + " REAL DEFAULT 0.0,"
                + KEY_CGST + " REAL DEFAULT 0.0,"
                + KEY_SGST + " REAL DEFAULT 0.0,"
                + KEY_TOTAL + " REAL DEFAULT 0.0" + ")")
        db.execSQL(createInvoicesTable)

        // Create Invoice Items Table
        val createInvoiceItemsTable = ("CREATE TABLE " + TABLE_INVOICE_ITEMS + "("
                + KEY_ID + " INTEGER PRIMARY KEY AUTOINCREMENT,"
                + KEY_INVOICE_NO + " TEXT NOT NULL,"
                + KEY_PRODUCT_ID + " INTEGER NOT NULL,"
                + KEY_PRODUCT_NAME + " TEXT,"
                + KEY_HSN_CODE + " TEXT,"
                + KEY_QUANTITY + " REAL,"
                + KEY_UNIT + " TEXT,"
                + KEY_UNIT_PRICE + " REAL,"
                + KEY_GST_RATE + " REAL,"
                + KEY_TAXABLE + " REAL,"
                + KEY_CGST + " REAL,"
                + KEY_SGST + " REAL,"
                + KEY_LINE_TOTAL + " REAL,"
                + "FOREIGN KEY (" + KEY_INVOICE_NO + ") REFERENCES " + TABLE_INVOICES + "(" + KEY_INVOICE_NO + ")" + ")")
        db.execSQL(createInvoiceItemsTable)

        // Seed Sample Products
        seedSampleData(db)
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_INVOICE_ITEMS)
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_INVOICES)
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_INVENTORY)
        onCreate(db)
    }

    private fun seedSampleData(db: SQLiteDatabase) {
        val samples = listOf(
            ContentValues().apply {
                put(KEY_QR_CODE, "8901030870925"); put(KEY_NAME, "Urea (46% N)"); put(KEY_HSN_CODE, "31021010")
                put(KEY_LOCATION_PATH, "Chemical Section > Row 1 > Slot AA"); put(KEY_UNIT, "Bag"); put(KEY_QUANTITY, 100.0)
                put(KEY_MRP, 500.0); put(KEY_COST_PRICE, 380.0); put(KEY_GST_RATE, 0.05)
            },
            ContentValues().apply {
                put(KEY_QR_CODE, "8901030870932"); put(KEY_NAME, "DAP (Diammonium Phos)"); put(KEY_HSN_CODE, "31053000")
                put(KEY_LOCATION_PATH, "Chemical Section > Row 1 > Slot AB"); put(KEY_UNIT, "Bag"); put(KEY_QUANTITY, 50.0)
                put(KEY_MRP, 1350.0); put(KEY_COST_PRICE, 1100.0); put(KEY_GST_RATE, 0.05)
            },
            ContentValues().apply {
                put(KEY_QR_CODE, "8901030870970"); put(KEY_NAME, "Zinc Sulphate"); put(KEY_HSN_CODE, "28330300")
                put(KEY_LOCATION_PATH, "Micro-Nutrient > Row 3 > Slot BB"); put(KEY_UNIT, "Kg"); put(KEY_QUANTITY, 200.0)
                put(KEY_MRP, 85.0); put(KEY_COST_PRICE, 65.0); put(KEY_GST_RATE, 0.18)
            },
            ContentValues().apply {
                put(KEY_QR_CODE, "8901030871045"); put(KEY_NAME, "Chlorpyrifos 20% EC"); put(KEY_HSN_CODE, "38081091")
                put(KEY_LOCATION_PATH, "Pesticide Section > Row 7 > Slot FA"); put(KEY_UNIT, "Litre"); put(KEY_QUANTITY, 30.0)
                put(KEY_MRP, 450.0); put(KEY_COST_PRICE, 350.0); put(KEY_GST_RATE, 0.12)
            }
        )
        for (cv in samples) {
            db.insert(TABLE_INVENTORY, null, cv)
        }
    }

    // --- Inventory Operations ---

    fun addProduct(qrCode: String?, name: String, hsn: String, location: String, unit: String, qty: Double, mrp: Double, cost: Double, gstRate: Double): Boolean {
        val db = this.writableDatabase
        val cv = ContentValues().apply {
            put(KEY_QR_CODE, qrCode?.trim()?.takeIf { it.isNotEmpty() })
            put(KEY_NAME, name)
            put(KEY_HSN_CODE, hsn)
            put(KEY_LOCATION_PATH, location)
            put(KEY_UNIT, unit)
            put(KEY_QUANTITY, qty)
            put(KEY_MRP, mrp)
            put(KEY_COST_PRICE, cost)
            put(KEY_GST_RATE, gstRate)
        }
        val result = db.insert(TABLE_INVENTORY, null, cv)
        return result != -1L
    }

    fun restockProduct(id: Int, qty: Double, cost: Double, mrp: Double): Boolean {
        val db = this.writableDatabase
        val cv = ContentValues().apply {
            put(KEY_COST_PRICE, cost)
            put(KEY_MRP, mrp)
        }
        db.update(TABLE_INVENTORY, cv, "$KEY_ID = ?", arrayOf(id.toString()))
        db.execSQL("UPDATE $TABLE_INVENTORY SET $KEY_QUANTITY = $KEY_QUANTITY + ? WHERE $KEY_ID = ?", arrayOf<Any>(qty, id))
        return true
    }

    fun getAllProducts(): List<Map<String, Any>> {
        val list = mutableListOf<Map<String, Any>>()
        val db = this.readableDatabase
        val cursor = db.rawQuery("SELECT * FROM $TABLE_INVENTORY ORDER BY $KEY_NAME ASC", null)
        if (cursor.moveToFirst()) {
            do {
                val map = HashMap<String, Any>()
                map["id"] = cursor.getInt(cursor.getColumnIndexOrThrow(KEY_ID))
                map["qr_code"] = cursor.getString(cursor.getColumnIndexOrThrow(KEY_QR_CODE)) ?: ""
                map["name"] = cursor.getString(cursor.getColumnIndexOrThrow(KEY_NAME))
                map["hsn_code"] = cursor.getString(cursor.getColumnIndexOrThrow(KEY_HSN_CODE))
                map["location_path"] = cursor.getString(cursor.getColumnIndexOrThrow(KEY_LOCATION_PATH)) ?: ""
                map["unit"] = cursor.getString(cursor.getColumnIndexOrThrow(KEY_UNIT)) ?: "Kg"
                map["quantity"] = cursor.getDouble(cursor.getColumnIndexOrThrow(KEY_QUANTITY))
                map["mrp"] = cursor.getDouble(cursor.getColumnIndexOrThrow(KEY_MRP))
                map["cost_price"] = cursor.getDouble(cursor.getColumnIndexOrThrow(KEY_COST_PRICE))
                map["gst_rate"] = cursor.getDouble(cursor.getColumnIndexOrThrow(KEY_GST_RATE))
                list.add(map)
            } while (cursor.moveToNext())
        }
        cursor.close()
        return list
    }

    fun getProductByQrCode(qrCode: String): Map<String, Any>? {
        val db = this.readableDatabase
        val cursor = db.rawQuery("SELECT * FROM $TABLE_INVENTORY WHERE $KEY_QR_CODE = ?", arrayOf(qrCode.trim()))
        var map: HashMap<String, Any>? = null
        if (cursor.moveToFirst()) {
            map = HashMap()
            map["id"] = cursor.getInt(cursor.getColumnIndexOrThrow(KEY_ID))
            map["qr_code"] = cursor.getString(cursor.getColumnIndexOrThrow(KEY_QR_CODE)) ?: ""
            map["name"] = cursor.getString(cursor.getColumnIndexOrThrow(KEY_NAME))
            map["hsn_code"] = cursor.getString(cursor.getColumnIndexOrThrow(KEY_HSN_CODE))
            map["location_path"] = cursor.getString(cursor.getColumnIndexOrThrow(KEY_LOCATION_PATH)) ?: ""
            map["unit"] = cursor.getString(cursor.getColumnIndexOrThrow(KEY_UNIT)) ?: "Kg"
            map["quantity"] = cursor.getDouble(cursor.getColumnIndexOrThrow(KEY_QUANTITY))
            map["mrp"] = cursor.getDouble(cursor.getColumnIndexOrThrow(KEY_MRP))
            map["cost_price"] = cursor.getDouble(cursor.getColumnIndexOrThrow(KEY_COST_PRICE))
            map["gst_rate"] = cursor.getDouble(cursor.getColumnIndexOrThrow(KEY_GST_RATE))
        }
        cursor.close()
        return map
    }

    // --- Invoice Operations ---

    fun generateInvoiceNo(): String {
        val db = this.readableDatabase
        val sdf = SimpleDateFormat("yyyyMM", Locale.getDefault())
        val prefix = "RS-" + sdf.format(Date()) + "-"
        val cursor = db.rawQuery("SELECT $KEY_INVOICE_NO FROM $TABLE_INVOICES WHERE $KEY_INVOICE_NO LIKE ? ORDER BY $KEY_ID DESC LIMIT 1", arrayOf(prefix + "%"))
        var seq = 1
        if (cursor.moveToFirst()) {
            val lastNo = cursor.getString(0)
            try {
                val parts = lastNo.split("-")
                val lastSeq = parts.last().toInt()
                seq = lastSeq + 1
            } catch (e: Exception) {
                // Ignore and use 1
            }
        }
        cursor.close()
        return String.format(Locale.getDefault(), "%s%04d", prefix, seq)
    }

    fun saveInvoice(invoiceNo: String, custName: String, taxable: Double, cgst: Double, sgst: Double, total: Double, cartItems: List<Map<String, Any>>): Boolean {
        val db = this.writableDatabase
        db.beginTransaction()
        try {
            val sdf = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
            val dateStr = sdf.format(Date())

            val cv = ContentValues().apply {
                put(KEY_INVOICE_NO, invoiceNo)
                put(KEY_CUST_NAME, if (custName.trim().isEmpty()) "Cash Customer" else custName.trim())
                put(KEY_DATE, dateStr)
                put(KEY_TAXABLE, taxable)
                put(KEY_CGST, cgst)
                put(KEY_SGST, sgst)
                put(KEY_TOTAL, total)
            }
            db.insert(TABLE_INVOICES, null, cv)

            for (item in cartItems) {
                val productId = item["product_id"] as Int
                val qty = item["quantity"] as Double
                val unitPrice = item["unit_price"] as Double
                val gstRate = item["gst_rate"] as Double
                
                val itemTaxable = Math.round(unitPrice * qty * 100.0) / 100.0
                val itemCgst = Math.round(itemTaxable * (gstRate / 2.0) * 100.0) / 100.0
                val itemSgst = itemCgst
                val itemTotal = Math.round((itemTaxable + itemCgst + itemSgst) * 100.0) / 100.0

                val itemCv = ContentValues().apply {
                    put(KEY_INVOICE_NO, invoiceNo)
                    put(KEY_PRODUCT_ID, productId)
                    put(KEY_PRODUCT_NAME, item["product_name"] as String)
                    put(KEY_HSN_CODE, item["hsn_code"] as String)
                    put(KEY_QUANTITY, qty)
                    put(KEY_UNIT, item["unit"] as String)
                    put(KEY_UNIT_PRICE, unitPrice)
                    put(KEY_GST_RATE, gstRate)
                    put(KEY_TAXABLE, itemTaxable)
                    put(KEY_CGST, itemCgst)
                    put(KEY_SGST, itemSgst)
                    put(KEY_LINE_TOTAL, itemTotal)
                }
                db.insert(TABLE_INVOICE_ITEMS, null, itemCv)

                // Deduct inventory stock
                db.execSQL("UPDATE $TABLE_INVENTORY SET $KEY_QUANTITY = $KEY_QUANTITY - ? WHERE $KEY_ID = ?", arrayOf<Any>(qty, productId))
            }
            db.setTransactionSuccessful()
            return true
        } catch (e: Exception) {
            return false
        } finally {
            db.endTransaction()
        }
    }

    fun getAllInvoices(): List<Map<String, Any>> {
        val list = mutableListOf<Map<String, Any>>()
        val db = this.readableDatabase
        val cursor = db.rawQuery("SELECT * FROM $TABLE_INVOICES ORDER BY $KEY_ID DESC", null)
        if (cursor.moveToFirst()) {
            do {
                val map = HashMap<String, Any>()
                map["invoice_no"] = cursor.getString(cursor.getColumnIndexOrThrow(KEY_INVOICE_NO))
                map["customer_name"] = cursor.getString(cursor.getColumnIndexOrThrow(KEY_CUST_NAME))
                map["invoice_date"] = cursor.getString(cursor.getColumnIndexOrThrow(KEY_DATE))
                map["taxable_value"] = cursor.getDouble(cursor.getColumnIndexOrThrow(KEY_TAXABLE))
                map["cgst_amount"] = cursor.getDouble(cursor.getColumnIndexOrThrow(KEY_CGST))
                map["sgst_amount"] = cursor.getDouble(cursor.getColumnIndexOrThrow(KEY_SGST))
                map["total_amount"] = cursor.getDouble(cursor.getColumnIndexOrThrow(KEY_TOTAL))
                list.add(map)
            } while (cursor.moveToNext())
        }
        cursor.close()
        return list
    }

    // --- Dashboard Metric Helpers ---

    fun getTodaySales(): Double {
        val db = this.readableDatabase
        val sdf = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
        val todayStr = sdf.format(Date())
        val cursor = db.rawQuery("SELECT SUM($KEY_TOTAL) FROM $TABLE_INVOICES WHERE strftime('%Y-%m-%d', $KEY_DATE) = ?", arrayOf(todayStr))
        var total = 0.0
        if (cursor.moveToFirst()) {
            total = cursor.getDouble(0)
        }
        cursor.close()
        return total
    }

    fun getWeeklySales(): Double {
        val db = this.readableDatabase
        val cal = Calendar.getInstance()
        cal.set(Calendar.DAY_OF_WEEK, cal.firstDayOfWeek)
        val sdf = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
        val weekStart = sdf.format(cal.time)
        val cursor = db.rawQuery("SELECT SUM($KEY_TOTAL) FROM $TABLE_INVOICES WHERE strftime('%Y-%m-%d', $KEY_DATE) >= ?", arrayOf(weekStart))
        var total = 0.0
        if (cursor.moveToFirst()) {
            total = cursor.getDouble(0)
        }
        cursor.close()
        return total
    }

    fun getMonthlySales(): Double {
        val db = this.readableDatabase
        val sdf = SimpleDateFormat("yyyy-MM", Locale.getDefault())
        val monthStr = sdf.format(Date())
        val cursor = db.rawQuery("SELECT SUM($KEY_TOTAL) FROM $TABLE_INVOICES WHERE strftime('%Y-%m', $KEY_DATE) = ?", arrayOf(monthStr))
        var total = 0.0
        if (cursor.moveToFirst()) {
            total = cursor.getDouble(0)
        }
        cursor.close()
        return total
    }

    fun getTotalInvoicesCount(): Int {
        val db = this.readableDatabase
        val cursor = db.rawQuery("SELECT COUNT(*) FROM $TABLE_INVOICES", null)
        var count = 0
        if (cursor.moveToFirst()) {
            count = cursor.getInt(0)
        }
        cursor.close()
        return count
    }
}
