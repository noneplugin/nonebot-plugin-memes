<div align="center">

  <a href="https://v2.nonebot.dev/">
    <img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot">
  </a>

# nonebot-plugin-memes

_✨ [Nonebot2](https://github.com/nonebot/nonebot2) 表情包制作插件 ✨_

<p align="center">
  <img src="https://img.shields.io/github/license/noneplugin/nonebot-plugin-memes" alt="license">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/nonebot-2.0.0rc1+-red.svg" alt="NoneBot">
  <a href="https://pypi.org/project/nonebot-plugin-memes">
    <img src="https://badgen.net/pypi/v/nonebot-plugin-memes" alt="pypi">
  </a>
  <a href="https://jq.qq.com/?_wv=1027&k=wDVNrMdr">
    <img src="https://img.shields.io/badge/QQ%E7%BE%A4-682145034-orange" alt="qq group">
  </a>
</p>

</div>


### 安装

- 使用 nb-cli

```
nb plugin install nonebot_plugin_memes
```

- 使用 pip

```
pip install nonebot_plugin_memes
```


### 配置项

> 以下配置项可在 `.env.*` 文件中设置，具体参考 [NoneBot 配置方式](https://v2.nonebot.dev/docs/tutorial/configuration#%E9%85%8D%E7%BD%AE%E6%96%B9%E5%BC%8F)

#### `memes_command_start`
 - 类型：`List[str]`
 - 默认：`[""]`
 - 说明：命令起始标记，默认包含空字符串

#### `memes_disabled_list`
 - 类型：`List[str]`
 - 默认：`[]`
 - 说明：禁用的表情包列表，需填写表情的`key`，可在 [meme-generator 表情列表](https://github.com/MeetWq/meme-generator/blob/main/docs/memes.md) 中查看。若只是临时关闭，可以用下文中的“表情包开关”

#### `memes_check_resources_on_startup`
 - 类型：`bool`
 - 默认：`True`
 - 说明：是否在启动时检查 `meme-generator` 资源


### 使用

**以下命令需要加[命令前缀](https://v2.nonebot.dev/docs/api/config#Config-command_start) (默认为`/`)，可自行设置为空**



#### 表情包开关

群主 / 管理员 / 超级用户 可以启用或禁用某些表情包

发送 `启用表情/禁用表情 [表情名/表情关键词]`，如：`禁用表情 摸`

超级用户 可以设置某个表情包的管控模式（黑名单/白名单）

发送 `全局启用表情 [表情名/表情关键词]` 可将表情设为黑名单模式；

发送 `全局禁用表情 [表情名/表情关键词]` 可将表情设为白名单模式；


### 特别感谢

- [Ailitonia/omega-miya](https://github.com/Ailitonia/omega-miya) 基于nonebot2的qq机器人

- [HibiKier/zhenxun_bot](https://github.com/HibiKier/zhenxun_bot) 基于 Nonebot2 和 go-cqhttp 开发，以 postgresql 作为数据库，非常可爱的绪山真寻bot

- [kexue-z/nonebot-plugin-nokia](https://github.com/kexue-z/nonebot-plugin-nokia) 诺基亚手机图生成
