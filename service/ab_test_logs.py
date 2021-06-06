from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json

from .database import Base
from service.query import Query, Result
from service.models import ModelName


class ABTestLogTable(Base):
    __tablename__ = "ab-test-logs"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, index=True, nullable=False)
    query = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    result = Column(String, nullable=False)


class ABTestLogBase(BaseModel):
    query_id: int
    query: Query
    model_name: ModelName
    result: Result


class ABTestLogCreate(ABTestLogBase):
    pass


class ABTestLog(ABTestLogBase):
    id: int

    class Config:
        orm_mode = True


def create(db: Session, ab_test_log: ABTestLogCreate):
    db_ab_test_log = ABTestLogTable(
        query_id=ab_test_log.query_id,
        query=ab_test_log.query.json(),
        model_name=ab_test_log.model_name,
        result=json.dumps(ab_test_log.result),
    )
    db.add(db_ab_test_log)
    db.commit()
    db.refresh(db_ab_test_log)
    return db_ab_test_log
