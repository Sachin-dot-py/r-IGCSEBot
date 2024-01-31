from redis_om import Field
from .ExtendedModel import ExtendedModel
from typing import Optional

class TempSessionData(ExtendedModel):
    user_id: str = Field(primary_key=True)
    subject: Optional[str]
    topics: Optional[list[str]]
    limit: Optional[int]
    minimum_year: Optional[int]
    users: Optional[list[str]]
    private: Optional[bool]