# 🚨emerGen: Emergency Response Assistant Application Using Vector DB-based LLM🚨
#### for 2025 Qualcomm Edge AI Hackathon
<br>

## Team UNIDs
Chaeyeon Jang, POSTECH: jcy2749@postech.ac.kr<br>
Taehwan Kim, SKKU: dmsdl5030@g.skku.edu<br>
Namseok Lee, KU: southstone0201@naver.com<br>
Seongmin Lee, KU: kyne0127@korea.ac.kr<br>

## Main Features
### 📘Guideline Generation Based on Similar Cases and Predefined Manuals
When a user provides key information such as their **current emergency situation, location, and injury severity**, **emerGen** follows a streamlined process to deliver **personalized emergency response guidelines**:

1. Searches a **vector database** for similar **past emergency cases** or relevant **manuals**
2. Combines the retrieved data with the user’s input
3. Uses a **lightweight on-device LLM** to generate a **customized emergency guideline** tailored to the situation
🔹 By leveraging a vector DB, the system delivers accurate information without requiring additional model training, enabling fast and practical responses.

### 💬Q&A service based on Qwen2.5 model
Users can chat directly with the LLM to ask questions and receive real-time, situation-specific answers related to their emergency.

### 🔎Keyword-Based Search of Past Cases
Users can simply enter keywords to search past emergency response cases and manuals stored in the vector database.

### 💡Efficient and Practical On-Device Architecture
-The system operates as a vector DB–driven on-device application, allowing it to function independently without relying on cloud infrastructure.

-Equipped with a small, efficient LLM, it runs smoothly even in environments with limited computing resources.

-Since all information retrieval is handled via the vector DB, no additional model fine-tuning is needed — new data or categories can be added directly to the DB, making the system easy to maintain, cost-effective, and highly practical for real-world use.
 
## Overall Pipeline of emerGen
"우리 이미지 넣어야함" 
<b>Step-by-step usage scenarios</b>  <br><br>
1.
2.
3.
4.
5.
6.

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

## Install
### Setup `python` environment
```bash
conda create --name streamlit python=3.10
```
```bash
pip install torch
pip install streamlit
pip install streamlit-audiorecorder
pip install streamlit-option-menu 
pip install accelerate datasets
pip install -i https://pypi.org/simple/ bitsandbytes
pip install transformers[torch] -U
pip install langchain langchain_community langchain_huggingface
pip install PyMuPDF faiss-gpu
pip install sentence-transformers peft opencv-python
pip install kiwipiepy konlpy langchain-teddynote
pip install numpy
pip install pandas
pip install tqdm
```

## Run Server
```bash
conda activate streamlit
```
```bash
streamlit run main.py
```



