import concurrent.futures
import requests
from bs4 import BeautifulSoup
import utils.llm_caller as llm_caller
import utils.constants as constants
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def parallel_scrape_caller(search_results, query, num_result):
    """
    Perform web scraping in parallel for the given search query's results with a timeout mechanism.

    Args:
        search_results_dict (dict): A dictionary containing search queries as keys and lists of search results as values.
        query (str): The search query.

    Returns:
        list: A list of dictionaries containing scraped data.
    """

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
                constants.LOGGER.error(
                    f"Error scraping {task_to_result[task]['link']}: {str(e)}",
                    exc_info=True,
                )

        # Cancel tasks that exceeded the timeout
        for task in not_done:
            task.cancel()
            constants.LOGGER.warning(
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

    try:
        # Set up a session with retries
        session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504]
        )
        session.mount("http://", HTTPAdapter(max_retries=retries))
        session.mount("https://", HTTPAdapter(max_retries=retries))

        response = requests.get(url, headers=constants.HEADERS, timeout=10)
        if (
            response.headers.get("Content-Type", "").split(";")[0]
            not in constants.VALID_CONTENT_TYPES
        ):
            return ""

        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "html.parser")

        elements = soup.find_all(constants.TAGS)
        content = "\n".join(
            [tag.get_text(strip=True) for tag in elements if tag.get_text(strip=True)]
        )

        return content if content else "none"
    except Exception as e:
        return " "
