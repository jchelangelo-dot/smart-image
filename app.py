import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. API 키 확인
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Secrets에 키가 없습니다!")
    st.stop()

# 2. 가장 안전한 설정법
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("구글 AI 테스트")

uploaded_file = st.file_uploader("사진을 올려주세요", type=["jpg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img)
    
    if st.button("AI야, 이 사진 뭐야?"):
        try:
            # 이미지 용량 최적화 후 전송
            img.thumbnail((512, 512))
            response = model.generate_content(["이 사진을 한 단어로 설명해줘", img])
            st.success(f"결과: {response.text}")
        except Exception as e:
            st.error(f"에러 발생: {e}")
            st.info("이 에러가 또 404라면 앱을 삭제 후 재생성해야 합니다.")
