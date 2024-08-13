from typing import Annotated

from meme_generator import Meme
from nonebot.adapters import Event
from nonebot.matcher import Matcher
from nonebot_plugin_session import SessionId, SessionIdType
from nonebot_plugin_waiter import waiter

from ..manager import meme_manager

UserId = Annotated[str, SessionId(SessionIdType.GROUP, include_bot_type=False)]


async def find_meme(matcher: Matcher, meme_name: str) -> Meme:
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
        return found_memes[0]

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
            return found_memes[index - 1]

    await matcher.finish()
