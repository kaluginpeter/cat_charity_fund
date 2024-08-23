from sqlalchemy import Column, String, Text
from sqlalchemy.schema import CheckConstraint
from sqlalchemy.orm import validates

from app.models.base import InvestmentBase


MIN_LENGTH_CONSTRAINT_NAME = '{}_min_length'
MIN_LENGTH_CONSTRAINT_EXPRESSION = (
    'length({}) > 1'
)
MIN_LENGTH_CONSTRAINT_ERROR = 'Поле {} должно иметь хотя бы 1 символ!'


class CharityProject(InvestmentBase):
    __tablename__ = 'charityproject'
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)

    __table_args__ = InvestmentBase.__table_args__ + (
        CheckConstraint(
            MIN_LENGTH_CONSTRAINT_EXPRESSION.format('name'),
            name=MIN_LENGTH_CONSTRAINT_NAME.format('name')
        ),
        CheckConstraint(
            MIN_LENGTH_CONSTRAINT_EXPRESSION.format('description'),
            name=MIN_LENGTH_CONSTRAINT_NAME.format('description')
        ),
    )

    @validates('name')
    def validate_name(self, key, name) -> str:
        if len(name) <= 1:
            raise ValueError(MIN_LENGTH_CONSTRAINT_ERROR.format('name'))
        return name

    @validates('description')
    def validate_description(self, key, description) -> str:
        if len(description) <= 1:
            raise ValueError(MIN_LENGTH_CONSTRAINT_ERROR.format('description'))
        return description
