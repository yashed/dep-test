import concurrent.futures
import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import utils.llm_caller as llm_caller
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


TAGS = ["p", "h1", "h2", "li"]


def parallel_scrape_caller(search_results, query, num_result):
    """
    Perform web scraping in parallel for the given search query's results with a timeout mechanism.

    Args:
        search_results_dict (dict): A dictionary containing search queries as keys and lists of search results as values.
        query (str): The search query.

    Returns:
        list: A list of dictionaries containing scraped data.
    """
    # search_results = search_results_dict.get(query, [])

    scraped_data = []
    max_workers = num_result
    timeout = 60

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as scraper:
        task_to_result = {
            scraper.submit(web_scraping_handle, result, query): result
            for result in search_results
        }

        # Wait for all tasks to complete or timeout
        done, not_done = concurrent.futures.wait(
            task_to_result.keys(),
            timeout=timeout,
            return_when=concurrent.futures.ALL_COMPLETED,
        )

        for task in done:
            try:
                scraped_item = task.result()
                if scraped_item:
                    scraped_data.append(scraped_item)
            except Exception as e:
                logger.error(
                    f"Error scraping {task_to_result[task]['link']}: {str(e)}",
                    exc_info=True,
                )

        # Cancel tasks that exceeded the timeout
        for task in not_done:
            task.cancel()
            logger.warning(
                f"Scraping task for {task_to_result[task]['link']} timed out."
            )

    return scraped_data


def web_scraping_handle(result, query):
    """
    Scrape content and summarize large content
    """
    url = result.get("link")
    if not url:
        return None

    raw_content = fetch_with_requests(url)

    # Handle large Content
    if len(raw_content) > 500000:
        content = ""
    elif len(raw_content) > 4000:
        content = llm_caller.summarize_large_content(raw_content, query, url)
    else:
        content = raw_content

    return {
        "title": result.get("title"),
        "link": url,
        "snippet": result.get("snippet"),
        "content": content,
    }


def fetch_with_requests(url):
    """
    Fetch content using requests and BeautifulSoup.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if "text/html" not in response.headers.get("Content-Type", ""):
            return ""

        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "html.parser")

        # Check if the page is JavaScript-rendered
        text_elements = len(soup.find_all(TAGS))
        script_elements = len(soup.find_all("script"))

        # if text_elements < 4 and script_elements > 5:
        #     return fetch_with_selenium(url)

        elements = soup.find_all(TAGS)
        content = "\n".join(
            [tag.get_text(strip=True) for tag in elements if tag.get_text(strip=True)]
        )

        return content if content else "none"
    except Exception as e:
        return " "


def fetch_with_selenium(url):
    """
    Fetch webpage content using Selenium for dynamic pages.
    """

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        elements = soup.find_all(TAGS)
        content = "\n".join(
            [tag.get_text(strip=True) for tag in elements if tag.get_text(strip=True)]
        )

        return content if content else "none"
    except Exception as e:
        return ""
    finally:
        driver.quit()
