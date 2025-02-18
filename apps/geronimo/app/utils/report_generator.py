import logging
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
from utils import json_format as json_format
from utils.llm_caller import run_chain
from utils.prompt_templates import (
    prompt_template_personal_summary,
    prompt_template_social_links,
    prompt_template_company_summary,
    prompt_template_competitors,
    prompt_template_news,
)

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


def parallel_chain_caller(lead_info):
    """
    Run all chains in parallel to generate insights.
    """
    name = f"{lead_info.firstName} {lead_info.lastName}"
    tasks = {
        "personal_summary": {
            "query": f"{name} in {lead_info.company}",
            "prompt": prompt_template_personal_summary,
            "num_results": 8,
        },
        "social_media_links": {
            "query": f"{name} in {lead_info.company}",
            "prompt": prompt_template_social_links,
            "num_results": 5,
        },
        "company_summary": {
            "query": f"{lead_info.company} in {lead_info.country} overview",
            "prompt": prompt_template_company_summary,
            "num_results": 5,
        },
        "company_competitors": {
            "query": f"{lead_info.company} competitors",
            "prompt": prompt_template_competitors,
            "num_results": 4,
        },
        "company_news": {
            "query": f"{lead_info.company} company in {lead_info.country} recent news",
            "prompt": prompt_template_news,
            "num_results": 4,
        },
    }

    with ThreadPoolExecutor() as executor:
        futures = {
            key: executor.submit(
                run_chain,
                name,
                lead_info,
                data["query"],
                data["prompt"],
                data["num_results"],
            )
            for key, data in tasks.items()
        }
        results = {key: future.result() for key, future in futures.items()}

    return format_response(results)


def format_response(response_data):
    """
    Format the response data into a JSON object.
    Args:
        response_data (dict): The response data from the chains.
    Returns:
        dict: The formatted JSON object.
    """

    return {
        "professional_summary": response_data.get("personal_summary", ""),
        "social_media_links": json_format.format_json_string(
            response_data.get("social_media_links", "")
        ),
        "company_summary": response_data.get("company_summary", ""),
        "company_competitors": ", ".join(
            filter(None, response_data.get("company_competitors", "").split("\n"))
        ),
        "company_news": json_format.format_json_string(
            response_data.get("company_news", "")
        ),
    }
