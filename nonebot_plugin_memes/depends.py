import re
import shlex
from typing import List, Optional

from nonebot.rule import Rule
from nonebot.typing import T_State
from nonebot.params import Depends
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent, unescape

from .config import memes_config

ARG_KEY = "ARG"
ARGS_KEY = "ARGS"
REGEX_DICT = "REGEX_DICT"
REGEX_GROUP = "REGEX_GROUP"
REGEX_ARG = "REGEX_ARG"

command_start = "|".join(memes_config.memes_command_start)


def regex(pattern: str) -> Rule:
    def checker(event: MessageEvent, state: T_State) -> bool:
        msg = event.get_message()
        msg_seg: MessageSegment = msg[0]
        if not msg_seg.is_text():
            return False

        seg_text = str(msg_seg).lstrip()
        matched = re.match(
            rf"(?:{command_start})(?:{pattern})", seg_text, re.IGNORECASE | re.S
        )
        if not matched:
            return False

        new_msg = msg.copy()
        seg_text = seg_text[matched.end() :].lstrip()
        if seg_text:
            new_msg[0].data["text"] = seg_text
        else:
            new_msg.pop(0)
        state[REGEX_DICT] = matched.groupdict()
        state[REGEX_GROUP] = matched.groups()
        state[REGEX_ARG] = new_msg

        msg_text = new_msg.extract_plain_text()
        state[ARG_KEY] = unescape(msg_text).strip()
        args: List[str] = []
        try:
            texts = shlex.split(msg_text)
        except:
            texts = msg_text.split()
        for text in texts:
            text = unescape(text).strip()
            if text:
                args.append(text)
        state[ARGS_KEY] = args

        return True

    return Rule(checker)


def Args(num: Optional[int] = None, prompt: bool = False):
    async def dependency(matcher: Matcher, state: T_State):
        args: List[str] = state[ARGS_KEY]
        if num is not None and len(args) != num:
            if prompt and args:
                await matcher.finish(f"该表情需要{num}段文字")
            return
        return args

    return Depends(dependency)


def RegexArg(key: str):
    async def dependency(state: T_State):
        args: dict = state[REGEX_DICT]
        return args.get(key, None)

    return Depends(dependency)


def RegexArgs(num: Optional[int] = None):
    async def dependency(state: T_State):
        args: List[str] = list(state[REGEX_GROUP])
        if num is not None and len(args) != num:
            return
        return args

    return Depends(dependency)


def Arg():
    async def dependency(state: T_State):
        arg: str = state[ARG_KEY]
        if arg:
            return arg

    return Depends(dependency)


def NoArg():
    async def dependency(args: List[str] = Args(0)):
        return

    return Depends(dependency)
