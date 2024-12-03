from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Union

from nonebot_plugin_orm import Model, get_session
from nonebot_plugin_uninfo import Session, SupportScope
from nonebot_plugin_uninfo.orm import (
    BotModel,
    SceneModel,
    SessionModel,
    UserModel,
    get_session_persist_id,
)
from sqlalchemy import ColumnElement, String, select
from sqlalchemy.orm import Mapped, mapped_column

from .utils import remove_timezone


class MemeGenerationRecord(Model):
    """表情调用记录"""

    __tablename__ = "nonebot_plugin_memes_memegenerationrecord_v2"
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


class SessionIdType(Enum):
    GLOBAL = 0
    USER = 1
    GROUP = 2
    GROUP_USER = 3


def scope_value(scope: Union[str, SupportScope]) -> str:
    return scope.value if isinstance(scope, SupportScope) else scope


def filter_statement(
    session: Session,
    id_type: SessionIdType,
    *,
    meme_key: Optional[str] = None,
    time_start: Optional[datetime] = None,
    time_stop: Optional[datetime] = None,
) -> list[ColumnElement[bool]]:
    filter_scene = True
    filter_user = True
    if id_type == SessionIdType.GLOBAL:
        filter_scene = False
        filter_user = False
    elif id_type == SessionIdType.GROUP:
        filter_user = False
    elif id_type == SessionIdType.USER:
        filter_scene = False

    whereclause: list[ColumnElement[bool]] = []
    whereclause.append(BotModel.self_id == session.self_id)
    whereclause.append(BotModel.scope == scope_value(session.scope))

    if filter_scene:
        whereclause.append(SceneModel.scene_id == session.scene.id)
        whereclause.append(SceneModel.scene_type == session.scene.type.value)
    if filter_user:
        whereclause.append(UserModel.user_id == session.user.id)

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
        .join(BotModel, BotModel.id == SessionModel.bot_persist_id)
        .join(SceneModel, SceneModel.id == SessionModel.scene_persist_id)
        .join(UserModel, UserModel.id == SessionModel.user_persist_id)
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
        .join(BotModel, BotModel.id == SessionModel.bot_persist_id)
        .join(SceneModel, SceneModel.id == SessionModel.scene_persist_id)
        .join(UserModel, UserModel.id == SessionModel.user_persist_id)
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
        .join(BotModel, BotModel.id == SessionModel.bot_persist_id)
        .join(SceneModel, SceneModel.id == SessionModel.scene_persist_id)
        .join(UserModel, UserModel.id == SessionModel.user_persist_id)
    )
    async with get_session() as db_session:
        results = (await db_session.scalars(statement)).all()
    return list(results)
