import streamlit as st
import easyocr
from PIL import Image
import numpy as np
from datetime import datetime
import io

st.set_page_config(page_title="AI 스마트 파일 관리자", layout="centered")

st.title("📂 AI 이미지 분석 & 파일 네이머")

# [핵심 수정] 모델 로드 시 수집되는 리소스를 최소화합니다.
@st.cache_resource
def load_reader():
    # download_enabled=True를 명시하고, 모델을 미리 메모리에 고정합니다.
    return easyocr.Reader(['ko', 'en'], gpu=False, download_enabled=True)

# 모델 로딩 시각화
with st.status("AI 모델 준비 중...", expanded=True) as status:
    st.write("텍스트 인식 엔진을 불러오고 있습니다 (최초 1회 소요)...")
    reader = load_reader()
    status.update(label="모델 준비 완료!", state="complete", expanded=False)

uploaded_file = st.file_uploader("사진을 선택하세요", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, use_container_width=True)
    
    # [중요] 분석 시 메모리 부하를 줄이기 위해 이미지 크기를 약간 조정합니다.
    if st.button("이미지 분석 시작"):
        with st.spinner('글자를 읽는 중입니다...'):
            # 이미지 용량이 너무 크면 에러가 날 수 있으므로 리사이징 고려
            img_np = np.array(image.convert('RGB'))
            raw_results = reader.readtext(img_np, detail=0)
        
        if raw_results:
            unique_words = list(dict.fromkeys([w.strip() for w in raw_results if len(w.strip()) >= 2]))
            recommended_pool = unique_words[:4]

            st.subheader("✍️ 파일 이름 설정")
            selected_keywords = st.multiselect("키워드 선택", options=recommended_pool)
            custom_name = st.text_input("직접 이름 추가")

            current_date = datetime.now().strftime("%Y%m%d")
            name_parts = [current_date]
            if selected_keywords: name_parts.append("_".join(selected_keywords))
            if custom_name: name_parts.append(custom_name.replace(" ", "_"))
            
            final_filename = f"{'_'.join(name_parts)}.png"
            st.info(f"📁 파일명: `{final_filename}`")

            buf = io.BytesIO()
            image.save(buf, format="PNG")
            st.download_button("💾 저장하기", data=buf.getvalue(), file_name=final_filename)
        else:
            st.warning("텍스트를 찾지 못했습니다.")
