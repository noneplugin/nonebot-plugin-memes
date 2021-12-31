import httpx
from pathlib import Path
from nonebot.log import logger
from aiocache import cached


data_path = Path() / 'data' / 'memes'


class DownloadError(Exception):
    pass


async def download(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                resp = await client.get(url, timeout=10)
                if resp.status_code != 200:
                    continue
                return resp.content
            except Exception as e:
                logger.warning(f'Error downloading {url}, retry {i}/3: {e}')
    raise DownloadError


async def get_resource(path: str, name: str) -> bytes:
    dir_path = data_path / path
    file_path = dir_path / name

    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)

    if not file_path.exists():
        url = f'https://cdn.jsdelivr.net/gh/MeetWq/nonebot-plugin-memes@main/resources/{path}/{name}'
        data = await download(url)
        if data:
            with file_path.open('wb') as f:
                f.write(data)
    if not file_path.exists():
        raise DownloadError
    return file_path.read_bytes()


@cached(ttl=600)
async def get_image(name: str) -> bytes:
    return await get_resource('images', name)


@cached(ttl=600)
async def get_font(name: str) -> bytes:
    return await get_resource('fonts', name)
