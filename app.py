import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. API 설정
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Streamlit Cloud 설정(Secrets)에서 GEMINI_API_KEY를 먼저 등록해주세요.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 2. 모델 설정 (최신 라이브러리 기준 표준 호출)
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("📂 스마트 AI 네이머")

uploaded_file = st.file_uploader("이미지 선택", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img)

    if st.button("🚀 AI 분석 시작", use_container_width=True):
        try:
            with st.spinner("AI가 분석 중입니다..."):
                # 최신 방식의 분석 요청
                response = model.generate_content([
                    "이 이미지의 핵심 키워드 5개를 콤마(,)로 구분해서 단어만 답해줘.", 
                    img
                ])
                st.success(f"추천 키워드: {response.text}")
                st.session_state.keywords = [w.strip() for w in response.text.split(',')]
        except Exception as e:
            # 여전히 에러가 난다면 상세 내용을 보여줌
            st.error(f"분석 중 오류 발생: {str(e)}")
            st.info("requirements.txt의 라이브러리 버전이 0.7.2 이상인지 확인해주세요.")
