import streamlit as st
from database.db_main import get_shop_settings, save_shop_settings
from config.settings import SHOP_NAME, SHOP_ADDRESS1, SHOP_ADDRESS2, SHOP_ADDRESS3, SHOP_PHONE, SHOP_EMAIL, GSTIN

def page_settings():
    st.title("⚙️ Shop Settings")
    st.markdown("Update your shop details here. These details will be reflected on your bills and dashboard.")
    
    # Load current settings from DB
    current_settings = get_shop_settings()
    
    with st.form("shop_settings_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            shop_name = st.text_input("Shop Name", value=current_settings.get("shop_name", SHOP_NAME))
            invoice_prefix = st.text_input("Invoice Prefix", value=current_settings.get("invoice_prefix", "RS-"), max_chars=10)
            gstin = st.text_input("GSTIN", value=current_settings.get("shop_gstin", GSTIN))
            phone = st.text_input("Phone Number", value=current_settings.get("shop_phone", SHOP_PHONE))
            
        with col2:
            address1 = st.text_input("Address Line 1", value=current_settings.get("shop_address1", SHOP_ADDRESS1))
            address2 = st.text_input("Address Line 2", value=current_settings.get("shop_address2", SHOP_ADDRESS2))
            address3 = st.text_input("Address Line 3 (City, Pincode)", value=current_settings.get("shop_address3", SHOP_ADDRESS3))
            email = st.text_input("Email", value=current_settings.get("shop_email", SHOP_EMAIL))
            
        submit = st.form_submit_button("Save Settings", type="primary")
        
        if submit:
            new_settings = {
                "shop_name": shop_name,
                "invoice_prefix": invoice_prefix.upper() if invoice_prefix else "RS-",
                "shop_gstin": gstin,
                "shop_phone": phone,
                "shop_address1": address1,
                "shop_address2": address2,
                "shop_address3": address3,
                "shop_email": email
            }
            save_shop_settings(new_settings)
            st.success("✅ Shop settings updated successfully! Changes will take effect immediately.")
            
            # Update session state right away
            st.session_state["shop_name"] = new_settings["shop_name"]
            st.session_state["shop_address1"] = new_settings["shop_address1"]
            st.session_state["shop_address2"] = new_settings["shop_address2"]
            st.session_state["shop_address3"] = new_settings["shop_address3"]
            st.session_state["shop_phone"] = new_settings["shop_phone"]
            st.session_state["shop_email"] = new_settings["shop_email"]
            st.session_state["shop_gstin"] = new_settings["shop_gstin"]
            st.session_state["invoice_prefix"] = new_settings["invoice_prefix"]
            st.session_state["shop_addr1"] = f'{new_settings["shop_address1"]}, {new_settings["shop_address2"]}'
            st.session_state["shop_addr2"] = new_settings["shop_address3"]
            
            st.rerun()

    st.markdown("---")
    st.markdown("### 🔒 Change Account Password")
    st.caption("Change your login credentials securely. Passwords will be cryptographically hashed.")
    
    with st.form("change_password_form"):
        old_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password", help="Minimum 6 characters")
        confirm_new_password = st.text_input("Confirm New Password", type="password")
        
        submit_pw = st.form_submit_button("Update Password", type="primary")
        
        if submit_pw:
            if not old_password or not new_password or not confirm_new_password:
                st.error("Please fill all password fields.")
            elif len(new_password) < 6:
                st.error("New password must be at least 6 characters.")
            elif new_password != confirm_new_password:
                st.error("New passwords do not match.")
            else:
                from database.db_main import get_user, update_user_password
                from utils.security import verify_password
                
                user_info = get_user(st.session_state.username)
                if user_info and verify_password(old_password, user_info["password_hash"], user_info["salt"]):
                    update_user_password(st.session_state.username, new_password)
                    st.success("✅ Password updated successfully! Please note your changes.")
                else:
                    st.error("❌ Incorrect current password.")
