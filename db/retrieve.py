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

#Load if it exists, otherwise build and save a new one
base_directory = "/NAS/internship/JCY/2025-summer/develop/emerGen/" #change to your own directory path
df = pd.read_csv(base_directory + "data/full_data.csv")
db_filename = os.path.join(base_directory, 'pdf_databases.pkl')
if os.path.exists(db_filename):
    pdf_databases = load_pdf_databases(db_filename)
else:
    pdf_databases = process_pdfs_from_dataframe(df, base_directory)
    save_pdf_databases(pdf_databases, db_filename)


### Inference ###
def process_output(category, input_data, task):
    global pdf_databases
    print(pdf_databases)

    #Retrieve relevant information from the given category
    retriever = pdf_databases[category]
    context = retriever.invoke(input_data)
    print(context)
    #Pass context and input to the QA model and return output
    response = get_LLM_output(task, context, input_data)
    return response

#for caseSearch task type
def retrieve(category, input_data, task):
    global pdf_databases
    
    retriever = pdf_databases[category]
    context = retriever.invoke(input_data)
    print(context)
    
    return context
    




