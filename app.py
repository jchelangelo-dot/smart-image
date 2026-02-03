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
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">📂 스마트 AI 네이머</div>', unsafe_allow_html=True)

# 2. Secrets에서 API 키 로드 및 설정
try:
    # st.secrets를 통해 안전하게 키를 가져옵니다.
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # 최신 안정화 모델인 gemini-1.5-flash를 사용합니다.
    model = genai.GenerativeModel('gemini-1.5-flash')
except KeyError:
    st.error("⚠️ Streamlit Settings > Secrets에 'GEMINI_API_KEY'를 먼저 설정해 주세요.")
    st.stop()
except Exception as e:
    st.error(f"⚠️ 설정 오류: {e}")
    st.stop()

# [함수] 날짜 인식 로직 강화
def extract_date(uploaded_file, image):
    filename = uploaded_file.name
    # 파일명에서 2026-01-27 또는 20260127 등 패턴 찾기
    date_match = re.search(r'(\d{4})[-_.]?(\d{2})[-_.]?(\d{2})', filename)
    if date_match:
        return f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}"
    try:
        # 사진 촬영 정보(EXIF) 확인
        exif_dict = piexif.load(image.info['exif'])
        date_str = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S').strftime('%Y.%m.%d')
    except:
        return datetime.now().strftime('%Y.%m.%d')

# 3. 파일 업로드 섹션
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file:
    img = Image.open(uploaded_file)
    date_prefix = extract_date(uploaded_file, img)
    
    st.image(img)
    st.write(f"📅 인식된 날짜: **{date_prefix}**")

    # AI 분석 버튼
    if st.button("🚀 AI 키워드 분석 시작", use_container_width=True):
        with st.spinner("AI가 이미지를 정밀 분석 중입니다..."):
            try:
                # 최신 API 호출 방식 적용
                response = model.generate_content([
                    "이 이미지의 핵심 내용을 파악해서 파일 이름으로 쓰기 좋은 단어 5개를 콤마(,)로 구분해서 답해줘. 단어만 보내줘.", 
                    img
                ])
                # 결과 텍스트 정제
                words = [w.strip() for w in response.text.replace('\n', '').split(',') if len(w.strip()) >= 1]
                st.session_state.keywords = words
                st.toast("분석 완료!")
            except Exception as e:
                st.error("분석 중 오류가 발생했습니다. API 키나 모델 설정을 확인해 주세요.")
                st.info(f"상세 에러: {e}")

    # 키워드 선택 (Pills)
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
    
    # 가독성 높은 결과창
    st.markdown(f'<div class="filename-box">{final_name}</div>', unsafe_allow_html=True)
    
    # 다운로드 버튼
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button(
        label="💾 이 이름으로 이미지 저장",
        data=buf.getvalue(),
        file_name=final_name,
        mime="image/png",
        use_container_width=True
    )
