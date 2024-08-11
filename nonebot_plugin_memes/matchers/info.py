from arclet.alconna import TextFormatter
from meme_generator import Meme
from nonebot.matcher import Matcher
from nonebot.utils import run_sync
from nonebot_plugin_alconna import Image, Text

from .utils import find_meme_and_handle


@find_meme_and_handle("表情详情", aliases={"表情帮助", "表情示例"})
async def _(matcher: Matcher, user_id: str, meme: Meme):
    keywords = "、".join([f'"{keyword}"' for keyword in meme.keywords])
    shortcuts = "、".join(
        [f'"{shortcut.humanized or shortcut.key}"' for shortcut in meme.shortcuts]
    )
    tags = "、".join([f'"{tag}"' for tag in meme.tags])

    image_num = f"{meme.params_type.min_images}"
    if meme.params_type.max_images > meme.params_type.min_images:
        image_num += f" ~ {meme.params_type.max_images}"

    text_num = f"{meme.params_type.min_texts}"
    if meme.params_type.max_texts > meme.params_type.min_texts:
        text_num += f" ~ {meme.params_type.max_texts}"

    default_texts = ", ".join([f'"{text}"' for text in meme.params_type.default_texts])

    args_info = ""
    if args_type := meme.params_type.args_type:
        formater = TextFormatter()
        for option in args_type.parser_options:
            opt = option.option()
            alias_text = (
                " ".join(opt.requires)
                + (" " if opt.requires else "")
                + "│".join(sorted(opt.aliases, key=len))
            )
            args_info += (
                f"\n  * {alias_text}{opt.separators[0]}"
                f"{formater.parameters(opt.args)} {opt.help_text}"
            )

    info = (
        f"表情名：{meme.key}"
        + f"\n关键词：{keywords}"
        + (f"\n快捷指令：{shortcuts}" if shortcuts else "")
        + (f"\n标签：{tags}" if tags else "")
        + f"\n需要图片数目：{image_num}"
        + f"\n需要文字数目：{text_num}"
        + (f"\n默认文字：[{default_texts}]" if default_texts else "")
        + (f"\n可选参数：{args_info}" if args_info else "")
    )
    info += "\n表情预览：\n"
    img = await run_sync(meme.generate_preview)()
    await (Text(info) + Image(raw=img)).finish()
