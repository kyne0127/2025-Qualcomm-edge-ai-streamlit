import os
import pandas as pd
from tqdm import tqdm

from create_db import process_pdfs_from_dataframe, load_pdf_databases, save_pdf_databases
from model import get_QA_output, get_guide_line_output

import warnings
warnings.filterwarnings("ignore")

### DB ###

# 있으면 가져오고 없으면 만들기
base_dir = "/home/a2024712006/qualcomm/"
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

    # 해당 category에서 관련된 정보 가져옴
    retriever = pdf_databases[category]
    context = retriever.invoke(input_data)
    print(context)
    # QA 모델에 입력후 출력
    if task == 'QA':
        response = get_QA_output(context, input_data)
    elif task == 'GuideLine':
        response = get_guide_line_output(context, input_data)
    else:
        raise ValueError("Invalid task. Choose either 'QA' or 'GuideLine'.")
    print('Answer:', response)

    return response





