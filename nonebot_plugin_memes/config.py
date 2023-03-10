from typing import List

from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    memes_command_start: List[str] = []
    memes_disabled_list: List[str] = []
    memes_check_resources_on_startup: bool = True


memes_config = Config.parse_obj(get_driver().config.dict())
