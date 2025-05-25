import os
import argparse

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.prompts import load_prompt
from langchain.prompts import PromptTemplate # Added for generic prompt
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, StrOutputParser

# --- Environment Variable Check ---
if "OPENAI_API_KEY" not in os.environ:
    print("Error: OPENAI_API_KEY environment variable not set.")
    print("Please set it before running the script, e.g., export OPENAI_API_KEY='your_key_here'")
    exit(1)

# --- Document Loading ---
def load_documents_from_directory(directory_path):
    """
    Loads all .txt files from the specified directory.
    """
    documents = []
    if not os.path.exists(directory_path):
        print(f"Error: Directory '{directory_path}' not found.")
        return documents
    if not os.path.isdir(directory_path):
        print(f"Error: '{directory_path}' is not a directory.")
        return documents

    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory_path, filename)
            try:
                loader = TextLoader(filepath, encoding='utf-8') # Specify encoding
                documents.extend(loader.load())
                print(f"Loaded: {filename}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
        else:
            print(f"Skipped non-txt file: {filename}")
    return documents

# --- Text Splitting ---
def split_documents(documents):
    """
    Splits loaded documents into smaller chunks.
    """
    if not documents:
        return []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(splits)} chunks.")
    return splits

# --- Embeddings and Vector Store ---
def create_vector_store(document_chunks):
    """
    Creates a FAISS vector store from document chunks and OpenAI embeddings.
    """
    if not document_chunks:
        return None
    embeddings = OpenAIEmbeddings()
    try:
        vectorstore = FAISS.from_documents(document_chunks, embeddings)
        print("FAISS vector store created.")
        return vectorstore
    except Exception as e:
        print(f"Error creating FAISS vector store: {e}")
        return None

# --- Prompt Template ---
def get_rag_prompt():
    """
    Tries to load a RAG prompt from Langchain Hub.
    Falls back to a generic prompt if the hub prompt is unavailable.
    """
    try:
        # Attempt to load the prompt from Langchain Hub
        prompt = load_prompt("rlm/rag-prompt")
        print("Loaded RAG prompt from Langchain Hub: rlm/rag-prompt")
    except Exception as e:
        print(f"Could not load 'rlm/rag-prompt' from Langchain Hub (Error: {e}). Using a generic prompt.")
        # Generic RAG prompt structure
        template = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question}
Context: {context}
Answer:"""
        prompt = PromptTemplate.from_template(template)
    return prompt

# --- RAG Chain Construction ---
def format_docs(docs):
    """
    Helper function to format retrieved documents into a single string.
    """
    return "\n\n".join(doc.page_content for doc in docs)

def create_rag_chain(retriever, prompt, llm):
    """
    Creates the RAG chain using Langchain Expression Language (LCEL).
    """
    rag_chain_from_docs = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | prompt
        | llm
        | StrOutputParser()
    )

    rag_chain_with_source = RunnableParallel(
        {"context": retriever, "question": RunnablePassthrough()}
    ).assign(answer=rag_chain_from_docs)
    
    print("RAG chain created.")
    return rag_chain_with_source

# --- Main Execution Block ---
def main():
    parser = argparse.ArgumentParser(description="Langchain RAG Pipeline CLI")
    parser.add_argument("question", nargs="?", type=str, help="The question to ask the RAG pipeline.")
    args = parser.parse_args()

    # --- 1. Load Documents ---
    docs_directory = "./documents"
    loaded_docs = load_documents_from_directory(docs_directory)

    if not loaded_docs:
        print("No documents loaded. Exiting.")
        return

    # --- 2. Split Documents ---
    doc_splits = split_documents(loaded_docs)
    if not doc_splits:
        print("No document splits created. Exiting.")
        return

    # --- 3. Create Vector Store ---
    vectorstore = create_vector_store(doc_splits)
    if not vectorstore:
        print("Failed to create vector store. Exiting.")
        return

    # --- 4. Get Retriever ---
    retriever = vectorstore.as_retriever()
    print("Retriever created from FAISS vector store.")

    # --- 5. Get Prompt ---
    prompt = get_rag_prompt()

    # --- 6. Initialize LLM ---
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    print("ChatOpenAI LLM initialized (gpt-3.5-turbo).")

    # --- 7. Create RAG Chain ---
    rag_chain = create_rag_chain(retriever, prompt, llm)

    # --- 8. Process Question ---
    if args.question:
        print(f"\nProcessing question: {args.question}")
        try:
            result = rag_chain.invoke(args.question)
            # The result from rag_chain_with_source is a dictionary
            # e.g. {"context": [doc1, doc2...], "question": "...", "answer": "..."}
            answer = result.get("answer", "No answer found.")
            print("\nAnswer:")
            print(answer)

            # Optionally print context for debugging
            # print("\nRetrieved Context:")
            # for i, doc in enumerate(result.get("context", [])):
            #     print(f"--- Context Doc {i+1} ---")
            #     print(doc.page_content)
            #     print(f"Source: {doc.metadata.get('source', 'N/A')}")
            #     print("----------------------")

        except Exception as e:
            print(f"Error invoking RAG chain: {e}")
    else:
        print("\nNo question provided. Use the --question argument or provide a question as a positional argument.")
        print("Usage: python main.py \"Your question here?\"")
        parser.print_help()

if __name__ == "__main__":
    main()
