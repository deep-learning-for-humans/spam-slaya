from . import db

import uuid
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


class RunStatusEnum(enum.Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    DELETING = "DELETING"
    DONE = "DONE"
    DONE_WITH_ERRORS = "DONE WITH ERRORS"


class MessageActionEnum(enum.Enum):
    TBD = "TBD"
    KEEP = "KEEP"
    DELETE = "DELETE"
    UNPROCESSED = "UNPROCESSED"


class User(db.Model):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    open_api_key = Column(String, nullable=True)
    gmail_credentials = Column(String, nullable=False)
    gmail_credential_expiry = Column(DateTime, nullable=False)

    runs = relationship('Run', back_populates='user')


class Run(db.Model):
    __tablename__ = 'runs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    scheduled_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    status = Column(Enum(RunStatusEnum), default=RunStatusEnum.QUEUED)
    to_process = Column(Integer, nullable=False)
    processed_count = Column(Integer, default=0)

    user = relationship('User', back_populates='runs')
    batches = relationship('RunBatch', back_populates='run')


class RunBatch(db.Model):
    __tablename__ = 'run_batches'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(UUID(as_uuid=True), ForeignKey('runs.id'), nullable=False)
    batch_id = Column(UUID(as_uuid=True), default=uuid.uuid4)
    message_id = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    action = Column(Enum(MessageActionEnum), nullable=False, default=MessageActionEnum.TBD)
    errors = Column(String, nullable=True)

    run = relationship('Run', back_populates='batches')
