from asyncio import sleep
from datetime import datetime
import enum
from typing import Optional
from dateutil import tz

from pydantic import BaseModel, Field

from plombery import register_pipeline, task, Trigger, get_logger


class InputParams(BaseModel):
    """Showcase all the available input types in Plombery"""

    gform_link: str 


@task
async def submit_google_form_data(params: InputParams) -> int:
    """ Submit data to a Google Form """

    logger = get_logger()

    return 1


register_pipeline(
    id="submit_gform_pipeline",
    description="""Automator pipeline that submits data to a Google Form""",
    tasks=[submit_google_form_data],
    params=InputParams,
)
