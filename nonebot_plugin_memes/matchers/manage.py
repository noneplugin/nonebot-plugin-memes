from meme_generator import Meme
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER, Permission
from nonebot_plugin_session import EventSession, SessionLevel

from ..manager import MemeMode, meme_manager
from .utils import find_meme_and_handle


def _is_private(session: EventSession) -> bool:
    return session.level == SessionLevel.LEVEL1


PERM_EDIT = SUPERUSER | Permission(_is_private)
PERM_GLOBAL = SUPERUSER


try:
    from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER

    PERM_EDIT |= GROUP_ADMIN | GROUP_OWNER
except ImportError:
    pass


@find_meme_and_handle("禁用表情", permission=PERM_EDIT)
async def _(matcher: Matcher, user_id: str, meme: Meme):
    meme_manager.block(user_id, meme.key)
    await matcher.finish(f"表情 {meme.key} 禁用成功")


@find_meme_and_handle("启用表情", permission=PERM_EDIT)
async def _(matcher: Matcher, user_id: str, meme: Meme):
    meme_manager.unblock(user_id, meme.key)
    await matcher.finish(f"表情 {meme.key} 启用成功")


@find_meme_and_handle("全局禁用表情", permission=PERM_GLOBAL)
async def _(matcher: Matcher, user_id: str, meme: Meme):
    meme_manager.change_mode(MemeMode.WHITE, meme.key)
    await matcher.finish(f"表情 {meme.key} 已设为白名单模式")


@find_meme_and_handle("全局启用表情", permission=PERM_GLOBAL)
async def _(matcher: Matcher, user_id: str, meme: Meme):
    meme_manager.change_mode(MemeMode.BLACK, meme.key)
    await matcher.finish(f"表情 {meme.key} 已设为黑名单模式")
