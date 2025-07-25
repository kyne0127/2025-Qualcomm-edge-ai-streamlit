import pickle
from tqdm import tqdm
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_teddynote.retrievers import KiwiBM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_community.vectorstores.utils import DistanceStrategy

from preprocess import process_pdf

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={'device': 'cuda'},
    encode_kwargs={'normalize_embeddings': True}
)

# 현재 chunks를 이용하여 vector db 생성
def create_vector_db(chunks):
    global embeddings
    db = FAISS.from_documents(chunks, embedding=embeddings, distance_strategy = DistanceStrategy.COSINE)
    return db

# 현재 chunk와 db를 이용하여 db와 연결된 retriever 생성
def get_retriver(chunks, db):
    kiwi_bm25_retriever = KiwiBM25Retriever.from_documents(chunks)
    faiss_retriever = db.as_retriever(search_kwargs={"k": 2})
    
    retriever = EnsembleRetriever(
        retrievers=[kiwi_bm25_retriever, faiss_retriever],
        weights=[0.5, 0.5],
        search_type="mmr",
    )

    return retriever


# 단일 PDF 파일 처리
#ex) path: ./data/지하구조물_매뉴얼.pdf, base_directory: /home/a2024712006/qualcomm/
def process_single_pdf(path, base_directory):
    path = base_directory + path
    category = path.split('/')[-1].split('_')[0] # 카테고리 추출
    print(f"Processing {category}...")
    
    chunks = process_pdf(path)
    db = create_vector_db(chunks)
    retriever = get_retriver(chunks, db)
    return category, retriever, chunks, db



# 모든 pdf 파일에 대해 카테고리별 vector db 생성
# df에 있는 Source_path를 기준으로 pdf 파일을 읽어와서 vector db 생성

def process_pdfs_from_dataframe(df, base_directory):
    pdf_databases = {}
    unique_paths = df['Source_path'].unique() # 중복되지 않은 경로만 추출

    for path in tqdm(unique_paths):
        category, retriever, chunks, db = process_single_pdf(path, base_directory)
        pdf_databases[category] = retriever

    return pdf_databases

# local 저장
def save_pdf_databases(pdf_databases, filename):
    with open(filename, 'wb') as f:
        pickle.dump(pdf_databases, f)

# local 로드 
def load_pdf_databases(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)
    
if __name__ == "__main__":
    print("Creating vector databases from PDF files...")
    base_directory = "/home/a2024712006/qualcomm/"
    df = pd.read_csv(base_directory + "data/full_data.csv")
    pdf_databases = process_pdfs_from_dataframe(df, base_directory)
    save_pdf_databases(pdf_databases, base_directory + "pdf_databases.pkl")
    print("Vector databases created and saved successfully.")
    
# 일단 고려사항 
# 1. 각 카테고리에 추가로 pdf 파일이 추가되면, 해당 카테고리의 retriever를 업데이트해야 함
# 2. 현재는 각 카테고리별 문서 1개씩만 처리하고 있지만, 여러 개의 문서를 처리할 수 있도록 확장 가능


 