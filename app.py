import streamlit as st
import google.generativeai as genai
from PIL import Image
from datetime import datetime
import io
import re
import piexif

# 1. 페이지 설정 및 디자인 (가독성 최적화)
st.set_page_config(page_title="스마트 AI 네이머", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; }
    .main-title { font-size: 1.6rem !important; font-weight: bold; margin-bottom: 1rem; }
    /* 파일명 표시 박스 */
    .filename-box {
        background-color: #f0f7ff;
        border: 2px solid #007AFF;
        padding: 15px;
        border-radius: 10px;
        font-weight: bold;
        color: #007AFF;
        font-size: 1.1rem;
        word-break: break-all;
        margin: 15px 0;
        text-align: center;
    }
    .stImage > img { max-width: 100%; border-radius: 12px; margin: 0 auto; display: block; }
    .stButton > button { height: 3.5rem; border-radius: 15px; font-weight: bold; background-color: #007AFF; color: white; }
    </style>
    """, unsafe_allow_html=True) # 오타 수정 완료

st.markdown('<div class="main-title">📂 스마트 AI 네이머</div>', unsafe_allow_html=True)

# 2. Secrets에서 API 키 로드
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # 최신 모델 설정
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ Streamlit Secrets에 'GEMINI_API_KEY'를 설정해 주세요.")
    st.stop()

# 날짜 인식 함수 강화 (파일명 우선)
def extract_date(uploaded_file, image):
    filename = uploaded_file.name
    # 파일명에서 YYYY-MM-DD 또는 YYYYMMDD 패턴 찾기
    date_match = re.search(r'(\d{4})[-_.]?(\d{2})[-_.]?(\d{2})', filename)
    if date_match:
        return f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
    try:
        exif_dict = piexif.load(image.info['exif'])
        date_str = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S').strftime('%Y.%m.%d')
    except:
        return datetime.now().strftime('%Y.%m.%d')

# 3. 메인 기능
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file:
    img = Image.open(uploaded_file)
    date_prefix = extract_date(uploaded_file, img)
    
    st.image(img)
    st.write(f"📅 인식된 날짜: **{date_prefix}**")

    if st.button("🚀 AI 키워드 분석 시작", use_container_width=True):
        with st.spinner("이미지를 분석하고 있습니다..."):
            try:
                # AI에게 이미지 분석 요청
                response = model.generate_content([
                    "이 이미지의 핵심 내용을 분석해서 파일 이름으로 쓰기 좋은 단어 5개를 콤마(,)로 구분해서 알려줘. 단어만 출력해줘.", 
                    img
                ])
                # 결과 텍스트 정제
                raw_text = response.text.replace('\n', '')
                words = [w.strip() for w in raw_text.split(',') if len(w.strip()) >= 1]
                st.session_state.keywords = words
                st.toast("분석 완료!")
            except Exception as e:
                st.error(f"분석 실패: {e}")

    if 'keywords' in st.session_state:
        st.write("▼ 파일명에 포함할 단어를 선택하세요")
        selected = st.pills("키워드", st.session_state.keywords, selection_mode="multi", label_visibility="collapsed")
        st.session_state.selected_list = selected

    st.write("---")
    custom_name = st.text_input("📝 직접 이름 추가 (선택)", placeholder="예: 거실_인테리어")

    # 4. 최종 파일명 조합
    selected_list = st.session_state.get('selected_list', [])
    name_parts = [date_prefix]
    
    if selected_list:
        name_parts.append("_".join(selected_list).replace(" ", ""))
    if custom_name:
        name_parts.append(custom_name.strip().replace(" ", "_"))
    
    final_name = f"{'_'.join(name_parts)}.png"
    
    st.markdown(f'<div class="filename-box">{final_name}</div>', unsafe_allow_html=True)
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button(
        label="💾 이 이름으로 이미지 저장",
        data=buf.getvalue(),
        file_name=final_name,
        mime="image/png",
        use_container_width=True
    )
