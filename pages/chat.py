import streamlit as st
import time
from utils import image_to_base64
from streamlit_option_menu import option_menu

st.set_page_config(page_title="chat", layout="centered")

# --- image ---
logo_img = image_to_base64("assets/logo.png")
agent_img = image_to_base64("assets/agent_orange.svg")


st.markdown("""<style>
            
            body { background: white; }
            .agent{
                background-color: #ffb894;
                padding: 10px 15px;
                border-radius: 20px;
                border-top-left-radius: 0;
                width: 300px;
            }
            
            .user{
                background-color: #FFF1EA;
                padding: 10px 15px;
                border-radius: 20px;
                border-top-right-radius: 0;
            }
            
            </style>""", unsafe_allow_html=True)
st.markdown(f"""
            <a href="/" target="_self" style="text-decoration:none;">
                <img src="data:image/png;base64,{logo_img}" style="width:120px; margin-bottom:10px; margin-top:-3rem;"/>
            </a>
            """, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [{'text': '상황에 맞는 카테고리를 선택해주세요.', "isUser": False}]
    st.session_state.category = ""
    st.session_state.input = ""
    st.session_state.is_loading = False
    st.session_state.initial = True

category_list = ['선택 안함', '구조물/건물 고립 사고', '고온산업시설 사고', '해상 사고', '산악 사고']

for message in st.session_state.messages:
    if not message['isUser']:
        message['text'] = message['text'].replace('\n', '<br/>')
        st.markdown(f"""
                    <div style="display:flex; justify-content: flex-start; margin-top:8px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:center; align-items:center; width:40px; height:40px; border-radius:100%; background-color:black; margin-right:7px;">
                                <img src="data:image/svg+xml;base64,{agent_img}" style="width:20px;"/>
                        </div>
                        <div class="agent">
                            {message['text']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        if st.session_state.initial:
            selected = option_menu(
                menu_title=None,
                options=category_list,
                icons=[""] * len(category_list),
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
                        "border": "2px solid #ffb894",
                        "width": "165px",
                        "padding": "12px 1px"
                    },
                    "nav-link-selected": {"background-color": "#ffb894", "color": "white"},
                }
            )
            if selected != "선택 안함":
                st.session_state.category = selected
                if selected == "구조물/건물 고립 사고":
                    st.session_state.messages.append({'text': f"""{selected} 카테고리를 선택하셨습니다.\n
                                                                    [예시 질문]\n
                                                                    1. 지하차도에 고립되어 있을 때 가장 먼저 뭐를 해야할까?\n
                                                                    2. 건물이 붕괴되었는데 출입문을 찾으려면 어떻게 해야돼?\n
                                                                    3. 침수된 지하주차장에 갇혀 있는데 뭐부터 해야돼?""", 'isUser': False})
                elif selected == '고온산업시설 사고':
                    st.session_state.messages.append({'text': f"""{selected} 카테고리를 선택하셨습니다.\n
                                                                    [예시 질문]\n
                                                                    - 산업시설에 고립되어 있을 때 가장 먼저 뭐를 해야할까?\n
                                                                    - 주변 온도가 점점 뜨거워질 때 어떻게 대처해야해?\n
                                                                    - 건물 비상 출입구는 보통 어디에 있어?""", 'isUser': False})
                
                elif selected == '해상 사고':
                    st.session_state.messages.append({'text': f"""{selected} 카테고리를 선택하셨습니다.\n
                                                                    [예시 질문]\n
                                                                    - 해상에서 조난 당했을 때 조난 신호는 어떻게 보내?\n
                                                                    - 배가 침몰하고 있는데 지금 대피해야 돼 아니면 선박에 있어야돼?\n
                                                                    - 언제 구명정 하강이 가능해?""", 'isUser': False})
                    
                elif selected == '산악 사고':
                    st.session_state.messages.append({'text': f"""{selected} 카테고리를 선택하셨습니다.\n
                                                                    [예시 질문]\n
                                                                    - 산 등산 중 길을 아예 잃었을 떄는 뭐부터 해야돼?\n
                                                                    - 저체온증을 막으려면 어떻게 해야될까?\n
                                                                    - 야생 곰을 만났을 때는 어떻게 하는게 가장 안전해?""", 'isUser': False})
                st.session_state.initial = False
                
    else: 
        st.markdown(f"""
                    <div style="display:flex; justify-content: flex-end; margin-top:8px;">
                        <div class="user">
                            {message['text']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


if st.session_state.is_loading:
    st.markdown()

st.markdown(f"""
            <div style="margin-top:30px;">
            </div>
            """, unsafe_allow_html=True)

user_input = st.chat_input("메시지를 입력하세요...")

# ---print user input and agent output    
if user_input:#if submitted and user_input.strip():
    st.session_state.messages.append({'text': user_input.strip(), 'isUser': True})
    st.rerun()  # 유저 메시지 바로 표시

# ---response processed and printed
if len(st.session_state.messages) >= 1 and st.session_state.messages[-1]["isUser"] and \
   (len(st.session_state.messages) == 1 or st.session_state.messages[-2]["isUser"] == False):

    with st.spinner("답변을 생성하는 중..."):
        time.sleep(2)

    user_text = st.session_state.messages[-1]['text']
    response = f"""{user_text}에 대한 응답입니다. 
    이 구조는 Streamlit에서 JS 기반 입력폼을 꾸미면서도 Python에 값을 정확히 넘기는 유일한 안정적 방식입니다.
    원한다면 다음도 추가 구현 가능:
    쿼리 파라미터로 전달 (SEO 및 URL 공유용)
    JS → Py로 WebSocket 전달 (비공식적)
    검색 결과 연동 및 데이터베이스 조회"""
    st.session_state.messages.append({'text': response, 'isUser': False})
    st.rerun()