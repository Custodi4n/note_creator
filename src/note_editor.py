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

    def switch_mode_change(e):
        selected_index = int(e.data)
        if selected_index == 0:
            cont_scroll_md.visible = False
            cont_content.visible = True
            page.update()
        if selected_index == 1:
            cont_content.visible = False
            cont_scroll_md.visible = True
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
        file_picker.pick_files(allowed_extensions=['png', 'jpg', 'gif', 'mp4'])

    title = flt.TextField(
            width=350,
            height=79,
            text_size=20,
            border_color="#252525",
            bgcolor="#252525",
            hint_text="Title",
            hint_style=flt.TextStyle(color="#9E9E9E"),
            color="#D1D1D1",
            max_length=30,
            border_radius=flt.border_radius.all(10),
            counter_style=flt.TextStyle(
                color="#060606"
            ),
            cursor_color="#D1D1D1"
        )

    content = flt.TextField(
            multiline=True,
            hint_text="Code",
            hint_style=flt.TextStyle(color="#9E9E9E"),
            width=350,
            color="#D1D1D1",
            height=500,
            border_radius=flt.border_radius.all(10),
            on_change=lambda e: update_markdown(),
            text_size=16,
            bgcolor="#252525",
            border_color="#252525",
            cursor_color="#D1D1D1",
        )

    cont_content = flt.Container(
        content=content,
        width=350,
        height=500,
        bgcolor="#252525",
        border_radius=flt.border_radius.all(10),
        visible=True
    )

    md = flt.Markdown(
        value="",
        selectable=True,
        extension_set=flt.MarkdownExtensionSet.GITHUB_WEB,
        code_theme=flt.MarkdownCodeTheme.A11Y_DARK,
    )

    scrollable_markdown = flt.Column(
        controls=[
            md
        ],
        width=300,
        height=450,

        scroll=flt.ScrollMode.ALWAYS,
    )
    cont_scroll_md = flt.Container(
        content=scrollable_markdown,
        width=350,
        height=500,
        bgcolor="#252525",
        border_radius=flt.border_radius.all(10),
        visible=False,
        padding=flt.padding.all(10)
    )

    exit_and_save = flt.Container(
        content=flt.IconButton(
            icon=flt.icons.ARROW_BACK,
            icon_size=32,
            icon_color="#9E9E9E",
            on_click=lambda e: save_note_to_db(page, title.value, content.value),
        ),
        alignment=flt.alignment.top_left,
    )
    paste_image = flt.Container(
        content=flt.IconButton(
            icon=flt.icons.IMAGE_OUTLINED,
            icon_size=32,
            icon_color="#9E9E9E",
            on_click=lambda e: open_file_picker(e)
        )
    )
    header = flt.Row(
        controls=[
            exit_and_save,
            paste_image
        ],
        alignment=flt.MainAxisAlignment.SPACE_BETWEEN
    )

    switch_mode = flt.CupertinoSegmentedButton(
        selected_index=0,
        selected_color="#D1D1D1",
        unselected_color="#060606",
        border_color="#9E9E9E",
        on_change=lambda e: switch_mode_change(e),
        width=200,
        controls=[
            flt.Text("Code"),
            flt.Text("Preview"),
        ]
    )

    page.navigation_bar = flt.BottomAppBar(
        elevation=6,
        shadow_color="#D1D1D1",
        bgcolor="#060606",
        height=60,
        content=flt.Row(
            controls=[
                switch_mode,
            ],
            alignment=flt.MainAxisAlignment.CENTER
        )
    )

    page.clean()
    page.add(
        header,
        flt.Stack([
            flt.Column([
                title,
                cont_scroll_md,
                cont_content,
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

    def switch_mode_change(e):
        update_markdown()
        selected_index = int(e.data)
        if selected_index == 0:
            cont_scroll_md.visible = False
            cont_content.visible = True
            page.update()
        if selected_index == 1:
            cont_content.visible = False
            cont_scroll_md.visible = True
            page.update()

    title = flt.TextField(
        width=350,
        height=79,
        text_size=20,
        border_color="#252525",
        bgcolor="#252525",
        hint_text="Title",
        hint_style=flt.TextStyle(color="#9E9E9E"),
        color="#D1D1D1",
        max_length=30,
        border_radius=flt.border_radius.all(10),
        counter_style=flt.TextStyle(
            color="#060606"
        ),
        cursor_color="#D1D1D1"
    )

    content = flt.TextField(
        multiline=True,
        hint_text="Code",
        hint_style=flt.TextStyle(color="#9E9E9E"),
        width=350,
        color="#D1D1D1",
        height=500,
        border_radius=flt.border_radius.all(10),
        on_change=lambda e: update_markdown(),
        text_size=16,
        bgcolor="#252525",
        border_color="#252525",
        cursor_color="#D1D1D1",
    )

    cont_content = flt.Container(
        content=content,
        width=350,
        height=500,
        bgcolor="#252525",
        border_radius=flt.border_radius.all(10),
        visible=True
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
            bgcolor="#252525",
            title=flt.Text("Confirmation"),
            content=flt.Text("Are you sure you want to continue?"),
            actions=[
                flt.ElevatedButton(text="Yes", color="#D1D1D1", bgcolor="#060606", on_click=lambda e: on_yes_click()),
                flt.ElevatedButton(text="Cancel", color="#D1D1D1", bgcolor="#060606", on_click=lambda e: on_no_click())
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
        file_picker.pick_files(allowed_extensions=['png', 'jpg', 'gif', 'mp4'])

    md = flt.Markdown(
        value="",
        selectable=True,
        extension_set=flt.MarkdownExtensionSet.GITHUB_WEB,
        code_theme=flt.MarkdownCodeTheme.A11Y_DARK
    )

    scrollable_markdown = flt.Column(
        controls=[
            md
        ],
        width=350,
        height=500,
        scroll=flt.ScrollMode.ALWAYS,
    )

    cont_scroll_md = flt.Container(
        content=scrollable_markdown,
        width=350,
        height=500,
        bgcolor="#252525",
        border_radius=flt.border_radius.all(10),
        visible=False,
        padding=flt.padding.all(10)
    )

    exit_and_save = flt.Container(
        content=flt.IconButton(
            icon=flt.icons.ARROW_BACK,
            icon_size=32,
            icon_color="#9E9E9E",
            on_click=lambda e: resave_note_to_db(page, title.value, content.value, note_id),
        ),
        alignment=flt.alignment.top_left,
    )

    delete = flt.Container(
        content=flt.IconButton(
            icon=flt.icons.DELETE_OUTLINE,
            icon_size=32,
            icon_color="#9E9E9E",
            on_click=lambda e: accept_window(),
        ),
        alignment=flt.alignment.top_right,
    )

    paste_image = flt.Container(
        content=flt.IconButton(
            icon=flt.icons.IMAGE_OUTLINED,
            icon_size=32,
            icon_color="#9E9E9E",
            on_click=lambda e: open_file_picker(e)
        )
    )

    header = flt.Container(
        content=flt.Row(
           controls=[
               exit_and_save,
               flt.Row(
                   controls=[
                       paste_image,
                       delete
                   ],
               ),
           ],
           alignment=flt.MainAxisAlignment.SPACE_BETWEEN,
        ),
    )

    switch_mode = flt.CupertinoSegmentedButton(
        selected_index=0,
        selected_color="#D1D1D1",
        unselected_color="#060606",
        border_color="#9E9E9E",
        on_change=lambda e: switch_mode_change(e),
        width=200,
        controls=[
            flt.Text("Code"),
            flt.Text("Preview"),
        ]
    )

    page.navigation_bar = flt.BottomAppBar(
        elevation=6,
        shadow_color="#D1D1D1",
        bgcolor="#060606",
        height=60,
        content=flt.Row(
            controls=[
                switch_mode,
            ],
            alignment=flt.MainAxisAlignment.CENTER
        )
    )

    page.clean()
    page.add(
        header,
        flt.Stack([
        flt.Column([
            title,
            cont_scroll_md,
            cont_content,
            ],
            expand=True
        ),
            ],
        ),
    )