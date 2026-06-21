import streamlit as st

def render_location_selector(tree, key_prefix="loc"):
    """
    Renders cascading select boxes based on the tree depth.
    Returns the final location_path string (e.g. "Wall 1 > Shelf A")
    """
    if not tree:
        st.warning("No Shop Layout defined! Please go to '🏪 Shop Layout' to map your store.")
        return ""
        
    path = []
    current_node = tree
    level = 1
    
    st.markdown("**Select Location Path:**")
    
    while True:
        options = ["-- Select --"] + list(current_node.keys())
        selected = st.selectbox(f"↳ Level {level}", options, key=f"{key_prefix}_lvl_{level}")
        
        if selected == "-- Select --":
            break
            
        path.append(selected)
        current_node = current_node[selected]
        
        if not current_node:
            break
            
        level += 1
        
    return " > ".join(path)

def render_step_header(step_num, title, description):
    import streamlit as st
    st.markdown(f"""
    <div class="step-header">
        <div class="step-number">{step_num}</div>
        <div class="step-details">
            <h2>{title}</h2>
            <p>{description}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(label, value, icon="📈"):
    import streamlit as st
    st.markdown(f"""
    <div class="custom-metric-card">
        <div class="metric-info">
            <span class="metric-label">{label}</span>
            <span class="metric-value">{value}</span>
        </div>
        <div class="metric-icon-box">
            {icon}
        </div>
    </div>
    """, unsafe_allow_html=True)

