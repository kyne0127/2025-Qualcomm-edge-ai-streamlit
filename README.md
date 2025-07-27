# 🚨emerGen: Emergency Response Assistant Application Using Vector DB-based LLM🚨
#### for 2025 Qualcomm Edge AI Hackathon
<br>

## Team UNIDs
Chaeyeon Jang, POSTECH: jcy2749@postech.ac.kr<br>
Taehwan Kim, SKKU: dmsdl5030@g.skku.edu<br>
Seongmin Lee, KU: kyne0127@korea.ac.kr<br>
Namseok Lee, KU: southstone0201@naver.com<br>

## Main Features
#### 📑Suggest guideline based on similar past cases + pre-defined manual
Given a user's prompt (current emergency situation, location, injury severity), emerGen:<br> 
1. Searches for similar past cases or relevant manuals in the vector database
2. Combines the user's prompt with retrieved data
3. Generates customized emergency guidelines through the LLM

#### 💬Q&A service based on Phi-2 model
Users directly chat with the LLM to ask questions and get answers about their current emergency situation

#### 🔎Search past emergency response cases with keywords
Users can search for past emergecy cases retrieved from the vector DB by simply entering keywords

## Overall Pipeline of emerGen
"우리 이미지 넣어야함" 
<b>Step-by-step usage scenarios</b>  <br><br>
1.
2.
3.
4.
5.
6.

## Install
### Setup `python` environment
```bash
pip install accelerate datasets
pip install -i https://pypi.org/simple/ bitsandbytes
pip install transformers[torch] -U
pip install langchain langchain_community langchain_huggingface
pip install PyMuPDF faiss-gpu
pip install sentence-transformers peft opencv-python
pip install kiwipiepy konlpy langchain-teddynote
pip install django
```

## Run Server
```bash

```
ex) Out of the box when you enter localhost:3000

## Repository Structure
``` bash
.
├── README.md
├── data/
│   ├── 구조물 고립 사고_매뉴얼.docx
│   ├── 구조물 고립 사고_사례.docx
│   ├── ...
│   ├── dial.json
│   └── full_data.csv
│   
### db
├── create_db.py
├── extract.py
├── model.py
├── preprocess.py
├── retrieve.py # vectordb query & model inference
│
### pages
├── case_search.py
├── chat.py
├── dial.py
├── guideline.py
│
### main
├── main.py
│
### util
└── utils.py
```

# Implementation Details 
In this section, we go into detail about how we implemented the functionality for each step.
If you simply want to use our application, you don't need to read it.
## Step1 - 제목
"이미지"
<b>STEP1 - 제목 <br>
</p>

- 설명 
## Step2 - 제목 
"이미지"
<b>STEP2 - 부제목 <br>
</p>
- 설명 

"이미지"
<b>STEP2 - 부제목 <br>
</p>

## Step3 - 제목
"이미지"
<b>STEP3 - 부제목 <br>
</p>

### Step 3-1: 제목
- 설명 

### Step 3-2: 제목 
- 설명
  
## Step4 - 제목
"이미지"

<b>STEP4 - 부제목 <br>
</p>

- 설명
