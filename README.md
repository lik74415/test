# Langchain RAG Demo Project

This project demonstrates a simple Retrieval Augmented Generation (RAG) pipeline using Langchain, OpenAI, and FAISS.
It allows you to ask questions based on the content of text documents stored in the `documents` directory.

## Project Structure

- `main.py`: The main Python script that runs the RAG pipeline.
- `requirements.txt`: A list of Python dependencies for the project.
- `documents/`: A directory containing the source text documents.
    - `doc1.txt`: Sample document 1.
    - `doc2.txt`: Sample document 2.

## Setup

1.  **Clone the repository (if applicable) or download the files.**

2.  **Create and activate a Python virtual environment:**

    ```bash
    python -m venv venv
    # On Windows
    # venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set your OpenAI API Key:**

    You need an OpenAI API key for this demo to work, as it uses OpenAI models for embeddings and generation.
    Set the `OPENAI_API_KEY` environment variable:

    -   **macOS/Linux:**
        ```bash
        export OPENAI_API_KEY='your_openai_api_key_here'
        ```
        (You might want to add this to your `.bashrc` or `.zshrc` for persistence)

    -   **Windows (PowerShell):**
        ```powershell
        $Env:OPENAI_API_KEY='your_openai_api_key_here'
        ```
        (For persistence, you might need to set it in System Environment Variables)

    -   **Windows (CMD):**
        ```bash
        set OPENAI_API_KEY=your_openai_api_key_here
        ```

    **Important:** Replace `your_openai_api_key_here` with your actual OpenAI API key.

## Running the Demo

To ask a question, run the `main.py` script with the `--question` argument:

```bash
python main.py --question "What is Langchain?"
```

Or:

```bash
python main.py --question "Explain RAG."
```

The script will process the documents in the `documents` directory, build a knowledge base, and then use it to answer your question.

## How it Works

The `main.py` script performs the following:
1.  Checks for the `OPENAI_API_KEY`.
2.  Loads text documents from the `./documents` directory.
3.  Splits the documents into smaller, manageable chunks.
4.  Generates numerical embeddings (vector representations) for these chunks using OpenAI's embedding models.
5.  Stores these embeddings in a FAISS vector store for efficient similarity searching.
6.  Creates a retriever that can fetch relevant document chunks based on a query.
7.  Uses a pre-defined prompt template suitable for RAG tasks.
8.  Initializes an OpenAI language model (e.g., GPT-3.5 Turbo).
9.  Constructs a RAG chain that:
    a.  Takes your question.
    b.  Retrieves relevant document chunks (context) using the retriever.
    c.  Formats a prompt including your question and the retrieved context.
    d.  Sends this prompt to the language model.
    e.  Returns the language model's answer.
10. Prints the answer to the console.
