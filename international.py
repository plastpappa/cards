import pathlib as path

ASSETS_DIR = path.Path().joinpath('assets').resolve()
FONT_DIR   = ASSETS_DIR.joinpath('font')
IMG_DIR    = ASSETS_DIR.joinpath('img')
