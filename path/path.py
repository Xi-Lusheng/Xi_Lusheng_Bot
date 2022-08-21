from pathlib import Path

try:
    import ujson as json
except ModuleNotFoundError:
    import json
import os

# 骂人语言路径
scold_data_path = Path() / 'data' / 'scold_data'

# @词库
AnimeThesaurus = json.load(open((Path() / 'data' / 'reply_data' / 'data.json').absolute(), "r", encoding="utf8"))

# 被动词库
Util_Json = json.load(open((Path() / 'data' / 'reply_data' / 'utils_data.json').absolute(), "r", encoding="utf8"))
