import streamlit as st
import easyocr
from PIL import Image
import numpy as np
from datetime import datetime
import io

# [페이지 설정]
st.set_page_config(page_title="AI 스마트 파일 관리자", layout="centered")

st.title("📂 AI 이미지 분석 & 파일 네이머")
st.write("이미지를 업로드하면 AI가 글자를 읽고 파일 이름을 추천해줍니다.")

# [1. AI 모델 로드 - GPU가 없는 환경에 맞춰 최적화]
@st.cache_resource
def load_reader():
    # gpu=False 설정은 서버 환경에서 속도와 안정성을 높여줍니다.
    return easyocr.Reader(['ko', 'en'], gpu=False)

# 모델 로드 시도
try:
    reader = load_reader()
except Exception as e:
    st.error(f"모델을 불러오는 중 오류가 발생했습니다. requirements.txt를 확인해주세요: {e}")

# [2. 파일 업로드 섹션]
uploaded_file = st.file_uploader("사진을 선택하세요 (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 이미지 열기
    image = Image.open(uploaded_file)
    
    st.divider()
    st.subheader("🖼️ 업로드된 이미지")
    # 최신 버전에 맞춘 이미지 출력 방식
    st.image(image, use_container_width=True)
    st.divider()

    # [3. AI 분석]
    with st.spinner('이미지 속 글자를 분석하고 있습니다...'):
        # PIL 이미지를 AI가 인식 가능한 배열로 변환
        img_array = np.array(image.convert('RGB'))
        # 텍스트 추출
        raw_results = reader.readtext(img_array, detail=0)
    
    # [4. 파일명 설정 UI]
    st.subheader("✍️ 파일 이름 짓기")
    
    if raw_results:
        # 중복 제거 및 의미 있는 단어 4개 추출
        unique_words = list(dict.fromkeys([w.strip() for w in raw_results if len(w.strip()) >= 2]))
        recommended_pool = unique_words[:4]

        selected_keywords = st.multiselect(
            "AI 추천 키워드 선택", 
            options=recommended_pool,
            default=recommended_pool[:1] if recommended_pool else []
        )
    else:
        st.info("글자를 찾지 못했습니다. 직접 이름을 입력해주세요.")
        selected_keywords = []

    custom_name = st.text_input("직접 이름 추가", placeholder="예: 영수증_식비")

    # [5. 파일명 조합]
    current_date = datetime.now().strftime("%Y%m%d")
    name_parts = [current_date]
    
    if selected_keywords:
        name_parts.append("_".join(selected_keywords).replace(" ", "_"))
    if custom_name:
        name_parts.append(custom_name.strip().replace(" ", "_"))
    
    final_filename = f"{'_'.join(name_parts)}.png"

    # [6. 최종 결과 및 저장]
    st.markdown(f"### 📁 생성될 파일명: `{final_filename}`")
    
    # 다운로드 준비
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="💾 이 이름으로 파일 저장하기",
        data=byte_im,
        file_name=final_filename,
        mime="image/png",
        use_container_width=True
    )
