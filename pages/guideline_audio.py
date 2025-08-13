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

st.set_page_config(page_title="audio guideline", layout="centered")


# --- Style ---
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


# --- load model ---
@st.cache_resource
def load_model():
    return whisper.load_model("small")

model = load_model()
print("model loaded successfully")

if "category" not in st.session_state:
    st.session_state.category = ""
if "guidelines" not in st.session_state:
    st.session_state.guidelines = []
if "is_loading" not in st.session_state:
    st.session_state.is_loading = False
if "is_submit" not in st.session_state:
    st.session_state.is_submit = False

logo_img = image_to_base64("assets/logo.png")
descript_img = image_to_base64("assets/descript.svg")

st.markdown(f"""
            <a href="/" target="_self" style="text-decoration:none;">
                <img src="data:image/png;base64,{logo_img}" style="width:120px; margin-bottom:40px; margin-top:-1.5rem;"/>
            </a>
            """, unsafe_allow_html=True)

# --- category selection ---
st.markdown(f"""
            <div style="font-weight:bold; font-size:20px;">
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

# --- speech guideline suggestion ---

#버튼을 누른 후 말을 하고, 설명이 끝나면 다시 버튼을 눌러 음성 인식을 종료하세요. 
st.markdown(f"""
            <div style="font-weight:bold; font-size:20px; margin-bottom:10px;">
                상황 설명
            </div>
            <div style="letter-spacing:-0.5px; margin-bottom:20px;">
                아래 내용이 포함되게 현재 상황에 대해 설명해주세요.
            <div/>

            <div style="display: flex; margin-top:20px; align-items:center;">
                <img src="data:image/svg+xml;base64, {descript_img}" style="height:20px; margin-right:5px;"/>
                <div style="font-weight:bold; font-size:16px; color:#ff762d;">상세 상황 설명:</div>
            </div>
            <div style="font-size:14px;">
                예) 지하주차장 천장이 일부 붕괴되어 지하에 10명 이상 갇힘.
            </div>
            
            <div style="display: flex; margin-top:5px; align-items:center;">
                <img src="data:image/svg+xml;base64, {descript_img}" style="height:20px; margin-right:5px;"/>
                <div style="font-weight:bold; font-size:16px; color:#ff762d;">장소 설명:</div>
            </div>
            <div style="font-size:14px;">
                예) 근처에 역삼역이 있고, 지하 깊이는 깊지 않음.
            </div>
            
            <div style="display: flex; margin-top:5px; align-items:center;">
                <img src="data:image/svg+xml;base64, {descript_img}" style="height:20px; margin-right:5px;"/>
                <div style="font-weight:bold; font-size:16px; color:#ff762d;">인원 및 사고 발생 시각 설명:</div>
            </div>
            <div style="font-size:14px;">
                예) 노약자 1명, 어린이 2명 있음. 10분 전 사고 발생.
            </div>
            
            <div style="display: flex; margin-top:5px; align-items:center;">
                <img src="data:image/svg+xml;base64, {descript_img}" style="height:20px; margin-right:5px;"/>
                <div style="font-weight:bold; font-size:16px; color:#ff762d;">특이 사항 설명:</div>
            </div>
            <div style="font-size:14px;">
                예) 휠체어 이용자가 있음, 다리 부상이 심함.
            </div>
            """, unsafe_allow_html=True)

st.markdown(f"""
                <div style="margin-bottom:10px;"></div>
            """, unsafe_allow_html=True)


# --- recording ---
audio = mic_recorder(
    start_prompt="클릭하여 녹음 시작",
    stop_prompt="⏹ 녹음 종료",
    use_container_width=True,
    key="recorder",
    format="wav"
)

if audio:
    audio_bytes = BytesIO(audio["bytes"])
    st.audio(audio_bytes, format="audio/wav")
    
    audio_bytes.seek(0)
    
    # aud_array = np.frombuffer(audio_bytes, np.int16).flatten().astype(np.float32) / 32768.0
    seg = AudioSegment.from_file(audio_bytes, format="wav")
    samples = np.array(seg.get_array_of_samples())
    if seg.channels > 1:
        samples = samples.reshape((-1, seg.channels)).mean(axis=1)
    
    max_int = float(1 << (8 * seg.sample_width - 1))
    samples = (samples / max_int).astype(np.float32)
    
    sr = seg.frame_rate
    if sr != 16000:
        samples = librosa.resample(samples, orig_sr=sr, target_sr=16000)
    
    
    output = model.transcribe(samples)
    st.write(output["text"])
    
    submitted = st.button("가이드라인 보기", use_container_width= True)
    
    if submitted:
        st.write("가이드라인")
        
        
# --- page transfer ---
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