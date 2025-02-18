import os

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import base64
import re
from dotenv import load_dotenv
import requests
from jinja2 import Template

# Load environment variables
load_dotenv(override=True)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_ENDPOINT = os.getenv("TOKEN_ENDPOINT")
API_ENDPOINT = os.getenv("API_ENDPOINT")
ALERT_FROM = os.getenv("FROM_EMAIL")
TEST_MAIL_ADDRESS = os.getenv("TEST_MAIL_ADDRESS")
FROM_EMAIL = os.getenv("FROM_EMAIL")

if not all([CLIENT_ID, CLIENT_SECRET, TOKEN_ENDPOINT, API_ENDPOINT]):
    raise ValueError("One or more required environment variables are missing!")


class EmailServiceClient:
    def __init__(self, client_id, client_secret, token_endpoint, api_endpoint):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_endpoint = token_endpoint
        self.api_endpoint = api_endpoint
        self.access_token = None

    def get_access_token(self):
        credentials = f"{self.client_id}:{self.client_secret}"
        basic_auth = base64.b64encode(credentials.encode()).decode()
        headers = {
            "Authorization": f"Basic {basic_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials"}
        response = requests.post(
            self.token_endpoint, headers=headers, data=data, verify=True
        )
        if response.status_code == 200:
            self.access_token = response.json()["access_token"]
            return self.access_token
        else:
            raise Exception(f"Failed to get access token: {response.text}")

    @retry(
        stop=stop_after_attempt(3),  # Retry up to 3 times
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
    )
    def send_email(
        self,
        to_email,
        template_content,
        subject,
        from_email,
        cc=None,
        bcc=None,
        attachments=None,
    ):
        if not self.access_token:
            self.get_access_token()
        encoded_template = base64.b64encode(template_content.encode()).decode()
        email_data = {
            "to": [to_email] if isinstance(to_email, str) else to_email,
            "from": from_email,
            "subject": subject,
            "template": encoded_template,
            "cc": cc if cc else [],
            "bcc": bcc if bcc else [],
            "attachments": attachments if attachments else [],
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        response = requests.post(
            f"{self.api_endpoint}/send-email",
            headers=headers,
            json=email_data,
            verify=True,
        )
        if response.status_code == 200:
            return "Email sent successfully"
        else:
            raise Exception(f"Failed to send email: {response.text}")


def load_template(template_path):
    """Loads the email template from file."""
    with open(template_path, "r") as file:
        return file.read()


def format_template(template, response_data):
    """
    Replaces placeholders in the template with the actual data.
    """

    formatted_data = {
        "person_profile": response_data.get(
            "professional_summary", "No Personal Detail Available"
        ),
        "social_media_links": response_data.get("social_media_links", None),
        "company_overview": response_data.get(
            "company_summary", "No Company Detail Available"
        ),
        "company_competitors": (
            response_data.get("company_competitors", "").split(",")
            if response_data.get("company_competitors")
            else []
        ),
        "company_news": response_data.get("company_news", None),
    }

    jinja_template = Template(template)

    rendered_template = jinja_template.render(formatted_data)

    return rendered_template


def send_mail(response_data, email_info):
    """
    Send an email using the new EmailServiceClient.

    Args:
        response_data (dict): The data to be sent in the email.
        email_info (dict): Email details (to, subject, etc.).
    """

    client = EmailServiceClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_endpoint=TOKEN_ENDPOINT,
        api_endpoint=API_ENDPOINT,
    )
    send_to = email_info.to if email_info.to else [None]
    subject = email_info.subject
    cc = email_info.cc if email_info.cc else []
    bcc = email_info.bcc if hasattr(email_info, "bcc") else []

    # Load and format the email template
    template_path = os.path.join(os.path.dirname(__file__), "mail_template.html")
    email_template = load_template(template_path)
    formatted_template = format_template(email_template, response_data)
    try:
        response = client.send_email(
            to_email=send_to,
            template_content=formatted_template,
            subject=subject,
            from_email=ALERT_FROM,
            cc=cc,
            bcc=bcc,
        )
        return response
    except Exception as e:
        return f"Email sending failed: {str(e)}"
