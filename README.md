# hackindia-spark-7-north-region-code-sharks
Hackathon team repository for Code Sharks - [hackindia-team:hackindia-spark-7-north-region:code-sharks]

# 🧬 Genetic Guardrail

### AI-Powered Pharmacogenomics Clinical Decision Support System (CDSS)

---

## 🚀 Overview

**Genetic Guardrail** is a production-ready backend system that leverages **genomic data (VCF files)** to provide **personalized drug safety recommendations**. It bridges the gap between **genetic insights and clinical decision-making**, enabling safer and more effective prescriptions.

---

## ❗ Problem Statement

Lack of integration between genomic data and clinical decision-making leads to **suboptimal and risky medication choices**, resulting in adverse drug reactions and ineffective treatments.

---

## 💡 Solution

<img width="1919" height="865" alt="image" src="https://github.com/user-attachments/assets/400b444f-bce1-42cf-88b1-56ef4cddcb17" />

Genetic Guardrail analyzes patient genomic data to:

* Identify enzyme phenotypes (e.g., CYP2D6, CYP2C19)
* Assess drug-specific risks using clinical rules (CPIC-based)
* Provide clear, actionable recommendations
* Ensure reliability with zero-failure architecture

---

## 🏗️ Architecture

```
VCF File → Agent 1 (Parser) → Agent 2 (Risk Engine)
         → Agent 3 (Clinical Explainer) → Final Output
                         ↓
                       Cache
```

---

## ⚙️ Key Features

### 🧬 Genomic Analysis

* Parses VCF files efficiently (streaming, large-file optimized)
* Maps variants → enzyme phenotypes

---

### ⚠️ Risk Engine (Clinical Logic)

* Deterministic CPIC-based drug risk evaluation
* Handles:

  * Poor / Intermediate / Normal / Ultra-Rapid metabolizers
  * Insufficient data scenarios

---

### 🤖 AI Clinical Explanation

* Generates human-readable medical insights
* Fallback-safe (Gemini optional, rule-based backup)

---

### ⚡ Performance & Reliability

* Zero-failure architecture (no 500 errors)
* Smart caching system (avoids recomputation)
* Early exit optimization for fast processing
* Timeout-safe AI handling

---

### 🔐 Authentication & User System

* Google OAuth-based authentication
* User-specific data storage (secure and isolated)

---

### 📂 File Management

* Persistent VCF storage
* File history retrieval per user
* Reuse previous genomic data for analysis

---

### 🧪 BioNeMo Integration (Simulation Layer)

* Simulates drug interaction for unknown drugs
* Fallback to AI explanation if unavailable

---

## 🔌 API Endpoints

| Endpoint              | Method | Description                         |
| --------------------- | ------ | ----------------------------------- |
| `/auth/login`         | GET    | Google OAuth login                  |
| `/auth/callback`      | GET    | OAuth callback handler              |
| `/files`              | GET    | Fetch user’s VCF history            |
| `/check-prescription` | POST   | Analyze drug risk (file or file_id) |

---

## 🧪 Example Response

```json
{
  "action": "Avoid",
  "risk_level": "High",
  "clinical_note": "CYP2D6 Poor Metabolizer detected. Codeine may be ineffective and unsafe.",
  "confidence": 0.95
}
```

---

## 🛠️ Tech Stack

* **Backend:** FastAPI (Python)
* **Database:** SQLite
* **Authentication:** Google OAuth (Authlib)
* **AI Integration:** Gemini (optional fallback)
* **Simulation:** NVIDIA BioNeMo (optional)
* **Frontend:** React / Flutter (in progress)

---

## ⚡ Getting Started

### 1️⃣ Clone Repository

```bash
git clone https://github.com/HackIndiaXYZ/hackindia-spark-7-north-region-code-sharks.git
cd backend
```

---

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Setup Environment Variables

Create `.env`:

```env
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
BIONEMO_API_KEY=your_key
```

---

### 4️⃣ Run Server

```bash
uvicorn main:app --reload --port 8000
```

---

### 5️⃣ Access API Docs

```
http://127.0.0.1:8000/docs
```

---

## 📱 Mobile Integration

The system can be accessed via:

* Flutter mobile app (USB-connected testing supported)
* React frontend dashboard (for visualization)

---

## 🔐 Security

* User-specific data isolation
* Secure OAuth authentication
* No exposure of sensitive genomic data

---

## 🚀 Future Scope

* 📊 Advanced visualization (risk charts, dashboards)
* 📄 Clinical PDF report generation
* 📱 Full-feature mobile app
* 🧠 Enhanced AI-driven decision support
* 🧬 Multi-drug interaction analysis

---

## 🏆 Why This Project Matters

Genetic Guardrail enables:

* Safer prescriptions
* Personalized medicine
* Reduced adverse drug reactions
* Data-driven clinical decisions

---

## 👨‍💻 Team

**Code Sharks** 🦈
HackIndia Spark 7 – North Region

---

## 📌 Final Note

This project demonstrates a **scalable, reliable, and clinically relevant system** that brings us closer to the future of **precision medicine**.

---




