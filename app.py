import streamlit as st
import google.generativeai as genai
from PIL import Image
from datetime import datetime
import io
import re
import piexif

# 1. 페이지 설정 및 모바일 가독성 최적화
st.set_page_config(page_title="스마트 AI 네이머", layout="centered")
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; }
    .main-title { font-size: 1.6rem !important; font-weight: bold; margin-bottom: 1rem; }
    .filename-box { background-color: #f0f7ff; border: 2px solid #007AFF; padding: 15px; border-radius: 10px; font-weight: bold; color: #007AFF; font-size: 1.1rem; word-break: break-all; margin: 15px 0; }
    .stImage > img { max-width: 100%; border-radius: 12px; margin: 0 auto; display: block; }
    .stButton > button { height: 3.5rem; border-radius: 15px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">📂 스마트 AI 네이머</div>', unsafe_allow_html=True)

# [핵심] Secrets에서 API 키 가져오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("⚠️ Streamlit Secrets에 'GEMINI_API_KEY'가 설정되지 않았습니다.")
    st.stop()

def extract_date(uploaded_file, image):
    filename = uploaded_file.name
    # 파일명 내 날짜 패턴 인식 (YYYY-MM-DD 또는 YYYYMMDD)
    date_match = re.search(r'(\d{4})[-_.]?(\d{2})[-_.]?(\d{2})', filename)
    if date_match:
        return f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
    try:
        exif_dict = piexif.load(image.info['exif'])
        date_str = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S').strftime('%Y.%m.%d')
    except:
        return datetime.now().strftime('%Y.%m.%d')

# 파일 업로드
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file:
    img = Image.open(uploaded_file)
    date_prefix = extract_date(uploaded_file, img)
    
    st.image(img)
    st.write(f"📅 인식된 날짜: **{date_prefix}**")

    # AI 분석 버튼
    if st.button("🚀 AI 키워드 추출 시작", use_container_width=True):
        with st.spinner("AI가 분석 중입니다..."):
            try:
                # 구글 AI에게 파일명용 키워드 요청
                response = model.generate_content([
                    "이 이미지에서 파일명으로 쓰기 좋은 핵심 명사 5개를 콤마로 구분해서 짧게 답해줘. 예: 거실, 인테리어, 가구, 조명, 디자인", 
                    img
                ])
                # 결과 텍스트에서 단어만 분리
                words = [w.strip() for w in response.text.replace('\n', '').split(',') if len(w.strip()) >= 1]
                st.session_state.keywords = words
                st.toast("분석 완료!")
            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {e}")

    # 키워드 선택 (Pills)
    if 'keywords' in st.session_state:
        selected = st.pills("추천 키워드 (멀티 선택 가능)", st.session_state.keywords, selection_mode="multi")
        st.session_state.selected_list = selected

    st.write("---")
    custom_name = st.text_input("📝 직접 이름 추가", placeholder="예: 유튜브_스크린샷")

    # 최종 파일명 조합
    selected_list = st.session_state.get('selected_list', [])
    name_parts = [date_prefix]
    if selected_list:
        name_parts.append("_".join(selected_list).replace(" ", ""))
    if custom_name:
        name_parts.append(custom_name.strip().replace(" ", "_"))
    
    final_name = f"{'_'.join(name_parts)}.png"
    
    # 가독성 높은 파일명 박스
    st.markdown(f'<div class="filename-box">{final_name}</div>', unsafe_allow_html=True)
    
    # 다운로드 준비
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button(
        label="💾 이 이름으로 저장하기",
        data=buf.getvalue(),
        file_name=final_name,
        mime="image/png",
        use_container_width=True
    )
