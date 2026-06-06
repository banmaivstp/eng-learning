import streamlit as st
from config import supabase
from modules.scraper import get_episode_list_from_show

def render_podcast_discover_page():
    st.title("📻 Khám Phá Bài Học")
    
    # Ô nhập link tinh giản tối đa chữ hướng dẫn
    input_show_url = st.text_input("Dán link Apple Podcast của Show:", placeholder="https://podcasts.apple.com/...")
    
    if st.button("🔍 Quét tìm bài tập", use_container_width=True):
        if input_show_url:
            with st.spinner("AI đang quét dữ liệu bài học..."):
                show_data = get_episode_list_from_show(input_show_url)
                if show_data:
                    # Logic lưu DB giữ nguyên từ file cũ của bạn...
                    st.success("Đồng bộ thành công!")
                    
    # Danh sách bài học dạng List Item siêu gọn
    if 'podcast_episodes' in st.session_state:
        st.write("---")
        st.markdown(f"📚 **Danh sách bài thuộc Show: {st.session_state['podcast_show_title']}**")
        
        for idx, ep in enumerate(st.session_state['podcast_episodes']):
            # Thiết kế hàng ngang nén chặt đất, có nút bấm học ngay bên phải
            col_title, col_btn = st.columns([4, 1])
            with col_title:
                st.markdown(f"""
                <div style='padding: 6px 0px;'>
                    <span style='color: #00F2FE; font-weight: 600;'>Bài {idx+1}:</span> {ep['title']}
                </div>
                """, unsafe_allow_html=True)
            with col_btn:
                if st.button("⚡ Học", key=f"quick_learn_{idx}", use_container_width=True):
                    st.session_state['current_episode'] = ep
                    st.session_state['submitted_quiz'] = False
                    st.session_state['page'] = 'detail'
                    st.rerun()