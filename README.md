# 🤖 AI Agent - Streamlit RAG Chatbot

An elegant, premium, and fully responsive **Streamlit** dashboard and AI Chatbot powered by **LangChain**, **Groq (llama-3.1-8b-instant)**, and **ChromaDB**. 

Users can ask questions about the default FAQ database directly, or upload custom PDF documents to query them on-the-fly.

---

## ⚡ Local Setup

Follow these steps to run the application on your computer:

1. **Install Dependencies**:
   Ensure you have Python installed, then install the package requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Streamlit App**:
   Start the application locally:
   ```bash
   streamlit run app.py
   ```
   A browser window will open automatically at `http://localhost:8501`.

---

## 🌐 Deploy Live to the Internet (Free)

You can deploy this application live on the web in 5 minutes using **Streamlit Community Cloud** for free.

### Step 1: Upload to GitHub
1. Go to [GitHub](https://github.com) and create a new repository (e.g., `ai-agent-chatbot`).
2. Open your terminal in this project directory and run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of AI Agent chatbot"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

### Step 2: Deploy on Streamlit Cloud
1. Visit [Streamlit Community Cloud](https://share.streamlit.io/) and log in using your GitHub account.
2. Click **New app**.
3. Select your repository (`ai-agent-chatbot`), branch (`main`), and set the Main file path to `app.py`.
4. Click **Deploy!**

Your app will be built and go live on a public URL (e.g. `https://your-app-name.streamlit.app/`).

### Step 3: Configure API Keys Secures (Optional but Recommended)
Instead of typing your Groq API key in the app GUI every time, you can secure it in the Streamlit Cloud Dashboard:
1. In your deployed app page, click **Settings** (bottom right) -> **Secrets**.
2. Add your keys in TOML format:
   ```toml
   GROQ_API_KEY = "gsk_your_actual_groq_key_here..."
   LANGCHAIN_API_KEY = "lsv2_your_langchain_key_here..."
   ```
3. Save. The app will reload and securely detect the keys automatically!
