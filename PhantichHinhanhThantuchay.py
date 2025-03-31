import streamlit as st
from PIL import Image
import google.generativeai as genai
import time
import tempfile
from PIL import ImageGrab
from dotenv import load_dotenv
import os
load_dotenv()

# Đảm bảo biến môi trường đã được thiết lập
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gen-lang-client-0382763815-044c7b8f5c68.json"
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
st.set_page_config(
    page_title="AI trợ giúp",
    layout="wide",
    page_icon="✅",
    initial_sidebar_state="expanded",
)

st.markdown(hide_st_style, unsafe_allow_html=True)
#API key deepseek: sk-997966a4069f4981a0091de5d3fdc79a
# API keys
#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

api_key = os.getenv("GOOGLE_API_KEY")
def stream_output(text):
    for char in text:
        yield char
        time.sleep(0.01)  # Simulate delay
def get_image_from_clipboard():
    try:
        # Lấy dữ liệu từ clipboard
        clipboard_data = pyperclip.paste()

        # Kiểm tra nếu dữ liệu là base64 (ảnh từ clipboard)
        if clipboard_data.startswith("data:image"):
            # Trích xuất phần base64 từ chuỗi
            header, encoded = clipboard_data.split(",", 1)
            image_data = base64.b64decode(encoded)

            # Chuyển đổi dữ liệu base64 thành hình ảnh
            image = Image.open(BytesIO(image_data))
            return image
        else:
            st.warning("Không tìm thấy hình ảnh trong clipboard!")
            return None
    except Exception as e:
        st.error(f"Lỗi khi đọc clipboard: {str(e)}")
        return None

def generate_image_caption(uploaded_file):
    if uploaded_file is not None:
        # Mở tệp dưới dạng hình ảnh
        image = Image.open(uploaded_file)

        # Tạo prompt mặc định cho mô hình
        prompt = """
        Trường hợp 1: Hình ảnh có nội dung về Đồ thị hàm lượng khí CO:
        Nếu nồng độ CO tăng dần theo thời gian, điều đó cho thấy quá trình cháy đang diễn ra. 
        Nếu CO tăng liên tục và với tốc độ nhanh, quá trình cháy đang diễn ra mạnh mẽ. 
        Đây là dấu hiệu đặc trưng của hiện tượng than tự cháy.
        Ngược lại, nếu nồng độ CO chỉ tăng trong vài phút rồi giảm, đó không phải là than tự cháy mà là hiện tượng phát sinh do hoạt động nổ mìn trong khai thác than hầm lò.
        Từ đó hãy nhận xét xem Hình này có hiện tượng than tự cháy không?
        Nếu không phải thì ngoài việc phân tích, giải thích thật chi tiết hãy kết luận là: Mặc dù trong thời điểm quan sát chưa có dấu hiệu của hiện tượng than tự cháy hoặc mức độ ôxy hóa than thấp, tuy nhiên vẫn cần tiếp tục theo dõi hàm lượng khí CO để quan trắc than tự cháy tại khu vực này.
        ==============================================================================================================================================================================================================================================================================================
        Trường hợp 2: Hình ảnh có nội dung về Đồ thị nhiệt độ:
        Nếu nhiệt độ tăng dần theo thời gian, điều đó cho thấy quá trình ôxy hóa than đang diễn ra từ từ. 
        Nếu nhiệt độ tăng liên tục và với tốc độ nhanh, quá trình ôxy hóa than đang diễn ra mạnh mẽ. 
        Đây là dấu hiệu đặc trưng của hiện tượng than tự cháy (còn gọi là cháy nội sinh trong than).
        Ngược lại, nếu nhiệt độ chỉ tăng trong vài phút rồi giảm, hoặc không có xu hướng tăng rõ rệt thì đó không phải là than tự cháy.
        Từ đó hãy nhận xét xem Hình này có hiện tượng than tự cháy không?
        Nếu không phải thì ngoài việc phân tích, giải thích thật chi tiết hãy kết luận là: Mặc dù trong thời điểm quan sát chưa có dấu hiệu của hiện tượng than tự cháy hoặc mức độ ôxy hóa than thấp, tuy nhiên vẫn cần tiếp tục theo dõi nhiệt độ để quan trắc than tự cháy tại khu vực này. 
        """

        # Cấu hình mô hình
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")

        # Gửi yêu cầu tạo caption
        response = model.generate_content([prompt, image])
        return response.text
    else:
        return "Vui lòng tải lên một hình ảnh hợp lệ!"

import base64
def main():
    st.markdown("<h3 style='font-size: 18px; color: #1E90FF;'>🌄 Ứng dụng AI để phân tích, phát hiện cảnh báo hiện tượng than tự cháy.</h3>", unsafe_allow_html=True)

    if st.button("Xử lý"):
        image = get_image_from_clipboard()  # Lấy ảnh từ clipboard

        if image is not None:
            # Tạo hai cột: cột 1 hiển thị hình ảnh, cột 2 hiển thị trả lời của AI
            col1, col2 = st.columns([1, 1])  # Tỷ lệ chiều rộng cột: 1 phần cho hình ảnh, 2 phần cho trả lời
            with col1:
                st.image(image, caption='Ảnh đồ thị', use_container_width=True)

            with col2:
                with st.spinner(text="Đang xử lí..."):
                    st.snow()
                    # Lưu ảnh vào file tạm để truyền vào hàm
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                        image.save(tmpfile.name, format="PNG")
                        tmpfile_path = tmpfile.name

                    # Gọi AI để phân tích
                    caption = generate_image_caption(tmpfile_path)
                    st.write_stream(stream_output("Trả lời: " + caption))
                    st.balloons()
        else:
            st.warning("Không tìm thấy ảnh trong clipboard! Hãy sao chép ảnh trước khi dán.")
if __name__ == "__main__":
    main()
