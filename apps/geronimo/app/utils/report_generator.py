from concurrent.futures import ThreadPoolExecutor
from utils import json_format as json_format
from utils.llm_caller import run_chain
import utils.constants as constants
from utils.prompt_templates import (
    prompt_template_personal_summary,
    prompt_template_social_links,
    prompt_template_company_summary,
    prompt_template_competitors,
    prompt_template_news,
)


def parallel_chain_caller(lead_info):
    """
    Run all chains in parallel to generate insights.
    """
    name = f"{lead_info.first_name} {lead_info.last_name}"
    tasks = {
        constants.PROFESSIONAL_SUMMARY: {
            "query": f"{name} in {lead_info.company}",
            "prompt": prompt_template_personal_summary,
            "num_results": 8,
        },
        constants.SOCIAL_MEDIA_LINKS: {
            "query": f"{name} in {lead_info.company}",
            "prompt": prompt_template_social_links,
            "num_results": 5,
        },
        constants.COMPANY_SUMMARY: {
            "query": f"{lead_info.company} in {lead_info.country} overview",
            "prompt": prompt_template_company_summary,
            "num_results": 5,
        },
        constants.COMPANY_COMPETITORS: {
            "query": f"{lead_info.company} competitors",
            "prompt": prompt_template_competitors,
            "num_results": 4,
        },
        constants.COMPANY_NEWS: {
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
        constants.PROFESSIONAL_SUMMARY: response_data.get(
            constants.PROFESSIONAL_SUMMARY, "No Personal Detail Available"
        ),
        constants.SOCIAL_MEDIA_LINKS: json_format.format_json_string(
            response_data.get(constants.SOCIAL_MEDIA_LINKS, None)
        ),
        constants.COMPANY_SUMMARY: response_data.get(
            constants.COMPANY_SUMMARY, "No Company Detail Available"
        ),
        constants.COMPANY_COMPETITORS: (
            response_data.get(constants.COMPANY_COMPETITORS, [])
            if isinstance(response_data.get(constants.COMPANY_COMPETITORS), list)
            else list(
                filter(
                    None,
                    [
                        competitor.strip()
                        for competitor in response_data.get(
                            constants.COMPANY_COMPETITORS, ""
                        )
                        .replace("\n", ",")
                        .split(",")
                    ],
                )
            )
        ),
        constants.COMPANY_NEWS: json_format.format_json_string(
            response_data.get(constants.COMPANY_NEWS, None)
        ),
    }
