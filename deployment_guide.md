# Deployment Guide: Hosting your Chat Assistant

Since this application is built using **Streamlit**, it communicates with the frontend using stateful WebSocket connections. 

---

## ⚠️ Important Note regarding Vercel
Vercel is designed for **serverless, stateless applications** (like Next.js, React, or FastAPI/Flask backend endpoints). 
* **WebSocket Limitation**: Vercel Serverless functions **do not support WebSockets** or stateful long-lived connections.
* **Timeout Limitation**: Vercel Serverless runs have a strict execution limit (10–15 seconds), which will cause timeouts when the app initializes heavy document search embeddings.
* **Result**: If you deploy a Streamlit app to Vercel, it will get stuck on an infinite loading screen.

Therefore, we highly recommend deploying your assistant to platforms that natively support Streamlit and WebSockets: **Streamlit Community Cloud** or **Hugging Face Spaces**. Both are 100% free.

---

## Option 1: Streamlit Community Cloud (Recommended & Easiest)
This is the official platform to host Streamlit apps directly from your GitHub repository for free.

### Step 1: Push Code to GitHub
1. Go to [GitHub](https://github.com) and create a new repository (e.g., `workspace-chat-assistant`).
2. Open your terminal in your project directory and run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Workspace Assistant"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

### Step 2: Deploy to Streamlit Cloud
1. Go to [Streamlit Share](https://share.streamlit.io/) and log in with your GitHub account.
2. Click **New app**.
3. Fill in the deployment details:
   - **Repository**: `your-github-username/workspace-chat-assistant`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Click **Deploy!**

### Step 3: Add API Secrets (Required)
Since we hid the API key inputs from the website interface, you need to configure them securely in your app's dashboard settings:
1. In your deployed app's webpage, click **Settings** (bottom-right) -> **Secrets**.
2. Paste your keys in TOML format:
   ```toml
   GROQ_API_KEY = "gsk_your_actual_groq_key_here..."
   LANGCHAIN_API_KEY = "lsv2_your_langchain_key_here..."
   ```
3. Click **Save**. The website will reload and run immediately!

---

## Option 2: Hugging Face Spaces (Alternative)
Hugging Face Spaces provides free, persistent hosting for ML and Streamlit apps.

### Step 1: Create a Space
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and log in.
2. Click **Create new Space**.
3. Configure the Space:
   - **Space Name**: `workspace-chat-assistant`
   - **SDK**: Select **Streamlit** (Python).
   - **Space License**: Public or Private.
4. Click **Create Space**.

### Step 2: Push your Code
You can upload your files (`app.py`, `requirements.txt`, `.streamlit/config.toml`) directly through the browser interface or push using Git:
```bash
git remote add hf https://huggingface.co/spaces/your-username/workspace-chat-assistant
git push -u hf main
```

### Step 3: Add Secret Variables
1. Go to your Space's **Settings** tab.
2. Scroll down to **Variables and secrets** -> **New secret**.
3. Add your secrets:
   - Name: `GROQ_API_KEY` / Value: `your-groq-key`
   - Name: `LANGCHAIN_API_KEY` / Value: `your-langchain-key`
4. The Space will automatically rebuild and go live!
