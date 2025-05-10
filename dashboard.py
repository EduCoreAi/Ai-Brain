import streamlit as st
import requests
import os
from datetime import datetime

API_URL = "http://localhost:1234/v1/chat/completions"

CLOUD_PROVIDERS = ["OpenAI GPT-4", "Anthropic Claude 3"]

st.set_page_config(page_title="AI-Brain v4.2.0", layout="wide")
st.title("AI-Brain v4.2.0 Dashboard")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Chat Panel ---
with st.expander("💬 Chat with AI-Brain", expanded=True):
    col1, col2 = st.columns([3,1])
    with col1:
        prompt = st.text_input("Enter your question:", key="chat_input")
    with col2:
        model = st.selectbox("Local Model", ["llama3", "mistral", "phi4-mini"], index=0)
        use_cloud = st.checkbox("Use Cloud AI")
        cloud_provider = st.selectbox("Cloud Provider", CLOUD_PROVIDERS, disabled=not use_cloud)

    if st.button("Send", key="chat_send") and prompt:
        with st.spinner("Thinking..."):
            try:
                payload = {
                    "prompt": prompt,
                    "model": model,
                    "use_cloud": use_cloud
                }
                r = requests.post(f"{API_URL}/chat", json=payload)
                if r.ok:
                    ai_response = r.json()["response"]
                    st.session_state.chat_history.append({
                        "user": prompt, 
                        "ai": ai_response,
                        "timestamp": datetime.now().isoformat(),
                        "model": "Cloud" if use_cloud else model
                    })
                    st.success(ai_response)
                else:
                    st.error(f"API Error: {r.text}")
            except Exception as e:
                st.error(f"Connection Error: {str(e)}")

    st.write("### Conversation History")
    for h in reversed(st.session_state.chat_history[-10:]):
        st.markdown(f"**You ({h['model']}):** {h['user']}")
        st.markdown(f"**AI:** {h['ai']}")
        st.caption(f"_{h['timestamp']}_")
        st.divider()

# --- Teach Panel ---
with st.expander("📚 Teach the Brain"):
    tab1, tab2 = st.tabs(["Upload Files", "Paste Text"])
    
    with tab1:
        uploaded_file = st.file_uploader("Choose a file", type=["txt", "md", "pdf"])
        domain_file = st.selectbox("Domain", ["general", "research", "manuals"], key="file_domain")
        if uploaded_file and st.button("Upload File"):
            with st.spinner("Ingesting..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                data = {"domain": domain_file}
                r = requests.post(
                    f"{API_URL}/ingest/file",
                    files=files,
                    data=data
                )
                if r.ok:
                    st.success(f"Ingested to {domain_file} domain!")
                else:
                    st.error(f"Error: {r.text}")
    
    with tab2:
        doc_text = st.text_area("Paste knowledge or notes:")
        domain_text = st.selectbox("Domain", ["general", "research", "manuals"], key="text_domain")
        if st.button("Ingest Text") and doc_text:
            # For now, treat as a fileless document (could add an endpoint for this)
            files = {"file": ("manual.txt", doc_text.encode("utf-8"))}
            data = {"domain": domain_text}
            r = requests.post(
                f"{API_URL}/ingest/file",
                files=files,
                data=data
            )
            if r.ok:
                st.success(f"Ingested to {domain_text} domain!")
            else:
                st.error(f"Error: {r.text}")

# --- Feedback Panel ---
with st.expander("📝 Feedback & Corrections"):
    if st.session_state.chat_history:
        last = st.session_state.chat_history[-1]
        st.write(f"**You:** {last['user']}")
        st.write(f"**AI:** {last['ai']}")
        rating = st.slider("Rate this answer:", 1, 5, 3)
        correction = st.text_area("Suggest a better answer (optional):")
        if st.button("Submit Feedback"):
            r = requests.post(f"{API_URL}/feedback", json={
                "prompt": last['user'],
                "response": last['ai'],
                "rating": rating,
                "correction": correction
            })
            if r.ok:
                st.success("Feedback submitted!")
            else:
                st.error(f"Error: {r.text}")
    else:
        st.info("Chat with the AI to enable feedback.")

# --- System Status Panel ---
with st.expander("⚙️ System Status"):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("API Health")
        try:
            r = requests.get(f"{API_URL}/health", timeout=5)
            st.success(f"API: {r.json()}")
        except Exception as e:
            st.error(f"API error: {e}")
    with col2:
        st.subheader("Knowledge Base")
        docs = requests.get(f"{API_URL}/documents").json()
        st.write(f"Total Documents: {len(docs)}")
        st.write(f"Recent Domains: {', '.join(set(d[3] for d in docs[:5]))}")

# --- Versioning & Backup Panel ---
with st.expander("🔄 Versioning & Backup"):
    st.write("### Backup Management")
    if st.button("Create Backup Snapshot"):
        os.makedirs("data/backups", exist_ok=True)
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.system(f"copy data\\ai-brain.db data\\backups\\{backup_name}.db")
        st.success(f"Backup created: {backup_name}")
    st.write("### Recent Feedback")
    feedback = requests.get(f"{API_URL}/feedback?limit=5").json()
    for f in feedback:
        st.caption(f"Rating: {f[3]}★ - {f[1][:50]}...")

st.caption("AI-Brain v4.2.0 | Local + Free Cloud Hybrid System | © 2025")
