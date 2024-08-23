from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.schema import CheckConstraint
from sqlalchemy.orm import validates

from app.core.db import Base

DEFAULT_INTEGER = 0
GREATER_THAN_ZERO_CONSTRAINT_NAME = '{}_greater_than_zero'
GREATER_THAN_ZERO_CONSTRAINT_ERROR = (
    'Поле {} должно быть больше нуля!'
)


class InvestmentBase(Base):
    __abstract__ = True
    full_amount = Column(Integer)
    fully_invested = Column(Boolean, default=False)
    invested_amount = Column(Integer, default=DEFAULT_INTEGER)
    create_date = Column(DateTime(timezone=True), default=datetime.now)
    close_date = Column(DateTime(timezone=True), default=datetime.now)

    __table_args__ = (
        CheckConstraint(
            'full_amount > 0',
            name=GREATER_THAN_ZERO_CONSTRAINT_NAME.format('full_amount')
        ),
    )

    @validates('full_amount')
    def validate_name(self, key, full_amount) -> str:
        if full_amount <= 0:
            raise ValueError(
                GREATER_THAN_ZERO_CONSTRAINT_ERROR.format('full_amount')
            )
        return full_amount