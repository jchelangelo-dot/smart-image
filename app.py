import streamlit as st
import easyocr
from PIL import Image
import numpy as np
from datetime import datetime
import io

st.set_page_config(page_title="AI 스마트 파일 관리자", layout="centered")

st.title("📂 AI 텍스트 분석 & 파일 관리")

# 1. 모델 로드 (캐싱)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['ko', 'en'])

reader = load_reader()

uploaded_file = st.file_uploader("이미지를 업로드하세요", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 이미지 표시
    image = Image.open(uploaded_file)
    st.image(image, caption='업로드된 이미지', use_container_width=True)
    
    with st.spinner('텍스트 분석 중...'):
        img_np = np.array(image)
        # 텍스트 추출
        raw_results = reader.readtext(img_np, detail=0)
        full_text = " ".join(raw_results)

    if full_text.strip():
        # 2. 키워드 추천 (간이 분석: 가장 긴 단어들 혹은 주요 단어 추출)
        # 실제로는 더 복잡한 NLP 모델을 쓸 수 있지만, 여기선 핵심 단어 위주로 뽑습니다.
        keywords = [word for word in raw_results if len(word) >= 2][:3] 
        recommended_keyword = "_".join(keywords).replace(" ", "")

        # 3. 파일명 생성 (날짜 + 키워드)
        current_date = datetime.now().strftime("%Y%m%d")
        new_filename = f"{current_date}_{recommended_keyword}.png"

        st.subheader("📝 분석 결과")
        st.success(f"추출된 텍스트: {full_text[:100]}...")
        st.info(f"💡 추천 키워드: {', '.join(keywords)}")

        # 4. 파일 이름 변경 및 다운로드 버튼
        # Streamlit은 서버 파일 시스템을 직접 건드리기보다 다운로드 방식으로 제공하는 것이 안전합니다.
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="✅ 분석된 파일명으로 다운로드",
            data=byte_im,
            file_name=new_filename,
            mime="image/png"
        )
        st.write(f"파일명 예시: `{new_filename}`")
    else:
        st.warning("이미지에서 텍스트를 찾을 수 없습니다.")
