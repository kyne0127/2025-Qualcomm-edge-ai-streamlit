import streamlit as st
from utils import image_to_base64
import time
from streamlit_option_menu import option_menu
from db.retrieve import process_output

st.set_page_config(page_title="guideline", layout="centered")

if "category" not in st.session_state:
    st.session_state.category = ""
if "guidelines" not in st.session_state:
    st.session_state.guidelines = []
if "is_loading" not in st.session_state:
    st.session_state.is_loading = False
if "is_submit" not in st.session_state:
    st.session_state.is_submit = False

## image import ##
submit_img = image_to_base64("assets/send.svg")
logo_img = image_to_base64("assets/logo.png")
speak_img = image_to_base64("assets/speak_black.svg")
play_img = image_to_base64("assets/play.svg")
sound_img = image_to_base64("assets/sound_wave.svg")

## style definition ##
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

st.markdown(f"""
            <a href="/" target="_self" style="text-decoration:none;">
                <img src="data:image/png;base64,{logo_img}" style="width:120px; margin-bottom:40px; margin-top:-3rem;"/>
            </a>
            """, unsafe_allow_html=True)

st.markdown(f"""
            <a href="/guideline_audio" target="_self" style="display:block; margin-bottom:25px; width:100%; padding: 14px 20px; font-weight:bold; font-size:16px; border-radius:100px; background-color:#fff1ea; text-decoration: none; color:black;">
                <div style="display:flex; justify-content:center; text-align:center; align-items:center;">
                    <img src="data:image/svg+xml;base64,{sound_img}" style="height:30px; margin-right:10px;"/>
                    <div>Describe the Situation by Voice</div>
                    <img src="data:image/svg+xml;base64,{sound_img}" style="height:30px; margin-left:10px;"/>
                    <img src="data:image/svg+xml;base64,{play_img}" style="height:22px; margin-left:4px;"/>
                </div>
            </a>
            """, unsafe_allow_html=True)


## category selection ##
st.markdown(f"""
            <div style="font-weight:bold; font-size:20px;">
                Category
            </div>
            """, unsafe_allow_html=True)

options=['None Selected', 'Collapse', 'High Temp', 'Maritime', 'Mountain', 'Gen Emergency']

selected = option_menu(
    menu_title=None,
    options=options,
    # icons= ["triangle", "triangle", "triangle", "triangle"],
    icons= [""] * len(options),
    orientation="horizontal",
    key="category_menu",
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


## input form ##
st.markdown(f"""
            <div style="font-weight:bold; font-size:20px; margin-top:0rem; margin-bottom:-2.5rem;">
                Detailed Situation
            </div>
            """, unsafe_allow_html=True)
situation = st.text_area(" ", placeholder="e.g. An underground parking lot has collapsed, and more than 10 people are trapped underground.", height=120) #현재 처한 상황에 대해 설명합니다. 
st.markdown(f"""
            <div style="font-weight:bold; font-size:20px; margin-top:0.3rem; margin-bottom:-2.5rem;">
                Location
            </div>
            """, unsafe_allow_html=True)
place = st.text_area(" ", placeholder="e.g. Near Yeoksam Station, and the underground level is not very deep.", height=120) #현재 있는 장소나 주변 환경에 대해 설명합니다. 
st.markdown(f"""
            <div style="font-weight:bold; font-size:20px; margin-top:0.3rem; margin-bottom:-2.5rem;">
                People Involved & Time of Incident
            </div>
            """, unsafe_allow_html=True)
num_and_time = st.text_area(" ", placeholder="e.g. 1 elderly person presents. The incident occurred 10 minutes ago.", height=70) #인원과 재난 시각에 대해 설명합니다.
st.markdown(f"""
            <div style="font-weight:bold; font-size:20px; margin-top:0.3rem; margin-bottom:-2.5rem;">
                Special Notes
            </div>
            """, unsafe_allow_html=True)
injury = st.text_area(" ", placeholder="e.g. One person is using a wheelchair, and one has a serious leg injury.", height=120)
# if button is pressed
if st.button("View Guidelines", use_container_width=True):
    if not situation.strip():
        st.warning("Detailed Situation is required.")
    else:
        st.session_state.is_loading = True
        st.session_state.is_submit = True
        with st.spinner("Generating guidelines..."):
            try:
                # time.sleep(2)
                input = f"detailed situation: {situation}, "
                if place: input+= f"location: {place}, "
                if num_and_time: input+= f"people involved & time of incident: {num_and_time}, "
                if injury: input+= f"special notes: {injury}, "
                
                index = st.session_state.category + "_" + "manual"
                output = process_output(index, input, "GuideLine")
                # output = f"""
                #     ### ** 비상 가이드라인
                #     1. 대피
                #     2. 전화로 상황 알리기
                # """
                
                chunks = [c for c in output.split('\n') if c.strip()]
                st.session_state.guidelines = chunks
            except Exception as e:
                st.session_state.guidelines = ["❌ An error has occured."]
            finally:
                st.session_state.is_loading = False

# print generated guidelines by Llama3.2-3b ##
if st.session_state.is_submit:
    st.markdown(f"""
            <div style="font-weight:bold; font-size:20px; color:#ff762d; margin-top:20px;">
               Guideline
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

## page transfer ##
st.markdown("---")
st.markdown(f"""
            <div style="display: flex; gap: 0.5rem; justify-content: center;">
                <a href="/chat" target="_self" class="chat-btn"> 
                    Continue with Q&A Chat
                </a>
                <a href="/case_search" target="_self" class="case-btn">
                    Continue with Q&A Chat
                </a>
            </div>
                """, unsafe_allow_html=True)
