from datetime import datetime, timedelta, timezone

from nonebot_plugin_orm import Model, get_session
from nonebot_plugin_session import Session, SessionIdType
from nonebot_plugin_session_orm import SessionModel, get_session_persist_id
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column


class MemeGenerationRecord(Model):
    """表情调用记录"""

    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    session_persist_id: Mapped[int]
    """ 会话持久化id """
    time: Mapped[datetime]
    """ 调用时间\n\n存放 UTC 时间 """
    meme_key: Mapped[str] = mapped_column(String(64))
    """ 表情名 """


async def record_meme_generation(session: Session, meme_key: str):
    session_persist_id = await get_session_persist_id(session)

    record = MemeGenerationRecord(
        session_persist_id=session_persist_id,
        time=datetime.now(timezone.utc),
        meme_key=meme_key,
    )
    async with get_session() as db_session:
        db_session.add(record)
        await db_session.commit()


async def get_meme_generation_keys(
    session: Session, id_type: SessionIdType, time_delta: timedelta
) -> list[str]:
    whereclause = SessionModel.filter_statement(
        session, id_type, include_bot_type=False
    )
    whereclause.append(
        MemeGenerationRecord.time >= (datetime.now(timezone.utc) - time_delta)
    )
    statement = (
        select(MemeGenerationRecord.meme_key)
        .where(*whereclause)
        .join(SessionModel, SessionModel.id == MemeGenerationRecord.session_persist_id)
    )
    async with get_session() as db_session:
        result = (await db_session.scalars(statement)).all()
    return list(result)
