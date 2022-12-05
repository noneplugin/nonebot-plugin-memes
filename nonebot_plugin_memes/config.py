from typing import List
from pydantic import BaseModel, Extra

from nonebot import get_driver


class Config(BaseModel, extra=Extra.ignore):
    memes_command_start: List[str] = [""]
    memes_resource_url: str = "https://ghproxy.com/https://raw.githubusercontent.com/noneplugin/nonebot-plugin-memes/v0.3.x/resources"
    memes_disabled_list: List[str] = []


memes_config = Config.parse_obj(get_driver().config.dict())
memes_config.memes_resource_url = memes_config.memes_resource_url.strip("/")
