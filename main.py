import streamlit as st
from utils import image_to_base64

st.set_page_config(page_title="emerGen", layout="centered")

logo_img = image_to_base64("assets/logo.png")
banner_img = image_to_base64("assets/main_banner_no_bg.png")
q_n_a_img = image_to_base64("assets/q&a.png")
case_search_img = image_to_base64("assets/case_search.png")
arrow_img = image_to_base64("assets/arrow_right.svg")


st.markdown("""
<style>
/* 기본 스타일 설정 */
body {
    font-family: 'Pretendard', sans-serif;
}

/* 배너 스타일 */
.banner-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2rem 1rem;
    position: relative;
}
.banner-text {
    flex: 1;
    # padding-left: 1rem;
}
.banner-head-orange {
    color: #ff762d;
    font-size: 24px;
    font-weight: 800;
    line-height: 1.2;
    letter-spacing: -0.3px;
}
.banner-head-black {
    color: black;
    font-size: 24px;
    font-weight: 800;
    line-height: 1.4;
    letter-spacing: -0.3px;
}
.banner-sub {
    font-size: 13px;
    margin-top: 0.5rem;
}
.banner-img {
    position: absolute;
    left: 18rem;
    bottom: 1;
    width: 180px;
    z-index: 0;
}

/* 가이드라인 버튼 */
a.guide-button {
    text-decoration: none;
    background-color: black;
    color: white;
    padding: 1.5rem;
    border-radius: 15px;
    margin-top: 2rem;
    width: 100%;
    max-width: 400px;
    display: flex;
    align-items: center;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
}
.guide-button-left {
    color: #ff762d;
    font-weight: bold;
    font-size: 16px;
    width: 100px;
    text-align: center;
}
.guide-button-right {
    font-size: 14px;
    text-align: left;
    margin-left: 1rem;
    letter-spacing: -0.2px;
}

/* Q&A / 사례 버튼 */
.button-row {
    display: flex;
    gap: 1rem;
    margin-top: 1.5rem;
}
a.qna-btn, a.case-btn {
    text-decoration: none;
    border-radius: 15px;
    height: 100px;
    width: 50%;
    font-weight: 700;
    font-size: 15px;
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
}
a.qna-btn {
    background-color: #ff762d;
    color: black;
}
a.case-btn {
    background-color: black;
    color: white;
}
.qna-btn img, .case-btn img {
    position: absolute;
    left: 1rem;
    width: 80px;
    height: auto;
}

/* 구조 요청 섹션 */
.footer {
    background-color: black;
    color: white;
    text-align: center;
    padding: 5rem 1rem;
    margin-top: 3rem;
    border-radius: 0;
}
.footer-title {
    font-size: 20px;
    font-weight: bold;
}
.footer-sub {
    font-size: 13px;
    margin-top: 0.5rem;
}
a.call-button {
    text-decoration: none;
    background-color: #ff762d;
    color: black;
    padding: 0.7rem 1.5rem;
    border-radius: 30px;
    font-size: 13px;
    font-weight: bold;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ---- HTML BODY ---- #
st.markdown(f"""
<img src="data:image/png;base64,{logo_img}" style="width:120px; marin-bottom:10px; margin-top:-2rem;"/>
<div class="banner-container">
    <div class="banner-text">
        <div class="banner-head-orange">여러분의 안전을 위해,</div>
        <div class="banner-head-black">비상 대응 어시스턴트</div>
        <div class="banner-sub">괜찮아요. 저에게 어떤 상황에 처해있는지 알려주세요.</div>
    </div>
    <img src="data:image/png;base64,{banner_img}" class="banner-img"/>
</div>

<!-- 가이드라인 보기 버튼 -->
<a href="/guideline" target="_self" class="guide-button">
    <div class="guide-button-left">가이드라인<br>보기</div>
    <div class="guide-button-right">지시에 따라 상황을 간단하게 입력하고,<br>대응 가이드라인 받기</div>
</a>

<!-- Q&A / 사례 검색 -->
<div class="button-row">
    <a href="/chat" target="_self" class="qna-btn">
        <div style="margin-left: 4rem; z-index: 0;">Q & A<br>채팅</div>
        <img src="data:image/png;base64,{q_n_a_img}" class="qna-btn img"/>
    </a>
    <a href="/case_search" target="_self" class="case-btn">
        <img src="data:image/png;base64,{case_search_img}" class="case-btn img"/>
        <div style="margin-left: 4rem; z-index: 0;">비슷한 사례<br>검색하기</div>
    </a>
</div>

<!-- 구조 요청 -->
<div class="footer">
    <div class="footer-title">구조 요청은 하셨나요?</div>
    <div class="footer-sub">가이드라인을 받기 전에, 구조 요청이 가장 먼저입니다.</div>
    <a href="/dial" target="_self" class="call-button">
        전화번호부 보기
        <img src="data:image/svg+xml;base64,{arrow_img}" style="height:16px; width:auto;"/>
    </a>
</div>
""", unsafe_allow_html=True)
