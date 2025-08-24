import streamlit as st
from utils import image_to_base64
from streamlit_option_menu import option_menu
import whisper
from audiorecorder import audiorecorder
from io import BytesIO
from streamlit_mic_recorder import mic_recorder
import numpy as np
from pydub import AudioSegment
import librosa
from db.retrieve import process_output

st.set_page_config(page_title="audio guideline", layout="centered")


## style definition ##
st.markdown("""
    <style>
    a.chat-btn, a.case-btn {
        text-decoration: none;
        color: black;
        font-weight: bold;
        background-color: #ff762d;
        border-radius: 100px;
        padding: 1rem 1.5rem;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)


# st.markdown("""
# <style>
#     button.btn.btn-outline-secondary {
#         background-color: #ff762d !important;
#         color: white !important;
#         border-radius: 12px !important;
#         font-weight: bold !important;
#         padding: 10px 20px !important;
#         border-color: #ff762d !important;
#     }
# </style>
# """, unsafe_allow_html=True)


## load Whisper model ##
@st.cache_resource
def load_model():
    return whisper.load_model("small", device='cpu')

model = load_model()
print(model.device)
print("model loaded successfully")

if "category" not in st.session_state:
    st.session_state.category = ""
if "guidelines" not in st.session_state:
    st.session_state.guidelines = []
if "is_loading" not in st.session_state:
    st.session_state.is_loading = False
if "is_submit" not in st.session_state:
    st.session_state.is_submit = False
if "is_clicked" not in st.session_state:
    st.session_state.is_clicked = False
if "stt_result" not in st.session_state:
    st.session_state.stt_result = ""

logo_img = image_to_base64("assets/logo.png")
descript_img = image_to_base64("assets/descript.svg")

st.markdown(f"""
            <a href="/" target="_self" style="text-decoration:none;">
                <img src="data:image/png;base64,{logo_img}" style="width:120px; margin-bottom:40px; margin-top:-1.5rem;"/>
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

## speech guideline suggestion ##
st.markdown(f"""
            <div style="font-weight:bold; font-size:20px; margin-bottom:10px;">
                Situation Description
            </div>
            <div style="margin-bottom:20px;">
                Please describe the current situation, including the details below.
            <div/>

            <div style="display: flex; margin-top:20px; align-items:center;">
                <img src="data:image/svg+xml;base64, {descript_img}" style="height:20px; margin-right:5px;"/>
                <div style="font-weight:bold; font-size:16px; color:#ff762d;">Detailed Situation:</div>
            </div>
            <div style="font-size:14px;">
                e.g. An underground parking lot has collapsed, and more than 10 people are trapped underground.
            </div>
            
            <div style="display: flex; margin-top:10px; align-items:center;">
                <img src="data:image/svg+xml;base64, {descript_img}" style="height:20px; margin-right:5px;"/>
                <div style="font-weight:bold; font-size:16px; color:#ff762d;">Location:</div>
            </div>
            <div style="font-size:14px;">
                e.g. Near Yeoksam Station, and the underground level is not very deep.
            </div>
            
            <div style="display: flex; margin-top:10px; align-items:center;">
                <img src="data:image/svg+xml;base64, {descript_img}" style="height:20px; margin-right:5px;"/>
                <div style="font-weight:bold; font-size:16px; color:#ff762d;">People Involved & Time of Incident:</div>
            </div>
            <div style="font-size:14px;">
                e.g. 1 elderly person presents. The incident occurred 10 minutes ago.
            </div>
            
            <div style="display: flex; margin-top:10px; align-items:center;">
                <img src="data:image/svg+xml;base64, {descript_img}" style="height:20px; margin-right:5px;"/>
                <div style="font-weight:bold; font-size:16px; color:#ff762d;">Special Notes:</div>
            </div>
            <div style="font-size:14px;">
                e.g. One person is using a wheelchair, and one has a serious leg injury.
            </div>
            """, unsafe_allow_html=True)

st.markdown(f"""
                <div style="margin-bottom:10px;"></div>
            """, unsafe_allow_html=True)


## get audio input ##
audio = mic_recorder(
    start_prompt="Click to start recording",
    stop_prompt="⏹ Stop recording",
    use_container_width=True,
    key="recorder",
    format="wav"
)

## if audio input is provided ##
if audio:
    # convert audio format to numpy
    audio_bytes = BytesIO(audio["bytes"])
    st.audio(audio_bytes, format="audio/wav")
    
    audio_bytes.seek(0)
    
    seg = AudioSegment.from_file(audio_bytes, format="wav")
    samples = np.array(seg.get_array_of_samples())
    if seg.channels > 1:
        samples = samples.reshape((-1, seg.channels)).mean(axis=1)
    
    max_int = float(1 << (8 * seg.sample_width - 1))
    samples = (samples / max_int).astype(np.float32)
    
    sr = seg.frame_rate
    if sr != 16000:
        samples = librosa.resample(samples, orig_sr=sr, target_sr=16000)
    
    
    result = model.transcribe(samples)
    st.session_state.stt_result = result["text"]
    st.markdown(f"""
                <div style="background-color: #fff1ea; border-radius: 20px; padding: 30px 30px; margin-bottom: 50px;">
                    <p style="text-align: center;">{result["text"]}</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.session_state.is_clicked = st.button("View Guidelines", use_container_width= True)
    
    
## if guideline button is clicked ##
if st.session_state.is_clicked:
    if not st.session_state.stt_result.strip():
        st.warning("Please describe the situation using your voice.")
    elif st.session_state.category == "None Selected":
        st.warning("Category selection is required.")
    else:    
        st.session_state.is_loading = True
        st.session_state.is_submit = True
        
        with st.spinner("Generating guidelines..."):
            try:
                index = st.session_state.category + "_" + "manual"
                output = process_output(index, st.session_state.stt_result, "GuideLine")
                # output = f"""
                #     ### ** 비상 가이드라인
                #     1. 대피
                #     2. 전화로 상황 알리기
                # """
                chunks = [c for c in output.split('\n') if c.strip()]
                st.session_state.guidelines = chunks
            except Exception as e:
                st.session_state.guidelines = ["❌ An error has occured."]
                print(e)
            finally:
                st.session_state.is_loading = False
                    
    
## print generated guidelines by Llama3.2-3b ##
if st.session_state.is_submit:
    st.markdown(f"""
            <div style="font-weight:bold; font-size:20px; color:#ff762d ;">
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