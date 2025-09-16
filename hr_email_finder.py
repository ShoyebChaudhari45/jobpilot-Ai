import requests
import re
import threading
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request, jsonify

# ================================
# CONFIGURATION
# ================================
SERPER_API_KEY = "d66eb145fa3055989ae126738a78073439c157ec"
GOOGLE_SEARCH_ENDPOINT = "https://google.serper.dev/search"

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
HR_KEYWORDS = ["hr", "career", "recruit", "jobs", "talent", "hiring", "peopleops"]
BAD_KEYWORDS = ["scam", "fraud", "complaint", "warning", "fake", "spam"]

STRICT_COMPANY_DOMAIN = False

# ================================
# GOOGLE SHEETS SETUP
# ================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1zbnVYC1UXYOXAXYpVpcwLbdyajZFgL7anjOWMQGNQHA/edit#gid=0"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_url(SHEET_URL).sheet1  # First sheet of the document

# ================================
# FLASK APP
# ================================
app = Flask(__name__)
search_progress = {"status": "idle", "progress": 0, "results": []}

# ================================
# SEARCH FUNCTIONS
# ================================
def google_search(query):
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "num": 20}
    try:
        resp = requests.post(GOOGLE_SEARCH_ENDPOINT, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json().get("organic", [])
    except:
        return []

def duckduckgo_search(query):
    try:
        resp = requests.get("https://api.duckduckgo.com/", params={"q": query, "format": "json"}, timeout=5)
        data = resp.json()
        results = []
        if "RelatedTopics" in data:
            for r in data["RelatedTopics"]:
                if "FirstURL" in r:
                    results.append({"link": r["FirstURL"]})
        return results
    except:
        return []

def extract_emails_from_page(url):
    try:
        page = requests.get(url, timeout=5)
        page.raise_for_status()
        page_text = page.text.lower()
        if any(bad in page_text for bad in BAD_KEYWORDS):
            return []
        emails = EMAIL_REGEX.findall(page.text)
        return list(set(emails))
    except:
        return []

def filter_hr_emails(emails, company):
    filtered = []
    for e in emails:
        e_lower = e.lower()
        if STRICT_COMPANY_DOMAIN and not e_lower.endswith(f"@{company.lower()}.com"):
            continue
        if any(k in e_lower for k in HR_KEYWORDS) or company.lower() in e_lower:
            filtered.append(e)
    return filtered

def append_to_sheet(company, job_role, email, source_url):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    platform = source_url.split("/")[2] if "://" in source_url else source_url
    sheet.append_row([company, job_role if job_role else "-", email, now, platform])

# ================================
# MAIN SEARCH FUNCTION
# ================================
def find_hr_emails(company, job_role):
    results = []
    queries = [
        f'"HR contact" "{company}" "@{company.lower()}.com"',
        f'"send your CV" "{company}" "@{company.lower()}.com"',
        f'"apply at" "{company}" "email"',
        f'"careers" "{company}" "contact" "@{company.lower()}.com"',
        f'"HR" "{company}" "{job_role}" "@{company.lower()}.com"' if job_role else f'"HR" "{company}" "@{company.lower()}.com"',
        f'site:twitter.com "{company}" "send your CV"',
        f'site:linkedin.com "{company}" "apply"',
        f'site:indeed.com "{company}" "apply"',
        f'site:glassdoor.com "{company}" "contact email"',
        f'site:naukri.com "{company}" "email"',
        f'site:foundit.in "{company}" "email"',
        f'site:angel.co "{company}" "hiring"',
        f'site:wellfound.com "{company}" "recruiter email"',
        f'site:github.com "{company}" "jobs"',
        f'site:crunchbase.com "{company}" "contact"'
    ]

    total_queries = len(queries)
    for idx, query in enumerate(queries, start=1):
        search_progress["progress"] = int((idx / total_queries) * 100)
        search_results = google_search(query)
        search_results += duckduckgo_search(query)

        for r in search_results:
            url = r.get("link")
            if not url:
                continue
            emails = extract_emails_from_page(url)
            hr_emails = filter_hr_emails(emails, company)
            for email in hr_emails:
                results.append((email, url, job_role))
                append_to_sheet(company, job_role, email, url)

    # Deduplicate by email
    unique_emails = {}
    for email, url, jr in results:
        if email not in unique_emails:
            unique_emails[email] = (url, jr)

    search_progress["status"] = "done"
    return [(email, unique_emails[email][0], unique_emails[email][1]) for email in unique_emails]

# ================================
# FLASK ROUTES
# ================================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start_search", methods=["POST"])
def start_search():
    data = request.get_json()
    company = data.get("company", "").strip()
    job_role = data.get("job_role", "").strip()

    if not company:
        return jsonify({"error": "Company name is required"}), 400

    search_progress["status"] = "searching"
    search_progress["progress"] = 0
    search_progress["results"] = []

    def run_search():
        results = find_hr_emails(company, job_role)
        search_progress["results"] = results

    threading.Thread(target=run_search).start()
    return jsonify({"status": "started"})

@app.route("/progress")
def get_progress():
    return jsonify(search_progress)

# ================================
# RUN APP
# ================================
if __name__ == "__main__":
    app.run(debug=True)
