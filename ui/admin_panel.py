# ui/admin_panel.py
import streamlit as st
import pandas as pd
from database.db_main import get_all_users, update_user_status, update_user_role, delete_user
from ui.components import render_metric_card

def page_admin_panel():
    """
    Renders administrative user approval and role management tools.
    Additional safety check confirms logged-in role is admin.
    """
    if st.session_state.get("user_role") != "admin":
        st.error("🚫 Access Denied: You do not have permissions to access the Admin Control Panel.")
        return

    st.subheader("👥 Admin Control Panel")
    st.caption("Manage user access permissions, registrations, and account authorization.")

    users = get_all_users()
    
    total_users = len(users)
    pending_users = [u for u in users if u["status"] == "pending"]
    approved_users = [u for u in users if u["status"] == "approved"]
    disabled_users = [u for u in users if u["status"] == "disabled"]

    # Render summary metric cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Total Accounts", f"{total_users}", "👥")
    with col2:
        render_metric_card("Pending Approval", f"{len(pending_users)}", "⏳")
    with col3:
        render_metric_card("Active Users", f"{len(approved_users)}", "🟢")
    with col4:
        render_metric_card("Disabled Accounts", f"{len(disabled_users)}", "🔴")

    st.markdown("---")

    # Section 1: Pending Approvals
    st.markdown("### ⏳ Pending Registration Requests")
    if not pending_users:
        st.info("No pending registration requests at the moment.")
    else:
        for u in pending_users:
            with st.expander(f"👤 {u['username']} (Requested: {u['created_at'][:10]})", expanded=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"**Username:** {u['username']} | **Requested:** {u['created_at']}")
                if c2.button("✅ Approve", key=f"app_{u['username']}", use_container_width=True, type="primary"):
                    update_user_status(u['username'], "approved")
                    st.success(f"Approved {u['username']} successfully!")
                    st.rerun()
                if c3.button("🗑 Reject / Delete", key=f"rej_{u['username']}", use_container_width=True):
                    delete_user(u['username'])
                    st.success(f"Rejected and deleted {u['username']}!")
                    st.rerun()

    st.markdown("---")

    # Section 2: Active & Disabled Users Table
    st.markdown("### 📋 User Registries")
    
    active_and_disabled = [u for u in users if u["status"] in ["approved", "disabled"]]
    
    if active_and_disabled:
        rows = []
        for u in active_and_disabled:
            rows.append({
                "Username": u["username"],
                "Role": "🛡️ Admin" if u["role"] == "admin" else "👤 User",
                "Status": "🟢 Active" if u["status"] == "approved" else "🔴 Disabled",
                "Joined Date": u["created_at"][:19].replace("T", " ")
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        
        st.markdown("**Manage existing accounts:**")
        for u in active_and_disabled:
            # Prevents demoting or disabling self
            if u["username"].lower() == st.session_state.username.lower():
                continue
                
            status_text = "🟢 Active" if u["status"] == "approved" else "🔴 Disabled"
            role_text = "🛡️ Admin" if u["role"] == "admin" else "👤 User"
            
            with st.expander(f"👤 {u['username']} ({role_text} · {status_text})", expanded=False):
                btn_cols = st.columns(3)
                
                # Toggle Status (Active / Disabled)
                if u["status"] == "approved":
                    if btn_cols[0].button("🔒 Disable Access", key=f"dis_{u['username']}", use_container_width=True):
                        update_user_status(u['username'], "disabled")
                        st.success(f"Disabled account: {u['username']}")
                        st.rerun()
                else:
                    if btn_cols[0].button("🔓 Enable Access", key=f"enb_{u['username']}", use_container_width=True):
                        update_user_status(u['username'], "approved")
                        st.success(f"Activated account: {u['username']}")
                        st.rerun()

                # Toggle Role (Demote / Promote)
                if u["role"] == "user":
                    if btn_cols[1].button("🛡️ Promote to Admin", key=f"prom_{u['username']}", use_container_width=True):
                        update_user_role(u['username'], "admin")
                        st.success(f"Promoted {u['username']} to administrator.")
                        st.rerun()
                else:
                    if btn_cols[1].button("👤 Demote to User", key=f"dem_{u['username']}", use_container_width=True):
                        update_user_role(u['username'], "user")
                        st.success(f"Demoted {u['username']} to standard user.")
                        st.rerun()

                # Delete Account
                if btn_cols[2].button("🗑 Delete Account", key=f"delu_{u['username']}", use_container_width=True):
                    delete_user(u['username'])
                    st.success(f"Deleted account: {u['username']}")
                    st.rerun()
    else:
        st.info("No active user accounts found.")
