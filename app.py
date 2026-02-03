import streamlit as st
import google.generativeai as genai
from PIL import Image
from datetime import datetime
import io
import re
import piexif

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="스마트 AI 네이머", layout="centered")
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; }
    .filename-box { background-color: #f0f7ff; border: 2px solid #007AFF; padding: 15px; border-radius: 10px; font-weight: bold; color: #007AFF; font-size: 1.2rem; word-break: break-all; margin: 15px 0; }
    </style>
    """, unsafe_allow_width=True)

st.title("📂 초정밀 AI 파일 네이머")

# API 키 설정 (보안을 위해 입력창 제공)
api_key = st.sidebar.text_input("AIzaSyBFgIMOPpV2qUraV83fgfkxDSUtw_k_6dM", type="password")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.warning("왼쪽 사이드바에 Gemini API Key를 입력해야 성능이 활성화됩니다.")

def extract_date(uploaded_file, image):
    filename = uploaded_file.name
    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
    if date_match:
        return f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
    try:
        exif_dict = piexif.load(image.info['exif'])
        date_str = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S').strftime('%Y.%m.%d')
    except:
        return datetime.now().strftime('%Y.%m.%d')

uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_file and api_key:
    img = Image.open(uploaded_file)
    date_prefix = extract_date(uploaded_file, img)
    
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.image(img, caption=f"📅 날짜: {date_prefix}")

    with col2:
        if st.button("🚀 초정밀 AI 분석 시작", use_container_width=True):
            with st.spinner("구글 AI가 이미지를 읽는 중..."):
                # AI에게 이미지와 프롬프트 전달
                response = model.generate_content([
                    "이 이미지 속의 주요 텍스트를 추출하고, 파일명으로 쓰기 좋은 핵심 키워드 5개를 단어 형태로만 나열해줘. 예: 거실, 인테리어, 가구, 조명, 디자인", 
                    img
                ])
                # 결과에서 단어만 추출
                ai_words = re.findall(r'[가-힣a-zA-Z0-9]{2,}', response.text)
                st.session_state.keywords = list(dict.fromkeys(ai_words))[:8]
            st.toast("분석 완료!", icon="✨")

        if 'keywords' in st.session_state:
            selected = st.pills("키워드 선택", st.session_state.keywords, selection_mode="multi")
            st.session_state.selected_list = selected

    st.divider()
    custom_name = st.text_input("📝 직접 이름 추가", placeholder="예: 유튜브_스크린샷")

    selected_str = "_".join(st.session_state.get('selected_list', [])).replace(" ", "")
    name_parts = [date_prefix]
    if selected_str: name_parts.append(selected_str)
    if custom_name: name_parts.append(custom_name.strip().replace(" ", "_"))
    
    final_name = f"{'_'.join(name_parts)}.png"
    st.markdown(f'<div class="filename-box">{final_name}</div>', unsafe_allow_html=True)
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button("💾 내 폰에 저장하기", data=buf.getvalue(), file_name=final_name, use_container_width=True)

