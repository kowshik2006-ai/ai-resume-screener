import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
import os
from datetime import datetime

st.set_page_config(page_title="AI Resume Screener 2026", page_icon="📄", layout="wide")

st.title("🚀 AI-Powered Resume Screener")
st.markdown("**Upload your resume + paste job description → Get instant AI scoring & feedback**")

# Sidebar for API key
with st.sidebar:
    st.header("🔑 Configuration")
    groq_api_key = st.text_input("Groq API Key", type="password", value=os.getenv("GROQ_API_KEY", ""))
    st.caption("Get free key from https://console.groq.com/keys")
    model = st.selectbox("Model", ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"], index=0)

if not groq_api_key:
    st.warning("⚠️ Please enter your Groq API key in the sidebar")
    st.stop()

client = Groq(api_key=groq_api_key)

# File uploader
resume_file = st.file_uploader("📤 Upload Resume (PDF only)", type=["pdf"])

job_description = st.text_area(
    "📋 Paste Job Description",
    height=200,
    placeholder="Paste the full job description here..."
)

analyze_button = st.button("🔥 Analyze Resume with AI", type="primary", use_container_width=True)

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

if analyze_button:
    if not resume_file:
        st.error("Please upload a resume PDF")
    elif not job_description.strip():
        st.error("Please paste the job description")
    else:
        with st.spinner("AI is analyzing your resume... (usually takes 8-12 seconds)"):
            resume_text = extract_text_from_pdf(resume_file)
            
            prompt = f"""
You are an expert technical recruiter with 15+ years of experience at FAANG companies.

Resume Text:
{resume_text}

Job Description:
{job_description}

Analyze the resume against the job description and return a STRICT JSON object with this exact structure (no extra text, no markdown):

{{
  "match_score": integer between 0 and 100,
  "strengths": ["point 1", "point 2", "point 3"],
  "weaknesses": ["point 1", "point 2"],
  "improvements": ["specific actionable suggestion 1", "suggestion 2"],
  "ats_tips": ["tip 1", "tip 2"],
  "overall_verdict": "Short one-line verdict (e.g. Strong Match / Good Fit / Needs Improvement)"
}}

Be honest, critical, and extremely specific.
"""

            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=1024,
                    response_format={"type": "json_object"}
                )
                
                import json
                result = json.loads(completion.choices[0].message.content)
                
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    score = result.get("match_score", 0)
                    color = "green" if score >= 80 else "orange" if score >= 60 else "red"
                    st.metric("🎯 Match Score", f"{score}%", delta=None)
                    st.markdown(f"<h3 style='color:{color}; text-align:center;'>{result.get('overall_verdict', '')}</h3>", unsafe_allow_html=True)
                
                with col2:
                    st.subheader("✅ Strengths")
                    for s in result.get("strengths", []):
                        st.success(s)
                    
                    st.subheader("⚠️ Areas of Improvement")
                    for w in result.get("weaknesses", []):
                        st.warning(w)
                    
                    st.subheader("💡 Suggested Improvements")
                    for imp in result.get("improvements", []):
                        st.info(imp)
                    
                    st.subheader("📌 ATS Optimization Tips")
                    for tip in result.get("ats_tips", []):
                        st.write("• " + tip)
                
                st.caption(f"Analyzed on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

st.divider()
st.markdown("**Made for freshers who want to stand out in 2026 placements**")