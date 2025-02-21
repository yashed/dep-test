import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import utils.report_generator as report_generator
from services.mail_service import send_mail_caller
import utils.constants as constants


# Create FastAPI instance
app = FastAPI()


# Define the request body schema
class EmailInfo(BaseModel):
    subject: str
    from_: str = Field(..., alias="from")
    to: list[str]
    cc: list[str]


class LeadInfo(BaseModel):
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    job_title: str = Field(..., alias="jobTitle")
    company: str
    country: str
    state: str
    area_of_interest: str = Field(..., alias="areaOfInterest")
    contact_reason: str = Field(..., alias="contactReason")
    industry: str
    can_help_comment: str = Field(..., alias="canHelpComment")


class LeadRequest(BaseModel):
    email_info: EmailInfo = Field(..., alias="emailInfo")
    lead_info: LeadInfo = Field(..., alias="leadInfo")


@app.post("/generate_report")
async def generate_report(request_data: LeadRequest):
    try:
        print("Request Data - ", request_data)
        lead_info = request_data.lead_info
        email_info = request_data.email_info

        response = report_generator.parallel_chain_caller(lead_info)
        send_mail_caller(response, email_info)

        return JSONResponse(
            content={
                "message": "Geronimo response sent successfully",
                "status": "success",
            },
            status_code=200,
        )

    except Exception as e:
        constants.LOGGER.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
