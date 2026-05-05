
# 🩺 Agentic Patient Triage System

## Overview

An AI-powered voice-based triage assistant designed for rural healthcare access.

The system:

* Collects patient symptoms via voice
* Classifies condition type
* Assesses severity (Mild / Severe)
* Provides home-care advice OR escalates to a doctor
* Sends structured email alerts for critical cases

---

## 🧠 Architecture

### Root Agent Flow

1. Speech-to-Text (Whisper)
2. LLM Reasoning (Groq - LLaMA 3)
3. Validation (Pydantic schema)
4. Safety Guardrails (rule-based overrides)
5. Response Generation
6. Text-to-Speech (gTTS)
7. Email Routing (SMTP for severe cases)

---

## ⚙️ Tech Stack

* LLM: Groq (llama-3.3-70b)
* Backend: Python
* UI: Streamlit
* ASR: OpenAI Whisper
* TTS: gTTS
* Validation: Pydantic
* Email: SMTP (Gmail App Password)

---

## 🚀 Setup

```bash
git clone <your_repo>
cd agentic-patient-triage

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create `.env`:

```
GROQ_API_KEY=your_key
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
```

---

## ▶️ Run Application

```bash
streamlit run app/ui.py
```

---

## 🧪 Example Flows

### ✅ Mild Case

**Input:** "I have cold and runny nose"

* Category: Upper Respiratory Issue
* Severity: Mild
* Output: Home remedies (hydration, rest)

---

### 🚨 Severe Case

**Input:** "I have chest pain and difficulty breathing"

* Severity overridden to Severe (guardrails)
* AI gives emergency warning
* Structured summary generated
* Email sent to doctor

---

## 🛡️ Safety Features

* Input validation for ASR errors
* Rule-based red flag detection
* Conservative severity classification
* No treatment advice for severe cases

---

## 📌 Future Improvements

* Multi-language support (Hindi, regional languages)
* Real-time voice streaming
* Integration with healthcare providers
* Patient history tracking

---

## 👨‍💻 Author

Abhishek Raghuwanshi
