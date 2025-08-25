import streamlit as st
import time
from utils import image_to_base64
from db.retrieve import retrieve
from db.model import get_LLM_output
from streamlit_option_menu import option_menu
import re

st.set_page_config(page_title="case_search", layout="centered")

## import image ##
paper_img = image_to_base64('assets/paper.svg')
logo_img = image_to_base64("assets/logo.png")

# style definition
st.markdown("""
    <style>
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
    
    @media (max-width: 410px){
        .nav-link{
            width:165px;
            margin: 6px 6px;
        }
    }
    </style>
""", unsafe_allow_html=True)

## logo ##
st.markdown(f"""
            <a href="/" target="_self" style="text-decoration:none;">
                <img src="data:image/png;base64,{logo_img}" style="width:120px; margin-bottom:10px; margin-top:-3rem;"/>
            </a>
            """, unsafe_allow_html=True)

## banner ##
st.markdown("""
    <div style="background-color: black; padding:15px; margin-bottom:50px;">
        <div class="title">Search for Similar Cases</div>
        <div class="description">
            Explore how emergency responses were carried out<br/>
            in past disaster situations<br/>
            similar to your current one.
        </div>
    </div>
""", unsafe_allow_html=True)

## category selection ##
options=['None Selected', 'Collapse', 'High Temp', 'Maritime', 'Mountain', 'Gen Emergency']

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

## search form ##
keyword = st.chat_input("Enter a keyword or brief description of the situation...")
# results = ['temporarys']

## if a search button has been pressed
if keyword:
    keyword = keyword.strip()
    if not keyword:
        st.warning("Please enter a keyword.")
    if selected == "None Selected":
        st.warning("Please select a category.")
    else:
        with st.spinner(f"Searching the vector database for cases related to '{keyword}'"):
            index = selected + "_" + "case"
            results = retrieve(index, keyword, "caseSearch") ##retrieve data from vectorDB and execute Llama3.2-3b model
            # results= re.findall(r"<case>(.*?)</case>", output, re.DOTALL)
        st.markdown(f"""<div style="display:flex; gap:20px; justify-content:center;">""", unsafe_allow_html = True)
        for result in results:
            output = get_LLM_output("caseSearch", result, keyword)
            st.markdown(f"""
                        <div style="background-color: white; padding: 25px 20px; border-radius:20px; width: 350px; min-height: 100px; margin-bottom: 30px;">
                            <div style="display:flex; margin-bottom:5px;">
                                <div style="color:#ff762d; font-weight:600; font-size:22px; letter-spacing:-0.2px; margin-bottom:-2px;">{selected}</div>
                                <img src="data:image/svg+xml;base64,{paper_img}" style="width:20px; margin-left:5px;"/>
                            </div>
                            <div>{output}</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        #<div style="color:#a6a6a6; font-size:12px; letter-spacing:-0.2px; margin-bottom:15px;">{result['date']}</div>
        st.markdown(f"</div>", unsafe_allow_html=True)
