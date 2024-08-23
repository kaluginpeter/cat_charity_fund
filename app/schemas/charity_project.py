from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt

MIN_STRING_LENGTH = 1
MAX_STRING_LENGTH = 100


class CharityProjectBase(BaseModel):
    name: str = Field(
        ...,
        min_length=MIN_STRING_LENGTH,
        max_length=MAX_STRING_LENGTH
    )
    description: str = Field(..., min_length=MIN_STRING_LENGTH)
    full_amount: PositiveInt

    class Config:
        arbitrary_types_allowed = True
        extra = Extra.forbid
        orm_mode = True


class CharityProjectCreate(CharityProjectBase):
    pass


class CharityProjectUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=MIN_STRING_LENGTH,
        max_length=MAX_STRING_LENGTH
    )
    description: Optional[str] = Field(None, min_length=MIN_STRING_LENGTH)
    full_amount: Optional[PositiveInt]

    class Config:
        arbitrary_types_allowed = True
        extra = Extra.forbid
        orm_mode = True


class CharityProjectDB(CharityProjectBase):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime = Field(datetime.now())
    close_date: datetime = Field(datetime.now())
