# 🧾 Smart Receipt & Bill Splitter

An AI-powered web application built with **Streamlit** and **Google Gemini Vision API** (`gemini-3.6-flash`) that automatically parses receipt images, extracts itemized bill components, and calculates proportional bill splits with taxes and fees.

---

## 🚀 Features

* **Receipt OCR & Vision Parsing:** Upload any receipt image (`.jpg`, `.jpeg`, `.png`) to automatically extract item names, quantities, and prices using Google Gemini Vision.
* **Structured Data Processing:** Utilizes `Pydantic` models to ensure strictly typed and validated JSON output for bill items, subtotal, taxes, and service charges.
* **Proportional Expense Splitting:** Dynamically assigns items to specific individuals and proportionally distributes overall taxes/tips based on individual item consumption.
* **Interactive UI:** Built using Streamlit for an intuitive, real-time dashboard experience.

---

## 🛠️ Tech Stack

* **Frontend/UI:** Streamlit
* **AI Model:** Google Gemini API (`gemini-3.6-flash` via `google-genai` SDK)
* **Data Validation:** Pydantic
* **Language & Runtime:** Python 3.10+
* **Image Processing:** Pillow (PIL)

---

## 📂 Project Structure

```text
Smart_Bill_Splitter/
├── app.py              # Main Streamlit application entry point
├── requirements.txt    # Project dependencies
├── README.md           # Project documentation
├── .gitignore          # File exclusions (excludes venv/)
└── .env.example        # Environment variable configuration template