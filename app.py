import streamlit as st
import google.generativeai as genai
from PIL import Image
from datetime import datetime
import io
import re
import piexif

# 페이지 설정
st.set_page_config(page_title="스마트 AI 네이머", layout="centered")

# 디자인 최적화 (오타 수정됨: unsafe_allow_html)
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; }
    .main-title { font-size: 1.6rem !important; font-weight: bold; margin-bottom: 0.5rem; }
    .filename-box { background-color: #f0f7ff; border: 2px solid #007AFF; padding: 15px; border-radius: 10px; font-weight: bold; color: #007AFF; font-size: 1.1rem; word-break: break-all; margin: 15px 0; }
    .stImage > img { max-width: 280px; border-radius: 10px; margin: 0 auto; display: block; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">📂 초정밀 AI 파일 네이머</div>', unsafe_allow_html=True)

# API 키 설정 (사이드바)
with st.sidebar:
    st.header("설정")
    api_key = st.text_input("Gemini API Key를 입력하세요", type="password")
    st.info("API Key는 Google AI Studio에서 무료로 발급 가능합니다.")

def extract_date(uploaded_file, image):
    filename = uploaded_file.name
    # 숫자 8자리(20260127) 혹은 6자리 인식 강화
    date_match = re.search(r'(\d{4})[-_.]?(\d{2})[-_.]?(\d{2})', filename)
    if date_match:
        return f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
    try:
        exif_dict = piexif.load(image.info['exif'])
        date_str = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S').strftime('%Y.%m.%d')
    except:
        return datetime.now().strftime('%Y.%m.%d')

uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file:
    img = Image.open(uploaded_file)
    date_prefix = extract_date(uploaded_file, img)
    
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.image(img)
        st.caption(f"📅 인식된 날짜: {date_prefix}")

    with col2:
        if not api_key:
            st.warning("분석을 위해 왼쪽 사이드바에 API Key를 입력해주세요.")
        else:
            if st.button("🚀 초정밀 AI 분석 시작", use_container_width=True):
                try:
                    # [중요] 최신 모델 명칭으로 업데이트
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    with st.spinner("구글 AI가 분석 중..."):
                        response = model.generate_content([
                            "이 이미지에서 파일명으로 쓸 핵심 명사 5개를 콤마로 구분해서 대답해줘.", img
                        ])
                        words = [w.strip() for w in response.text.split(',') if len(w.strip()) >= 1]
                        st.session_state.keywords = words
                    st.toast("분석 완료!")
                except Exception as e:
                    st.error(f"오류: API 키를 다시 확인해주세요.")

        if 'keywords' in st.session_state:
            selected = st.pills("키워드 선택", st.session_state.keywords, selection_mode="multi")
            st.session_state.selected_list = selected

    st.write("---")
    custom_name = st.text_input("📝 직접 이름 추가", placeholder="예: 유튜브_스크린샷")

    selected_list = st.session_state.get('selected_list', [])
    name_parts = [date_prefix]
    if selected_list: name_parts.append("_".join(selected_list))
    if custom_name: name_parts.append(custom_name.strip().replace(" ", "_"))
    
    final_name = f"{'_'.join(name_parts)}.png"
    st.markdown(f'<div class="filename-box">{final_name}</div>', unsafe_allow_html=True)
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button("💾 파일 저장하기", data=buf.getvalue(), file_name=final_name, use_container_width=True)
