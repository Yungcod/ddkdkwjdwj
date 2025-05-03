from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup
import csv
import time

HEADERS = {"User-Agent": "Mozilla/5.0"}

def init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=webdriver.ChromeService(ChromeDriverManager().install()), options=options)
    return driver

def scrape_realitymix(driver):
    url = "https://realitymix.cz/vyhledavani/praha/pronajem-bytu.html"
    driver.get(url)
    time.sleep(2)  # даём странице прогрузиться
    soup = BeautifulSoup(driver.page_source, "html.parser")

    results = []
    # ищем все ссылки на детали квартир
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # на RealityMix все объявления ведут на /byt/ или /detail/
        if href.startswith("/byt/") or href.startswith("/detail/"):
            title = a.get_text(strip=True)
            if title:
                full = "https://realitymix.cz" + href
                results.append({"Source": "RealityMix", "Title": title, "Link": full})
    return results

def scrape_expats(driver):
    url = "https://www.expats.cz/praguerealestate/apartments/for-rent/prague-region"
    driver.get(url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    results = []
    # на Expats все объявления ведут на /praguerealestate/
    for a in soup.find_all("a", href=True):
        if "/praguerealestate/" in a["href"]:
            title = a.get_text(strip=True)
            if title:
                full = "https://www.expats.cz" + a["href"]
                results.append({"Source": "Expats", "Title": title, "Link": full})
    return results

def scrape_bazos():
    url = "https://reality.bazos.cz/prodam/byt/?hledat=praha"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.content, "html.parser")

    results = []
    for ad in soup.select(".inzeratynadpis"):
        try:
            title = ad.get_text(strip=True)
            link = "https://reality.bazos.cz" + ad.find("a")["href"]
            results.append({"Source": "Bazos", "Title": title, "Link": link})
        except:
            continue
    return results

def save_to_csv(data, filename="output.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Source", "Title", "Link"])
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    driver = init_driver()
    all_data = []

    print("🔎 Scraping RealityMix...")
    all_data += scrape_realitymix(driver)

    print("🔎 Scraping Expats.cz...")
    all_data += scrape_expats(driver)

    driver.quit()

    print("🔎 Scraping Bazos.cz...")
    all_data += scrape_bazos()

    save_to_csv(all_data)
    print(f"✅ Done! Collected {len(all_data)} listings into output.csv")
