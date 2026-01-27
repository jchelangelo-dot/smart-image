import streamlit as st
import easyocr
from PIL import Image
import numpy as np
from datetime import datetime
import io

# 앱 설정
st.set_page_config(page_title="AI 스마트 파일 관리자", layout="centered")

st.title("📂 AI 이미지 분석 & 파일 네이머")

# 1. OCR 모델 로드 (캐싱)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['ko', 'en'])

reader = load_reader()

# 2. 파일 업로드 섹션
uploaded_file = st.file_uploader("분석할 이미지를 업로드하세요", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # --- [이미지 표시 부분] ---
    image = Image.open(uploaded_file)
    
    # 구분선을 넣고 이미지를 화면에 출력합니다.
    st.divider()
    st.subheader("🖼️ 업로드된 이미지")
    st.image(image, use_container_width=True) 
    st.divider()
    # -----------------------

    with st.spinner('AI가 텍스트를 읽고 키워드를 뽑아내고 있습니다...'):
        img_np = np.array(image)
        raw_results = reader.readtext(img_np, detail=0)
    
    if raw_results:
        # 3. 키워드 추천 및 사용자 입력
        unique_words = list(dict.fromkeys([w.strip() for w in raw_results if len(w.strip()) >= 2]))
        recommended_pool = unique_words[:4]

        st.subheader("✍️ 파일 이름 설정")
        
        # 키워드 선택
        selected_keywords = st.multiselect("AI 추천 키워드 선택", options=recommended_pool)
        
        # 직접 입력
        custom_name = st.text_input("직접 이름 추가", placeholder="예: 영수증_식비")

        # 4. 최종 파일명 조합 (날짜 + 키워드 + 직접입력)
        current_date = datetime.now().strftime("%Y%m%d")
        keyword_str = "_".join(selected_keywords).replace(" ", "")
        
        name_parts = [current_date]
        if keyword_str: name_parts.append(keyword_str)
        if custom_name: name_parts.append(custom_name.replace(" ", "_"))
        
        final_filename = f"{'_'.join(name_parts)}.png"

        # 결과 미리보기 및 저장
        st.info(f"📁 생성될 파일명: **{final_filename}**")

        buf = io.BytesIO()
        image.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="💾 설정한 이름으로 다운로드",
            data=byte_im,
            file_name=final_filename,
            mime="image/png"
        )
    else:
        st.warning("텍스트를 추출하지 못했습니다. 직접 이름을 입력해 주세요.")
        custom_name = st.text_input("파일명 입력")
        if custom_name:
            final_filename = f"{datetime.now().strftime('%Y%m%d')}_{custom_name}.png"
            st.download_button("💾 저장하기", data=image, file_name=final_filename)
