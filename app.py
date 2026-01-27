import streamlit as st
import pytesseract
from PIL import Image, ImageOps, ImageEnhance
import numpy as np
from datetime import datetime
import io
import re
import piexif

# 1. 페이지 설정 및 모바일 전용 UI 커스텀
st.set_page_config(page_title="스마트 AI 네이머", layout="centered")

# CSS를 사용하여 상단 제목과 여백을 극단적으로 줄입니다.
st.markdown("""
    <style>
    /* 상단 기본 여백 제거 */
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    
    /* 제목 크기 축소 및 상단 밀착 */
    .main-title { font-size: 1.5rem !important; font-weight: bold; margin-bottom: 0.5rem; text-align: left; }
    
    /* 업로드 박스 높이 조절 */
    div[data-testid="stFileUploader"] section { padding: 0.5rem; }
    
    /* 미리보기 이미지 크기 제한 (모바일 배려) */
    .stImage > img { max-width: 250px; border-radius: 8px; margin: 0 auto; display: block; }
    
    /* 버튼들 모서리 둥글게 */
    .stButton > button { border-radius: 12px; height: 2.8rem; font-weight: bold; }
    
    /* 키워드 선택(Pills) 가독성 */
    div[data-testid="stHorizontalBlock"] { gap: 0.5rem; }
    </style>
    """, unsafe_allow_html=True)

# 줄어든 텍스트 제목
st.markdown('<div class="main-title">📂 스마트 AI 네이머</div>', unsafe_allow_html=True)

# [함수] 이미지 전처리 및 날짜 추출
def preprocess_image(image):
    gray_img = ImageOps.grayscale(image)
    enhancer = ImageEnhance.Contrast(gray_img)
    return enhancer.enhance(2.0)

def get_creation_date(image):
    try:
        exif_dict = piexif.load(image.info['exif'])
        date_str = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S').strftime('%Y%m%d')
    except:
        return datetime.now().strftime('%Y%m%d')

# 파일 업로드
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    detected_date = get_creation_date(img)
    
    # 모바일에서도 세로 길이를 줄이기 위해 컬럼 배치
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.image(img)
        st.caption(f"📅 {detected_date}")

    with col2:
        if st.button("🔍 분석 시작", use_container_width=True):
            with st.spinner("분석중.."):
                processed_img = preprocess_image(img)
                text = pytesseract.image_to_string(processed_img, lang='kor+eng', config='--psm 11')
                words = re.findall(r'[가-힣a-zA-Z0-9]{2,}', text)
                st.session_state.keywords = list(dict.fromkeys(words))[:8]
            st.toast("완료!", icon="✨")

        if 'keywords' in st.session_state and st.session_state.keywords:
            # Pills를 사용하여 공간 절약
            selected = st.pills("키워드", st.session_state.keywords, selection_mode="multi")
            st.session_state.selected_list = selected

    # 파일명 설정 구간 (여백 최소화)
    custom_name = st.text_input("직접 이름 추가", placeholder="예: 아이디어_캡처", label_visibility="collapsed")

    # 파일명 조합
    selected_str = "_".join(st.session_state.get('selected_list', [])).replace(" ", "")
    name_parts = [detected_date]
    if selected_str: name_parts.append(selected_str)
    if custom_name: name_parts.append(custom_name.strip().replace(" ", "_"))
    
    final_name = f"{'_'.join(name_parts)}.png"

    # 결과 표시 및 저장 버튼 밀착
    st.code(final_name, language=None)
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button(
        label="💾 저장하기",
        data=buf.getvalue(),
        file_name=final_name,
        mime="image/png",
        use_container_width=True
    )
