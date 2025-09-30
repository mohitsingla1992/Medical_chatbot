# Streamlit page config
import streamlit as st
from PIL import Image
import pytesseract
import fitz  # PyMuPDF for PDFs
import re

from report_handler import summarize_report
from symptom_checker import check_symptoms
from rag_engine5 import chatbot_interaction
from rag_engine5 import ask_medical_question
from rag_engine5 import get_medication_info

# Tesseract config
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Streamlit page config

st.set_page_config(page_title="AI Medical Assistant", layout="wide")
# Custom CSS to resize sidebar width
# Custom CSS to style layout
st.markdown("""
    <style>
        /* Narrow and center the main content */
        .main .block-container {
            max-width: 900px;
            margin: auto;
            padding-top: 1rem;
            padding-bottom: 2rem;
        }

        /* Reduce sidebar width */
        [data-testid="stSidebar"] {
            width: 220px;
        }
        [data-testid="stSidebar"] > div:first-child {
            width: 220px;
        }
    </style>
""", unsafe_allow_html=True)



#st.image("images/images.png", caption="Medical Assistant", use_container_width=True)
st.image("images/images.png", use_container_width=False, width=200) 
st.header("🩺 AI Medical Assistant Chatbot")

# Load and display logo in sidebar
with st.sidebar:
    st.markdown("### 🧾 Patient Information")

    age = st.number_input("Enter Age", min_value=1, max_value=100, step=1)
    gender = st.selectbox("Select Gender", ["Male", "Female", "Other"])
    ethnicity = st.selectbox("Select Ethnicity/Region", [
        "Asian", "African", "European", "Hispanic", "Middle Eastern", "Other"
    ])

    st.markdown("### 🩹 Health History")

    preexisting_diseases = st.multiselect(
        "Preexisting Diseases (Cured)", 
        ["Diabetes", "Hypertension", "Asthma", "Cancer", "Tuberculosis", "Other"]
    )
    preexisting_other = st.text_input("Specify other preexisting disease (if any)")

    existing_diseases = st.multiselect(
        "Existing Diseases", 
        ["Diabetes", "Hypertension", "Heart Disease", "Kidney Disease", "Thyroid", "Other"]
    )
    existing_other = st.text_input("Specify other existing disease (if any)")

    current_medications = st.text_area("Current Medications (if any)")

    surgeries = st.multiselect(
        "Surgeries (if any)", 
        ["Appendectomy", "Gallbladder Removal", "Heart Bypass", "Knee Replacement", "C-section", "Other"]
    )
    surgeries_other = st.text_input("Specify other surgery (if any)")


# Tabs for features
tab1, tab2, tab3,tab4,tab5 = st.tabs(["Symptom Checker", "Upload Report", "Ask a Medical Question (RAG)","Find a Specialist Using AI","Medication Information"])

# Helper function to extract text
def extract_text_from_file(file):
    file_type = file.type
    if file_type == "text/plain":
        return file.read().decode("utf-8", errors="ignore")
    elif file_type == "application/pdf":
        pdf_text = ""
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            for page in doc:
                pdf_text += page.get_text()
        return pdf_text
    elif file_type.startswith("image/"):
        image = Image.open(file)
        return pytesseract.image_to_string(image)
    else:
        return "Unsupported file type."

# Tab 1: Symptom Checker
# # Tab 1: Symptom Checker
with tab1:
    if "symptom_history" not in st.session_state:
        st.session_state.symptom_history = []

    user_input = st.chat_input("Describe your symptoms...")

    if user_input:
        # Prepare detailed medical history
        medical_history = {
            "Age": age,
            "Gender": gender,
            "Ethnicity": ethnicity,
            "Preexisting Diseases": preexisting_diseases + ([preexisting_other] if preexisting_other else []),
            "Existing Diseases": existing_diseases + ([existing_other] if existing_other else []),
            "Current Medications": current_medications,
            "Surgeries": surgeries + ([surgeries_other] if surgeries_other else []),
            "Symptoms": user_input
        }

        # Format as text (or JSON if your model prefers structured input)
        patient_info = "\n".join([f"{key}: {value}" for key, value in medical_history.items()])

        st.session_state.symptom_history.append({"role": "user", "content": user_input})

        with st.spinner("Analyzing symptoms..."):
            response = check_symptoms(patient_info, st.session_state.symptom_history)

        st.session_state.symptom_history.append({"role": "assistant", "content": response})
        

    # Display chat history
    for msg in st.session_state.symptom_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if st.session_state.symptom_history and st.session_state.symptom_history[-1]["role"] == "assistant":
        with st.expander("💬 Was this response helpful?"):
            
            feedback = st.radio(
                "Please rate the usefulness of this response:",
                ["👍 Helpful", "👎 Not Helpful", "😐 Neutral"],
                key=f"symptom_feedback_{len(st.session_state.symptom_history)}"
            )
            additional_comments = st.text_area(
                "Any suggestions or concerns?",
                key=f"symptom_comment_{len(st.session_state.symptom_history)}"
            )
            if st.button("Submit Feedback", key=f"submit_symptom_feedback_{len(st.session_state.symptom_history)}"):
                st.success("✅ Thanks for your feedback!")        
        st.info("💡 Still have questions? Feel free to ask more in the **Ask a Medical Question (RAG)** tab.")

# Tab 2: Upload and Summarize Report
with tab2:
    st.subheader("📤 Upload and Summarize Medical Report")
    uploaded_file = st.file_uploader(
        "Upload medical report (PDF, TXT, or image)", 
        type=["txt", "pdf", "png", "jpg", "jpeg"],
        key="report_file"
    )

    if uploaded_file is not None:
        extracted_text = extract_text_from_file(uploaded_file)
        if st.button("Summarize Report"):
            summary = summarize_report(extracted_text)
            st.session_state["report_summary"] = summary

        if "report_summary" in st.session_state:
            st.markdown("### 📝 Summary")
            st.write(st.session_state["report_summary"])

            with st.expander("💬 Was this summary helpful?"):
                report_feedback = st.radio(
                    "Please rate the accuracy of the summary:",
                    ["✅ Accurate", "❌ Inaccurate", "🤔 Needs improvement"],
                    key="report_feedback"
                )
                report_comments = st.text_area("Any comments or corrections?", key="report_comments")
                if st.button("Submit Report Feedback"):
                    st.success("✅ Thank you for your feedback!")
            st.info("💡 Have further questions about this report? Jump to the **Ask a Medical Question (RAG)** tab to get detailed answers.")


# Tab 3: Medical Chatbot (LLM Only)
with tab3:
    st.subheader("💬 Ask Any Medical Question")
    
    # Pre-fill with last selected follow-up or question
    user_query = st.text_area(
        "Enter your medical question",
        value=st.session_state.get("user_query", "")
    )
    
    if st.button("Get Answer", key="get_llm_answer"):
        if user_query:
            result = chatbot_interaction(user_query)
            st.session_state["llm_answer"] = result["answer"]
            st.session_state["llm_followups"] = result["followup_questions"]
            st.session_state["user_query"] = user_query
        else:
            st.warning("⚠️ Please enter a question.")
    
    if "llm_answer" in st.session_state:
        st.markdown("### ✅ Answer")
        st.markdown(st.session_state["llm_answer"])

        if "llm_followups" in st.session_state and st.session_state["llm_followups"]:
            st.markdown("---")
            st.markdown("#### 🤔 Follow-up Questions")
            for i, q in enumerate(st.session_state["llm_followups"], 1):
                if st.button(f"{i}. {q}", key=f"followup_{i}"):
                    st.session_state["user_query"] = q
                    st.rerun()  # Automatically re-trigger answer generation
    
        with st.expander("💬 Was this answer helpful?"):
            feedback = st.radio(
                "How would you rate the answer?",
                ["👍 Helpful", "👎 Not Helpful", "😐 Neutral"],
                key="llm_feedback"
            )
            comments = st.text_area("Any suggestions to improve the answer?", key="llm_comments")
            if st.button("Submit Feedback"):
                st.success("✅ Thanks for your feedback!")

# ------------------------ Tab 4: Specialist Finder (LLM-Based) ------------------------ #
with tab4:
    st.header("👨‍⚕️ Find a Specialist Using AI")
    symptom_input = st.text_input("Describe your symptom (e.g., chest pain, blurry vision):")

    if st.button("Recommend Specialist"):
        if symptom_input:
            prompt = f"""
You are a medical assistant. Based on the symptom provided by the user, suggest the most appropriate type of specialist doctor. 
The symptom is: "{symptom_input}". 
Respond with only the name of the specialist, such as Cardiologist, Dermatologist, Psychiatrist, etc.
"""

            try:
                response = ask_medical_question(prompt)
                st.success(f"👉 You should consult a **{response.strip()}**.")
            except Exception as e:
                st.error(f"⚠️ Failed to get recommendation: {e}")
        else:
            st.warning("Please enter your symptom.")

with tab5:
    st.header("💊 Medication Information")
    med_name = st.text_input("Enter medication name:")
    
    if st.button("Get Medication Info") and med_name.strip():
        with st.spinner("Fetching structured medication details..."):
            try:
                info = get_medication_info(med_name.strip())
                # Render the response using markdown so structure shows nicely
                st.markdown(info)
            except Exception as e:
                st.error(f"❌ Failed to get medication info: {e}")

