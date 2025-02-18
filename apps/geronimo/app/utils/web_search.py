import concurrent.futures
import os
import requests
import logging
from dotenv import load_dotenv
from utils.web_scrape import web_scraping_handle
from langchain_google_community import GoogleSearchAPIWrapper


# Load environment variables
load_dotenv(override=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Fetching the variables from the .env file
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


if not all(
    [
        GOOGLE_CSE_ID,
        GOOGLE_API_KEY,
    ]
):
    raise ValueError("Please ensure all the necessary environment variables are set.")


def google_search(query, num_results=5):
    """
    Perform Google searches for a given query using the Google Search API with retry mechanism.

    Args:
        query (str): The search query.
        num_results (int): Number of results to retrieve.

    Returns:
        dict: A dictionary containing search results.
    """
    google_search_wrapper = GoogleSearchAPIWrapper()

    try:
        search_results = google_search_wrapper.results(query, num_results=num_results)
        if not search_results:
            raise Exception(f"No search results found")
        return search_results

    except Exception as e:
        raise
