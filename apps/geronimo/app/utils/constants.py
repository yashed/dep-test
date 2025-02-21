import logging
import utils.config as config

logging.basicConfig(
    level=getattr(logging, config.LOGGING_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

LOGGER = logging.getLogger(__name__)

# Chains Keys
PROFESSIONAL_SUMMARY = "professional_summary"
SOCIAL_MEDIA_LINKS = "social_media_links"
COMPANY_SUMMARY = "company_summary"
COMPANY_COMPETITORS = "company_competitors"
COMPANY_NEWS = "company_news"

# valid tags to scrape
TAGS = ["p", "h1", "h2", "li", "div", "title", "description", "to", "message"]

# web page content types
VALID_CONTENT_TYPES = {
    "text/html",
    "application/xhtml+xml",
    "text/xml",
    "application/xml",
}

# User agent header
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    )
}
