import streamlit as st
import easyocr
from PIL import Image
import numpy as np

st.set_page_config(page_title="AI 텍스트 추출기", layout="centered")

st.title("🔍 이미지 텍스트 분석기")
st.write("이미지를 업로드하면 AI가 한글과 영어를 읽어줍니다.")

# 모델 로드 (캐싱을 통해 속도 향상)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['ko', 'en'])

reader = load_reader()

uploaded_file = st.file_uploader("이미지를 선택하세요...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='업로드된 이미지', use_container_width=True)
    
    with st.spinner('AI가 글자를 읽고 있습니다...'):
        # OCR 분석
        img_np = np.array(image)
        results = reader.readtext(img_np, detail=0)
        
    st.subheader("📝 추출된 결과")
    if results:
        for text in results:
            st.info(text)
    else:
        st.warning("텍스트를 찾지 못했습니다.")
