import streamlit as st
import pytesseract
from PIL import Image, ImageOps, ImageEnhance
import numpy as np
from datetime import datetime
import io
import re
import piexif

# 페이지 설정
st.set_page_config(page_title="스마트 AI 파일 관리자", layout="centered")

# CSS 최적화
st.markdown("""
    <style>
    .stImage > img { max-width: 300px; border-radius: 10px; border: 1px solid #ddd; }
    .stButton > button { border-radius: 20px; height: 3em; background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

st.title("📂 스마트 AI 파일 네이머")

# [함수] 이미지 전처리: 대비 향상 및 흑백화
def preprocess_image(image):
    # 1. 그레이스케일 변환
    gray_img = ImageOps.grayscale(image)
    # 2. 대비(Contrast) 대폭 향상
    enhancer = ImageEnhance.Contrast(gray_img)
    enhanced_img = enhancer.enhance(2.0) 
    return enhanced_img

# [함수] 파일 생성(촬영) 날짜 추출
def get_creation_date(image, uploaded_file):
    try:
        # 1. EXIF 데이터 확인 (사진 촬영 날짜)
        exif_dict = piexif.load(image.info['exif'])
        date_str = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S').strftime('%Y%m%d')
    except:
        # 2. 메타데이터가 없으면 오늘 날짜 사용
        return datetime.now().strftime('%Y%m%d')

# 파일 업로드
uploaded_file = st.file_uploader("사진 업로드", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file:
    img = Image.open(uploaded_file)
    
    # 생성 날짜 감지
    detected_date = get_creation_date(img, uploaded_file)
    
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.image(img, caption=f"날짜 감지: {detected_date}")

    with col2:
        if st.button("🔍 인식률 향상 분석 시작", use_container_width=True):
            with st.spinner("이미지 최적화 및 단어 추출 중..."):
                # 전처리 적용 후 텍스트 읽기
                processed_img = preprocess_image(img)
                text = pytesseract.image_to_string(processed_img, lang='kor+eng', config='--psm 11')
                
                # 단어 정제
                words = re.findall(r'[가-힣a-zA-Z0-9]{2,}', text)
                st.session_state.keywords = list(dict.fromkeys(words))[:6]
            st.toast("분석 및 전처리 완료!", icon="✨")

        if 'keywords' in st.session_state and st.session_state.keywords:
            st.write("**추천 키워드:**")
            selected = st.pills("키워드", st.session_state.keywords, selection_mode="multi", label_visibility="collapsed")
            st.session_state.selected_list = selected
        else:
            st.session_state.selected_list = []

    st.divider()
    custom_name = st.text_input("직접 이름 추가", placeholder="예: 인테리어_아이디어")

    # 파일명 조합 (감지된 날짜 사용)
    selected_str = "_".join(st.session_state.get('selected_list', [])).replace(" ", "")
    
    name_parts = [detected_date] # 파일 생성/촬영 날짜 적용
    if selected_str: name_parts.append(selected_str)
    if custom_name: name_parts.append(custom_name.strip().replace(" ", "_"))
    
    final_name = f"{'_'.join(name_parts)}.png"

    st.success(f"📁 생성될 파일명: `{final_name}`")

    # 저장 버튼
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button(
        label="💾 최종 파일명으로 저장",
        data=buf.getvalue(),
        file_name=final_name,
        mime="image/png",
        use_container_width=True
    )
