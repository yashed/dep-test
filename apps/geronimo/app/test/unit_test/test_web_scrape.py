import pytest
from unittest import mock
from unittest.mock import MagicMock, patch
import requests
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import sys
import os
from bs4 import BeautifulSoup

# Add the app directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from utils.web_scrape import (
    parallel_scrape_caller,
    web_scraping_handle,
    fetch_with_requests,
)


# Common fixtures
@pytest.fixture
def mock_fetch_with_requests():
    with mock.patch("utils.web_scrape.fetch_with_requests") as mock_fetch:
        yield mock_fetch


@pytest.fixture
def mock_llm_caller():
    with mock.patch("utils.llm_caller.summarize_large_content") as mock_llm:
        yield mock_llm


@pytest.fixture
def mock_thread_pool_executor():
    with mock.patch("concurrent.futures.ThreadPoolExecutor") as mock_executor:
        yield mock_executor


@pytest.fixture
def mock_web_scraping_handle():
    with mock.patch("utils.web_scrape.web_scraping_handle") as mock_web_scraping:
        yield mock_web_scraping


@pytest.fixture
def search_results_fixture():
    """Fixture for common search results data"""
    return [
        {
            "link": "https://example.com/page1",
            "title": "Example 1",
            "snippet": "Snippet 1",
        },
        {
            "link": "https://example.com/page2",
            "title": "Example 2",
            "snippet": "Snippet 2",
        },
    ]


# Test data for fetch_with_requests parametrized tests
FETCH_WITH_REQUESTS_TEST_CASES = [
    # Test Case 01: Valid text/html content (HTML Page)
    (
        200,
        {"Content-Type": "text/html; charset=UTF-8"},
        "<html><body><h1>Title</h1><p>Paragraph</p><li>Item 1</li></body></html>",
        "Title\nParagraph\nItem 1",
        None,
    ),
    # Test Case 02: Valid application/xhtml+xml content (XHTML Page)
    (
        200,
        {"Content-Type": "application/xhtml+xml"},
        "<html xmlns='http://www.w3.org/1999/xhtml'><body><h1>Header</h1><p>Content</p></body></html>",
        "Header\nContent",
        None,
    ),
    # Test Case 03: Valid text/xml content (XML Page)
    (
        200,
        {"Content-Type": "text/xml"},
        "<root><title>XML Title</title><description>XML Description</description></root>",
        "XML Title\nXML Description",
        None,
    ),
    # Test Case 04: Valid application/xml content (XML Document)
    (
        200,
        {"Content-Type": "application/xml"},
        "<note><to>User</to><message>Hello</message></note>",
        "User\nHello",
        None,
    ),
    # Test Case 05: Invalid content type (application/json)
    (
        200,
        {"Content-Type": "application/json"},
        '{"message": "This is JSON"}',
        "",
        None,
    ),
    # Test Case 06: Invalid content type (text/plain)
    (
        200,
        {"Content-Type": "text/plain"},
        "This is plain text",
        "",
        None,
    ),
    # Test Case 07: Valid content type but no relevant tags
    (
        200,
        {"Content-Type": "text/html"},
        "<html><body><script>console.log('JS')</script></body></html>",
        "none",
        None,
    ),
    # Test Case 08: Empty body, no content
    (
        200,
        {"Content-Type": "text/html"},
        "<html><body></body></html>",
        "none",
        None,
    ),
    # Test Case 09: Large HTML page (Performance Check)
    (
        200,
        {"Content-Type": "text/html"},
        "<html><body>"
        + "".join(f"<p>Item {i}</p>" for i in range(100))
        + "</body></html>",
        "\n".join(f"Item {i}" for i in range(100)),
        None,
    ),
    # Test Case 10: Server error response (500)
    (
        500,
        {"Content-Type": "text/html"},
        "",
        " ",
        requests.exceptions.RequestException,
    ),
    # Test Case 11: Timeout error simulation
    (None, None, None, " ", requests.exceptions.Timeout),
    # Test Case 12: Network error simulation
    (None, None, None, " ", requests.exceptions.ConnectionError),
]


class TestParallelScraping:
    """Tests for parallel scraping functionality"""

    def test_parallel_scrape_caller_success(
        self,
        mock_fetch_with_requests,
        mock_llm_caller,
        mock_thread_pool_executor,
        mock_web_scraping_handle,
    ):
        """Test successful parallel scraping"""
        # Test data setup
        search_results = [
            {
                "link": "https://example.com/page1",
                "title": "Example 1",
                "snippet": "Snippet 1",
            },
            {
                "link": "https://example.com/page2",
                "title": "Example 2",
                "snippet": "Snippet 2",
            },
        ]
        query = "test query"
        num_result = 2

        # Create mock futures
        mock_future1 = MagicMock()
        mock_future2 = MagicMock()
        mock_future1.result.return_value = {
            "title": "Example 1",
            "link": "https://example.com/page1",
            "snippet": "Snippet 1",
            "content": "Some content",
        }
        mock_future2.result.return_value = {
            "title": "Example 2",
            "link": "https://example.com/page2",
            "snippet": "Snippet 2",
            "content": "Some content",
        }

        # Mock ThreadPoolExecutor
        mock_executor = MagicMock()
        mock_thread_pool_executor.return_value.__enter__.return_value = mock_executor
        mock_executor.submit.side_effect = [mock_future1, mock_future2]

        with mock.patch("concurrent.futures.wait") as mock_wait:
            mock_wait.return_value = ([mock_future1, mock_future2], set())
            result = parallel_scrape_caller(search_results, query, num_result)

            assert len(result) == 2
            assert result[0]["title"] == "Example 1"
            assert result[0]["content"] == "Some content"
            assert result[1]["title"] == "Example 2"
            assert result[1]["content"] == "Some content"

    def test_parallel_scrape_caller_empty_results(
        self, mock_thread_pool_executor, search_results_fixture
    ):
        """Test handling of empty search results"""
        result = parallel_scrape_caller([], "test query", 2)
        assert len(result) == 0

    def test_parallel_scrape_caller_none_values(
        self, mock_thread_pool_executor, mock_web_scraping_handle
    ):
        """Test handling of None values in search results"""
        search_results = [
            {"link": None, "title": None, "snippet": None},
            {"link": "https://example.com", "title": "Test", "snippet": None},
        ]
        mock_future = MagicMock()
        mock_future.result.return_value = {
            "title": "Test",
            "link": "https://example.com",
            "snippet": None,
            "content": "Some content",
        }

        mock_executor = MagicMock()
        mock_thread_pool_executor.return_value.__enter__.return_value = mock_executor
        mock_executor.submit.return_value = mock_future

        with mock.patch("concurrent.futures.wait") as mock_wait:
            mock_wait.return_value = ([mock_future], set())
            result = parallel_scrape_caller(search_results, "test query", 2)
            assert len(result) == 1
            assert result[0]["snippet"] is None

    def test_parallel_scrape_caller_connection_error(
        self, mock_thread_pool_executor, search_results_fixture
    ):
        """Test handling of connection errors"""
        mock_future = MagicMock()
        mock_future.result.side_effect = ConnectionError("Failed to connect")

        mock_executor = MagicMock()
        mock_thread_pool_executor.return_value.__enter__.return_value = mock_executor
        mock_executor.submit.return_value = mock_future

        with mock.patch("concurrent.futures.wait") as mock_wait:
            mock_wait.return_value = ([mock_future], set())
            result = parallel_scrape_caller(search_results_fixture, "test query", 2)
            assert len(result) == 0

    def test_parallel_scrape_caller_timeout(
        self, mock_fetch_with_requests, mock_llm_caller, mock_thread_pool_executor
    ):
        """Test handling of timeout errors"""
        search_results = [
            {
                "link": "https://example.com/page1",
                "title": "Example 1",
                "snippet": "Snippet 1",
            },
            {
                "link": "https://example.com/page2",
                "title": "Example 2",
                "snippet": "Snippet 2",
            },
        ]

        mock_future = MagicMock()
        mock_future.result.side_effect = requests.exceptions.Timeout()

        mock_executor = MagicMock()
        mock_thread_pool_executor.return_value.__enter__.return_value = mock_executor
        mock_executor.submit.return_value = mock_future

        with mock.patch("concurrent.futures.wait") as mock_wait:
            mock_wait.return_value = (set(), {mock_future})
            result = parallel_scrape_caller(search_results, "test query", 2)
            assert len(result) == 0
            assert mock_executor.submit.called


class TestWebScraping:
    """Tests for web scraping functionality"""

    def test_web_scraping_handle(self, mock_llm_caller, mock_fetch_with_requests):
        """Test web scraping handle function"""
        mock_fetch_with_requests.return_value = "Some content"
        result = {
            "link": "https://example.com/page1",
            "title": "Example 1",
            "snippet": "Snippet 1",
        }
        output = web_scraping_handle(result, "test query")

        assert output["content"] == "Some content"
        assert output["title"] == "Example 1"
        assert output["link"] == "https://example.com/page1"
        assert output["snippet"] == "Snippet 1"

    def test_fetch_with_requests_invalid_url(self):
        """Test handling of invalid URLs"""
        with mock.patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException
            result = fetch_with_requests("https://invalid-url.com")
            assert result == " "

    @pytest.mark.parametrize(
        "mock_status, mock_headers, mock_text, expected_output, exception_scenario",
        FETCH_WITH_REQUESTS_TEST_CASES,
    )
    def test_fetch_with_requests(
        self,
        mock_status,
        mock_headers,
        mock_text,
        expected_output,
        exception_scenario,
    ):
        """Test fetch_with_requests function with different content types and scenarios"""
        with patch("requests.get") as mock_get:
            if exception_scenario:
                mock_get.side_effect = exception_scenario
            else:
                mock_response = MagicMock()
                mock_response.status_code = mock_status
                mock_response.headers = mock_headers
                mock_response.text = mock_text
                mock_response.raise_for_status = MagicMock()
                mock_get.return_value = mock_response

            result = fetch_with_requests("https://example.com")
            assert result == expected_output
