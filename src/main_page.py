import flet as flt
import sqlite3

# Функция для показа экрана основного меню
def main_screen(page: flt.Page):
    # page.window_width = 375
    # page.window_height = 812
    from note_editor import open_create_note_editor, open_note_editor
    page.padding = flt.Padding(top=35, left=10, right=10, bottom=0)
    page.bgcolor="#222831"
    page.fonts = {
        "Alata": "Alata-Regular.ttf"
    }
    page.theme = flt.Theme(font_family="Alata")

    def on_search_change(e):
        keyword = e.control.value
        notes = get_notes_from_db(keyword)
        update_note_list(notes)

    def update_note_list(notes):
        note_list.controls.clear()
        note_list.controls.extend([create_note_container(note) for note in notes])

        page.update()

    search_field = flt.TextField(
        prefix_icon=flt.icons.SEARCH,
        border_radius=flt.border_radius.all(30),
        text_size=16,
        color="#76ABAE",
        cursor_color="#76ABAE",
        focused_border_color="#76ABAE",
        content_padding=5,
        on_change=on_search_change
    )

    search_bar = flt.Container(
        content=search_field,
        border_radius=flt.border_radius.all(30),
        width=280,
        height=45,
        bgcolor="#EEEEEE",
    )

    parameters = flt.IconButton(
        icon=flt.icons.MORE_VERT,
        icon_size=32,
        icon_color="#76ABAE",
    )

    header = flt.Row(
        controls=[
            search_bar,
            parameters,
        ],
        spacing=10,
    )

    def get_notes_from_db(keyword):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        if keyword == "":
            cursor.execute("SELECT id, title, updated_at FROM Notes")
        else:
            cursor.execute('''
                SELECT id, title, updated_at FROM Notes
                WHERE title LIKE ?
            ''', (f'%{keyword}%',))

        notes = cursor.fetchall()
        conn.close()
        return [{"id": note[0], "title": note[1], "date": note[2]} for note in notes]

    def create_note_container(note):
        return flt.Container(
            content=flt.Column([
                flt.Text(note["title"], size=16),
                flt.Text(note["date"], size=12, opacity=0.5)
            ]),
            padding=flt.padding.all(10),
            alignment=flt.alignment.center_left,
            bgcolor="#31363F",
            border_radius=flt.border_radius.all(10),
            height=60,
            width=page.width * 0.9,
            on_click=lambda __, note_id=note["id"]: open_note_editor(page, note_id)
        )

    notes = get_notes_from_db("")

    note_list = flt.ListView(
        controls=[
            create_note_container(note) for note in notes
        ],
        padding=flt.padding.symmetric(horizontal=10, vertical=20),
        spacing=10,
        height=550

    )

    add_button = flt.IconButton(
        icon=flt.icons.ADD_CIRCLE_OUTLINE,
        on_click=lambda _: open_create_note_editor(page),
        icon_size=48,
        icon_color="#76ABAE",
    )

    page.bottom_appbar = flt.BottomAppBar(
        elevation=6,
        shadow_color="#222831",
        bgcolor="#31363F",
        height=70,
        content=flt.Row(
            controls=[
                flt.Container(
                    content=flt.IconButton(
                        icon=flt.icons.LAYERS_OUTLINED,
                        icon_color="#76ABAE",
                        icon_size=30,
                        on_click=lambda e: print("Notes button clicked"),
                    ),
                    bgcolor="#31363F",
                    expand=True,
                    height=100
                ),
                flt.Container(
                    content=flt.IconButton(
                        icon=flt.icons.CALENDAR_TODAY_OUTLINED,
                        icon_color="#76ABAE",
                        icon_size=30,
                        on_click=lambda e: print("Calendar button clicked"),
                        opacity=0.5,
                    ),
                    bgcolor="#31363F",
                    expand=True,
                    height=100
                )
            ],
        )
    )

    page.controls.clear()
    page.add(
        flt.Container(
            content=header,
            alignment=flt.alignment.top_center,
        ),
        note_list,
        flt.Container(
            content=add_button,
            alignment=flt.alignment.bottom_right,
        ),
    )
    page.update()