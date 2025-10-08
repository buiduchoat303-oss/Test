# ===================== KHUNG CHAT HỎI – ĐÁP VỚI GEMINI (THÊM MỚI) =====================
st.divider()
st.subheader("💬 Khung chat hỏi – đáp với Gemini")

# --- Sidebar: nhập API key (fallback nếu chưa có trong Secrets) ---
with st.sidebar:
    st.markdown("### 🔑 Gemini API Key")
    st.caption("Nếu bạn đã cấu hình `GEMINI_API_KEY` trong Secrets thì có thể bỏ qua ô này.")
    api_key_chat_input = st.text_input("Nhập GEMINI_API_KEY (ẩn)", type="password")

# Lấy API key: ưu tiên Secrets, sau đó đến input bên sidebar
api_key_chat = (
    st.secrets.get("GEMINI_API_KEY") 
    or api_key_chat_input
)

# Lưu lịch sử chat trong session_state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # mỗi phần tử: {"role": "user"|"assistant", "content": "..."}

# Hiển thị lịch sử chat
for msg in st.session_state.chat_history:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])

# Tuỳ chọn đính kèm ngữ cảnh bảng phân tích hiện tại
attach_ctx = st.checkbox("📎 Đính kèm bảng phân tích hiện tại vào câu hỏi (nếu có)", value=False)

# Hàm chuyển lịch sử chat sang định dạng Gemini
def _to_gemini_contents(_
