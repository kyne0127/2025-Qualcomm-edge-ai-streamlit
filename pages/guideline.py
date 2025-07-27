import streamlit as st
from utils import image_to_base64
import time
from streamlit_option_menu import option_menu
from db.retrieve import process_output

st.set_page_config(page_title="guideline", layout="centered")

# 상태 초기화
if "category" not in st.session_state:
    st.session_state.category = ""
if "guidelines" not in st.session_state:
    st.session_state.guidelines = []
if "is_loading" not in st.session_state:
    st.session_state.is_loading = False
if "is_submit" not in st.session_state:
    st.session_state.is_submit = False

# --- Image ---
submit_img = image_to_base64("assets/send.svg")
logo_img = image_to_base64("assets/logo.png")

# --- Style ---
st.markdown("""
    <style>
    .category-button {
        padding: 10px 20px;
        border-radius: 30px;
        border: 2px solid #ff762d;
        font-weight: bold;
        font-size: 14px;
        cursor: pointer;
        margin: 5px;
        display: inline-block;
    }
    .selected {
        background-color: #ff762d;
        color: white;
    }
    .unselected {
        background-color: #FFF1EA;
        color: black;
    }
    a.chat-btn, a.case-btn {
        text-decoration: none;
        color: black;
        font-weight: bold;
        background-color: #ff762d;
        border-radius: 100px;
        padding: 1rem 1.5rem;
        font-size: 14px;
    }
    .submit-btn{
        background-color: black;
        width: 45px;
        height: 45px;
        border-radius:100px;
        justify-content: center;
        align-items: center;
    }
    
    @media (max-width: 410px){
        .nav-link{
            width:165px;
            margin: 6px 6px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- category selection ---
st.markdown(f"""
            <a href="/" target="_self" style="text-decoration:none;">
                <img src="data:image/png;base64,{logo_img}" style="width:120px; margin-bottom:40px; margin-top:-3rem;"/>
            </a>
            <div style="font-weight:bold; font-size:22px;">
                카테고리
            </div>
            """, unsafe_allow_html=True)

options=['구조물 고립 사고', '고온산업시설 사고', '해상 사고', '산악 사고', '일반 응급']

selected = option_menu(
    menu_title=None,
    options=options,
    # icons= ["triangle", "triangle", "triangle", "triangle"],
    icons= [""] * len(options),
    orientation="horizontal",
    styles={
        "container": {
            "padding": "0", 
            "background-color": "white", 
            "flex-wrap": "wrap",
        },
        "icon":{
            "display": "none",
        },
        "nav-link": {
            "font-size": "14px",
            "font-weight": "bold",
            "text-align": "center",
            "background-color": "#fff1ea",
            "border-radius": "100px",
            "margin": "6px 6px",
            "border": "2px solid #ff762d",
            "width": "165px",
            "padding": "12px 1px"
        },
        "nav-link-selected": {"background-color": "#ff762d", "color": "white"},
    }
)
st.session_state["category"] = selected


# --- input form ---
st.markdown(f"""
            <div style="font-weight:bold; font-size:20px; margin-top:0rem; margin-bottom:-2.5rem;">
                상세 상황 설명
            </div>
            """, unsafe_allow_html=True)
situation = st.text_area(" ", placeholder="예) 지하주차장 천장이 일부 붕괴되어 지하에 10명 이상 갇힘.", height=120) #현재 처한 상황에 대해 설명합니다. 
st.markdown(f"""
            <div style="font-weight:bold; font-size:20px; margin-top:0.3rem; margin-bottom:-2.5rem;">
                장소 설명
            </div>
            """, unsafe_allow_html=True)
place = st.text_area(" ", placeholder="예) 근처에 역삼역이 있고, 지하 깊이는 깊지 않음.", height=120) #현재 있는 장소나 주변 환경에 대해 설명합니다. 
st.markdown(f"""
            <div style="font-weight:bold; font-size:20px; margin-top:0.3rem; margin-bottom:-2.5rem;">
                인원 및 사고 발생 시각 설명
            </div>
            """, unsafe_allow_html=True)
num_and_time = st.text_area(" ", placeholder="예) 노약자 1명, 어린이 2명 있음. 10분 전 사고 발생.", height=70) #인원과 재난 시각에 대해 설명합니다.
st.markdown(f"""
            <div style="font-weight:bold; font-size:20px; margin-top:0.3rem; margin-bottom:-2.5rem;">
                특이 사항 설명
            </div>
            """, unsafe_allow_html=True)
injury = st.text_area(" ", placeholder="예) 휠체어 이용자가 있음, 다리 부상이 심함", height=120)

# if button is pressed
if st.button("가이드라인 보기", use_container_width=True):
    if not situation.strip():
        st.warning("상황 설명은 필수입니다.")
    else:
        st.session_state.is_loading = True
        st.session_state.is_submit = True
        with st.spinner("가이드라인 생성 중..."):
            try:
                # time.sleep(2)
                input = f"상황: {situation}, "
                if place: input+= f"장소: {place}, "
                if num_and_time: input+= f"인원 및 사건 발생 시각: {num_and_time}, "
                if injury: input+= f"특이사항: {injury}, "
                
                index = st.session_state.category + "_" + "메뉴얼"
                output = process_output(index, input, "GuideLine")
                chunks = [c for c in output.split('\n') if c.strip()]
                st.session_state.guidelines = chunks
            except Exception as e:
                st.session_state.guidelines = ["❌ 오류가 발생했습니다."]
            finally:
                st.session_state.is_loading = False

# 출력
if st.session_state.is_submit:
    st.markdown(f"""
            <div style="font-weight:bold; font-size:20px; color:#ff762d ;">
               가이드라인
            </div>
            """, unsafe_allow_html=True)
    for line in st.session_state.guidelines:
        if line.startswith("### **"):
            st.markdown(f"##### {line.replace('### **', '').replace('**','')}")
        elif line.startswith("- **"):
            st.markdown(f"**{line.replace('- **','').replace('**','')}**")
        elif line.startswith("- "):
            st.markdown(f"- {line}")
        elif line.startswith("**"):
            st.markdown(f"**{line.replace('**','')}**")
        else:
            st.write(line)

# 페이지 전환 (Streamlit 내부 링크 또는 안내)
st.markdown("---")
st.markdown(f"""
            <div style="display: flex; gap: 0.5rem; justify-content: center;">
                <a href="/chat" target="_self" class="chat-btn"> 
                    이어서 Q&A 채팅하기
                </a>
                <a href="/case_search" target="_self" class="case-btn">
                    비슷한 대응 사례 찾기
                </a>
            </div>
                """, unsafe_allow_html=True)
