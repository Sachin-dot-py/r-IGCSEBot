from redis_om import Field
from .ExtendedModel import ExtendedModel
from .Question import Question
import uuid

class Session(ExtendedModel):
    session_id: str = Field(primary_key=True, default=str(uuid.uuid4()).split('-')[0]) 
    channel_id: str = Field(index=True)
    thread_id: str = Field(index=True)
    subject: str = Field(index=True)
    topics: list[str] = Field(index=True)
    limit: int
    minimum_year: int 
    users: list[str]
    started_by: str = Field(index=True)
    # Integer has been used instead of bool since redisearch doesn't support indexing for type bool.
    private: int = Field(index=True)
    paused: int = Field(index=True)
    currently_solving: str = Field(index=True, default="none")
    expire_time: int = Field(index=True)
