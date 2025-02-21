import pytest
from unittest.mock import patch
import json
import sys
import os

# Add the app directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from utils.report_generator import format_response
from utils.json_format import format_json_string

DUMMY_RESPONSES = [
    # Test Case 1: Normal response with structured data
    {
        "professional_summary": "John Doe is a software engineer with over 5 years of experience in web development...",
        "social_media_links": """```json
        [
            {"platform": "LinkedIn", "url": "https://www.linkedin.com/in/johndoe"},
            {"platform": "GitHub", "url": "https://github.com/johndoe"}
        ]
        ```""",
        "company_summary": "TechCorp is a leading technology company specializing in cloud computing...",
        "company_competitors": "Google, Microsoft, AWS",
        "company_news": """```json
        [
            {"title": "TechCorp launches AI-powered analytics platform", "url": "https://technews.com/techcorp-ai-launch", "description": "TechCorp has introduced an AI-driven analytics platform."}
        ]
        ```""",
    },
    # Test Case 2: Empty response
    {
        "professional_summary": "",
        "social_media_links": "```json\n[]\n```",
        "company_summary": "",
        "company_competitors": "",
        "company_news": "```json\n[]\n```",
    },
    # Test Case 3: Missing keys
    {
        "professional_summary": "Jane Smith is a data scientist specializing in AI and machine learning.",
        "social_media_links": "```json\n[]\n```",
    },
    # Test Case 4: Malformed JSON in social media links
    {
        "professional_summary": "jhon known is a cybersecurity expert with 10 years of experience.",
        "social_media_links": """```json
        [
            {"platform": "LinkedIn", "url": "https://www.linkedin.com/in/jhonknown"
        ]
        ```""",
    },
    # Test Case 5: Malformed JSON in company news
    {
        "professional_summary": "Sarah Lee is a software developer at FinTech Inc.",
        "company_news": """```json
        [
            {"title": "FinTech Inc raises $50M in Series B funding", "url": "https://news.fintech.com/series-b"
        ]
        ```""",
    },
    # Test Case 6: Nested JSON inside a string
    {
        "professional_summary": "jhon known is a full-stack developer at StartupXYZ.",
        "social_media_links": """```json
        [
            {"platform": "Twitter", "url": "https://twitter.com/alicebrown"}
        ]
        ```""",
        "company_news": """```json
        [
            {"title": "StartupXYZ releases new mobile app", "url": "https://technews.com/startupxyz-app", "description": "{'details': 'A revolutionary new app designed to improve user experience'}"}
        ]
        ```""",
    },
    # Test Case 7: chain fails
    {
        "professional_summary": "Geronimo was unable to gather data",
        "social_media_links": "Geronimo was unable to gather data",
        "company_summary": "Geronimo was unable to gather data",
        "company_competitors": "Geronimo was unable to gather data",
        "company_news": "Geronimo was unable to gather data",
    },
    # Test Case 8: Large response with multiple competitors and news articles
    {
        "professional_summary": "jhon known is the CTO of CloudTech, leading innovation in cloud computing.",
        "social_media_links": """```json
        [
            {"platform": "LinkedIn", "url": "https://linkedin.com/in/davidwilson"},
            {"platform": "GitHub", "url": "https://github.com/davidwilson"},
            {"platform": "Twitter", "url": "https://twitter.com/davidwilson"}
        ]
        ```""",
        "company_summary": "CloudTech is a pioneering cloud service provider...",
        "company_competitors": "AWS, Google Cloud, Microsoft Azure, IBM Cloud",
        "company_news": """```json
        [
            {"title": "CloudTech partners with Fortune 500 companies", "url": "https://news.cloudtech.com/partnerships", "description": "CloudTech has secured major deals."},
            {"title": "CloudTech announces data center expansion", "url": "https://news.cloudtech.com/expansion", "description": "The company plans to build new data centers."}
        ]
        ```""",
    },
    # Test Case 9: one chain fails (professional_summary)
    {
        "professional_summary": "Geronimo was unable to gather data",
        "social_media_links": """```json
        [
            {"platform": "LinkedIn", "url": "https://linkedin.com/in/davidwilson"},
            {"platform": "GitHub", "url": "https://github.com/davidwilson"},
        ]
        ```""",
        "company_summary": "CloudTech is a pioneering cloud serv",
        "company_competitors": "AWS, Google Cloud, Microsoft Azure, IBM Cloud",
        "company_news": """```json
        [
            {"title": "CloudTech partners with Fortune 500 companies", "url": "https://news.cloudtech.com/partnerships", "description": "CloudTech has secured major deals."},
        ]
        ```""",
    },
    # Test Case 10: one chain fails (social medial links)
    {
        "professional_summary": "Jhon know is a deveoploer in ...",
        "social_media_links": "Geronimo was unable to gather data",
        "company_summary": "CloudTech is a pioneering cloud serv",
        "company_competitors": "AWS, Google Cloud, Microsoft Azure, IBM Cloud",
        "company_news": """```json
        [
            {"title": "CloudTech partners with Fortune 500 companies", "url": "https://news.cloudtech.com/partnerships", "description": "CloudTech has secured major deals."},
        ]
        ```""",
    },
    # Test Case 11: one chain fails (company competitors)
    {
        "professional_summary": "Jhon know is a deveoploer in ...",
        "social_media_links": """```json
        [
            {"platform": "LinkedIn", "url": "https://linkedin.com/in/davidwilson"},
            {"platform": "GitHub", "url": "https://github.com/davidwilson"},
        ]
        ```""",
        "company_summary": "CloudTech is a pioneering cloud serv",
        "company_competitors": "Geronimo was unable to gather data",
        "company_news": """```json
        [
            {"title": "CloudTech partners with Fortune 500 companies", "url": "https://news.cloudtech.com/partnerships", "description": "CloudTech has secured major deals."},
        ]
        ```""",
    },
]

REQUIRED_FIELDS = [
    "professional_summary",
    "social_media_links",
    "company_summary",
    "company_competitors",
    "company_news",
]


@pytest.mark.parametrize("input_data", DUMMY_RESPONSES)
@patch(
    "utils.json_format.format_json_string",
    side_effect=lambda x: json.dumps(x) if x else None,
)
def test_format_response(mock_json_formatter, input_data):
    """Test format_response function with different input cases."""
    result = format_response(input_data)

    # Ensure the result is a dictionary
    assert isinstance(result, dict), "Output is not a dictionary"

    # Ensure all required fields are present in the result
    for field in REQUIRED_FIELDS:
        assert field in result, f"Missing field: {field}"
