from datetime import datetime
from typing import Optional

from pydantic import BaseModel, PositiveInt, Field


class DonationBase(BaseModel):
    full_amount: PositiveInt = Field(...)
    comment: Optional[str]

    class Config:
        orm_mode = True


class DonationCreate(DonationBase):
    pass


class DonationUpdate(DonationBase):
    pass


class DonationDB(DonationBase):
    id: int
    create_date: datetime
    user_id: int
    invested_amount: int
    fully_invested: bool
    close_date: datetime
