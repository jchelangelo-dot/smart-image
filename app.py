import streamlit as st
import google.generativeai as genai
from PIL import Image
from datetime import datetime
import io
import re
import piexif

# 페이지 설정
st.set_page_config(page_title="AI 네이머", layout="centered")

# CSS (오타 수정 및 디자인)
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    .filename-box { background-color: #f0f7ff; border: 2px solid #007AFF; padding: 15px; border-radius: 10px; font-weight: bold; color: #007AFF; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# API 설정 (Secrets 확인)
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Secrets에 GEMINI_API_KEY를 설정해주세요.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 모델 로드 (가장 호환성 높은 명칭 사용)
@st.cache_resource
def get_model():
    return genai.GenerativeModel('gemini-1.5-flash')

model = get_model()

def extract_date(uploaded_file, image):
    filename = uploaded_file.name
    date_match = re.search(r'(\d{4})[-_.]?(\d{2})[-_.]?(\d{2})', filename)
    if date_match:
        return f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
    return datetime.now().strftime('%Y.%m.%d')

st.title("📂 스마트 AI 네이머")

uploaded_file = st.file_uploader("이미지 선택", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file:
    img = Image.open(uploaded_file)
    date_prefix = extract_date(uploaded_file, img)
    st.image(img)

    if st.button("🚀 AI 분석 시작", use_container_width=True):
        try:
            # 이미지 전처리 (용량이 너무 크면 오류가 날 수 있어 리사이징)
            img.thumbnail((1024, 1024))
            
            with st.spinner("AI 분석 중..."):
                # 가장 안정적인 프롬프트 방식
                response = model.generate_content(["이 이미지의 핵심 키워드 5개를 콤마로 구분해서 답해줘.", img])
                if response.text:
                    words = [w.strip() for w in response.text.split(',') if len(w.strip()) >= 1]
                    st.session_state.keywords = words
                else:
                    st.error("AI가 결과를 반환하지 않았습니다.")
        except Exception as e:
            st.error(f"분석 실패: {str(e)}")

    if 'keywords' in st.session_state:
        selected = st.pills("키워드 선택", st.session_state.keywords, selection_mode="multi")
        st.session_state.selected_list = selected or []

        # 파일명 조합
        selected_str = "_".join(st.session_state.selected_list)
        final_name = f"{date_prefix}_{selected_str}.png" if selected_str else f"{date_prefix}.png"
        
        st.markdown(f'<div class="filename-box">{final_name}</div>', unsafe_allow_html=True)
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button("💾 저장하기", data=buf.getvalue(), file_name=final_name, use_container_width=True)
