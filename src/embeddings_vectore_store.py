import os
from google.cloud import bigquery
from langchain_huggingface import HuggingFaceEmbeddings  # Changed to HuggingFace embeddings
from langchain_google_community import BigQueryLoader  # Updated import
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
PROJECT_ID = "hackathon-playground-461714"
BIGQUERY_DATASET = "synthetic_customer_conversations"
BIGQUERY_TABLE = "customer_support_translated_sentiment"
BIGQUERY_TABLE_ID = f"{PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"
VECTOR_STORE_PATH = "./chroma_db"

# --- Initialize Clients ---
# Using free HuggingFace embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",  # Free and efficient model
    model_kwargs={'device': 'cpu'},  # Use CPU (change to 'cuda' if you have GPU)
    encode_kwargs={'normalize_embeddings': True}  # Normalize embeddings for better similarity search
)

def load_and_embed_data():
    """
    Loads data from BigQuery, splits it into chunks, and embeds it into a vector store.
    """
    print(f"Loading data from BigQuery table: {BIGQUERY_TABLE_ID}")

    # Fixed SQL query with proper string handling
    query = f"""
    SELECT
        id,
        new_broad_category,
        category,
        incoming_email_en,
        reply_en,
        CONCAT(
            'Customer query: ', COALESCE(incoming_email_en, ''), '\\n',
            'Broad Category: ', COALESCE(new_broad_category, ''), '\\n',
            'Specific Category: ', COALESCE(category, ''), '\\n',
            'Agent reply: ', COALESCE(reply_en, '')
        ) AS full_context_text
    FROM
        `{BIGQUERY_TABLE_ID}`
    WHERE
        incoming_email_en IS NOT NULL AND incoming_email_en != ''
        AND reply_en IS NOT NULL AND reply_en != ''
    LIMIT 1000
    """

    loader = BigQueryLoader(
        query=query,
        project=PROJECT_ID,
        page_content_columns=["full_context_text"],
        metadata_columns=["id", "new_broad_category", "category", "incoming_email_en", "reply_en"]
    )

    documents = loader.load()

    print(f"Loaded {len(documents)} documents from BigQuery.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=20,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    print("Creating/updating vector store...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_STORE_PATH
    )
    vectorstore.persist()
    print(f"Vector store created/updated and persisted to {VECTOR_STORE_PATH}")

if __name__ == "__main__":
    load_and_embed_data()
    print("Data loading and embedding process completed.")