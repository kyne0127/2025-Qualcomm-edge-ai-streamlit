import pickle
from tqdm import tqdm
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_teddynote.retrievers import KiwiBM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_community.vectorstores.utils import DistanceStrategy

from db.preprocess import process_pdf

embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-base",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

#Create a vector database from given chunks
def create_vector_db(chunks):
    global embeddings
    db = FAISS.from_documents(chunks, embedding=embeddings, distance_strategy = DistanceStrategy.COSINE)
    return db

#Create a retriever connected to the database using given chunks and db
def get_retriver(chunks, db):
    kiwi_bm25_retriever = KiwiBM25Retriever.from_documents(chunks)
    faiss_retriever = db.as_retriever(search_kwargs={"k": 2})
    
    retriever = EnsembleRetriever(
        retrievers=[kiwi_bm25_retriever, faiss_retriever],
        weights=[0.5, 0.5],
        search_type="mmr",
    )

    return retriever


#Process a single PDF file
#ex) path: ./data/TunnelManual.pdf, base_directory: /home/user/project/
def process_single_pdf(path, base_directory):
    path = base_directory + path
    category = path.split('/')[-1].split('_')[0] #extract category
    case_or_manual = path.split('/')[-1].split('_')[1].split('.')[0] ##extract manual/case
    print(f"Processing {category}...")
    
    chunks = process_pdf(path)
    db = create_vector_db(chunks)
    retriever = get_retriver(chunks, db)
    return category, case_or_manual, retriever, chunks, db



#Create category-based vector databases for all PDF files
#Read PDF files based on source_path in the dataframe and create vector DBs
def process_pdfs_from_dataframe(df, base_directory):
    pdf_databases = {}
    unique_paths = df['Source_path'].unique() # extract unique paths only

    for path in tqdm(unique_paths):
        category, case_or_manual, retriever, chunks, db = process_single_pdf(path, base_directory)
        index = category + "_" + case_or_manual
        pdf_databases[index] = retriever

    print(pdf_databases)
    return pdf_databases

#Save vector databases locally
def save_pdf_databases(pdf_databases, filename):
    with open(filename, 'wb') as f:
        pickle.dump(pdf_databases, f)

#Load vector databases locally
def load_pdf_databases(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)
    
if __name__ == "__main__":
    print("Creating vector databases from PDF files...")
    base_directory = "/NAS/internship/JCY/2025-summer/develop/emerGen/" ##change to your own directory path
    df = pd.read_csv(base_directory + "data/full_data.csv")
    pdf_databases = process_pdfs_from_dataframe(df, base_directory)
    save_pdf_databases(pdf_databases, base_directory + "pdf_databases.pkl")
    print("Vector databases created and saved successfully.")

 
