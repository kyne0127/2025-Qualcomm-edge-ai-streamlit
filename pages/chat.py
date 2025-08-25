import streamlit as st
import time
from utils import image_to_base64
from streamlit_option_menu import option_menu
from db.retrieve import process_output

st.set_page_config(page_title="chat", layout="centered")

## import image ##
logo_img = image_to_base64("assets/logo.png")
agent_img = image_to_base64("assets/agent_orange.svg")
sound_img = image_to_base64("assets/sound_wave.svg")

## style definition ##
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
            <div style="display:flex; align-items:center;">
                <a href="/" target="_self" style="text-decoration:none;">
                    <img src="data:image/png;base64,{logo_img}" style="width:120px; margin-bottom:10px; margin-top:-3rem;"/>
                </a>
                <a href="/chat_audio" target="_self" style="display:flex; margin-left:auto; width:50px; height:50px; border-radius:100px; background-color:#eff2f6; justify-content:center; align-items:center;">
                    <img src="data:image/svg+xml;base64,{sound_img}" style="width:30px;"/>
                </a>
            </div>
            """, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [{'text': 'Please select the category that best fits your situation.', "isUser": False}]
if "category" not in st.session_state:
    st.session_state.category = ""
if "input" not in st.session_state:
    st.session_state.input = ""
if "is_loading" not in st.session_state:
    st.session_state.is_loading = False
if "initial" not in st.session_state:
    st.session_state.initial = True

category_list = ['None Selected', 'Collapse', 'High Temp', 'Maritime', 'Mountain', 'Gen Emergency']

## show user, agent messages on the screen
for message in st.session_state.messages:
    if not message['isUser']: ##if agent
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
        if st.session_state.initial: ##show category options
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
            st.session_state.category = selected
            
            if selected != "None Selected": ##suggest user recommended questions for each selected category
                if selected == "Collapse":
                    st.session_state.messages.append({'text': f"""You have selected the {selected} category.\n
                                                                    [Example Questions]\n
                                                                    1. What should I do first when trapped in an underpass?\n
                                                                    2. A building has collapsed — how can I find an exit?\n
                                                                    3. I’m trapped in a flooded underground parking lot — what should I do first?""", 'isUser': False})
                elif selected == 'High Temp':
                    st.session_state.messages.append({'text': f"""You have selected the {selected} category.\n
                                                                    [Example Questions]\n
                                                                    - What should I do first when trapped in an industrial facility?\n
                                                                    - How should I respond as the surrounding temperature keeps rising?\n
                                                                    - Where are emergency exits usually located in buildings?""", 'isUser': False})
                
                elif selected == 'Maritime':
                    st.session_state.messages.append({'text': f"""You have selected the {selected} category.\n
                                                                    [Example Questions]\n
                                                                    - How do I send a distress signal when stranded at sea?\n
                                                                    - The ship is sinking — should I evacuate now or stay on board?\n
                                                                    - When is it safe to launch a lifeboat?""", 'isUser': False})
                    
                elif selected == 'Mountain':
                    st.session_state.messages.append({'text': f"""You have selected the {selected} category.\n
                                                                    [Example Questions]\n
                                                                    - What should I do first when I’ve completely lost the trail while hiking?\n
                                                                    - How can I prevent hypothermia?\n
                                                                    - What’s the safest way to respond to encountering a wild bear?""", 'isUser': False})
                    
                elif selected == 'Gen Emergency':
                    st.session_state.messages.append({'text': f"""You have selected the {selected} category.\n
                                                                    [Example Questions]\n
                                                                    - What should I do if I cut my hand with a kitchen knife?\n
                                                                    - What should I do first if I have an allergic reaction to food?\n
                                                                    - I feel unwell due to the heat — how should I respond?""", 'isUser': False})
                st.session_state.initial = False
                
    else: #if user
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

user_input = st.chat_input("Enter a message...")

## print user input and agent output ##
if user_input: #if submitted and user_input.strip():
    st.session_state.messages.append({'text': user_input.strip(), 'isUser': True})
    st.rerun() # immediately show user's prompt as soon as user enters his/her questions

## agent's response processed and printed ##
if len(st.session_state.messages) >= 1 and st.session_state.messages[-1]["isUser"] and \
   (len(st.session_state.messages) == 1 or st.session_state.messages[-2]["isUser"] == False):

    with st.spinner("Generating Responses..."):
        user_text = st.session_state.messages[-1]['text']
        index = st.session_state.category + "_" + "manual"
        response = process_output(index, user_text, "QA")
        # response = "If you cut your hand with a kitchen knife, immediately visit a doctor."
        
    st.session_state.messages.append({'text': response, 'isUser': False})
    st.rerun()