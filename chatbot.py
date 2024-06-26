
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_community.chat_models import ChatOpenAI

OPENAI_API_KEY = "Paste your api key"

# Set up Streamlit sidebar
st.sidebar.title("Your Documents")
file = st.sidebar.file_uploader("Upload a PDF file to start asking questions", type="pdf")

# Main content area
st.header("Chatbot")

# Process PDF and generate response
if file is not None:
    try:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            separators="\n",
            chunk_size=1000,
            chunk_overlap=150,
            length_function=len
        )
        chunks = text_splitter.split_text(text)

        # Generate embeddings
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

        # Create vector store - FAISS
        vector_store = FAISS.from_texts(chunks, embeddings)

        # Get user question
        user_question = st.text_input("Type your question here")

        # Perform similarity search and generate response
        if user_question:
            match = vector_store.similarity_search(user_question)

            # Load language model for question answering
            llm = ChatOpenAI(
                openai_api_key=OPENAI_API_KEY,
                temperature=0,
                max_tokens=1000,
                model_name="gpt-3.5-turbo"
            )

            # Run question answering chain
            chain = load_qa_chain(llm, chain_type="stuff")
            response = chain.run(input_documents=match, question=user_question)

            # Display response
            st.write("Response:", response)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
