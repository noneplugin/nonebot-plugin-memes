from collections.abc import Awaitable
from typing import Annotated, Callable, Optional

from meme_generator import Meme
from nonebot.adapters import Event
from nonebot.matcher import Matcher
from nonebot.permission import Permission
from nonebot_plugin_alconna import Alconna, Args, on_alconna
from nonebot_plugin_session import SessionId, SessionIdType
from nonebot_plugin_waiter import waiter

from ..manager import meme_manager

UserId = Annotated[str, SessionId(SessionIdType.GROUP, include_bot_type=False)]


def find_meme_and_handle(
    command: str,
    *,
    aliases: Optional[set[str]] = None,
    permission: Optional[Permission] = None,
):
    def wrapper(func: Callable[[Matcher, str, Meme], Awaitable[None]]):
        find_matcher = on_alconna(
            Alconna(command, Args["meme_name", str]),
            aliases=aliases,
            block=True,
            priority=11,
            use_cmd_start=True,
            permission=permission,
        )

        @find_matcher.handle()
        async def _(matcher: Matcher, user_id: UserId, meme_name: str):
            found_memes = meme_manager.find(meme_name)
            found_num = len(found_memes)

            if found_num == 0:
                if searched_memes := meme_manager.search(meme_name, limit=5):
                    await matcher.finish(
                        f"表情 {meme_name} 不存在，你可能在找：\n"
                        + "\n".join(
                            f"* {meme.key} ({'/'.join(meme.keywords)})"
                            for meme in searched_memes
                        )
                    )
                else:
                    await matcher.finish(f"表情 {meme_name} 不存在！")

            if found_num == 1:
                await func(matcher, user_id, found_memes[0])

            await matcher.send(
                f"找到 {found_num} 个表情，请发送编号选择：\n"
                + "\n".join(
                    f"{i + 1}. {meme.key} ({'/'.join(meme.keywords)})"
                    for i, meme in enumerate(found_memes)
                )
            )

            @waiter(waits=["message"], keep_session=True)
            async def get_response(event: Event):
                return event.get_plaintext()

            for _ in range(3):
                resp = await get_response.wait(timeout=15)
                if resp is None:
                    await matcher.finish()
                elif not resp.isdigit():
                    await matcher.send("输入错误，请输入数字")
                    continue
                elif not (1 <= (index := int(resp)) <= found_num):
                    await matcher.send("输入错误，请输入正确的数字")
                    continue
                else:
                    await func(matcher, user_id, found_memes[index - 1])

    return wrapper
