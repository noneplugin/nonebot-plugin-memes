import re
from typing import List, Optional, Tuple

from nonebot import get_driver
from nonebot.adapters import Event, Message, MessageSegment
from nonebot.params import Command, CommandArg
from nonebot.rule import TRIE_VALUE, Rule, TrieRule
from nonebot.typing import T_State

from .config import memes_config
from .depends import MSG_KEY, TEXTS_KEY

command_start = memes_config.memes_command_start or list(
    get_driver().config.command_start
)


def command_rule(commands: List[str]) -> Rule:
    for command in commands:
        for start in command_start:
            TrieRule.add_prefix(f"{start}{command}", TRIE_VALUE(start, (command,)))

    def checker(
        state: T_State,
        cmd: Optional[Tuple[str, ...]] = Command(),
        msg: Message = CommandArg(),
    ) -> bool:
        if cmd and cmd[0] in commands:
            state[MSG_KEY] = msg
            return True
        return False

    return Rule(checker)


def regex_rule(patterns: List[str]) -> Rule:
    start = "|".join(command_start)
    pattern = "|".join([rf"(?:{p})" for p in patterns])

    def checker(event: Event, state: T_State) -> bool:
        if not (msg := event.get_message()):
            return False
        msg_seg: MessageSegment = msg[0]
        if not msg_seg.is_text():
            return False

        seg_text = str(msg_seg).lstrip()
        matched = re.match(rf"(?:{start}){pattern}", seg_text, re.IGNORECASE)
        if not matched:
            return False

        msg.pop(0)
        new_msg = msg.__class__(seg_text[matched.end() :].lstrip())
        for new_seg in reversed(new_msg):
            msg.insert(0, new_seg)
        state[MSG_KEY] = msg
        state[TEXTS_KEY] = list(matched.groups())
        return True

    return Rule(checker)
