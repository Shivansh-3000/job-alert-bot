import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import json
import os
import re

# ================= CONFIG ================= #

EMAIL = "gairolashivansh@gmail.com"
APP_PASSWORD = "fzexahbrwolmyfja"

TELEGRAM_TOKEN = "8512201575:AAGg4d8P5IqQ7w3me7gkNVD9DVZOHGEPY8s"
CHAT_ID = "1099624376"

KEYWORDS = [
    ".net", "c#", "asp.net",
    ".net core", "dot net",
    "edi", "electronic data interchange"
]

SEEN_FILE = "seen_jobs.json"

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
        r"2\s*years"
    ]

    return any(re.search(p, text) for p in patterns)

# ================= ALERTS ================= #

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

# ================= VISA ================= #

def scrape_visa():
    jobs = []
    url = "https://jobs.visa.com/jobs"

    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    for job in soup.select("a.job-title"):
        title = job.text.strip()
        link = "https://jobs.visa.com" + job["href"]

        if keyword_match(title):
            jobs.append({"company": "Visa", "title": title, "link": link})

    return jobs

# ================= AMAZON ================= #

def scrape_amazon():
    jobs = []
    url = "https://www.amazon.jobs/en/search?keywords=.net"

    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    for job in soup.select(".job-title"):
        title = job.text.strip()
        parent = job.find_parent("a")

        if parent and keyword_match(title):
            link = "https://www.amazon.jobs" + parent["href"]
            jobs.append({"company": "Amazon", "title": title, "link": link})

    return jobs

# ================= FLIPKART ================= #

def scrape_flipkart():
    jobs = []
    url = "https://www.flipkartcareers.com/#!/joblist"

    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    for job in soup.select("a"):
        title = job.text.strip()
        link = job.get("href")

        if title and keyword_match(title):
            jobs.append({"company": "Flipkart", "title": title, "link": link})

    return jobs

# ================= MASTERCARD ================= #

def scrape_mastercard():
    jobs = []
    url = "https://careers.mastercard.com/us/en/search-results"

    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    for job in soup.select("a"):
        title = job.text.strip()
        link = job.get("href")

        if title and keyword_match(title):
            jobs.append({
                "company": "Mastercard",
                "title": title,
                "link": link
            })

    return jobs

# ================= PAYPAL ================= #

def scrape_paypal():
    jobs = []
    url = "https://careers.paypal.com/us/en/search-results"

    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    for job in soup.select("a"):
        title = job.text.strip()
        link = job.get("href")

        if title and keyword_match(title):
            jobs.append({
                "company": "PayPal",
                "title": title,
                "link": link
            })

    return jobs

# ================= RAZORPAY ================= #

def scrape_razorpay():
    jobs = []
    url = "https://razorpay.com/jobs/"

    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    for job in soup.select("a"):
        title = job.text.strip()
        link = job.get("href")

        if title and keyword_match(title):
            jobs.append({
                "company": "Razorpay",
                "title": title,
                "link": link
            })

    return jobs

# ================= WALMART ================= #

def scrape_walmart():
    jobs = []
    url = "https://careers.walmart.com/results"

    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    for job in soup.select("a"):
        title = job.text.strip()
        link = job.get("href")

        if title and keyword_match(title):
            jobs.append({
                "company": "Walmart",
                "title": title,
                "link": link
            })

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

    return jobs

# ================= COMBINE ================= #

def scrape_all():
    jobs = []

    scrapers = [
        scrape_visa,
        scrape_amazon,
        scrape_flipkart,
        scrape_mastercard,
        scrape_paypal,
        scrape_razorpay,
        scrape_walmart,
        scrape_indeed
    ]

    for scraper in scrapers:
        try:
            jobs += scraper()
        except:
            pass

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

            send_email("New Product Company Job 🚀", message)
            send_telegram(message)

            seen.append(job["link"])

    save_seen(seen)

# ================= RUN ================= #

if __name__ == "__main__":
    main()
