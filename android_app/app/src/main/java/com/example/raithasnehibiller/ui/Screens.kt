package com.example.raithasnehibiller.ui

import android.content.Context
import android.print.PrintAttributes
import android.print.PrintManager
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.raithasnehibiller.data.DatabaseHelper
import java.text.DecimalFormat

// Color Definitions
val BrandGreenPrimary = Color(0xFF1B5E20)
val BrandGreenSecondary = Color(0xFF2E7D32)
val BrandLightBg = Color(0xFFF8FAFC)
val BrandCardBg = Color(0xFFFFFFFF)
val TextDark = Color(0xFF0F172A)
val TextGray = Color(0xFF64748B)
val BorderColor = Color(0xFFE2E8F0)
val AccentAmber = Color(0xFFD97706)

val df = DecimalFormat("₹ #,##0.00")

@Composable
fun MetricCard(title: String, value: String, icon: @Composable () -> Unit, modifier: Modifier = Modifier) {
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(16.dp))
            .background(BrandCardBg)
            .border(1.dp, BorderColor, RoundedCornerShape(16.dp))
            .padding(20.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween,
            modifier = Modifier.fillMaxWidth()
        ) {
            Column {
                Text(text = title.uppercase(), fontSize = 11.sp, fontWeight = FontWeight.Bold, color = TextGray, letterSpacing = 0.5.sp)
                Spacer(modifier = Modifier.height(6.dp))
                Text(text = value, fontSize = 22.sp, fontWeight = FontWeight.ExtraBold, color = TextDark)
            }
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(Color(0xFFE8F5E9)),
                contentAlignment = Alignment.Center
            ) {
                icon()
            }
        }
    }
}

// ── 1. DASHBOARD SCREEN ───────────────────────────────────────────────────────
@Composable
fun DashboardScreen(dbHelper: DatabaseHelper) {
    var todaySales by remember { mutableStateOf(0.0) }
    var weeklySales by remember { mutableStateOf(0.0) }
    var monthlySales by remember { mutableStateOf(0.0) }
    var invoiceCount by remember { mutableStateOf(0) }
    var recentInvoices by remember { mutableStateOf(listOf<Map<String, Any>>()) }

    LaunchedEffect(Unit) {
        todaySales = dbHelper.getTodaySales()
        weeklySales = dbHelper.getWeeklySales()
        monthlySales = dbHelper.getMonthlySales()
        invoiceCount = dbHelper.getTotalInvoicesCount()
        recentInvoices = dbHelper.getAllInvoices().take(10)
    }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(BrandLightBg)
            .padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(20.dp)
    ) {
        item {
            Text(text = "Dashboard", fontSize = 24.sp, fontWeight = FontWeight.Bold, color = TextDark)
            Text(text = "Store overview statistics.", fontSize = 14.sp, color = TextGray)
            Spacer(modifier = Modifier.height(10.dp))
        }

        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                MetricCard("Today's Sales", df.format(todaySales), { Icon(Icons.Default.DateRange, "", tint = BrandGreenPrimary) }, Modifier.weight(1f))
                MetricCard("Weekly Sales", df.format(weeklySales), { Icon(Icons.Default.TrendingUp, "", tint = BrandGreenPrimary) }, Modifier.weight(1f))
                MetricCard("Monthly Sales", df.format(monthlySales), { Icon(Icons.Default.Star, "", tint = BrandGreenPrimary) }, Modifier.weight(1f))
                MetricCard("Total Invoices", invoiceCount.toString(), { Icon(Icons.Default.Receipt, "", tint = BrandGreenPrimary) }, Modifier.weight(1f))
            }
        }

        item {
            // Quick Invoice Action Card
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(16.dp))
                    .background(Brush.horizontalGradient(listOf(Color(0xFFE8F5E9), Color(0xFFC8E6C9))))
                    .border(1.dp, Color(0xFFA5D6A7), RoundedCornerShape(16.dp))
                    .padding(24.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(3f)) {
                        Text("🌱 Create New Invoice", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = BrandGreenPrimary)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text("Launch checkout panel to process local sales using barcode QR scan or manual search.", fontSize = 13.sp, color = Color(0xFF334155))
                    }
                }
            }
        }

        item {
            Text(text = "Recent Invoices", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = TextDark)
            Spacer(modifier = Modifier.height(4.dp))
        }

        if (recentInvoices.isEmpty()) {
            item {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(12.dp))
                        .background(BrandCardBg)
                        .border(1.dp, BorderColor, RoundedCornerShape(12.dp))
                        .padding(32.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text("No local invoices created yet.", color = TextGray, fontSize = 14.sp)
                }
            }
        } else {
            items(recentInvoices) { inv ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(12.dp))
                        .background(BrandCardBg)
                        .border(1.dp, BorderColor, RoundedCornerShape(12.dp))
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(text = inv["invoice_no"] as String, fontWeight = FontWeight.Bold, color = TextDark)
                        Text(text = "Date: " + inv["invoice_date"] as String, fontSize = 12.sp, color = TextGray)
                        Text(text = "Customer: " + inv["customer_name"] as String, fontSize = 13.sp, color = TextDark)
                    }
                    Text(text = df.format(inv["total_amount"] as Double), fontWeight = FontWeight.ExtraBold, color = BrandGreenPrimary, fontSize = 16.sp)
                }
            }
        }
    }
}

// ── 2. INVENTORY SCREEN ──────────────────────────────────────────────────────
@Composable
fun InventoryScreen(dbHelper: DatabaseHelper) {
    var tabIndex by remember { mutableStateOf(0) }
    var products by remember { mutableStateOf(listOf<Map<String, Any>>()) }
    val tabs = listOf("📋 View Catalog", "➕ Add Product", "🔄 Restock")

    fun reload() {
        products = dbHelper.getAllProducts()
    }

    LaunchedEffect(Unit) {
        reload()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BrandLightBg)
            .padding(24.dp)
    ) {
        Text(text = "Inventory Management", fontSize = 24.sp, fontWeight = FontWeight.Bold, color = TextDark)
        Spacer(modifier = Modifier.height(16.dp))

        TabRow(selectedTabIndex = tabIndex, containerColor = BrandLightBg) {
            tabs.forEachIndexed { index, title ->
                Tab(
                    selected = tabIndex == index,
                    onClick = { tabIndex = index },
                    text = { Text(title, fontWeight = FontWeight.SemiBold) }
                )
            }
        }
        Spacer(modifier = Modifier.height(20.dp))

        when (tabIndex) {
            0 -> { // View Catalog
                LazyColumn(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    if (products.isEmpty()) {
                        item { Text("No products in catalog.", color = TextGray) }
                    }
                    items(products) { p ->
                        val qty = p["quantity"] as Double
                        val unit = p["unit"] as String
                        val status = if (qty < 10) "🔴 LOW STOCK" else "🟢 OK"
                        
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(12.dp))
                                .background(BrandCardBg)
                                .border(1.dp, BorderColor, RoundedCornerShape(12.dp))
                                .padding(16.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(2f)) {
                                Text(p["name"] as String, fontWeight = FontWeight.Bold, color = TextDark, fontSize = 15.sp)
                                Text("HSN: ${p["hsn_code"]} | GST: ${((p["gst_rate"] as Double) * 100).toInt()}%", fontSize = 12.sp, color = TextGray)
                                Text("Location: " + (p["location_path"] as String).ifEmpty { "Not specified" }, fontSize = 12.sp, color = TextGray)
                            }
                            Column(horizontalAlignment = Alignment.End, modifier = Modifier.weight(1f)) {
                                Text("$qty $unit", fontWeight = FontWeight.Bold, color = TextDark)
                                Text(status, fontSize = 11.sp, fontWeight = FontWeight.Bold, color = if (qty < 10) Color.Red else BrandGreenPrimary)
                                Text(df.format(p["mrp"] as Double), fontSize = 13.sp, fontWeight = FontWeight.Bold, color = BrandGreenPrimary)
                            }
                        }
                    }
                }
            }
            1 -> { // Add Product Form
                var qrCode by remember { mutableStateOf("") }
                var name by remember { mutableStateOf("") }
                var hsn by remember { mutableStateOf("") }
                var location by remember { mutableStateOf("") }
                var unit by remember { mutableStateOf("Kg") }
                var qty by remember { mutableStateOf("") }
                var mrp by remember { mutableStateOf("") }
                var cost by remember { mutableStateOf("") }
                var gstLabel by remember { mutableStateOf("5%") }
                val gstOptions = listOf("0%", "5%", "12%", "18%", "28%")

                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(16.dp))
                        .background(BrandCardBg)
                        .border(1.dp, BorderColor, RoundedCornerShape(16.dp))
                        .padding(24.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    OutlinedTextField(value = qrCode, onValueChange = { qrCode = it }, label = { Text("QR Barcode (Optional)") }, modifier = Modifier.fillMaxWidth())
                    OutlinedTextField(value = name, onValueChange = { name = it }, label = { Text("Product Name *") }, modifier = Modifier.fillMaxWidth())
                    OutlinedTextField(value = hsn, onValueChange = { hsn = it }, label = { Text("HSN Code *") }, modifier = Modifier.fillMaxWidth())
                    OutlinedTextField(value = location, onValueChange = { location = it }, label = { Text("Layout Location (e.g. Wall 1 > Shelf A)") }, modifier = Modifier.fillMaxWidth())
                    
                    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        OutlinedTextField(value = qty, onValueChange = { qty = it }, label = { Text("Opening Stock *") }, modifier = Modifier.weight(1f), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number))
                        OutlinedTextField(value = unit, onValueChange = { unit = it }, label = { Text("Unit (Kg/Bag/Nos)") }, modifier = Modifier.weight(1f))
                    }
                    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        OutlinedTextField(value = mrp, onValueChange = { mrp = it }, label = { Text("MRP per Unit *") }, modifier = Modifier.weight(1f), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number))
                        OutlinedTextField(value = cost, onValueChange = { cost = it }, label = { Text("Cost Price *") }, modifier = Modifier.weight(1f), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number))
                    }

                    Text("GST Rate Slab", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = TextGray)
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        gstOptions.forEach { opt ->
                            val selected = gstLabel == opt
                            Button(
                                onClick = { gstLabel = opt },
                                colors = ButtonDefaults.buttonColors(containerColor = if (selected) BrandGreenPrimary else Color.LightGray)
                            ) {
                                Text(opt, color = Color.White)
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))
                    Button(
                        onClick = {
                            val rate = gstLabel.replace("%", "").toDouble() / 100.0
                            if (name.isNotEmpty() && hsn.isNotEmpty() && qty.isNotEmpty() && mrp.isNotEmpty()) {
                                val success = dbHelper.addProduct(
                                    qrCode, name, hsn, location, unit,
                                    qty.toDoubleOrNull() ?: 0.0,
                                    mrp.toDoubleOrNull() ?: 0.0,
                                    cost.toDoubleOrNull() ?: 0.0,
                                    rate
                                )
                                if (success) {
                                    name = ""; hsn = ""; location = ""; qty = ""; mrp = ""; cost = ""; qrCode = ""
                                    reload()
                                    tabIndex = 0
                                }
                            }
                        },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(containerColor = BrandGreenPrimary)
                    ) {
                        Text("Add Product to Inventory", fontSize = 16.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }
            2 -> { // Restock Form
                var selectedProduct by remember { mutableStateOf<Map<String, Any>?>(null) }
                var restockQty by remember { mutableStateOf("") }
                var updateCost by remember { mutableStateOf("") }
                var updateMrp by remember { mutableStateOf("") }
                var dropdownExpanded by remember { mutableStateOf(false) }

                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(16.dp))
                        .background(BrandCardBg)
                        .border(1.dp, BorderColor, RoundedCornerShape(16.dp))
                        .padding(24.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    Box(modifier = Modifier.fillMaxWidth()) {
                        OutlinedTextField(
                            value = selectedProduct?.get("name") as? String ?: "Select Product",
                            onValueChange = {},
                            readOnly = true,
                            label = { Text("Select Product to Restock") },
                            modifier = Modifier.fillMaxWidth().clickable { dropdownExpanded = true },
                            trailingIcon = { Icon(Icons.Default.ArrowDropDown, "") }
                        )
                        DropdownMenu(expanded = dropdownExpanded, onDismissRequest = { dropdownExpanded = false }) {
                            products.forEach { p ->
                                DropdownMenuItem(
                                    text = { Text(p["name"] as String) },
                                    onClick = {
                                        selectedProduct = p
                                        updateCost = p["cost_price"].toString()
                                        updateMrp = p["mrp"].toString()
                                        dropdownExpanded = false
                                    }
                                )
                            }
                        }
                    }

                    if (selectedProduct != null) {
                        OutlinedTextField(value = restockQty, onValueChange = { restockQty = it }, label = { Text("Received Qty") }, modifier = Modifier.fillMaxWidth(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number))
                        OutlinedTextField(value = updateCost, onValueChange = { updateCost = it }, label = { Text("Cost Price per Unit") }, modifier = Modifier.fillMaxWidth(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number))
                        OutlinedTextField(value = updateMrp, onValueChange = { updateMrp = it }, label = { Text("MRP per Unit") }, modifier = Modifier.fillMaxWidth(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number))

                        Button(
                            onClick = {
                                val pid = selectedProduct!!["id"] as Int
                                val q = restockQty.toDoubleOrNull() ?: 0.0
                                val c = updateCost.toDoubleOrNull() ?: 0.0
                                val m = updateMrp.toDoubleOrNull() ?: 0.0
                                if (q > 0) {
                                    dbHelper.restockProduct(pid, q, c, m)
                                    selectedProduct = null
                                    restockQty = ""
                                    reload()
                                    tabIndex = 0
                                }
                            },
                            modifier = Modifier.fillMaxWidth(),
                            colors = ButtonDefaults.buttonColors(containerColor = BrandGreenPrimary)
                        ) {
                            Text("Confirm Restock", fontSize = 16.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }
}

// ── 3. NEW BILL SCREEN ────────────────────────────────────────────────────────
@Composable
fun NewBillScreen(dbHelper: DatabaseHelper, context: Context) {
    var qrCodeInput by remember { mutableStateOf("") }
    var customerName by remember { mutableStateOf("") }
    var cartList = remember { mutableStateListOf<HashMap<String, Any>>() }
    var catalog by remember { mutableStateOf(listOf<Map<String, Any>>()) }
    var manualDropdownExpanded by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        catalog = dbHelper.getAllProducts()
    }

    // Calculations
    var taxableVal = 0.0
    var totalCgst = 0.0
    var totalSgst = 0.0
    var grandTotal = 0.0

    for (item in cartList) {
        val qty = item["quantity"] as Double
        val unitPrice = item["unit_price"] as Double
        val rate = item["gst_rate"] as Double
        
        val lineTaxable = Math.round(unitPrice * qty * 100.0) / 100.0
        val lineCgst = Math.round(lineTaxable * (rate / 2.0) * 100.0) / 100.0
        val lineSgst = lineCgst
        val lineTotal = lineTaxable + lineCgst + lineSgst
        
        taxableVal += lineTaxable
        totalCgst += lineCgst
        totalSgst += lineSgst
        grandTotal += lineTotal
    }

    fun addItemToCart(prod: Map<String, Any>) {
        val pid = prod["id"] as Int
        val existing = cartList.find { (it["product_id"] as Int) == pid }
        if (existing != null) {
            val curQty = existing["quantity"] as Double
            existing["quantity"] = curQty + 1.0
        } else {
            val item = HashMap<String, Any>().apply {
                put("product_id", pid)
                put("product_name", prod["name"] as String)
                put("hsn_code", prod["hsn_code"] as String)
                put("quantity", 1.0)
                put("unit", prod["unit"] as String)
                put("unit_price", prod["mrp"] as Double)
                put("gst_rate", prod["gst_rate"] as Double)
            }
            cartList.add(item)
        }
        // Force list update trigger
        val temp = cartList.toList()
        cartList.clear()
        cartList.addAll(temp)
    }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(BrandLightBg)
            .padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text(text = "New Billing Invoice", fontSize = 24.sp, fontWeight = FontWeight.Bold, color = TextDark)
            Text(text = "Scan QR codes or add manually.", fontSize = 14.sp, color = TextGray)
        }

        // Section 1: Scan Barcode
        item {
            Card(colors = CardDefaults.cardColors(containerColor = BrandCardBg)) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("📱 Step 1: Scan Product", fontSize = 15.sp, fontWeight = FontWeight.Bold, color = BrandGreenPrimary)
                    OutlinedTextField(
                        value = qrCodeInput,
                        onValueChange = {
                            qrCodeInput = it
                            if (it.endsWith("\n") || it.length >= 13) {
                                val match = dbHelper.getProductByQrCode(it.trim())
                                if (match != null) {
                                    addItemToCart(match)
                                    qrCodeInput = ""
                                }
                            }
                        },
                        label = { Text("Scan QR Barcode Input") },
                        placeholder = { Text("Use USB barcode scanner or type code...") },
                        modifier = Modifier.fillMaxWidth()
                    )

                    Text("OR Add Item Manually", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = TextGray)
                    Box(modifier = Modifier.fillMaxWidth()) {
                        Button(
                            onClick = { manualDropdownExpanded = true },
                            colors = ButtonDefaults.buttonColors(containerColor = BrandGreenSecondary)
                        ) {
                            Icon(Icons.Default.Add, "")
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("Select Product From Catalog")
                        }
                        DropdownMenu(expanded = manualDropdownExpanded, onDismissRequest = { manualDropdownExpanded = false }) {
                            catalog.forEach { p ->
                                DropdownMenuItem(
                                    text = { Text(p["name"] as String) },
                                    onClick = {
                                        addItemToCart(p)
                                        manualDropdownExpanded = false
                                    }
                                )
                            }
                        }
                    }
                }
            }
        }

        // Section 2: Review Cart
        item {
            Text("🛒 Step 2: Items in Cart", fontSize = 15.sp, fontWeight = FontWeight.Bold, color = BrandGreenPrimary)
        }

        if (cartList.isEmpty()) {
            item {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(12.dp))
                        .background(BrandCardBg)
                        .border(1.dp, BorderColor, RoundedCornerShape(12.dp))
                        .padding(32.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text("No items added yet. Scan a code to start billing.", color = TextGray)
                }
            }
        } else {
            items(cartList) { item ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(12.dp))
                        .background(BrandCardBg)
                        .border(1.dp, BorderColor, RoundedCornerShape(12.dp))
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(2f)) {
                        Text(item["product_name"] as String, fontWeight = FontWeight.Bold, color = TextDark)
                        Text(df.format(item["unit_price"] as Double) + " per " + item["unit"] as String, fontSize = 12.sp, color = TextGray)
                    }
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        modifier = Modifier.weight(1.5f)
                    ) {
                        IconButton(onClick = {
                            val cur = item["quantity"] as Double
                            if (cur > 1) {
                                item["quantity"] = cur - 1.0
                            } else {
                                cartList.remove(item)
                            }
                            val temp = cartList.toList()
                            cartList.clear()
                            cartList.addAll(temp)
                        }) {
                            Icon(Icons.Default.Remove, "")
                        }
                        Text(item["quantity"].toString(), fontWeight = FontWeight.Bold)
                        IconButton(onClick = {
                            val cur = item["quantity"] as Double
                            item["quantity"] = cur + 1.0
                            val temp = cartList.toList()
                            cartList.clear()
                            cartList.addAll(temp)
                        }) {
                            Icon(Icons.Default.Add, "")
                        }
                    }
                }
            }
        }

        // Section 3: Receipt Summary
        if (cartList.isNotEmpty()) {
            item {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(16.dp))
                        .background(Color(0xFFFFFDF5))
                        .border(2.dp, BorderColor, RoundedCornerShape(16.dp))
                        .padding(24.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    Text("Receipt Invoice Summary", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = TextGray, letterSpacing = 0.5.sp)
                    Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                        Text("Taxable Value", color = TextDark)
                        Text(df.format(taxableVal), fontWeight = FontWeight.Bold)
                    }
                    Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                        Text("CGST Amount", color = TextDark)
                        Text(df.format(totalCgst), fontWeight = FontWeight.Bold)
                    }
                    Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                        Text("SGST Amount", color = TextDark)
                        Text(df.format(totalSgst), fontWeight = FontWeight.Bold)
                    }
                    Spacer(modifier = Modifier.height(4.dp))
                    Row(
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Grand Total (GST Incl.)", fontWeight = FontWeight.Bold, color = TextDark, fontSize = 16.sp)
                        Text(df.format(grandTotal), fontWeight = FontWeight.ExtraBold, color = BrandGreenPrimary, fontSize = 24.sp)
                    }
                }
            }

            // Step 4: Generate Bill
            item {
                Card(colors = CardDefaults.cardColors(containerColor = BrandCardBg)) {
                    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        Text("🖨️ Step 3: Customer & Print", fontSize = 15.sp, fontWeight = FontWeight.Bold, color = BrandGreenPrimary)
                        OutlinedTextField(
                            value = customerName,
                            onValueChange = { customerName = it },
                            label = { Text("Customer Name (Optional)") },
                            placeholder = { Text("Cash Customer") },
                            modifier = Modifier.fillMaxWidth()
                        )

                        Button(
                            onClick = {
                                val invNo = dbHelper.generateInvoiceNo()
                                val success = dbHelper.saveInvoice(
                                    invNo, customerName, taxableVal, totalCgst, totalSgst, grandTotal, cartList.toList()
                                )
                                if (success) {
                                    Toast.makeText(context, "Invoice Saved: $invNo", Toast.LENGTH_SHORT).show()
                                    // Trigger Print Manager WebView
                                    printInvoiceHtml(context, invNo, customerName, taxableVal, totalCgst, totalSgst, grandTotal, cartList.toList())
                                    cartList.clear()
                                    customerName = ""
                                }
                            },
                            modifier = Modifier.fillMaxWidth(),
                            colors = ButtonDefaults.buttonColors(containerColor = BrandGreenPrimary)
                        ) {
                            Icon(Icons.Default.Print, "")
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("Generate Bill & Print Receipt", fontSize = 16.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }
}

// WebView HTML Print Adapter
private fun printInvoiceHtml(context: Context, invNo: String, custName: String, taxable: Double, cgst: Double, sgst: Double, total: Double, items: List<Map<String, Any>>) {
    val shopName = "Sri Lakshmi Venkateshwara Traders"
    val shopAddress = "#20, Mysore Bangalore Expressway, Mandya"
    val shopPhone = "+91-9743007647"
    val shopGstin = "29CDTPB8883L1ZH"

    val sdf = SimpleDateFormat("dd-MM-yyyy HH:mm", Locale.getDefault())
    val dateStr = sdf.format(Date())

    val itemsHtml = StringBuilder()
    items.forEachIndexed { i, map ->
        val qty = map["quantity"] as Double
        val price = map["unit_price"] as Double
        val itemTax = qty * price
        itemsHtml.append("""
            <tr>
                <td>${i + 1}</td>
                <td>${map["product_name"]}</td>
                <td>${map["hsn_code"]}</td>
                <td>$qty ${map["unit"]}</td>
                <td>₹${String.format(Locale.US, "%.2f", price)}</td>
                <td>₹${String.format(Locale.US, "%.2f", itemTax)}</td>
            </tr>
        """.trimIndent())
    }

    val htmlContent = """
        <html>
        <head>
            <style>
                body { font-family: monospace; font-size: 12px; margin: 10px; color: #000; }
                .header { text-align: center; margin-bottom: 12px; }
                .title { font-size: 16px; font-weight: bold; }
                .meta { margin-bottom: 10px; border-bottom: 1px dashed #000; padding-bottom: 8px; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 10px; }
                th, td { text-align: left; padding: 4px; }
                th { border-bottom: 1px solid #000; }
                .totals { margin-top: 10px; border-top: 1px dashed #000; padding-top: 8px; }
                .totals-row { display: flex; justify-content: space-between; margin-bottom: 4px; }
                .footer { text-align: center; margin-top: 20px; font-size: 10px; }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">$shopName</div>
                <div>$shopAddress</div>
                <div>Phone: $shopPhone</div>
                <div>GSTIN: $shopGstin</div>
            </div>
            <div class="meta">
                <div><b>Invoice:</b> $invNo</div>
                <div><b>Date:</b> $dateStr</div>
                <div><b>Customer:</b> ${if (custName.trim().isEmpty()) "Cash Customer" else custName}</div>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Item</th>
                        <th>HSN</th>
                        <th>Qty</th>
                        <th>MRP</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    $itemsHtml
                </tbody>
            </table>
            <div class="totals">
                <div class="totals-row"><span>Taxable Value:</span> <span>₹${String.format(Locale.US, "%.2f", taxable)}</span></div>
                <div class="totals-row"><span>CGST Amount:</span> <span>₹${String.format(Locale.US, "%.2f", cgst)}</span></div>
                <div class="totals-row"><span>SGST Amount:</span> <span>₹${String.format(Locale.US, "%.2f", sgst)}</span></div>
                <div class="totals-row" style="font-weight:bold; font-size:14px;"><span>Grand Total:</span> <span>₹${String.format(Locale.US, "%.2f", total)}</span></div>
            </div>
            <div class="footer">
                Thank you for visiting! Come back again.<br>Raitha Snehi Biller System
            </div>
        </body>
        </html>
    """.trimIndent()

    val webView = WebView(context)
    webView.webViewClient = object : WebViewClient() {
        override fun onPageFinished(view: WebView?, url: String?) {
            val printManager = context.getSystemService(Context.PRINT_SERVICE) as PrintManager
            val printAdapter = webView.createPrintDocumentAdapter("Bill_$invNo")
            printManager.print("Raitha_Snehi_Bill_$invNo", printAdapter, PrintAttributes.Builder().build())
        }
    }
    webView.loadDataWithBaseURL(null, htmlContent, "text/html", "UTF-8", null)
}

// ── 4. LOCATION SEARCH SCREEN ────────────────────────────────────────────────
@Composable
fun SearchScreen(dbHelper: DatabaseHelper) {
    var searchQuery by remember { mutableStateOf("") }
    var results by remember { mutableStateOf(listOf<Map<String, Any>>()) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BrandLightBg)
            .padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(text = "Search Product Locations", fontSize = 24.sp, fontWeight = FontWeight.Bold, color = TextDark)
        
        OutlinedTextField(
            value = searchQuery,
            onValueChange = {
                searchQuery = it
                if (it.trim().isNotEmpty()) {
                    results = dbHelper.getAllProducts().filter { p ->
                        (p["name"] as String).contains(it, ignoreCase = true) ||
                        (p["qr_code"] as String).contains(it)
                    }
                } else {
                    results = emptyList()
                }
            },
            label = { Text("Search catalog...") },
            placeholder = { Text("Type name, or scan barcode...") },
            leadingIcon = { Icon(Icons.Default.Search, "") },
            modifier = Modifier.fillMaxWidth()
        )

        LazyColumn(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            if (results.isEmpty() && searchQuery.trim().isNotEmpty()) {
                item { Text("No matching products found.", color = TextGray) }
            }
            items(results) { p ->
                val qty = p["quantity"] as Double
                val unit = p["unit"] as String
                val sc = if (qty < 10) "🔴" else "🟢"
                
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(12.dp))
                        .background(BrandCardBg)
                        .border(1.dp, BorderColor, RoundedCornerShape(12.dp))
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(text = "🌱 " + p["name"] as String, fontWeight = FontWeight.Bold, color = TextDark, fontSize = 16.sp)
                        Text(text = "HSN: " + p["hsn_code"] as String + " | GST: " + ((p["gst_rate"] as Double) * 100).toInt() + "%", fontSize = 12.sp, color = TextGray)
                        Text(text = "📍 Location: " + (p["location_path"] as String).ifEmpty { "Not set" }, fontSize = 13.sp, color = TextDark, fontWeight = FontWeight.SemiBold)
                        Text(text = "$sc Stock Qty: $qty $unit | MRP: " + df.format(p["mrp"] as Double), fontSize = 13.sp, color = TextGray)
                    }
                }
            }
        }
    }
}

// ── 5. SETTINGS SCREEN ────────────────────────────────────────────────────────
@Composable
fun SettingsScreen(context: Context) {
    var shopName by remember { mutableStateOf("Sri Lakshmi Venkateshwara Traders") }
    var invoicePrefix by remember { mutableStateOf("RS-") }
    var shopGstin by remember { mutableStateOf("29CDTPB8883L1ZH") }
    var shopPhone by remember { mutableStateOf("+91-9743007647") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BrandLightBg)
            .padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(text = "Settings & Shop Configuration", fontSize = 24.sp, fontWeight = FontWeight.Bold, color = TextDark)
        Spacer(modifier = Modifier.height(10.dp))

        Card(colors = CardDefaults.cardColors(containerColor = BrandCardBg), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("Store Details Configuration", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = BrandGreenPrimary)
                OutlinedTextField(value = shopName, onValueChange = { shopName = it }, label = { Text("Shop Name") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = invoicePrefix, onValueChange = { invoicePrefix = it }, label = { Text("Invoice Prefix") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = shopGstin, onValueChange = { shopGstin = it }, label = { Text("Shop GSTIN") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = shopPhone, onValueChange = { shopPhone = it }, label = { Text("Shop Phone Number") }, modifier = Modifier.fillMaxWidth())

                Button(
                    onClick = {
                        Toast.makeText(context, "Configurations Saved!", Toast.LENGTH_SHORT).show()
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = BrandGreenPrimary),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Save Settings Configurations", fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}
