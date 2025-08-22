import os
import pandas as pd
from tqdm import tqdm

from db.create_db import process_pdfs_from_dataframe, load_pdf_databases, save_pdf_databases
# from db.model import get_QA_output, get_guide_line_output, get_case_search_output
from db.model import get_LLM_output

import warnings
import unicodedata

warnings.filterwarnings("ignore")

### DB ###

# 있으면 가져오고 없으면 만들기
base_dir = "/NAS/internship/JCY/2025-summer/develop/emerGen/"
df = pd.read_csv(base_dir + "data/full_data.csv")
db_filename = os.path.join(base_dir, 'pdf_databases.pkl')
if os.path.exists(db_filename):
    pdf_databases = load_pdf_databases(db_filename)
else:
    pdf_databases = process_pdfs_from_dataframe(df, base_dir)
    save_pdf_databases(pdf_databases, db_filename)


### Inference ###
def process_output(category, input_data, task):
    global pdf_databases
    print(pdf_databases)
    
    # normalized_category = unicodedata.normalize("NFC", category)
    # normalized_db = {unicodedata.normalize("NFC", k): v for k, v in pdf_databases.items()}

    
    # import unicodedata

    # print("[사용자 입력 category]", category)
    # print("[입력 bytes]", category.encode())
    # print("[입력 NFC]", unicodedata.normalize("NFC", category).encode())
    # print("[입력 NFD]", unicodedata.normalize("NFD", category).encode())

    # for k in pdf_databases.keys():
    #     print("\n[KEY] 원래:", k)
    #     print("→ bytes:", k.encode())
    #     print("→ NFC:", unicodedata.normalize("NFC", k).encode())
    #     print("→ NFD:", unicodedata.normalize("NFD", k).encode())
    #     print("→ matched NFC?", unicodedata.normalize("NFC", k) == unicodedata.normalize("NFC", category))

    # 해당 category에서 관련된 정보 가져옴
    retriever = pdf_databases[category]
    context = retriever.invoke(input_data)
    print(context)
    # QA 모델에 입력후 출력
    response = get_LLM_output(task, context, input_data)
    return response

def retrieve(category, input_data):
    global pdf_databases
    
    retriever = pdf_databases[category]
    context = retriever.invoke(input_data)
    
    return context
    




