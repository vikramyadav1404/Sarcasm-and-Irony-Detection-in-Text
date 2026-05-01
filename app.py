import streamlit as st
import torch
import json
import PyPDF2
import docx
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ============================================================
# LOAD MODEL
# ============================================================
MODEL_PATH = "deberta_model"

# Load label mappings
with open(f"{MODEL_PATH}/label2id.json", "r") as f:
    label2id = json.load(f)

id2label = {v: k for k, v in label2id.items()}

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()


# ============================================================
# FILE HELPERS
# ============================================================
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text


def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])


# ============================================================
# PREDICTION FUNCTION
# ============================================================
def predict(text):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=128
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=-1).cpu().numpy()[0]

    scores = {id2label[i]: float(probs[i]) for i in range(len(probs))}
    return scores


# ============================================================
# STREAMLIT FRONTEND
# ============================================================

st.title("🎭 Sarcasm / Irony Detector – Percentage Mode")

st.write("Paste text OR upload a file. Then choose the category you want the **probability score** for.")

uploaded_file = st.file_uploader("Upload .txt / .pdf / .docx", type=["txt", "pdf", "docx"])
input_text = st.text_area("Or paste text here")

# Determine input text
text_to_predict = ""

if uploaded_file is not None:
    if uploaded_file.type == "text/plain":
        text_to_predict = uploaded_file.read().decode("utf-8")

    elif uploaded_file.type == "application/pdf":
        text_to_predict = extract_text_from_pdf(uploaded_file)

    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text_to_predict = extract_text_from_docx(uploaded_file)

elif input_text.strip():
    text_to_predict = input_text.strip()


# ============================================================
# LABEL SELECTION
# ============================================================
st.subheader("Select Label to Predict")

label_choice = st.radio(
    "Choose one",
    ["sarcasm", "irony", "regular", "figurative"]
)


# ============================================================
# RUN PREDICTION
# ============================================================
if st.button("Get Probability Score"):
    if not text_to_predict.strip():
        st.error("Please paste text or upload a file.")
    else:
        lines = [l.strip() for l in text_to_predict.split("\n") if l.strip()]

        st.subheader("Results")

        for idx, line in enumerate(lines, 1):
            scores = predict(line)
            prob = scores[label_choice] * 100  # Convert to %

            st.write(f"### 📝 Line {idx}:")
            st.write(f"**Text:** {line}")
            st.success(f"🎯 Probability for **{label_choice.upper()}** = **{prob:.2f}%**")
            st.write("---")
