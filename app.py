import streamlit as st
import easyocr
from PIL import Image
import numpy as np
from datetime import datetime
import io

st.set_page_config(page_title="AI 스마트 파일 네이머", layout="centered")

st.title("📂 AI 키워드 선택 & 파일 저장")

@st.cache_resource
def load_reader():
    return easyocr.Reader(['ko', 'en'])

reader = load_reader()

uploaded_file = st.file_uploader("이미지를 업로드하세요", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='업로드된 이미지', use_container_width=True)
    
    with st.spinner('AI가 단어를 분석 중입니다...'):
        img_np = np.array(image)
        # 텍스트 추출
        raw_results = reader.readtext(img_np, detail=0)
    
    if raw_results:
        # 1. 키워드 추천 로직 (길이 순으로 상위 4개 추출)
        # 중복 제거 후 의미 있는 단어 4개 선정
        unique_words = list(dict.fromkeys([w.strip() for w in raw_results if len(w.strip()) >= 2]))
        recommended_pool = unique_words[:4]

        st.subheader("💡 AI 추천 키워드")
        st.write("파일명에 포함할 키워드를 선택하세요 (최대 4개)")
        
        # 2. 사용자 키워드 선택 (Multiselect)
        selected_keywords = st.multiselect(
            "키워드 선택", 
            options=recommended_pool, 
            default=recommended_pool[:2] if recommended_pool else []
        )

        # 3. 날짜 및 최종 파일명 생성
        current_date = datetime.now().strftime("%Y%m%d")
        keyword_str = "_".join(selected_keywords).replace(" ", "")
        
        # 선택된 키워드가 있으면 날짜_키워드, 없으면 날짜만
        if keyword_str:
            final_filename = f"{current_date}_{keyword_str}.png"
        else:
            final_filename = f"{current_date}.png"

        st.info(f"📁 생성될 파일명: `{final_filename}`")

        # 4. 저장(다운로드) 버튼
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="💾 이 이름으로 파일 저장하기",
            data=byte_im,
            file_name=final_filename,
            mime="image/png"
        )
    else:
        st.warning("이미지에서 추출할 단어를 찾지 못했습니다.")
