# ===================== KHUNG CHAT HỎI – ĐÁP VỚI GEMINI (THÊM MỚI) =====================
st.divider()
st.subheader("💬 Khung chat hỏi – đáp với Gemini")

# --- Sidebar: nhập API key (fallback nếu chưa có trong Secrets) ---
with st.sidebar:
    st.markdown("### 🔑 Gemini API Key")
    st.caption("Nếu bạn đã cấu hình `GEMINI_API_KEY` trong Secrets thì có thể bỏ qua ô này.")
    api_key_chat_input = st.text_input("Nhập GEMINI_API_KEY (ẩn)", type="password")

# Lấy API key: ưu tiên Secrets, sau đó đến input bên sidebar
# (Không sửa mã cũ: chỉ bổ sung cách lấy key cho khung chat mới)
api_key_chat = st.secrets.get("GEMINI_API_KEY") or api_key_chat_input

# Lưu lịch sử chat trong session_state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # [{'role': 'user'|'assistant', 'content': '...'}]

# Hiển thị lịch sử chat
for msg in st.session_state.chat_history:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])

# Tuỳ chọn đính kèm ngữ cảnh bảng phân tích hiện tại
attach_ctx = st.checkbox("📎 Đính kèm bảng phân tích hiện tại vào câu hỏi (nếu có)", value=False)

# Hàm chuyển lịch sử chat sang định dạng Gemini
def _to_gemini_contents(history, system_hint=None):
    """
    Chuyển [{'role':'user'|'assistant','content':str}, ...]
    -> contents cho Gemini: [{'role':'user'|'model','parts':[str]}, ...]
    """
    contents = []
    if system_hint:
        contents.append({"role": "user", "parts": [system_hint]})  # đưa system hint như 1 user-msg đầu
    for m in history:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [m["content"]]})
    return contents

# Ô nhập chat
user_question = st.chat_input("Nhập câu hỏi về tài chính/kế toán/doanh nghiệp...")

# Nút xoá lịch sử chat
col_reset, _ = st.columns([1, 9])
with col_reset:
    if st.button("🗑️ Xoá lịch sử chat"):
        st.session_state.chat_history = []
        st.rerun()

if user_question:
    # Ghép ngữ cảnh bảng phân tích (nếu có và được chọn)
    composed_question = user_question
    if attach_ctx and "df_processed" in locals():
        try:
            # Giới hạn 30 dòng để tránh prompt quá lớn
            preview_md = df_processed.head(30).to_markdown(index=False)
            composed_question += (
                "\n\n[Ngữ cảnh bảng phân tích hiện tại (tối đa 30 dòng)]\n" + preview_md
            )
        except Exception:
            pass

    # Lưu & hiển thị tin nhắn người dùng
    st.session_state.chat_history.append({"role": "user", "content": composed_question})
    with st.chat_message("user"):
        st.markdown(composed_question)

    # Gọi Gemini trả lời
    with st.chat_message("assistant"):
        if not api_key_chat:
            st.error("Chưa có GEMINI_API_KEY. Hãy cấu hình trong Secrets hoặc nhập ở Sidebar.")
        else:
            try:
                client = genai.Client(api_key=api_key_chat)
                model_name = "gemini-2.5-flash"

                system_hint = (
                    "Bạn là trợ lý AI chuyên phân tích tài chính. "
                    "Trả lời ngắn gọn, có lập luận và trích số liệu khi cần. "
                    "Nếu thiếu dữ liệu, hãy nêu giả định rõ ràng."
                )

                gemini_contents = _to_gemini_contents(
                    st.session_state.chat_history, system_hint=system_hint
                )

                with st.spinner("Gemini đang soạn trả lời..."):
                    resp = client.models.generate_content(
                        model=model_name,
                        contents=gemini_contents
                    )
                    answer = getattr(resp, "text", None) or "Không nhận được nội dung phản hồi từ Gemini."

                st.markdown(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})

            except APIError as e:
                st.error(f"Lỗi gọi Gemini API: {e}")
            except Exception as e:
                st.error(f"Đã xảy ra lỗi không xác định khi chat: {e}")
# ================== HẾT KHUNG CHAT HỎI – ĐÁP VỚI GEMINI (THÊM MỚI) ====================
