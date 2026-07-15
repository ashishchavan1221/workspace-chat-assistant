import streamlit as st
import os
import tempfile
import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

# Dynamic search fallback logic
try:
    from langchain_chroma import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    VECTOR_SEARCH_AVAILABLE = False

try:
    from langchain_community.retrievers import BM25Retriever
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False

from langchain_groq import ChatGroq

# Set up page configurations
st.set_page_config(
    page_title="Workspace Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Silent API Key configurations (not displayed on screen)
groq_api_key = os.environ.get("GROQ_API_KEY", "")
langchain_api_key = os.environ.get("LANGCHAIN_API_KEY", "")

os.environ["GROQ_API_KEY"] = groq_api_key
if langchain_api_key:
    os.environ["LANGCHAIN_API_KEY"] = langchain_api_key
    os.environ["LANGCHAIN_TRACKING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "ai-chatbot"

# Custom premium CSS
st.markdown("""
<style>
    /* Google Font Import */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        background-color: #0F0C20;
        zoom: 1.08;
    }
    
    /* Hide Streamlit default headers & sidebar */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div[data-testid="stSidebar"] {display: none;}
    
    /* Main Layout Margins */
    .main .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 900px;
    }
    
    /* Title Gradient styling */
    .title-gradient {
        background: linear-gradient(135deg, #a29bfe 10%, #6c5ce7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.5rem;
        text-align: center;
        margin-bottom: 5px;
        letter-spacing: -1.5px;
    }
    
    .subtitle-text {
        color: #b2bec3;
        font-size: 1.25rem;
        text-align: center;
        margin-top: 0px;
        margin-bottom: 25px;
        font-weight: 300;
    }
    
    /* Status Badge styling */
    .status-badge-container {
        text-align: center;
        margin-bottom: 25px;
    }
    
    .status-badge {
        display: inline-block;
        background: rgba(108, 92, 231, 0.12);
        border: 1px solid rgba(108, 92, 231, 0.25);
        border-radius: 30px;
        padding: 6px 18px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #a29bfe;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 15px rgba(108, 92, 231, 0.1);
    }
    
    /* Collapsible Expander customization */
    .stExpander {
        background-color: #1D1934 !important;
        border: 1px solid rgba(108, 92, 231, 0.15) !important;
        border-radius: 12px !important;
        margin-bottom: 25px;
    }
    
    /* Chat inputs */
    .stChatInput {
        border-radius: 12px !important;
        border: 1px solid rgba(108, 92, 231, 0.2) !important;
        background-color: #1D1934 !important;
        color: white !important;
    }

    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0f0c20;
    }
    ::-webkit-scrollbar-thumb {
        background: #342a59;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #6c5ce7;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to cache HuggingFace Embeddings
@st.cache_resource(show_spinner="Loading embedding model (this may take a minute)...")
def get_embedding_model():
    if not VECTOR_SEARCH_AVAILABLE:
        return None
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Main document parsing and database/retriever creation function
def setup_retriever(source_type, uploaded_file=None):
    # Determine the identifier for caching source
    source_id = source_type
    if source_type == "Upload Custom PDF" and uploaded_file is not None:
        source_id = f"PDF_{uploaded_file.name}_{uploaded_file.size}"
        
    # Check if we already have this retriever initialized
    if "retriever" in st.session_state and st.session_state.get("current_source_id") == source_id:
        return st.session_state.retriever

    # Otherwise build a new retriever
    with st.spinner("Processing document and preparing search engine..."):
        documents = []
        
        if source_type == "Default FAQs":
            url = "https://codeunnati.edunetfoundation.com/faqs"
            try:
                response = requests.get(url, timeout=15)
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Extract FAQS content or text elements
                text_content = ""
                faq_div = soup.find("div", {"class": "faqs"}) or soup.find("main")
                if faq_div:
                    text_content = faq_div.get_text(separator="\n")
                else:
                    text_content = soup.get_text(separator="\n")
                
                # Clean text spacing
                cleaned_text = "\n".join([line.strip() for line in text_content.splitlines() if line.strip()])
                documents = [Document(page_content=cleaned_text, metadata={"source": url})]
            except Exception as e:
                st.error(f"Error fetching URL: {str(e)}")
                return None
        
        elif source_type == "Upload Custom PDF" and uploaded_file is not None:
            try:
                # Save uploaded file to temp file to read via PDF loader
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                
                loader = PyPDFLoader(tmp_path)
                documents = loader.load()
                
                os.remove(tmp_path)
            except Exception as e:
                st.error(f"Error parsing PDF: {str(e)}")
                return None
        
        else:
            return None

        if not documents:
            return None

        # Text splitting
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        texts = text_splitter.split_documents(documents)

        retriever = None
        retriever_type = "None"

        # Build retriever based on availability
        if VECTOR_SEARCH_AVAILABLE:
            try:
                embeddings = get_embedding_model()
                vectorstore = Chroma.from_documents(documents=texts, embedding=embeddings)
                retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
                retriever_type = "Semantic Search (Vector)"
            except Exception as e:
                if BM25_AVAILABLE:
                    retriever = BM25Retriever.from_documents(texts)
                    retriever_type = "Keyword Search (BM25 Fallback)"
                else:
                    st.error(f"Search engine build failed: {str(e)}")
                    return None
        elif BM25_AVAILABLE:
            retriever = BM25Retriever.from_documents(texts)
            retriever_type = "Keyword Search (BM25)"
        else:
            st.error("Error: No search engine package (langchain-chroma or rank-bm25) is available.")
            return None

        # Save to state
        st.session_state.retriever = retriever
        st.session_state.retriever_type = retriever_type
        st.session_state.current_source_id = source_id
        return retriever

# Custom Query function that retrieves context and invokes LLM directly
def get_answer(query, retriever, api_key):
    docs = retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    prompt = f"""You are a helpful and friendly personal assistant.
You have access to the following context, which is the loaded document:
{context}

Answer the user's question.
- If the question is related to the context document, answer it based on the context. Do not mention "based on the context provided" or similar phrases; just answer directly and naturally.
- If the question is not related to the context (e.g. booking flights, general queries, everyday tasks, advice), do NOT say "I don't know based on the context" or mention the document. Instead, answer the question as a helpful general assistant using your general knowledge, and offer suggestions, steps, or guides to help the user.

Question: {query}
Answer:"""
    
    llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=api_key, temperature=0.6)
    response = llm.invoke(prompt)
    return response.content


# Layout centering logic using st.columns
left_margin, center_col, right_margin = st.columns([1.2, 5, 1.2])

with center_col:
    # Main Header
    st.markdown("<h1 class='title-gradient'>💬 Workspace Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle-text'>A clean, modern chat interface designed for your documents.</p>", unsafe_allow_html=True)

    # Document configuration inside a clean expander
    with st.expander("📂 Configure Knowledge Source", expanded=False):
        source_type = st.radio(
            "Select document source:",
            options=["Default FAQs", "Upload Custom PDF"],
            index=0
        )
        uploaded_file = None
        if source_type == "Upload Custom PDF":
            uploaded_file = st.file_uploader("Upload PDF document:", type=["pdf"])

    # Initialize retriever
    retriever = setup_retriever(source_type, uploaded_file)

    # Display active search engine status
    if retriever:
        source_name = source_type if source_type != "Upload Custom PDF" else (uploaded_file.name if uploaded_file else "Uploaded PDF")
        st.markdown(
            f"""
            <div class="status-badge-container">
                <span class="status-badge">🟢 {st.session_state.get('retriever_type', 'Ready')} | Source: {source_name}</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="status-badge-container">
                <span class="status-badge" style="color: #ff7675; border-color: rgba(255, 118, 117, 0.4); background: rgba(255, 118, 117, 0.08);">
                    🔴 Waiting for Document Input
                </span>
            </div>
            """, 
            unsafe_allow_html=True
        )

    # Chat interface
    if not groq_api_key:
        st.warning("⚠️ Groq API Key environment variable is missing. Please set GROQ_API_KEY to start the chatbot.")
    elif not retriever:
        if source_type == "Upload Custom PDF":
            st.info("📂 Expand the configuration menu above and upload a PDF to initiate.")
        else:
            st.error("❌ Failed to load the default FAQ database. Check your network configuration.")
    else:
        # Initialize message list in session state if empty
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! How can I help you today? Feel free to ask me anything about the document or any general questions."}
            ]

        # Render conversation transcript
        for message in st.session_state.messages:
            avatar = "👤" if message["role"] == "assistant" else "🧑"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask a question..."):
            with st.chat_message("user", avatar="🧑"):
                st.markdown(prompt)
            
            st.session_state.messages.append({"role": "user", "content": prompt})

            try:
                with st.chat_message("assistant", avatar="👤"):
                    message_placeholder = st.empty()
                    with st.spinner("Typing..."):
                        response_text = get_answer(prompt, retriever, groq_api_key)
                    
                    message_placeholder.markdown(response_text)
                
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                st.error(f"An error occurred during query execution: {str(e)}")
