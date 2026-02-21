import requests
import smtplib
import os
import json
import re
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

# ================= CONFIG (FROM GITHUB SECRETS) ================= #

EMAIL = os.environ.get("EMAIL")
APP_PASSWORD = os.environ.get("APP_PASSWORD")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

SEEN_FILE = "seen_jobs.json"

KEYWORDS = [
    ".net", "c#", "asp.net",
    ".net core", "dot net",
    "edi", "electronic data interchange"
]

HEADERS = {"User-Agent": "Mozilla/5.0"}

# ================= UTIL ================= #

def keyword_match(text):
    text = text.lower()
    return any(k in text for k in KEYWORDS)

def experience_match(text):
    text = text.lower()

    patterns = [
        r"1\s*-\s*2\s*years",
        r"1\s*to\s*2\s*years",
        r"1\s*year",
        r"2\s*years",
        r"0\s*-\s*2\s*years",
        r"1\s*-\s*3\s*years"
    ]

    return any(re.search(p, text) for p in patterns)

# ================= ALERTS ================= #

def send_email(subject, body):
    if not EMAIL or not APP_PASSWORD:
        print("Email credentials missing")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL, APP_PASSWORD)
    server.send_message(msg)
    server.quit()

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram credentials missing")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

# ================= STORAGE ================= #

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return json.load(f)
    return []

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f)

# ================= GREENHOUSE API ================= #

def scrape_greenhouse(company, board):
    jobs = []
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"

    try:
        res = requests.get(url)
        data = res.json()

        for job in data.get("jobs", []):
            title = job["title"]
            link = job["absolute_url"]

            if keyword_match(title):
                jobs.append({
                    "company": company,
                    "title": title,
                    "link": link
                })

    except Exception as e:
        print(f"{company} Greenhouse error:", e)

    return jobs

# ================= LEVER API ================= #

def scrape_lever(company, board):
    jobs = []
    url = f"https://api.lever.co/v0/postings/{board}"

    try:
        res = requests.get(url)
        data = res.json()

        for job in data:
            title = job["text"]
            link = job["hostedUrl"]

            if keyword_match(title):
                jobs.append({
                    "company": company,
                    "title": title,
                    "link": link
                })

    except Exception as e:
        print(f"{company} Lever error:", e)

    return jobs

# ================= INDEED BACKUP ================= #

def scrape_indeed():
    jobs = []

    URLS = [
        "https://in.indeed.com/jobs?q=.net+developer",
        "https://in.indeed.com/jobs?q=c%23+developer",
        "https://in.indeed.com/jobs?q=edi+developer"
    ]

    for url in URLS:
        try:
            res = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(res.text, "html.parser")

            for job in soup.select(".job_seen_beacon"):
                title = job.select_one("h2").text.strip()
                desc = job.text.lower()
                link = "https://in.indeed.com" + job.select_one("a")["href"]

                if keyword_match(title + desc) and experience_match(desc):
                    jobs.append({
                        "company": "Indeed",
                        "title": title,
                        "link": link
                    })

        except Exception as e:
            print("Indeed error:", e)

    return jobs

# ================= MAIN SCRAPER ================= #

def scrape_all():
    jobs = []

    # Greenhouse companies
    jobs += scrape_greenhouse("Atlassian", "atlassian")
    jobs += scrape_greenhouse("Freshworks", "freshworks")

    # Lever companies
    jobs += scrape_lever("Razorpay", "razorpay")
    jobs += scrape_lever("Meesho", "meesho")

    # Backup aggregator
    jobs += scrape_indeed()

    print("Total jobs found:", len(jobs))
    return jobs

# ================= MAIN ================= #

def main():
    seen = load_seen()
    jobs = scrape_all()

    for job in jobs:
        if job["link"] not in seen:

            message = f"""
New Job Opening 🚀

Company: {job['company']}
Role: {job['title']}
Link: {job['link']}
"""

            print("New job detected:", job["title"])

            send_email("New Product Company Job 🚀", message)
            send_telegram(message)

            seen.append(job["link"])

    save_seen(seen)

if __name__ == "__main__":
    main()
