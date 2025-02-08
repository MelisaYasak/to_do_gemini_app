from ..db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from ..m_user.user import User


class Todo(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey(User.id))
    