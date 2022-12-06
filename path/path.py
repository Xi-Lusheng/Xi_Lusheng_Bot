from pathlib import Path
try:
    import ujson as json
except ModuleNotFoundError:
    import json

# 语音路径
scold_data_path = Path() / 'data' / 'scold_data'

# 钉宫语音路径
ding_gong_path = Path() / 'data' / 'scold_data' / 'ding_gong'

# 动漫语音路径
comic_voice_path = Path() / 'data' / 'scold_data' / 'comic_voice'

# 表情包路径
emo_data_path = Path() / 'data' / 'emo_data'

# @对话词库
AnimeThesaurus = json.load(open((Path() / 'data' / 'reply_data' / 'data.json').absolute(), "r", encoding="utf8"))

# 被动词库
Util_Json = json.load(open((Path() / 'data' / 'reply_data' / 'utils_data.json').absolute(), "r", encoding="utf8"))
