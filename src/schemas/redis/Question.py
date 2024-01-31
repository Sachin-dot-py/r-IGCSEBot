from redis_om import Field
from .ExtendedModel import ExtendedModel
from typing import Optional
        
class Question(ExtendedModel):
    question_name: str = Field(primary_key=True)
    questions: list[object]
    answers: str | list[str]
    solved: int = 0
    user_answers: dict[str, str] = {}
    session_id: str = Field(index=True)