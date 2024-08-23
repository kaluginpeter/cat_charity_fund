from sqlalchemy import Column, Text, Integer, ForeignKey

from app.models.base import InvestmentBase


class Donation(InvestmentBase):
    __tablename__ = 'donation'
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)