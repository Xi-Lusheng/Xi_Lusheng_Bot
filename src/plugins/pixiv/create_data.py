import pathlib
import os


def create_file():
    pathlib.Path('data').mkdir(parents=True, exist_ok=True)
    pathlib.Path('data/pixiv_data/image').mkdir(parents=True, exist_ok=True)
    pathlib.Path('data/pixiv_data/image_r18').mkdir(parents=True, exist_ok=True)
    # if not os.path.exists('data/pixiv_data/out.png'):





