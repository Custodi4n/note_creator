import flet as flt
import sqlite3

def main_screen(page: flt.Page):
    from note_editor import open_create_note_editor, open_note_editor
    page.padding = flt.Padding(top=35, left=0, right=0, bottom=0)
    page.bgcolor = "#060606"
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
        bgcolor="#060606",
        text_size=16,
        color="#D1D1D1",
        cursor_color="#D1D1D1",
        border_color="#9E9E9E",
        focused_bgcolor="#252525",
        focused_border_color="#D1D1D1",
        content_padding=5,
        on_change=on_search_change
    )

    search_bar = flt.Container(
        content=search_field,
        border_radius=flt.border_radius.all(30),
        width=280,
        height=45,
        bgcolor=None,
    )

    parameters = flt.IconButton(
        icon=flt.icons.MORE_VERT,
        icon_size=32,
        icon_color="#D1D1D1",
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
                flt.Text(note["title"], size=16, color="#D1D1D1"),
                flt.Text(note["date"], size=12, opacity=0.5, color="#D1D1D1")
            ]),
            padding=flt.padding.all(10),
            alignment=flt.alignment.center_left,
            bgcolor="#252525",
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
        height=550,

    )

    add_button = flt.IconButton(
        icon=flt.icons.ADD_CIRCLE_OUTLINE,
        on_click=lambda _: open_create_note_editor(page),
        icon_size=42,
        icon_color="#D1D1D1",
    )

    def switch_to_calendar_page(e):
        from calendar_page import calendar_screen
        selected_index = int(e.data)
        if selected_index == 1:
            page.clean()
            calendar_screen(page)

    page.navigation_bar = flt.CupertinoNavigationBar(
        selected_index=0,
        bgcolor="#060606",
        inactive_color="#9E9E9E",
        active_color="#D1D1D1",
        icon_size=32,
        height=60,
        on_change=lambda e: switch_to_calendar_page(e),
        destinations=[
            flt.NavigationBarDestination(icon=flt.icons.EVENT_NOTE_OUTLINED),
            flt.NavigationBarDestination(icon=flt.icons.CALENDAR_TODAY_OUTLINED),
        ]
    )
    page.navigation_bar.elevation = 10
    page.navigation_bar.indicator_shape = 10
    page.navigation_bar.shadow_color = "#D1D1D1"

    page.controls.clear()
    page.add(
        flt.Container(
            content=header,
            alignment=flt.alignment.top_center,
            padding=flt.padding.only(left=10),
            height=45,
        ),
        note_list,
        flt.Container(
            content=add_button,
            alignment=flt.alignment.bottom_right,
            padding=flt.padding.only(right=15, bottom=40)
            ),
        )
    page.update()