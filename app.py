import streamlit as st
import pytesseract
from PIL import Image
import numpy as np
from datetime import datetime
import io
import re

# 페이지 설정
st.set_page_config(page_title="AI 스마트 파일 네이머", layout="centered")

# 디자인 최적화 (이미지 크기 및 간격)
st.markdown("""
    <style>
    .stImage > img { max-width: 320px; border-radius: 10px; border: 1px solid #ddd; }
    .stButton > button { border-radius: 20px; height: 3em; background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

st.title("📂 가벼운 AI 파일 네이머")

# 파일 업로드
uploaded_file = st.file_uploader("사진 업로드", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file:
    img = Image.open(uploaded_file)
    
    # 2컬럼 레이아웃 (세로 길이 축소)
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.image(img, caption="미리보기")

    with col2:
        if st.button("🔍 텍스트 분석 시작", use_container_width=True):
            with st.spinner("단어 읽는 중..."):
                # Tesseract 실행 (한글 + 영어 설정)
                # config 설명: --psm 11은 텍스트 영역을 최대한 많이 찾아내라는 설정입니다.
                text = pytesseract.image_to_string(img, lang='kor+eng', config='--psm 11')
                
                # 특수문자 제거 및 단어 정제 (2글자 이상 단어 추출)
                words = re.findall(r'[가-힣a-zA-Z0-9]{2,}', text)
                st.session_state.keywords = list(dict.fromkeys(words))[:6]
            st.toast("분석 완료!", icon="✨")

        # 키워드 선택 (Pills - 한눈에 보임)
        if 'keywords' in st.session_state and st.session_state.keywords:
            st.write("**추천 키워드:**")
            selected = st.pills("키워드", st.session_state.keywords, selection_mode="multi", label_visibility="collapsed")
            st.session_state.selected_list = selected
        else:
            st.session_state.selected_list = []

    # 이름 확정 섹션
    st.divider()
    custom_name = st.text_input("직접 이름 추가", placeholder="예: 거실_인테리어")

    # 파일명 조합
    date_str = datetime.now().strftime("%Y%m%d")
    selected_str = "_".join(st.session_state.get('selected_list', [])).replace(" ", "")
    
    name_parts = [date_str]
    if selected_str: name_parts.append(selected_str)
    if custom_name: name_parts.append(custom_name.strip().replace(" ", "_"))
    
    final_name = f"{'_'.join(name_parts)}.png"

    st.success(f"📁 파일명: `{final_name}`")

    # 저장 버튼
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button(
        label="💾 이 이름으로 저장하기",
        data=buf.getvalue(),
        file_name=final_name,
        mime="image/png",
        use_container_width=True
    )
