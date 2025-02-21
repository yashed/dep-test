from langchain.chains import LLMChain
import utils.constants as constants
import utils.config as config
from datetime import datetime
from langchain_openai import AzureChatOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)
from utils.prompt_templates import (
    prompt_template_summarization,
)

# Initialize ChatOpenAI model
llm = AzureChatOpenAI(
    azure_endpoint=config.OPENAI_API_BASE,
    azure_deployment=config.OPENAI_DEPLOYMENT_NAME,
    openai_api_key=config.OPENAI_API_KEY,
    temperature=0.0,
    request_timeout=30,
)


def run_chain(name, lead_info, query, llm_prompt, num_results):
    """
    Fetch Google results, scrape content, and run the LLM chain.
    """
    import utils.web_search as web_search
    import utils.web_scrape as web_scrape

    search_results = web_search.google_search(query, num_results)

    formatted_results = web_scrape.parallel_scrape_caller(
        search_results, query, num_results
    )

    # get date to pass to chain
    today_date = datetime.today().strftime("%Y-%m-%d")

    chain = LLMChain(llm=llm, prompt=llm_prompt, output_key="result")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=8)
    )
    def invoke_chain():
        return chain.invoke(
            {
                "name": name,
                "company": lead_info.company,
                "position": lead_info.job_title,
                "country": lead_info.country,
                "google_results": formatted_results,
                "date": today_date,
            }
        )["result"]

    try:
        return invoke_chain()
    except Exception as e:
        constants.LOGGER.error(f"Chain Failed: {str(e)}")
        return "Geronimo was unable to gather data"


def summarize_large_content(content, query, url, chunk_size=80000, overlap=2000):
    """
    Summarize large content by splitting it into chunks and summarizing each chunk sequentially.

    Args:
        content (str): The large content to be summarized.
        query (str): The query related to the content.
        chunk_size (int): The size of each chunk.
        overlap (int): The overlap between chunks.

    Returns:
        str: The summarized content.
    """

    chunks = []
    start = 0
    while start < len(content):
        end = min(start + chunk_size, len(content))
        chunks.append(content[start:end])
        start += chunk_size - overlap

    chain = LLMChain(llm=llm, prompt=prompt_template_summarization)

    chunk_summaries = []
    for chunk in chunks:
        try:
            chunk_summary = chain.run({"query": query, "chunk": chunk})

            chunk_summaries.append(chunk_summary)
        except Exception as e:
            constants.LOGGER.error(f"Error summarizing chunk: {str(e)}", exc_info=True)
            chunk_summaries.append("")

    combined_summary = "\n".join(chunk_summaries)

    if len(combined_summary) > chunk_size:
        return summarize_large_content(combined_summary, query, chunk_size, overlap)

    return combined_summary
