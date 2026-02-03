import streamlit as st
import easyocr  # 성능을 위해 다시 복귀
from PIL import Image, ImageOps
import numpy as np
from datetime import datetime
import io
import re

# 1. 페이지 설정 및 디자인 (최상단 밀착)
st.set_page_config(page_title="스마트 네이머", layout="centered")
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    .main-title { font-size: 1.5rem !important; font-weight: bold; margin-bottom: 0.5rem; }
    .filename-box { background-color: #f0f7ff; border: 2px solid #007AFF; padding: 12px; border-radius: 10px; font-weight: bold; color: #007AFF; word-break: break-all; }
    .stImage > img { max-width: 100%; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">📂 스마트 AI 네이머</div>', unsafe_allow_html=True)

# [핵심] EasyOCR을 메모리 효율적으로 로드
@st.cache_resource
def load_ocr():
    # 모델을 읽어올 때 한글과 영어를 명시하고 GPU 없이 CPU 최적화
    return easyocr.Reader(['ko', 'en'], gpu=False)

def extract_date(uploaded_file):
    filename = uploaded_file.name
    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
    if date_match:
        return f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
    return datetime.now().strftime('%Y.%m.%d')

# 모델 사전 로드
reader = load_ocr()

uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file:
    img = Image.open(uploaded_file)
    date_prefix = extract_date(uploaded_file)
    
    st.image(img)
    st.write(f"📅 인식된 날짜: **{date_prefix}**")

    if st.button("🔍 고성능 AI 분석 시작 (약 5초 소요)", use_container_width=True):
        with st.spinner("AI가 정밀하게 글자를 읽고 있습니다..."):
            # 딥러닝 인식을 위해 RGB 변환 및 넘파이 변환
            img_np = np.array(img.convert('RGB'))
            # [EasyOCR 실행]
            results = reader.readtext(img_np, detail=0)
            # 단어 정제: 2글자 이상, 특수문자 제외
            clean_words = [re.sub(r'[^\w]', '', w) for w in results if len(w.strip()) >= 2]
            st.session_state.keywords = list(dict.fromkeys(clean_words))[:10]
        st.toast("분석 완료!", icon="✅")

    if 'keywords' in st.session_state and st.session_state.keywords:
        selected = st.pills("추천 키워드", st.session_state.keywords, selection_mode="multi")
        st.session_state.selected_list = selected

    st.divider()
    custom_name = st.text_input("📝 직접 이름 추가", placeholder="예: 인테리어_아이디어")

    # 파일명 조합
    selected_list = st.session_state.get('selected_list', [])
    selected_str = "_".join(selected_list)
    name_parts = [date_prefix]
    if selected_str: name_parts.append(selected_str)
    if custom_name: name_parts.append(custom_name.strip().replace(" ", "_"))
    
    final_name = f"{'_'.join(name_parts)}.png"
    st.markdown(f'<div class="filename-box">{final_name}</div>', unsafe_allow_html=True)
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button("💾 저장하기", data=buf.getvalue(), file_name=final_name, use_container_width=True)
