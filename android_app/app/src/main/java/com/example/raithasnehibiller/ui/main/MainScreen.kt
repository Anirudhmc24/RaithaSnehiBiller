package com.example.raithasnehibiller.ui.main

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.raithasnehibiller.data.DatabaseHelper
import com.example.raithasnehibiller.ui.*

enum class ScreenTab(val title: String, val icon: ImageVector) {
    Dashboard("Dashboard", Icons.Default.Home),
    NewBill("New Bill", Icons.Default.Receipt),
    Inventory("Inventory", Icons.Default.List),
    SearchLocation("Search Location", Icons.Default.Search),
    Settings("Settings", Icons.Default.Settings)
}

@Composable
fun MainScreen(
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val dbHelper = remember { DatabaseHelper(context) }
    var currentTab by remember { mutableStateOf(ScreenTab.Dashboard) }

    Row(
        modifier = modifier
            .fillMaxSize()
            .background(BrandLightBg)
    ) {
        // Left Sidebar Navigation
        Column(
            modifier = Modifier
                .width(260.dp)
                .fillMaxHeight()
                .background(BrandGreenPrimary)
                .padding(vertical = 24.dp, horizontal = 16.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Column {
                // Header / Branding
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.padding(bottom = 32.dp, start = 8.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Spa,
                        contentDescription = "Logo",
                        tint = Color.White,
                        modifier = Modifier.size(32.dp)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text(
                            text = "Raitha Snehi",
                            color = Color.White,
                            fontSize = 18.sp,
                            fontWeight = FontWeight.ExtraBold,
                            letterSpacing = 0.5.sp
                        )
                        Text(
                            text = "Biller System",
                            color = Color.White.copy(alpha = 0.7f),
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Medium
                        )
                    }
                }

                // Nav Items
                ScreenTab.values().forEach { tab ->
                    val isSelected = currentTab == tab
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 4.dp)
                            .clip(RoundedCornerShape(12.dp))
                            .background(if (isSelected) Color.White.copy(alpha = 0.15f) else Color.Transparent)
                            .clickable { currentTab = tab }
                            .padding(horizontal = 16.dp, vertical = 12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = tab.icon,
                            contentDescription = tab.title,
                            tint = if (isSelected) Color.White else Color.White.copy(alpha = 0.7f),
                            modifier = Modifier.size(22.dp)
                        )
                        Spacer(modifier = Modifier.width(16.dp))
                        Text(
                            text = tab.title,
                            color = if (isSelected) Color.White else Color.White.copy(alpha = 0.7f),
                            fontSize = 15.sp,
                            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium
                        )
                    }
                }
            }

            // Bottom Footer
            Column(
                modifier = Modifier.padding(start = 8.dp, bottom = 8.dp)
            ) {
                Text(
                    text = "Sri Lakshmi Venkateshwara Traders",
                    color = Color.White.copy(alpha = 0.6f),
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "Offline Mode v1.0",
                    color = Color.White.copy(alpha = 0.4f),
                    fontSize = 10.sp
                )
            }
        }

        // Right Main Content Pane
        Box(
            modifier = Modifier
                .weight(1f)
                .fillMaxHeight()
        ) {
            when (currentTab) {
                ScreenTab.Dashboard -> DashboardScreen(dbHelper = dbHelper)
                ScreenTab.NewBill -> NewBillScreen(dbHelper = dbHelper, context = context)
                ScreenTab.Inventory -> InventoryScreen(dbHelper = dbHelper)
                ScreenTab.SearchLocation -> SearchScreen(dbHelper = dbHelper)
                ScreenTab.Settings -> SettingsScreen(context = context)
            }
        }
    }
}

