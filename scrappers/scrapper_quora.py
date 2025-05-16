from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import random

keywords = ["bullying", "racism", "hate", "discrimination", "slur", "abuse", "prejudice"]

def setup_driver():
    options = Options()
    options.add_argument("--headless=new")  # Use new headless mode (more stable)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

def random_delay(min_sec=2, max_sec=5):
    time.sleep(random.uniform(min_sec, max_sec))

def scrape_quora(max_pages=2, max_answers_per_question=3):
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)
    results = []

    for keyword in keywords:
        print(f"\n🔍 Searching Quora for: {keyword}")
        search_url = f"https://www.quora.com/search?q={keyword}"
        driver.get(search_url)
        time.sleep(4)

        visited_links = set()

        for page in range(max_pages):
            print(f"📄 Scanning page {page + 1} for keyword '{keyword}'...")
            random_delay()

            question_links = []
            try:
                links = driver.find_elements(By.XPATH, "//a[contains(@href, '/What-') and not(contains(@href,'/profile/'))]")
                question_links = list(set([l.get_attribute("href") for l in links if l.get_attribute("href")]))
                print(f"🔗 Found {len(question_links)} links")
            except Exception as e:
                print(f"⚠️ Could not extract links: {e}")

            if not question_links:
                print("❌ No question links found.")
                continue

            for i, link in enumerate(question_links):
                if link in visited_links:
                    continue
                visited_links.add(link)

                try:
                    driver.get(link)
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
                    time.sleep(2)

                    question = driver.title.strip()

                    # Scroll down to ensure answers load
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3)

                    answers = driver.find_elements(By.CSS_SELECTOR, "div.q-text.qu-display--block")
                    if not answers:
                        print(f"❌ No answers found on: {link}")
                        continue

                    for j, ans in enumerate(answers[:max_answers_per_question]):
                        text = ans.text.strip().replace("\n", " ")[:700]
                        if text:
                            results.append([keyword, question, link, j + 1, text])
                            print(f"✅ Answer {j + 1} for: {question[:50]}...")

                except Exception as e:
                    print(f"⚠️ Error processing {link}: {e}")
                    continue

            # Scroll to bottom to load more results
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            random_delay(3, 5)

        print(f"🔎 Completed keyword: {keyword}")

    driver.quit()

    # Save to CSV
    with open("quora_selenium_results.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Keyword", "Question", "URL", "Answer #", "Top Answer (truncated)"])
        writer.writerows(results)

    print(f"\n✅ Done. {len(results)} answers saved to quora_selenium_results.csv.")

if __name__ == "__main__":
    scrape_quora(max_pages=2, max_answers_per_question=3)
