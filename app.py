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

# [1. AI 모델 로드 - 캐싱 처리로 속도 최적화]
@st.cache_resource
def load_reader():
    # 한글(ko)과 영어(en)를 인식하도록 설정
    return easyocr.Reader(['ko', 'en'])

try:
    reader = load_reader()
except Exception as e:
    st.error(f"모델 로드 중 오류가 발생했습니다: {e}")

# [2. 파일 업로드 섹션]
uploaded_file = st.file_uploader("사진을 선택하거나 여기로 끌어다 놓으세요", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 이미지 열기 및 표시
    image = Image.open(uploaded_file)
    
    st.divider()
    st.subheader("🖼️ 업로드된 이미지 확인")
    # 최신 버전과 구버전 호환성을 위해 속성 설정
    st.image(image, use_container_width=True)
    st.divider()

    # [3. AI 분석 시작]
    with st.spinner('AI가 이미지 속 글자를 읽고 있습니다...'):
        # PIL 이미지를 numpy 배열로 변환 (EasyOCR 인식용)
        img_np = np.array(image)
        # 텍스트 추출 (detail=0은 좌표 없이 글자만 가져옴)
        raw_results = reader.readtext(img_np, detail=0)
    
    # [4. 파일명 설정 UI]
    st.subheader("✍️ 새 파일 이름 짓기")
    
    # 분석된 단어가 있을 경우
    if raw_results:
        # 중복 제거 및 2글자 이상 단어 4개 선정
        unique_words = list(dict.fromkeys([w.strip() for w in raw_results if len(w.strip()) >= 2]))
        recommended_pool = unique_words[:4]

        # AI 키워드 선택 (멀티셀렉트)
        selected_keywords = st.multiselect(
            "AI 추천 키워드 (클릭하여 선택)", 
            options=recommended_pool,
            help="선택한 순서대로 파일명에 추가됩니다."
        )
    else:
        st.info("이미지에서 추출할 단어를 찾지 못했습니다. 직접 이름을 입력해 주세요.")
        selected_keywords = []

    # 직접 이름 입력란
    custom_name = st.text_input("직접 이름 추가 (선택사항)", placeholder="예: 영수증_식비")

    # [5. 파일명 조합 및 생성]
    # 오늘 날짜 가져오기 (YYYYMMDD)
    current_date = datetime.now().strftime("%Y%m%d")
    
    # 조각 모으기
    name_parts = [current_date] # 날짜는 항상 기본
    
    # 선택된 키워드 추가 (공백은 언더바로 변경)
    if selected_keywords:
        keyword_str = "_".join(selected_keywords).replace(" ", "_")
        name_parts.append(keyword_str)
    
    # 직접 입력한 이름 추가 (공백은 언더바로 변경)
    if custom_name:
        name_parts.append(custom_name.strip().replace(" ", "_"))
    
    # 최종 파일명 (확장자 포함)
    final_filename = f"{'_'.join(name_parts)}.png"

    # [6. 결과 미리보기 및 저장 버튼]
    st.markdown(f"### 📁 생성될 파일명: `{final_filename}`")
    
    # 이미지 데이터를 바이트로 변환하여 다운로드 준비
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    byte_im = buf.getvalue()

    # 저장 버튼
    st.download_button(
        label="💾 설정한 이름으로 파일 저장하기",
        data=byte_im,
        file_name=final_filename,
        mime="image/png",
        use_container_width=True
    )
