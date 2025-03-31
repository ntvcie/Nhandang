import os
import tempfile
import time
from PIL import Image
import streamlit as st
import google.generativeai as genai
# Cấu hình trang Streamlit
st.set_page_config(
    page_title="AI Trợ giúp",
    layout="wide",
    page_icon="✅",
    initial_sidebar_state="expanded",
)
# Ẩn các phần không cần thiết của Streamlit
hide_st_style = """
    <style>
        .block-container {
            padding-top: 0rem;  /* Giảm khoảng cách phía trên */
            padding-left: 1rem;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Hàm tạo dòng ký tự với độ trễ (simulate delay)
def stream_output(text):
    for char in text:
        yield char
        time.sleep(0.01)  # Simulate delay

# Hàm tạo mô tả cho hình ảnh sử dụng Google Gemini API
def generate_image_caption(uploaded_file):
    if uploaded_file is not None:
        try:
            # Mở tệp dưới dạng hình ảnh
            image = Image.open(uploaded_file)

            # Prompt mặc định cho mô hình
            prompt = """
            Trường hợp 1: Hình ảnh có nội dung về Đồ thị hàm lượng khí CO:
            - Nếu nồng độ CO tăng dần theo thời gian, điều đó cho thấy quá trình cháy đang diễn ra.
            - Nếu CO tăng liên tục và với tốc độ nhanh, quá trình cháy đang diễn ra mạnh mẽ.
              Đây là dấu hiệu đặc trưng của hiện tượng than tự cháy.
            - Ngược lại, nếu nồng độ CO chỉ tăng trong vài phút rồi giảm, đó không phải là than tự cháy 
              mà là hiện tượng phát sinh do hoạt động nổ mìn trong khai thác than hầm lò.
            Từ đó hãy nhận xét xem Hình này có hiện tượng than tự cháy không?
            Nếu không phải thì ngoài việc phân tích, giải thích thật chi tiết hãy kết luận là:
            Mặc dù trong thời điểm quan sát chưa có dấu hiệu của hiện tượng than tự cháy hoặc mức độ ôxy hóa than thấp,
            tuy nhiên vẫn cần tiếp tục theo dõi hàm lượng khí CO để quan trắc than tự cháy tại khu vực này.

            Trường hợp 2: Hình ảnh có nội dung về Đồ thị nhiệt độ:
            - Nếu nhiệt độ tăng dần theo thời gian, điều đó cho thấy quá trình ôxy hóa than đang diễn ra từ từ.
            - Nếu nhiệt độ tăng liên tục và với tốc độ nhanh, quá trình ôxy hóa than đang diễn ra mạnh mẽ.
              Đây là dấu hiệu đặc trưng của hiện tượng than tự cháy (còn gọi là cháy nội sinh trong than).
            - Ngược lại, nếu nhiệt độ chỉ tăng trong vài phút rồi giảm, hoặc không có xu hướng tăng rõ rệt
              thì đó không phải là than tự cháy.
            Từ đó hãy nhận xét xem Hình này có hiện tượng than tự cháy không?
            Nếu không phải thì ngoài việc phân tích, giải thích thật chi tiết hãy kết luận là:
            Mặc dù trong thời điểm quan sát chưa có dấu hiệu của hiện tượng than tự cháy hoặc mức độ ôxy hóa than thấp,
            tuy nhiên vẫn cần tiếp tục theo dõi nhiệt độ để quan trắc than tự cháy tại khu vực này.
            """

            # Cấu hình mô hình Google Gemini
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            model = genai.GenerativeModel("gemini-2.0-flash-exp")

            # Gửi yêu cầu tạo mô tả
            response = model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            return f"Lỗi khi xử lý hình ảnh: {str(e)}"
    else:
        return "Vui lòng tải lên một hình ảnh hợp lệ!"

# Hàm chính của ứng dụng
def main():
    st.markdown("<h3 style='font-size: 18px; color: #1E90FF;'>🌄 Ứng dụng AI để phân tích, phát hiện cảnh báo hiện tượng than tự cháy.</h3>", unsafe_allow_html=True)

    # Widget tải lên hình ảnh
    uploaded_file = st.file_uploader("Tải lên hình ảnh", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        # Tạo hai cột: cột 1 hiển thị hình ảnh, cột 2 hiển thị trả lời của AI
        col1, col2 = st.columns([1, 2])  # Tỷ lệ chiều rộng cột: 1 phần cho hình ảnh, 2 phần cho trả lời

        with col1:
            st.image(uploaded_file, caption='Ảnh đồ thị', use_container_width=True)

        with col2:
            with st.spinner(text="Đang xử lý..."):
                st.snow()
                # Lưu ảnh vào file tạm để truyền vào hàm
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                    image = Image.open(uploaded_file)
                    image.save(tmpfile.name, format="PNG")
                    tmpfile_path = tmpfile.name

                # Gọi AI để phân tích
                caption = generate_image_caption(tmpfile_path)
                st.write_stream(stream_output("Trả lời: " + caption))
                st.balloons()
    else:
        st.warning("Vui lòng tải lên một hình ảnh hợp lệ!")

# Chạy ứng dụng
if __name__ == "__main__":
    main()
