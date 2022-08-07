from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    appid: str = ""
    salt: str = ""
    key: str = ""
