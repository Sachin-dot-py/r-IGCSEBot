from redis_om import Field
from .ExtendedModel import ExtendedModel

class View(ExtendedModel):
    # This exists for the sole purpose of making views persistent.
    view_id: str = Field(primary_key=True)
    message_id: str = Field(index=True)