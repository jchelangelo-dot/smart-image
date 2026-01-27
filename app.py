import streamlit as st
import google.generativeai as genai
from PIL import Image
from datetime import datetime
import io

# --- 설정 ---
st.set_page_config(page_title="AI 파일명 추천기", layout="centered")

# 사용자님의 API 키 (보안을 위해 실제 서비스 시에는 비밀 관리가 필요합니다)
API_KEY = "AIzaSyBFgIMOPpV2qUraV83fgfkxDSUtw_k_6dM"
genai.configure(api_key=API_KEY)

st.title("📱 AI 스마트 파일명 추천")
st.write("이미지를 찍거나 업로드하면 AI가 파일명을 제안합니다.")

# 1. 파일 업로드 (스마트폰에서는 카메라 촬영 선택 가능)
uploaded_file = st.file_uploader("이미지 업로드", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption='선택된 이미지', use_container_width=True)
    
    if st.button("✨ AI 분석 시작"):
        with st.spinner("AI가 분석 중입니다..."):
            try:
                # 최신 모델 사용
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = "이 이미지의 핵심 키워드 4개를 뽑아줘. 결과는 반드시 콤마로 구분된 영문 대문자만 보내줘. 예: SEOUL,FOOD,CAFE,TRAVEL"
                
                response = model.generate_content([prompt, image])
                
                if response.text:
                    keywords = [k.strip().upper() for k in response.text.split(',')]
                    st.session_state['keywords'] = keywords
                    st.success("키워드 추출 완료!")
                else:
                    st.error("AI 응답이 비어있습니다.")
            except Exception as e:
                st.error(f"분석 실패: {str(e)[:50]}")

    # 2. 키워드 선택 및 파일명 조합
    if 'keywords' in st.session_state:
        st.write("파일명에 포함할 키워드를 선택하세요:")
        selected = st.multiselect("키워드 선택", st.session_state['keywords'], default=st.session_state['keywords'][:2])
        
        date_str = datetime.now().strftime("%y%m%d")
        tags_str = "_".join(selected)
        final_name = f"{date_str}_{tags_str}.png" if tags_str else f"{date_str}_IMAGE.png"
        
        # 파일명 수정 가능하게 텍스트 박스 제공
        new_filename = st.text_input("최종 파일명:", value=final_name)
        
        # 3. 결과 다운로드
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        st.download_button(
            label="💾 변경된 이름으로 저장",
            data=img_byte_arr,
            file_name=new_filename,
            mime="image/png"

        )
