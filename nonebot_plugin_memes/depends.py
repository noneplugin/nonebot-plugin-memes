from typing import List

from meme_generator.meme import Meme
from nonebot.adapters import Bot, Event, Message
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot_plugin_alconna import At, Image, Text, UniMessage, image_fetch
from nonebot_plugin_alconna.uniseg.segment import reply_handle
from nonebot_plugin_userinfo import ImageSource, UserInfo, get_user_info

from .config import memes_config
from .utils import split_text

MSG_KEY = "MSG"
TEXTS_KEY = "TEXTS"
USER_INFOS_KEY = "USER_INFOS"
IMAGE_SOURCES_KEY = "IMAGE_SOURCES"


class AlcImage(ImageSource):
    bot: Bot
    event: Event
    state: T_State
    img: Image

    class Config:
        arbitrary_types_allowed: bool = True

    async def get_image(self) -> bytes:
        result = await image_fetch(self.event, self.bot, self.state, self.img)
        if isinstance(result, bytes):
            return result
        raise NotImplementedError("image fetch not implemented")


def split_msg(meme: Meme):
    async def dependency(bot: Bot, event: Event, state: T_State):
        texts: List[str] = []
        user_infos: List[UserInfo] = []
        image_sources: List[ImageSource] = []

        msg: Message = state[MSG_KEY]
        uni_msg = UniMessage()
        if msg:
            uni_msg = await UniMessage.generate(message=msg)
        uni_msg_with_reply = UniMessage()
        if reply := await reply_handle(event, bot):
            if isinstance(reply.msg, Message) and reply.msg:
                uni_msg_with_reply = await UniMessage.generate(message=reply.msg)
        uni_msg_with_reply.extend(uni_msg)

        for msg_seg in uni_msg_with_reply:
            if isinstance(msg_seg, At):
                if user_info := await get_user_info(bot, event, msg_seg.target):
                    if image_source := user_info.user_avatar:
                        image_sources.append(image_source)
                    user_infos.append(user_info)

            elif isinstance(msg_seg, Image):
                image_sources.append(
                    AlcImage(bot=bot, event=event, state=state, img=msg_seg)
                )

            elif isinstance(msg_seg, Text):
                raw_text = msg_seg.text
                for text in split_text(raw_text):
                    if text.startswith("@") and (user_id := text[1:]):
                        if user_info := await get_user_info(bot, event, user_id):
                            if image_source := user_info.user_avatar:
                                image_sources.append(image_source)
                            user_infos.append(user_info)

                    elif text == "自己":
                        if user_info := await get_user_info(
                            bot, event, event.get_user_id()
                        ):
                            if image_source := user_info.user_avatar:
                                image_sources.append(image_source)
                            user_infos.append(user_info)

                    elif text:
                        texts.append(text)

        # 当所需图片数为 2 且已指定图片数为 1 时，使用 发送者的头像 作为第一张图
        if meme.params_type.min_images == 2 and len(image_sources) == 1:
            if user_info := await get_user_info(bot, event, event.get_user_id()):
                if image_source := user_info.user_avatar:
                    image_sources.insert(0, image_source)
                user_infos.insert(0, user_info)

        # 当所需图片数为 1 且没有已指定图片时，使用发送者的头像
        if memes_config.memes_use_sender_when_no_image and (
            meme.params_type.min_images == 1 and len(image_sources) == 0
        ):
            if user_info := await get_user_info(bot, event, event.get_user_id()):
                if image_source := user_info.user_avatar:
                    image_sources.append(image_source)
                user_infos.append(user_info)

        # 当所需文字数 >0 且没有输入文字时，使用默认文字
        texts = state.get(TEXTS_KEY, []) + texts
        if memes_config.memes_use_default_when_no_text and (
            meme.params_type.min_texts > 0 and len(texts) == 0
        ):
            texts = meme.params_type.default_texts

        state[TEXTS_KEY] = texts
        state[USER_INFOS_KEY] = user_infos
        state[IMAGE_SOURCES_KEY] = image_sources

    return Depends(dependency)
