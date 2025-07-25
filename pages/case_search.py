import streamlit as st
import time
from utils import image_to_base64
from db.retrieve import retrieve
from streamlit_option_menu import option_menu

st.set_page_config(page_title="case_search", layout="centered")

## --image --
paper_img = image_to_base64('assets/paper.svg')
logo_img = image_to_base64("assets/logo.png")

# style definition
st.markdown("""
    <style>
    /* 전체 배경색 검정 html, body, [data-testid="stApp"]  */ 
    html, body, [data-testid="stApp"] {
        background-color: black; //!important
    }

    .title {
        font-size: 27px;
        color: #ff762d;
        font-weight: 800;
        text-align: center;
        margin-top: 40px;
    }

    .description {
        font-size: 14px;
        color: white;
        text-align: center;
        margin-top: 12px;
        line-height: 1.6;
        letter-spacing: -0.2px;
    }

    .search-row {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 30px;
    }

    .search-input {
        width: 250px;
        height: 50px;
        border-radius: 9999px;
        padding: 0 16px;
        font-size: 14px;
        border: none;
        outline: none;
    }

    .search-button {
        width: 48px;
        height: 48px;
        background-color: #ff762d;
        border: none;
        border-radius: 9999px;
        margin-left: 12px;
        display: flex;
        justify-content: center;
        align-items: center;
        cursor: pointer;
    }

    .search-button img {
        width: 24px;
        height: 24px;
    }
    </style>
""", unsafe_allow_html=True)

# logo
st.markdown(f"""
            <a href="/" target="_self" style="text-decoration:none;">
                <img src="data:image/png;base64,{logo_img}" style="width:120px; margin-bottom:10px; margin-top:-3rem;"/>
            </a>
            """, unsafe_allow_html=True)

# banner
st.markdown("""
    <div style="background-color: black; padding:15px; margin-bottom:50px;">
        <div class="title">비슷한 사례 찾기</div>
        <div class="description">
            현재 상황과 비슷한 과거 재난 상황 속에서,<br/>
            어떻게 비상 대응을 했는지<br/>
            그 사례들을 자세하게 살펴보세요.
        </div>
    </div>
""", unsafe_allow_html=True)

#category selection

options=['구조물 고립 사고', '고온산업시설 사고', '해상 사고', '산악 사고']

selected = option_menu(
    menu_title=None,
    options=options,
    # icons= ["triangle", "triangle", "triangle", "triangle"],
    icons= [""] * len(options),
    orientation="horizontal",
    styles={
        "container": {
            "padding": "0", 
            "background-color": "black", 
            "flex-wrap": "wrap",
        },
        "icon":{
            "display": "none",
        },
        "nav-link": {
            "font-size": "14px",
            "font-weight": "bold",
            "text-align": "center",
            "background-color": "black",
            "color": "white",
            "border-radius": "100px",
            "margin": "6px 6px",
            "border": "2px solid #ff762d",
            "width": "165px",
            "padding": "12px 1px"
        },
        "nav-link-selected": {"background-color": "#ff762d", "color": "white"},
    }
)


#search form
keyword = st.chat_input("키워드나 간단한 상황을 입력하세요...")

results = [{'title': '화재', 'contents': '건물에서 화재가 발생했다.', 'date': '2020-01-09'},
           {'title': '지하구조물 고립', 'contents': '많은 양의 비로 아파트 지하주차장이 침수되었는데, 차를 빼러 내려간 주민 1명이 지하주차장에 고립되었다가 구조되었다.', 'date': '2020-01-09'},
           {'title': '해상 사고', 'contents': '스쿠버다이빙을 하던 중 심한 두통이 발생하였다.', 'date': '2020-01-09'},
           {'title': '화재', 'contents': '건물에서 화재가 발생했다.', 'date': '2020-01-09'},
        ]




# if button has been pressed
if keyword:
    keyword = keyword.strip()
    if not keyword:
        st.warning("키워드를 입력해주세요.")
    with st.spinner(f"'{keyword}'에 대한 사례를 vector db에서 검색 중입니다."):
        index = selected + "_" + "사례"
        results = retrieve(index, keyword)
    st.markdown(f"""<div style="display:flex; gap:20px; justify-content:center;">""", unsafe_allow_html = True)
    for result in results:
        st.markdown(f"""
                    <div style="background-color: white; padding: 25px 20px; border-radius:20px; width: 350px; min-height: 100px; margin-bottom: 30px;">
                        <div style="display:flex; margin-bottom:5px;">
                            <div style="color:#ff762d; font-weight:600; font-size:22px; letter-spacing:-0.2px; margin-bottom:-2px;">{selected}</div>
                            <img src="data:image/svg+xml;base64,{paper_img}" style="width:20px; margin-left:5px;"/>
                        </div>
                        <div>{result.page_content}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    #<div style="color:#a6a6a6; font-size:12px; letter-spacing:-0.2px; margin-bottom:15px;">{result['date']}</div>
    
    st.markdown(f"</div>", unsafe_allow_html=True)
