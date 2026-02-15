import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import json
import os

# ================= CONFIG ================= #

EMAIL = "gairolashivansh@gmail.com"
APP_PASSWORD = "Arjoo_bhai3000"

TELEGRAM_TOKEN = "8512201575:AAGg4d8P5IqQ7w3me7gkNVD9DVZOHGEPY8s"
CHAT_ID = "1099624376"

KEYWORDS = [
    ".net", "c#", "asp.net",
    ".net core", "edi",
    "electronic data interchange"
]

URLS = [
    "https://in.indeed.com/jobs?q=.net+developer",
    "https://in.indeed.com/jobs?q=c%23+developer",
    "https://in.indeed.com/jobs?q=edi+developer",
]

SEEN_FILE = "seen_jobs.json"

# ================= EMAIL ================= #

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL, APP_PASSWORD)
    server.send_message(msg)
    server.quit()

# ================= TELEGRAM ================= #

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

# ================= STORAGE ================= #

def load_seen():
    if os.path.exists(SEEN_FILE):
        return json.load(open(SEEN_FILE))
    return []

def save_seen(seen):
    json.dump(seen, open(SEEN_FILE, "w"))

# ================= SCRAPER ================= #

def scrape():
    jobs = []

    for url in URLS:
        res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")

        for job in soup.select(".job_seen_beacon"):
            title = job.select_one("h2").text.lower()
            link = "https://in.indeed.com" + job.select_one("a")["href"]
            desc = job.text.lower()

            if any(k in title + desc for k in KEYWORDS):

                # Experience filter
                if "1 year" in desc or "2 year" in desc or "1-2" in desc:

                    jobs.append({
                        "title": title,
                        "link": link
                    })

    return jobs

# ================= MAIN ================= #

def main():
    send_email("Test Alert ", "GitHub workflow working")
    send_telegram("Test Alert  Workflow working")
    seen = load_seen()
    jobs = scrape()

    for job in jobs:
        if job["link"] not in seen:

            message = f"""
New Job Opening 🚀

Role: {job['title']}
Link: {job['link']}
"""

            send_email("New .NET / C# Job 🚀", message)
            send_telegram(message)

            seen.append(job["link"])

    save_seen(seen)

if __name__ == "__main__":
    main()

