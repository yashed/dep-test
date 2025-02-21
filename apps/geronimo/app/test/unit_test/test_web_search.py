import pytest
from unittest.mock import patch
import sys
import os

# Add the app directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from utils.web_search import google_search


@pytest.mark.parametrize(
    "query, num_results, mock_response",
    [
        (
            "Python testing",
            5,
            [{"title": "Python Testing Guide", "link": "https://example.com"}],
        ),
        ("Machine Learning", 3, [{"title": "ML Basics", "link": "https://ml.com"}]),
        ("", 5, []),
    ],
)
def test_google_search(query, num_results, mock_response):
    """Test google_search function with different scenarios."""

    with patch("utils.web_search.GoogleSearchAPIWrapper") as MockSearchAPI:
        mock_instance = MockSearchAPI.return_value
        mock_instance.results.return_value = mock_response

        if not mock_response:  # Expect an exception for no results
            with pytest.raises(Exception, match="No search results found"):
                google_search(query, num_results)
        else:
            results = google_search(query, num_results)
            assert isinstance(results, list)
            assert len(results) == len(mock_response)
            assert results == mock_response


def test_google_search_api_failure():
    """Test google_search when the API call fails."""
    with patch("utils.web_search.GoogleSearchAPIWrapper") as MockSearchAPI:
        mock_instance = MockSearchAPI.return_value
        mock_instance.results.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            google_search("Test Query", 5)
