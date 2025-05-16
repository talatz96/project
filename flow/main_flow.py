# flows/main_flow.py
from prefect import flow, task

from scrappers.scrapper_reddit import scrape_reddit
# from scrappers.scrapper_quora import scrape_quora
# from scrappers.scrapper_twitter import scrape_twitter

from transformations.transform import clean_reddit_titles_from_db
from transformations.label_reddit import main as label_data

@task
def reddit_scraping_flow():
    scrape_reddit()

# @task
# def quora_scraping_flow():
#     scrape_quora()

# @task
# def twitter_scraping_flow():
#     scrape_twitter()

@task
def quality_check_flow():
    clean_reddit_titles_from_db()

@task
def llm_labeling_flow():
    label_data()

@flow
def main_flow():
    reddit_scraping_flow()
    quality_check_flow()
    llm_labeling_flow()

if __name__ == "__main__":
    main_flow()
