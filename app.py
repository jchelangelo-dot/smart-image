import streamlit as st
import easyocr
from PIL import Image
import numpy as np
from datetime import datetime
import io

# 1. 페이지 설정 (아이콘과 제목)
st.set_page_config(page_title="스마트 파일 네이머", layout="centered")

# CSS를 이용해 간격 및 이미지 크기 미세 조정
st.markdown("""
    <style>
    .stImage > img { max-width: 350px; border-radius: 10px; margin-bottom: 10px; }
    .stButton > button { border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📂 AI 파일 네이머")

# 2. 모델 로드 (최초 1회)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['ko', 'en'], gpu=False)

# 로딩 후 잠깐만 메시지 띄우기
if 'model_ready' not in st.session_state:
    with st.spinner("AI 준비 중..."):
        st.session_state.reader = load_reader()
        st.session_state.model_ready = True
        st.toast("✅ 모델 준비 완료!", icon="🤖")

# 3. 파일 업로드
uploaded_file = st.file_uploader("사진 업로드", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file:
    img = Image.open(uploaded_file)
    
    # 레이아웃을 2컬럼으로 나누어 세로 길이를 줄임
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.image(img, caption="미리보기", use_container_width=False)

    with col2:
        if st.button("🔍 텍스트 분석 시작", use_container_width=True):
            with st.spinner("분석 중..."):
                img_np = np.array(img.convert('RGB'))
                raw_results = st.session_state.reader.readtext(img_np, detail=0)
                st.session_state.keywords = list(dict.fromkeys([w.strip() for w in raw_results if len(w.strip()) >= 2]))[:6]

        # 4. 키워드 선택 (Pills 형태 - 한눈에 다 보임)
        if 'keywords' in st.session_state and st.session_state.keywords:
            st.write("**추천 키워드 (클릭하여 선택):**")
            selected = st.pills("키워드", st.session_state.keywords, selection_mode="multi")
            st.session_state.selected_list = selected
        else:
            st.session_state.selected_list = []

    # 5. 이름 확정 및 저장 섹션
    st.divider()
    custom_name = st.text_input("직접 이름 추가", placeholder="예: 거실_인테리어")

    # 파일명 조합
    date_str = datetime.now().strftime("%Y%m%d")
    selected_str = "_".join(st.session_state.get('selected_list', [])).replace(" ", "_")
    
    name_parts = [date_str]
    if selected_str: name_parts.append(selected_str)
    if custom_name: name_parts.append(custom_name.strip().replace(" ", "_"))
    
    final_name = f"{'_'.join(name_parts)}.png"

    st.success(f"📁 파일명: `{final_name}`")

    # 다운로드 버튼
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button(
        label="💾 이 이름으로 저장하기",
        data=buf.getvalue(),
        file_name=final_name,
        mime="image/png",
        use_container_width=True
    )
