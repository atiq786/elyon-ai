# 🚀 Elyon AI — Playwright Failure Analyzer

AI-powered debugging for Playwright tests using LLM + Vision.

---

## ✨ What it does

Elyon automatically analyzes failed Playwright tests and gives:

- 🔍 Root cause analysis
- 🧠 AI reasoning (based on logs + screenshots)
- ⚡ Quick Fix suggestions (copy-paste ready)
- 📍 Exact failure location (file + line number)
- 🖼️ Screenshot-aware debugging (Vision-enabled)

---

## 🧠 Example Output

Failure Type: Selector mismatch  Issue: Test tried to click "Sign In" but UI shows "Login"  Suggested Fix: await page.click('button:has-text("Login")');

---

## 🏗️ Architecture

Playwright Test Runner         ↓ Elyon Reporter (Node.js)         ↓ FastAPI Backend (Python)         ↓ LLM (OpenAI / Claude)

---

## ⚙️ Setup

### 1. Clone repo
git clone https://github.com/atiq786/elyon-ai.git cd elyon-ai

### 2. Backend
cd backend pip install -r requirements.txt uvicorn main:app --reload

### 3. Run Playwright tests
cd ../playwright-tests npm install npx playwright test

---

## 🧪 Features

- ✅ AI-powered root cause detection
- ✅ Screenshot + log analysis
- ✅ Multi-LLM support (OpenAI + Claude)
- ✅ Quick Fix suggestions
- 🚧 Self-healing (coming soon)

---

## 🚀 Vision

Elyon aims to become the "Copilot for Test Failures" —  
reducing debugging time from minutes to seconds.

---

## 👨‍💻 Author

Atiq Rahman  
Built with ❤️ to eliminate flaky debugging fo
