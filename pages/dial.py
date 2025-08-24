import streamlit as st
from utils import image_to_base64
import json

st.set_page_config(page_title="dial", layout="centered")

## import image ##
logo_img = image_to_base64("assets/logo.png")
call_img = image_to_base64("assets/call.svg")

## logo ##
st.markdown(f"""
            <a href="/" target="_self" style="text-decoration:none;">
                <img src="data:image/png;base64,{logo_img}" style="width:120px; margin-bottom:10px; margin-top:-3rem;"/>
            </a>
            """, unsafe_allow_html=True)

st.markdown(f"""
            <div style="display:flex; flex-direction:column; padding:25px 10px; justify-content:center; align-items:center;">
                <div style="font-size:24px; font-weight:700; color:#ff762d; margin-bottom:10px;">전화번호부 검색</div>
                <div style="font-size:14px; letter-spacing:-0.2px; text-align:center;">긴급 신고 전화번호를 찾고<br/>빠르게 신고하세요.</div>
            </div>
            """, unsafe_allow_html=True)

with open("data/dial.json", "r", encoding="utf-8") as f:
    dials = json.load(f)

dialbox_html = ""
for dial in dials:
    dialbox_html += f"""
    <div style="margin-bottom:20px; width:160px; box-shadow:0px 2px 8px rgba(0,0,0,0.15); padding: 25px 15px; border-radius:20px;">
        <div style="font-size:20px; font-weight:700; letter-spacing:-0.2px; color:#ff762d">{dial['전화번호']}</div>
        <div style="margin-bottom:15px;">{dial['기관']}</div>
        <a href="tel:{dial['번호']}" style="display:flex; background-color: black; padding:10px 15px; text-decoration:none; width:120px; align-items:center; border-radius:100px; justify-content:center;">
            <div style="text-decoration:none; color:#ff762d; font-size:12px; font-weight:600;">바로 전화 걸기</div>
            <img src="data:image/svg+xml;base64,{call_img}" style="width:20px;"/>
        </a>
    </div>
    """
    
st.markdown(f"""
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap:10px; place-items:center;">
            {dialbox_html}
            """, unsafe_allow_html=True)