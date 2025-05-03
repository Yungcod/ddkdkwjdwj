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


def scrape_expats():
    url = "https://www.expats.cz/praguerealestate/apartments/for-rent/prague-region"
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.content, "html.parser")
    results = []
    for a in soup.select("div.listing-title a"):
        try:
            title = a.get_text(strip=True)
            href  = a["href"]
            full  = "https://www.expats.cz" + href
            results.append({"Source": "Expats", "Title": title, "Link": full})
        except:
            continue
    return results


def scrape_bazos(keyword: str = "", pages: int = 1):
    """
    Скрейпит Bazos.cz по параметрам:
      keyword — фильтр по заголовку (частичное совпадение)
      pages   — количество страниц для обхода
    """
    results = []
    base_url = "https://reality.bazos.cz/prodam/byt/?hledat=praha&page={}"

    for page in range(1, pages + 1):
        url = base_url.format(page)
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.content, "html.parser")
        ads = soup.select(".inzeratynadpis")

        for ad in ads:
            try:
                title = ad.get_text(strip=True)
                if keyword and keyword.lower() not in title.lower():
                    continue
                link = "https://reality.bazos.cz" + ad.find("a")["href"]
                results.append({
                    "Source": "Bazos",
                    "Title": title,
                    "Link": link
                })
            except Exception:
                continue

    print(f"Bazos: найдено {len(results)} объявлений (pages={pages}, keyword='{keyword}')")
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
