from  sqlalchemy import TIMESTAMP, Column,Integer,String,Boolean,DateTime, text
from .database import Base
from datetime import datetime
class Post(Base):
    __tablename__="post"


    id=Column(Integer,primary_key=True,nullable=False)
    title=Column(String,nullable=False)
    content=Column(String,nullable=False)
    published=Column(Boolean,default=True)
    time = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    
