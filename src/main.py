import os
import json
from access_control import filter_documents_by_role
import openai
import faiss
import pickle
import time
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_community.llms import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from auth import authenticate_user
from log import log_access


# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Paths
DATA_DIR = "../data"
QUERIES_FILE = os.path.join(DATA_DIR, "queries.json")
INDEX_PATH = "faiss_index.pkl"

# Load and process multiple documents
def load_documents_from_directory(directory):
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    documents = []
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        ext = os.path.splitext(file_name)[1].lower()
        
        if ext == ".txt":
            loader = TextLoader(file_path)
        elif ext == ".pdf":
            loader = PyPDFLoader(file_path)
        else:
            continue 
        
        documents.extend(loader.load())
    
    return documents

# Split documents into chunks dynamically
def split_documents(documents, chunk_size=500, chunk_overlap=100):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(documents)

# Create or load FAISS index
def create_faiss_index(chunks, index_path=INDEX_PATH):
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=OPENAI_API_KEY)

    if os.path.exists(index_path):
        with open(index_path, "rb") as f:
            vector_store = pickle.load(f)
    else:
        vector_store = FAISS.from_documents(chunks, embeddings)
        with open(index_path, "wb") as f:
            pickle.dump(vector_store, f)
    
    return vector_store

# Retrieve top K relevant documents
def retrieve_documents(query, vector_store, role_id, top_k=3):
    retrieved_docs = vector_store.similarity_search(query, k=top_k)
    return filter_documents_by_role(role_id, retrieved_docs)

# Generate response using GPT-4
def generate_response(query, retrieved_docs, max_retries=5):
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"

    for attempt in range(max_retries):
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that answers questions based on provided context."},
                    {"role": "user", "content": prompt}
                ],
            )
            return response.choices[0].message["content"]
        except openai.RateLimitError:
            wait_time = (2 ** attempt)
            print(f"Rate limit hit. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    raise Exception("Max retries reached. Try again later.")

# Load queries from JSON file
def load_queries(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Query file not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Main function
def main():
    # Prompt for user credentials
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    user_data = authenticate_user(username, password)
    if not user_data:
        print("Authentication failed.")
        return
    role_id = user_data["role_id"]
    user_id = user_data["user_id"]
    try:
        # Load and process documents
        documents = load_documents_from_directory(DATA_DIR)
        if not documents:
            print("No valid documents found.")
            return
        
        chunks = split_documents(documents)
        vector_store = create_faiss_index(chunks)

        # Load queries
        queries = load_queries(QUERIES_FILE)

        results = []
        for query_data in queries:
            query = query_data["question"]
            retrieved_docs = retrieve_documents(query, vector_store, role_id)
            response = generate_response(query, retrieved_docs)
            
            # Log access for each retrieved document
            for doc in retrieved_docs:
                # Assume each doc has an 'id' in metadata; if not, use a fallback value.
                doc_id = doc.metadata.get("id", -1)
                log_access(user_id, doc_id, "GRANTED")
            
            results.append({
                "query_id": query_data["query_id"],
                "question": query,
                "retrieved_docs": [
                    {"source": doc.metadata.get("source", "Unknown"), "content": doc.page_content[:500]}
                    for doc in retrieved_docs
                ],
                "response": response
            })

        # Save results to a JSON file
        output_file = os.path.join(DATA_DIR, "results.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)

        print(f"Results saved to {output_file}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
