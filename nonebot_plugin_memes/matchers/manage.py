from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER, Permission
from nonebot_plugin_alconna import Alconna, Args, on_alconna
from nonebot_plugin_session import EventSession, SessionLevel

from ..manager import MemeMode, meme_manager
from .utils import UserId, find_meme


def _is_private(session: EventSession) -> bool:
    return session.level == SessionLevel.LEVEL1


PERM_EDIT = SUPERUSER | Permission(_is_private)
PERM_GLOBAL = SUPERUSER


try:
    from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER

    PERM_EDIT |= GROUP_ADMIN | GROUP_OWNER
except ImportError:
    pass


block_matcher = on_alconna(
    Alconna("禁用表情", Args["meme_name", str]),
    block=True,
    priority=11,
    use_cmd_start=True,
    permission=PERM_EDIT,
)
unblock_matcher = on_alconna(
    Alconna("启用表情", Args["meme_name", str]),
    block=True,
    priority=11,
    use_cmd_start=True,
    permission=PERM_EDIT,
)
block_gl_matcher = on_alconna(
    Alconna("全局禁用表情", Args["meme_name", str]),
    block=True,
    priority=11,
    use_cmd_start=True,
    permission=PERM_GLOBAL,
)
unblock_gl_matcher = on_alconna(
    Alconna("全局启用表情", Args["meme_name", str]),
    block=True,
    priority=11,
    use_cmd_start=True,
    permission=PERM_GLOBAL,
)


@block_matcher.handle()
async def _(matcher: Matcher, user_id: UserId, meme_name: str):
    meme = await find_meme(matcher, meme_name)
    meme_manager.block(user_id, meme.key)
    await matcher.finish(f"表情 {meme.key} 禁用成功")


@unblock_matcher.handle()
async def _(matcher: Matcher, user_id: UserId, meme_name: str):
    meme = await find_meme(matcher, meme_name)
    meme_manager.unblock(user_id, meme.key)
    await matcher.finish(f"表情 {meme.key} 启用成功")


@block_gl_matcher.handle()
async def _(matcher: Matcher, meme_name: str):
    meme = await find_meme(matcher, meme_name)
    meme_manager.change_mode(MemeMode.WHITE, meme.key)
    await matcher.finish(f"表情 {meme.key} 已设为白名单模式")


@unblock_gl_matcher.handle()
async def _(matcher: Matcher, meme_name: str):
    meme = await find_meme(matcher, meme_name)
    meme_manager.change_mode(MemeMode.BLACK, meme.key)
    await matcher.finish(f"表情 {meme.key} 已设为黑名单模式")
