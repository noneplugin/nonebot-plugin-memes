from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from nonebot_plugin_orm import Model, get_session
from nonebot_plugin_session import Session, SessionIdType
from nonebot_plugin_session_orm import SessionModel, get_session_persist_id
from sqlalchemy import ColumnElement, String, select
from sqlalchemy.orm import Mapped, mapped_column

from .utils import remove_timezone


class MemeGenerationRecord(Model):
    """表情调用记录"""

    __tablename__ = "nonebot_plugin_memes_memegenerationrecord"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    session_persist_id: Mapped[int]
    """ 会话持久化id """
    time: Mapped[datetime]
    """ 调用时间\n\n存放 UTC 时间 """
    meme_key: Mapped[str] = mapped_column(String(64))
    """ 表情名 """


@dataclass
class MemeRecord:
    time: datetime
    meme_key: str


async def record_meme_generation(session: Session, meme_key: str):
    session_persist_id = await get_session_persist_id(session)

    record = MemeGenerationRecord(
        session_persist_id=session_persist_id,
        time=remove_timezone(datetime.now(timezone.utc)),
        meme_key=meme_key,
    )
    async with get_session() as db_session:
        db_session.add(record)
        await db_session.commit()


def filter_statement(
    session: Session,
    id_type: SessionIdType,
    *,
    meme_key: Optional[str] = None,
    time_start: Optional[datetime] = None,
    time_stop: Optional[datetime] = None,
) -> list[ColumnElement[bool]]:
    whereclause = SessionModel.filter_statement(
        session, id_type, include_bot_type=False
    )
    if meme_key:
        whereclause.append(MemeGenerationRecord.meme_key == meme_key)
    if time_start:
        whereclause.append(MemeGenerationRecord.time >= remove_timezone(time_start))
    if time_stop:
        whereclause.append(MemeGenerationRecord.time <= remove_timezone(time_stop))
    return whereclause


async def get_meme_generation_records(
    session: Session,
    id_type: SessionIdType,
    *,
    meme_key: Optional[str] = None,
    time_start: Optional[datetime] = None,
    time_stop: Optional[datetime] = None,
) -> list[MemeRecord]:
    whereclause = filter_statement(
        session, id_type, meme_key=meme_key, time_start=time_start, time_stop=time_stop
    )
    statement = (
        select(MemeGenerationRecord.time, MemeGenerationRecord.meme_key)
        .where(*whereclause)
        .join(SessionModel, SessionModel.id == MemeGenerationRecord.session_persist_id)
    )
    async with get_session() as db_session:
        results = (await db_session.execute(statement)).all()
    return [MemeRecord(result[0], result[1]) for result in results]


async def get_meme_generation_times(
    session: Session,
    id_type: SessionIdType,
    *,
    meme_key: Optional[str] = None,
    time_start: Optional[datetime] = None,
    time_stop: Optional[datetime] = None,
) -> list[datetime]:
    whereclause = filter_statement(
        session, id_type, meme_key=meme_key, time_start=time_start, time_stop=time_stop
    )
    statement = (
        select(MemeGenerationRecord.time)
        .where(*whereclause)
        .join(SessionModel, SessionModel.id == MemeGenerationRecord.session_persist_id)
    )
    async with get_session() as db_session:
        results = (await db_session.scalars(statement)).all()
    return list(results)


async def get_meme_generation_keys(
    session: Session,
    id_type: SessionIdType,
    *,
    time_start: Optional[datetime] = None,
    time_stop: Optional[datetime] = None,
) -> list[str]:
    whereclause = filter_statement(
        session, id_type, time_start=time_start, time_stop=time_stop
    )
    statement = (
        select(MemeGenerationRecord.meme_key)
        .where(*whereclause)
        .join(SessionModel, SessionModel.id == MemeGenerationRecord.session_persist_id)
    )
    async with get_session() as db_session:
        results = (await db_session.scalars(statement)).all()
    return list(results)
