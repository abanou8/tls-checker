import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests

# إعدادات تيليجرام
TELEGRAM_BOT_TOKEN = '8010680995:AAHN5OFDSpPkiNgWHTJUgP1Uu6-iYWMbrRY'
TELEGRAM_CHAT_ID = '6548192281'

# إعداد Chrome بدون واجهة رسومية
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

# رابط صفحة التوثيق
URL = "https://legalization-de.tlscontact.com/appointment/eg/egCAI2de/212570"

# التاريخ المطلوب: قبل 15 أكتوبر 2025
LAST_ACCEPTABLE_DATE = datetime(2025, 10, 15)

def send_telegram(message):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        data={"chat_id": TELEGRAM_CHAT_ID, "text": message}
    )

def parse_date(text):
    formats = [
        "%d/%m/%Y",
        "%d/%m",
        "%d %B %Y",
        "%d %B",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %b %Y",
        "%d %b",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(text, fmt)
            if dt.year == 1900:
                dt = dt.replace(year=2025)
            return dt
        except:
            continue
    return None

def check_appointment():
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(URL)
        time.sleep(7)

        date_elements = driver.find_elements(By.CSS_SELECTOR, "button, div, span")

        found_early_date = False
        earliest_date = None

        for el in date_elements:
            text = el.text.strip()
            if not text:
                continue
            dt = parse_date(text)
            if dt:
                if not earliest_date or dt < earliest_date:
                    earliest_date = dt
                if dt < LAST_ACCEPTABLE_DATE:
                    message = (f"📢 تم العثور على موعد مبكر للتوثيق!\n"
                               f"📅 التاريخ: {dt.strftime('%d/%m/%Y')}\n"
                               f"📍 الفرع: TLScontact")
                    send_telegram(message)
                    found_early_date = True
                    break

        driver.quit()

        if not found_early_date:
            last_checked = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            if earliest_date:
                message = (f"✅ تم الفحص في {last_checked}، ولكن لم يتم العثور على موعد مبكر.\n"
                           f"🗓 أقرب موعد متاح هو {earliest_date.strftime('%d/%m/%Y')}.")
            else:
                message = (f"✅ تم الفحص في {last_checked}، ولم يتم العثور على أي مواعيد متاحة حتى الآن.")
            send_telegram(message)

    except Exception as e:
        send_telegram(f"⚠️ حصل خطأ أثناء الفحص:\n{e}")

if __name__ == "__main__":
    while True:
        check_appointment()
        time.sleep(300)  # 5 دقائق
