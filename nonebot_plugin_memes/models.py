from io import BytesIO
from dataclasses import dataclass
from typing import List, Tuple, Union, Protocol


class Func(Protocol):
    async def __call__(self, texts: List[str]) -> Union[str, BytesIO]:
        ...


@dataclass
class NormalMeme:
    keywords: Tuple[str, ...]
    thumbnail: str
    func: Func

    def __post_init__(self):
        self.arg_num = 1


@dataclass
class MultiArgMeme(NormalMeme):
    examples: Tuple[str, ...]

    def __post_init__(self):
        self.arg_num = len(self.examples)
