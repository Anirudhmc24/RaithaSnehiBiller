import streamlit as st
from database.db_main import get_shop_layout, save_shop_layout

def render_node(node_name, children, path):
    """Recursively render a node and its children."""
    # Path is a list of node names, e.g., ["Wall 1", "Shelf A"]
    path_str = " > ".join(path)
    
    with st.expander(f"📍 {node_name}", expanded=True):
        c1, c2 = st.columns([3, 1])
        new_child = c1.text_input(f"Add inside '{node_name}'", key=f"add_in_{path_str}")
        if c2.button("➕ Add Node", key=f"btn_add_{path_str}"):
            if new_child and new_child not in children:
                children[new_child] = {}
                save_shop_layout(st.session_state.shop_layout_tree)
                st.rerun()
        
        if len(path) > 0: # Cannot delete root from here, wait we can delete anything
            if st.button(f"🗑️ Delete '{node_name}'", key=f"del_{path_str}", type="secondary"):
                # Delete logic requires modifying the parent, handled outside via session state 
                st.session_state.node_to_delete = path
                st.rerun()

        st.markdown("---")
        for child_name, child_dict in children.items():
            render_node(child_name, child_dict, path + [child_name])

def delete_node_at_path(tree, path):
    if len(path) == 1:
        if path[0] in tree:
            del tree[path[0]]
    else:
        parent = tree
        for p in path[:-1]:
            parent = parent[p]
        if path[-1] in parent:
            del parent[path[-1]]

def page_shop_layout():
    st.markdown("## 🏪 Shop Layout Builder")
    st.caption("Build your flexible shop location hierarchy here. You can add Walls, Cupboards, Shelves, or any custom location nodes.")
    
    if "shop_layout_tree" not in st.session_state:
        st.session_state.shop_layout_tree = get_shop_layout()
        
    if "node_to_delete" in st.session_state:
        delete_node_at_path(st.session_state.shop_layout_tree, st.session_state.node_to_delete)
        save_shop_layout(st.session_state.shop_layout_tree)
        del st.session_state.node_to_delete
        st.rerun()

    # Add Root Node
    st.markdown("### Add Root Location")
    c1, c2 = st.columns([3, 1])
    new_root = c1.text_input("Name (e.g. Wall 1, Floor Display)", key="new_root")
    if c2.button("➕ Add Root Node", type="primary", use_container_width=True):
        if new_root and new_root not in st.session_state.shop_layout_tree:
            st.session_state.shop_layout_tree[new_root] = {}
            save_shop_layout(st.session_state.shop_layout_tree)
            st.rerun()

    st.markdown("---")
    st.markdown("### Current Layout Hierarchy")
    
    if not st.session_state.shop_layout_tree:
        st.info("No layout defined yet. Add a root node above to get started!")
    else:
        for root_name, root_dict in st.session_state.shop_layout_tree.items():
            render_node(root_name, root_dict, [root_name])
