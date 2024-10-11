import flet as flt
from main_page import main_screen
from create_db import create_database
def main(page: flt.Page):
    create_database()
    main_screen(page)

flt.app(target=main, name="note_creator", assets_dir="assets")