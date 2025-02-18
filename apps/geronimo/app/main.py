import os
from fastapi import FastAPI, HTTPException, Request, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.security.api_key import APIKeyHeader
import utils.report_generator as report_generator
from services.mail_service import send_mail
from dotenv import load_dotenv
import logging

load_dotenv(override=True)

# Create FastAPI instance
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Enable CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define the request body schema
class EmailInfo(BaseModel):
    subject: str
    from_: str
    to: list[str]
    cc: list[str]


class LeadInfo(BaseModel):
    firstName: str
    lastName: str
    jobTitle: str
    company: str
    country: str
    state: str
    areaOfInterest: str
    contactReason: str
    industry: str
    canHelpComment: str


class LeadRequest(BaseModel):
    emailInfo: EmailInfo
    leadInfo: LeadInfo


@app.post("/generate_data")
async def generate_data(request_data: LeadRequest):
    try:
        lead_info = request_data.leadInfo
        email_info = request_data.emailInfo

        response = report_generator.parallel_chain_caller(lead_info)
        send_mail(response, email_info)

        return JSONResponse(
            content={
                "message": "Geronimo response sent successfully",
                "status": "success",
            },
            status_code=200,
        )

    # HTTP exceptions
    except HTTPException:
        raise
    # unexpected errors
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
