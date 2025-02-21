# Geronimo V1.0.1

A Streamlit application that leverages Langchain for various tasks. This README provides setup and installation instructions to get the project running on your system.

---

## Prerequisites

Before setting up the project, ensure the following are installed:

1. **Python**  
   Install Python (version 3.8 or above). You can download it from [Python's official website](https://www.python.org/downloads/).

---

## Setting Up the Project

### Create and Activate a Virtual Environment

It is recommended to use a virtual environment to manage dependencies for this project.

##### **On Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

##### **On macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### **Install Required Dependencies:**

After activating the virtual environment, install all the dependencies listed in the requirements.txt file:

```bash
pip install -r requirements.txt
```

#### **Set Up the .env File:**

Create a file named `.env` in the root directory of the project and add the following environment variables:

#### **.env**

```bash
# Google API Credentials
GOOGLE_API_KEY="<your_google_api_key>"
GOOGLE_CSE_ID="<your_google_cse_id>"
GOOGLE_SERACH_URL="<your_google_search_url>"

# Azure OpenAI Credentials
AZURE_OPENAI_API_KEY="<your_azure_api_key>"
OPENAI_API_BASE="<your_openai_api_base>"
OPENAI_DEPLOYMENT_NAME="<your_openai_deployment_name>"
OPENAI_API_VERSION="<your_openai_api_version>"

# API Developer Portal Mail Service
CLIENT_ID="<your_client_id>"
CLIENT_SECRET="<your_client_secret>"
TOKEN_ENDPOINT="<your_token_endpoint>"
API_ENDPOINT="<your_api_endpoint>"
FROM_EMAIL="<your_from_email>"

# Logger level
LOGGING_LEVEL=INFO
```

Replace the placeholders with your respective API keys and credentials.

#### **Running the Project:**

To start the project, run the following command in your terminal:

```bash
uvicorn main:app --reload
```

This will launch the Python service. The service will be accessible at the following URL:

```
http://localhost:8000
```

#### **Accessing the API:**

To generate insights, you need to use the following endpoint:

```
POST http://localhost:8000/generate_report/
```

#### **Required Request Payload:**

When sending a request to the endpoint, you must pass the following JSON data:

```json
{
  "emailInfo": {
    "subject": "<Email Subject>",
    "from": "<Sender Email>",
    "to": ["<Recipient Email>"] ,
    "cc": ["<CC Email>"]
  },
  "leadInfo": {
    "firstName": "<First Name>",
    "lastName": "<Last Name>",
    "jobTitle": "<Job Title>",
    "company": "<Company>",
    "country": "<Country>",
    "state": "<State>",
    "areaOfInterest": "<Area of Interest>",
    "contactReason": "<Reason for Contact>",
    "industry": "<Industry>",
    "canHelpComment": "<How You Can Help>"
  }
}
```

Replace the placeholder values (`<First Name>`, `<Company>`, etc.) with the actual data you want to submit.

#### **Response:**

If the request is successful, you will receive a response like this:

```json
{
  "message": "Geronimo response sent successfully",
  "status": "success"
}
```

In case of an error, a proper HTTP error code and message will be returned.

---

This README provides all necessary steps to set up, configure, and run the Geronimo project efficiently.

