from redis_om import Field
from .ExtendedModel import ExtendedModel

class User(ExtendedModel):
    user_id: str = Field(primary_key=True)
    playing: bool = False
    subject: str = None
    session_id: str = None