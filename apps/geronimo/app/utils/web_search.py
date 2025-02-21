from utils.web_scrape import web_scraping_handle
from langchain_google_community import GoogleSearchAPIWrapper


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
