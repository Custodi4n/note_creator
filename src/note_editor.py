import flet as flt
import sqlite3
from datetime import datetime
import os

def open_create_note_editor(page):
    page.padding = flt.Padding(top=35, left=10, right=10, bottom=0)
    page.fonts = {
        "Alata": "Alata-Regular.ttf"
    }
    page.theme = flt.Theme(font_family="Alata")

    def update_markdown():
        md.value = content.value
        page.update()

    def preview_mode_change():
        preview.style = flt.ButtonStyle(
            color="#EEEEEE",
            bgcolor="#76ABAE",
            shape=flt.RoundedRectangleBorder(radius=10)
        )
        code.style = flt.ButtonStyle(
            color="#76ABAE",
            bgcolor="#31363F",
            shape=flt.RoundedRectangleBorder(radius=10)
        )
        content.visible = False
        scrollable_markdown.visible = True
        page.update()

    def code_mode_change():
        code.style = flt.ButtonStyle(
            color="#EEEEEE",
            bgcolor="#76ABAE",
            shape=flt.RoundedRectangleBorder(radius=10)
        )
        preview.style = flt.ButtonStyle(
            color="#76ABAE",
            bgcolor="#31363F",
            shape=flt.RoundedRectangleBorder(radius=10)
        )
        scrollable_markdown.visible = False
        content.visible = True
        page.update()

    def file_picker_result(e):
        if e.files:
            file_path = e.files[0].path
            relative_path = os.path.relpath(file_path)
            relative_path = relative_path.replace("\\", "/")
            path_to_image = f"\n![Image]({relative_path})"
            content.value += path_to_image

        page.update()

    def open_file_picker(e):
        file_picker = flt.FilePicker(on_result=file_picker_result)
        page.add(file_picker)
        file_picker.pick_files(allowed_extensions=['png', 'jpg'])

    title = flt.TextField(
            width=300,
            text_size=20,
            border_color="#222831",
            hint_text="Заголовок",
            multiline=True,
            max_lines=2,
            max_length=40,
            counter_style=flt.TextStyle(
                color="#222831"
            )
        )

    content = flt.TextField(
            multiline=True,
            hint_text="Вводить тут",
            width=350,
            height=500,
            on_change=lambda e: update_markdown(),
            text_size=16,
            border_color="#222831",
            visible=True,
        )

    md = flt.Markdown(
        value="",
        selectable=True,
        extension_set=flt.MarkdownExtensionSet.GITHUB_WEB
    )

    scrollable_markdown = flt.Column(
        controls=[
            md
        ],
        width=350,
        height=500,
        scroll=flt.ScrollMode.ALWAYS,
        visible=False
    )

    code = flt.ElevatedButton(
        text="Код",
        style=flt.ButtonStyle(color="#EEEEEE", bgcolor="#76ABAE", shape=flt.RoundedRectangleBorder(radius=10)),
        on_click=lambda e: code_mode_change(),
    )

    preview = flt.ElevatedButton(
        text="Предпросмотр",
        style=flt.ButtonStyle(color="#76ABAE", bgcolor="#31363F", shape=flt.RoundedRectangleBorder(radius=10)),
        on_click=lambda e: preview_mode_change(),
    )

    switch_mode_code = flt.Container(
        content=code,
        bgcolor="#31363F",
        border_radius=flt.border_radius.only(top_left=10, bottom_left=10)
    )

    switch_mode_preview = flt.Container(
        content=preview,
        bgcolor="#31363F",
        border_radius=flt.border_radius.only(top_right=10, bottom_right=10)
    )

    switch_mode = flt.Row(
        controls=[
            switch_mode_code,
            switch_mode_preview
        ],
        spacing=0,
    )

    exit_and_save = flt.Container(
        content=flt.IconButton(
            icon=flt.icons.ARROW_BACK,
            icon_size=32,
            icon_color="#76ABAE",
            on_click=lambda e: save_note_to_db(page, title.value, content.value),
        ),
        alignment=flt.alignment.top_left,
    )

    page.bottom_appbar = flt.BottomAppBar(
        elevation=6,
        shadow_color="#222831",
        bgcolor="#31363F",
        height=70,
        content=flt.Row(
            controls=[
                switch_mode,
                flt.IconButton(
                    icon=flt.icons.IMAGE_OUTLINED,
                    icon_size=30,
                    icon_color="#76ABAE",
                    expand=True,
                    on_click=open_file_picker
                ),
            ],
        )
    )

    page.clean()
    page.add(
        exit_and_save,
        flt.Stack([
            flt.Column([
                title,
                scrollable_markdown,
                content,
                ],
                expand=True
            ),
            ],
        )
    )

def save_note_to_db(page, note_title, note_content):
    from main_page import main_screen
    if note_title != "":
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        created_at = datetime.now()
        created_at = created_at.strftime('%Y-%m-%d')
        updated_at = created_at

        cursor.execute('''
            INSERT INTO Notes (title, content, created_at, updated_at)
            VALUES(?, ?, ?, ?)
        ''', (note_title, note_content, created_at, updated_at))

        conn.commit()
        conn.close()

    main_screen(page)


def resave_note_to_db(page, note_title, note_content, note_id):
    from main_page import main_screen
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE Notes
        SET title = ?, content = ?, updated_at = CURRENT_DATE
        WHERE id = ?
        ''', (note_title, note_content, note_id))

    conn.commit()
    conn.close()

    main_screen(page)

def open_note_editor(page, note_id):
    page.padding = flt.Padding(top=35, left=10, right=10, bottom=0)
    page.fonts = {
        "Alata": "Alata-Regular.ttf"
    }
    page.theme = flt.Theme(font_family="Alata")

    def update_markdown():
        md.value = content.value
        page.update()

    def preview_mode_change():
        update_markdown()
        preview.style = flt.ButtonStyle(
            color="#EEEEEE",
            bgcolor="#76ABAE",
            shape=flt.RoundedRectangleBorder(radius=10)
        )
        code.style = flt.ButtonStyle(
            color="#76ABAE",
            bgcolor="#31363F",
            shape=flt.RoundedRectangleBorder(radius=10)
        )
        content.visible = False
        scrollable_markdown.visible = True
        page.update()

    def code_mode_change():
        code.style = flt.ButtonStyle(
            color="#EEEEEE",
            bgcolor="#76ABAE",
            shape=flt.RoundedRectangleBorder(radius=10)
        )
        preview.style = flt.ButtonStyle(
            color="#76ABAE",
            bgcolor="#31363F",
            shape=flt.RoundedRectangleBorder(radius=10)
        )
        scrollable_markdown.visible = False
        content.visible = True
        page.update()

    title = flt.TextField(
        width=300,
        text_size=30,
        border_color="#222831",
        hint_text="Title",
        multiline=True,
        max_lines=1,
        max_length=30,
        counter_style=flt.TextStyle(
            color="#222831"
        )
    )

    content = flt.TextField(
        multiline=True,
        width=350,
        height=500,
        on_change=lambda e: update_markdown(),
        text_size=16,
        border_color="#222831",
        visible=True,
    )

    def find_note_in_db(note_id):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, content
            FROM Notes 
            WHERE id = ?
            ''', (note_id,))
        note_data = cursor.fetchone()

        if note_data:
            title.value = note_data[0]
            content.value = note_data[1]

        page.update()
        conn.close()

    find_note_in_db(note_id)

    def accept_window():
        acc_window = flt.AlertDialog(
            title=flt.Text("Подтверждение"),
            content=flt.Text("Вы уверены, что хотите продолжить?"),
            actions=[
                flt.ElevatedButton(text="Да", on_click=lambda e: on_yes_click()),
                flt.ElevatedButton(text="Отмена", on_click=lambda e: on_no_click())
            ],
            actions_alignment=flt.alignment.bottom_center
        )
        page.dialog = acc_window
        acc_window.open = True
        page.update()

    def on_yes_click():
        from main_page import main_screen
        page.dialog.open = False
        page.update()
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute('''
                DELETE FROM Notes WHERE id = ?
            ''', (note_id,))
        conn.commit()
        conn.close()

        main_screen(page)

    def on_no_click():
        page.dialog.open = False
        page.update()

    def file_picker_result(e):
        if e.files:
            file_path = e.files[0].path
            relative_path = os.path.relpath(file_path)
            relative_path = relative_path.replace("\\", "/")
            path_to_image = f"\n![Image]({relative_path})"
            content.value += path_to_image

        page.update()

    def open_file_picker(e):
        file_picker = flt.FilePicker(on_result=file_picker_result)
        page.add(file_picker)
        file_picker.pick_files(allowed_extensions=['png', 'jpg'])

    md = flt.Markdown(
        value="",
        selectable=True,
        extension_set=flt.MarkdownExtensionSet.GITHUB_WEB
    )

    scrollable_markdown = flt.Column(
        controls=[
            md
        ],
        width=350,
        height=500,
        scroll=flt.ScrollMode.ALWAYS,
        visible=False
    )

    code = flt.ElevatedButton(
        text="Код",
        style=flt.ButtonStyle(color="#EEEEEE", bgcolor="#76ABAE", shape=flt.RoundedRectangleBorder(radius=10)),
        on_click=lambda e: code_mode_change(),
    )

    preview = flt.ElevatedButton(
        text="Предпросмотр",
        style=flt.ButtonStyle(color="#76ABAE", bgcolor="#31363F", shape=flt.RoundedRectangleBorder(radius=10)),
        on_click=lambda e: preview_mode_change(),
    )

    switch_mode_code = flt.Container(
        content=code,
        bgcolor="#31363F",
        border_radius=flt.border_radius.only(top_left=10, bottom_left=10)
    )

    switch_mode_preview = flt.Container(
        content=preview,
        bgcolor="#31363F",
        border_radius=flt.border_radius.only(top_right=10, bottom_right=10)
    )

    switch_mode = flt.Row(
        controls=[
            switch_mode_code,
            switch_mode_preview
        ],
        spacing=0,
    )

    exit_and_save = flt.Container(
        content=flt.IconButton(
            icon=flt.icons.ARROW_BACK,
            icon_size=32,
            icon_color="#76ABAE",
            on_click=lambda e: resave_note_to_db(page, title.value, content.value, note_id),
        ),
        alignment=flt.alignment.top_left,
    )

    share = flt.Container(
        content=flt.IconButton(
            icon=flt.icons.SHARE_OUTLINED,
            icon_size=32,
            icon_color="#76ABAE",
        ),
        alignment=flt.alignment.top_right,
    )

    delete = flt.Container(
        content=flt.IconButton(
            icon=flt.icons.DELETE_OUTLINE,
            icon_size=32,
            icon_color="#76ABAE",
            on_click=lambda e: accept_window(),
        ),
        alignment=flt.alignment.top_right,
    )

    header = flt.Container(
        content=flt.Row(
           controls=[
               exit_and_save,
               flt.Row(
                   controls=[
                       share,
                       delete
                   ],
               ),
           ],
           alignment=flt.MainAxisAlignment.SPACE_BETWEEN,
        ),
    )

    page.bottom_appbar = flt.BottomAppBar(
        elevation=6,
        shadow_color="#222831",
        bgcolor="#31363F",
        height=70,
        content=flt.Row(
            controls=[
                switch_mode,
                flt.IconButton(
                    icon=flt.icons.IMAGE_OUTLINED,
                    icon_size=30,
                    icon_color="#76ABAE",
                    expand=True,
                    on_click=open_file_picker
                ),
            ]
        )
    )

    page.clean()
    page.add(
        header,
        flt.Stack([
        flt.Column([
            title,
            scrollable_markdown,
            content,
            ],
            expand=True
        ),
            ],
        ),
    )