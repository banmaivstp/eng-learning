import streamlit as st
import jwt

def render_clean_sidebar(supabase):
    """Hiển thị Sidebar thanh thoát, không chứa thông tin thừa"""
    auth_data = st.session_state.get("auth", {})
    if not auth_data:
        return
        
    token_data = auth_data.get("token", {}) if isinstance(auth_data, dict) else {}
    id_token = token_data.get("id_token") if isinstance(token_data, dict) else auth_data.get("id_token")
    
    if id_token:
        try:
            user_profile = jwt.decode(id_token, options={"verify_signature": False})
            
            # Khối Profile hàng ngang siêu gọn (Tiết kiệm vùng đất vàng)
            col_av, col_txt = st.sidebar.columns([1, 3])
            with col_av:
                st.image(user_profile.get("picture", ""), width=38) # Thu nhỏ avatar tối đa
            with col_txt:
                st.markdown(f"**{user_profile.get('name')}**")
                
            # Lấy thông tin chuỗi ngày nhanh gọn
            user_id = user_profile.get("sub")
            try:
                streak_res = supabase.table("user_streaks").select("current_streak").eq("user_id", user_id).execute()
                streak_num = streak_res.data[0].get("current_streak", 0) if streak_res.data else 0
                st.sidebar.markdown(f"🔥 Chuỗi hiện tại: **{streak_num} ngày**")
            except:
                pass
        except Exception:
            pass

    st.sidebar.write("---")
    
    # Menu điều hướng chính phân tách rõ ràng thành 3 tab/page riêng biệt
    st.sidebar.markdown("🎯 **Menu ứng dụng**")
    page_selection = st.sidebar.radio(
        "Chọn màn hình làm việc:",
        ["📊 Bảng Tiến Độ", "📻 Tìm Bài Học Mới", "🎧 Phòng Học Thử Thách"],
        label_visibility="collapsed"
    )
    
    # Đồng bộ state với menu lựa chọn mới
    page_map = {
        "📊 Bảng Tiến Độ": "dashboard",
        "📻 Tìm Bài Học Mới": "discover",
        "🎧 Phòng Học Thử Thách": "detail"
    }
    st.session_state['page'] = page_map[page_selection]
    
    st.sidebar.write("---")
    if st.sidebar.button("🚪 Đăng xuất", use_container_width=True):
        if "auth" in st.session_state:
            del st.session_state["auth"]
        st.rerun()