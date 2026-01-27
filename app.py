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

# [핵심] 요소 겹침 및 잘림 방지를 위한 강제 스타일 적용
st.markdown("""
    <style>
    /* 1. 전체 화면 여백 확보 및 배경 */
    .main { background-color: #ffffff; }
    .block-container { 
        padding-top: 2rem !important; 
        padding-bottom: 5rem !important; /* 하단 버튼이 가려지지 않게 여유 공간 확보 */
        max-width: 95% !important;
    }
    
    /* 2. 요소 간 간격 강제 부여 (Overlap 방지) */
    div.stButton, div.stDownloadButton, div.stTextInput, div.stMultiSelect {
        margin-top: 15px !important;
        margin-bottom: 15px !important;
    }

    /* 3. 텍스트가 잘리지 않도록 높이 자동 조절 */
    .stButton > button, .stDownloadButton > button {
        height: auto !important;
        min-height: 3.5rem !important;
        padding: 10px !important;
        white-space: normal !important; /* 글자가 길어도 다음 줄로 넘어가게 함 */
        line-height: 1.2 !important;
    }

    /* 4. 파일명 박스 (잘림 방지 및 가독성) */
    .filename-box {
        background-color: #f8f9fa;
        border: 2px solid #007AFF;
        padding: 20px;
        border-radius: 10px;
        font-weight: bold;
        color: #007AFF;
        word-break: break-all; /* 긴 파일명도 줄바꿈 처리 */
        margin: 20px 0;
        display: block;
        width: 100%;
    }

    /* 5. 이미지 크기 고정 및 중앙 정렬 */
    .stImage > img {
        max-width: 100% !important;
        height: auto !important;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📂 AI PIC 네이밍")

# [함수] 전처리 및 날짜
def preprocess_image(image):
    return ImageEnhance.Contrast(ImageOps.grayscale(image)).enhance(2.5)

def get_creation_date(image):
    try:
        exif_dict = piexif.load(image.info['exif'])
        date_str = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S').strftime('%Y%m%d')
    except:
        return datetime.now().strftime('%Y%m%d')

# 파일 업로드
uploaded_file = st.file_uploader("사진을 선택하세요", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    detected_date = get_creation_date(img)
    
    # 모바일에서 겹침 방지를 위해 가로 배치가 아닌 세로 배치를 권장하지만, 
    # 일단은 간격을 넓힌 상태로 유지합니다.
    st.image(img)
    st.write(f"📅 **파일 날짜:** {detected_date}")

    if st.button("🔍 이미지 분석 시작 (클릭)", use_container_width=True):
        with st.spinner("단어를 찾는 중..."):
            processed_img = preprocess_image(img)
            text = pytesseract.image_to_string(processed_img, lang='kor+eng', config='--psm 11')
            words = re.findall(r'[가-힣a-zA-Z0-9]{2,}', text)
            st.session_state.keywords = list(dict.fromkeys(words))[:8]
        st.toast("분석 완료!")

    if 'keywords' in st.session_state and st.session_state.keywords:
        st.write("▼ 아래에서 키워드를 선택하세요")
        selected = st.pills("추천 키워드", st.session_state.keywords, selection_mode="multi")
        st.session_state.selected_list = selected

    st.write("---")
    custom_name = st.text_input("📝 직접 이름 입력 (선택)", placeholder="내용을 입력해주세요")

    # 파일명 조합
    selected_list = st.session_state.get('selected_list', [])
    selected_str = "_".join(selected_list).replace(" ", "")
    name_parts = [detected_date]
    if selected_str: name_parts.append(selected_str)
    if custom_name: name_parts.append(custom_name.strip().replace(" ", "_"))
    
    final_name = f"{'_'.join(name_parts)}.png"

    # 최종 파일명 박스
    st.markdown(f'<div class="filename-box">{final_name}</div>', unsafe_allow_html=True)
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button(
        label="💾 위 이름으로 내 폰에 저장",
        data=buf.getvalue(),
        file_name=final_name,
        mime="image/png",
        use_container_width=True
    )


