import streamlit as st
import pytesseract
from PIL import Image, ImageOps, ImageEnhance
import numpy as np
from datetime import datetime
import io
import re
import piexif

# 1. 페이지 설정
st.set_page_config(page_title="스마트 네이머", layout="centered")

# [디자인] 모바일 최적화 및 요소 간격 확보
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; padding-bottom: 5rem !important; }
    .main-title { font-size: 1.6rem !important; font-weight: bold; margin-bottom: 1rem; }
    
    /* 요소 간격 확보 */
    div.stButton, div.stDownloadButton, div.stTextInput { margin-top: 10px; margin-bottom: 10px; }

    /* 파일명 표시 박스 */
    .filename-box {
        background-color: #f0f7ff;
        border: 2px solid #007AFF;
        padding: 15px;
        border-radius: 10px;
        font-weight: bold;
        color: #007AFF;
        word-break: break-all;
        margin: 15px 0;
    }
    
    /* 이미지 크기 조절 */
    .stImage > img { max-width: 100%; height: auto; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">📂 스마트 AI 네이머</div>', unsafe_allow_html=True)

# [함수] 이미지 전처리
def preprocess_image(image):
    return ImageEnhance.Contrast(ImageOps.grayscale(image)).enhance(2.5)

# [함수] 파일명 또는 메타데이터에서 날짜 추출
def extract_date(uploaded_file, image):
    # 1. 파일 이름에서 날짜 형식 (YYYY-MM-DD) 검색
    filename = uploaded_file.name
    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
    
    if date_match:
        # 찾은 경우 YYYY.MM.DD 형식으로 반환
        return f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
    
    # 2. 파일 이름에 없으면 EXIF 메타데이터 확인
    try:
        exif_dict = piexif.load(image.info['exif'])
        date_str = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S').strftime('%Y.%m.%d')
    except:
        # 3. 모두 없으면 오늘 날짜 반환
        return datetime.now().strftime('%Y.%m.%d')

# 파일 업로드
uploaded_file = st.file_uploader("사진을 선택하세요", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file:
    img = Image.open(uploaded_file)
    
    # [핵심] 날짜 인식 적용
    final_date_prefix = extract_date(uploaded_file, img)
    
    st.image(img)
    st.write(f"📅 **인식된 날짜:** {final_date_prefix}")

    if st.button("🔍 이미지 분석 시작", use_container_width=True):
        with st.spinner("단어를 분석 중..."):
            processed_img = preprocess_image(img)
            text = pytesseract.image_to_string(processed_img, lang='kor+eng', config='--psm 11')
            words = re.findall(r'[가-힣a-zA-Z0-9]{2,}', text)
            st.session_state.keywords = list(dict.fromkeys(words))[:8]
        st.toast("분석 완료!")

    if 'keywords' in st.session_state and st.session_state.keywords:
        st.write("▼ 키워드 선택")
        selected = st.pills("키워드", st.session_state.keywords, selection_mode="multi", label_visibility="collapsed")
        st.session_state.selected_list = selected

    st.write("---")
    custom_name = st.text_input("📝 직접 이름 입력", placeholder="추가 내용을 입력하세요")

    # 파일명 조합 (YYYY.MM.DD_ 형식 적용)
    selected_list = st.session_state.get('selected_list', [])
    selected_str = "_".join(selected_list).replace(" ", "")
    
    name_parts = [final_date_prefix] # 인식된 날짜 (YYYY.MM.DD)
    if selected_str: name_parts.append(selected_str)
    if custom_name: name_parts.append(custom_name.strip().replace(" ", "_"))
    
    # 부품들을 '_'로 잇고 확장자 추가
    final_filename = f"{'_'.join(name_parts)}.png"

    # 최종 파일명 강조
    st.markdown(f'<div class="filename-box">{final_filename}</div>', unsafe_allow_html=True)
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button(
        label="💾 이 이름으로 저장하기",
        data=buf.getvalue(),
        file_name=final_filename,
        mime="image/png",
        use_container_width=True
    )
