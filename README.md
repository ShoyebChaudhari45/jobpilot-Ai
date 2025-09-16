# 🤖 JobPilot AI — HR Email Finder

JobPilot AI is a Flask-based tool that helps you **find HR/recruiter emails** of companies by searching the web (Google Serper API + DuckDuckGo), extracting emails from webpages, filtering HR-related contacts, and storing results in **Google Sheets** automatically.  

---

## ✨ Features
- 🔍 Search HR/recruiter emails by **company name** and optional **job role**
- 🌐 Uses **Google Serper API** + DuckDuckGo for queries
- 📩 Extracts emails from webpages using regex
- 🛡️ Filters emails with HR-related keywords (HR, career, recruiter, hiring, etc.)
- 📝 Saves results (company, role, email, source, timestamp) to **Google Sheets**
- 📊 Progress tracking via Flask endpoints
- 🗂️ Excludes bad domains/pages (scam, spam, fraud, etc.)
- ⚡ Runs locally or can be deployed to cloud

---

## 🛠️ Tech Stack
- **Python 3.9+**
- [Flask](https://flask.palletsprojects.com/) (Web Framework)
- [Requests](https://requests.readthedocs.io/) (API + Web scraping)
- [gspread](https://github.com/burnash/gspread) (Google Sheets API)
- [oauth2client](https://github.com/google/oauth2client) (Service account auth)
- **Regex** for email extraction

---

<img width="333" height="171" alt="image" src="https://github.com/user-attachments/assets/1be2a2dc-a4be-4602-afa1-162f106c1ef6" />



---

## ⚡ Setup & Installation

### 1️⃣ Clone the repo
```bash
git clone https://github.com/ShoyebChaudhari45/jobpilot-Ai.git
cd jobpilot-Ai/job

2️⃣ Create virtual environment
python -m venv venv
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate        # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Add credentials

Place your Google Service Account JSON as credentials.json (kept out of git).

Share your Google Sheet with your service account email.

Update the SHEET_URL in hr_email_finder.py.

5️⃣ Add .env file

Create .env in project root:

SERPER_API_KEY=your_serper_api_key
FLASK_ENV=development

6️⃣ Run the app
python hr_email_finder.py


Access it at http://127.0.0.1:5000/
.

🚀 Deployment

For production (Heroku/Render/etc.):

Add gunicorn to requirements.txt

Create a Procfile:

web: gunicorn hr_email_finder:app


Use environment variables instead of committing secrets.

📜 License

MIT License — free to use, modify, and distribute.

👨‍💻 Author

Developed by Shoyeb Chaudhari
 ✨
