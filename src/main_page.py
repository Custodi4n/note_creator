import flet as flt
import sqlite3
import calendar
from datetime import datetime
import time
import copy

# Функция для показа экрана основного меню
def main_screen(page: flt.Page):
    page.window_width = 375
    page.window_height = 812
    from note_editor import open_create_note_editor, open_note_editor
    page.padding = flt.Padding(top=36, left=0, right=0, bottom=0)
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
        return flt.ElevatedButton(
            content=flt.Container(
                content=flt.Column([
                    flt.Text(note["title"], size=16, color="#D1D1D1"),
                    flt.Text(note["date"], size=12, opacity=0.5, color="#D1D1D1")
                ]),
                padding=flt.padding.only(top=10, bottom=10),
                alignment=flt.alignment.center_left,
                width=page.width * 0.9,
                border_radius=flt.border_radius.all(5),
                on_click=lambda __, note_id=note["id"]: open_note_editor(page, note_id)
            ),
            height=60,
            width=page.width * 0.9,
            bgcolor="#252525",
            style=flt.ButtonStyle(shape=flt.RoundedRectangleBorder(10))
        )

    notes = get_notes_from_db("")

    note_list = flt.ListView(
        controls=[
            create_note_container(note) for note in notes
        ],
        padding=flt.padding.symmetric(horizontal=10, vertical=20),
        spacing=10,
        height=540,

    )

    date = ""

    # Функция для получения напоминаний с фильтрацией
    def get_filtered_reminders(filter_type):
        now = datetime.now()
        cur_year = now.year
        cur_month = now.month
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        if filter_type == "This month":
            # Напоминания только за текущий месяц
            year_month = f"{cur_month:02d}-{cur_year}"
            cursor.execute('''
                SELECT task_name, reminder_time, reminder_date, id FROM Reminders
                WHERE reminder_date LIKE ?
                ORDER BY reminder_date ASC, reminder_time ASC
            ''', (f'%{year_month}',))
        elif filter_type == "All":
            # Все напоминания
            cursor.execute('''
                SELECT task_name, reminder_time, reminder_date, id FROM Reminders
                ORDER BY reminder_date ASC, reminder_time ASC
            ''')

        reminders = cursor.fetchall()
        conn.close()

        # Группируем напоминания по дате
        grouped_reminders = {}
        for reminder in reminders:
            date = reminder[2]
            if date not in grouped_reminders:
                grouped_reminders[date] = []
            grouped_reminders[date].append({
                "name": reminder[0],
                "time": reminder[1],
                "date": date,
                "id": reminder[3],
            })

        return grouped_reminders

    # Функция для создания списка напоминаний с учётом формата даты
    def create_grouped_reminder_view_with_format(grouped_reminders, filter_type):
        grouped_controls = []

        for date, reminders in grouped_reminders.items():
            # Показываем только день или полную дату
            day_reminder = date if filter_type == "All" else date[:2]

            # Добавляем заголовок дня/даты
            grouped_controls.append(
                flt.Text(value=day_reminder, size=18, weight=flt.FontWeight.BOLD,
                         text_align=flt.TextAlign.CENTER)
            )
            # Добавляем горизонтальную линию
            grouped_controls.append(
                flt.Container(
                    bgcolor="#252525",
                    height=1,
                    width=page.width * 0.9,
                    opacity=0.3
                )
            )
            # Добавляем напоминания
            for reminder in reminders:
                grouped_controls.append(create_reminder_container(reminder))

        return grouped_controls

    # Callback для смены фильтра
    def on_filter_change(e):
        selected_filter = "This month" if e.control.selected_index == 0 else "All"
        update_reminder_list_with_filter(selected_filter)

    # Функция для создания контейнера напоминания
    def create_reminder_container(reminder):
        return flt.Column([
            flt.ElevatedButton(
                content=flt.Container(
                    content=flt.Column([
                        flt.Text(reminder["name"], size=16, color="#D1D1D1"),
                        flt.Text(reminder["time"], size=12, opacity=0.5, color="#D1D1D1")
                    ]),
                    padding=flt.padding.only(top=10, bottom=10),
                    alignment=flt.alignment.center_left,
                    width=page.width * 0.9,
                    border_radius=flt.border_radius.all(5)
                ),
                height=60,
                width=page.width * 0.9,
                bgcolor="#252525",
                style=flt.ButtonStyle(shape=flt.RoundedRectangleBorder(10))
            )
        ])

    # Инициализация BottomSheet
    bottom_date = flt.BottomSheet(
        content=flt.Container(
            padding=flt.padding.only(bottom=20, top=20, left=20, right=20),
            bgcolor="#252525",
            content=flt.CupertinoSlidingSegmentedButton(
                selected_index=0,
                thumb_color="#252525",
                bgcolor="#060606",
                controls=[
                    flt.Text("This month"),
                    flt.Text("All"),
                ],
                on_change=on_filter_change  # Callback при смене фильтра
            ),
            width=page.width
        )
    )
    is_icon_rotated = {"value": False}  # Используем словарь для изменения внутри замыкания
    def toggle_icon_rotation(e):
        # Меняем состояние поворота
        is_icon_rotated["value"] = not is_icon_rotated["value"]

        # Применяем поворот с анимацией
        icon.rotate = flt.transform.Rotate(3.1 if is_icon_rotated["value"] else 0)
        icon.update()  # Обновляем иконку для отображения изменений

    # Контейнер кнопки для открытия BottomSheet
    cont_button = flt.Container(
        content=flt.Text("This month", size=20, color="#D1D1D1"),
        padding=flt.padding.only(left=20),
        on_click=lambda e: (toggle_icon_rotation(e), page.open(bottom_date))
    )
    icon = flt.Icon(name=flt.icons.KEYBOARD_ARROW_DOWN_SHARP, color="#D1D1D1", size=14, rotate=flt.transform.Rotate(0),
                    animate_rotation=flt.animation.Animation(duration=250, curve=flt.animation.AnimationCurve.EASE_IN_OUT))

    reminders_list_filter = flt.Container(
        content=flt.Row(
            controls=[
                cont_button,
                icon
            ],
        ),
        alignment=flt.alignment.center_left,
        padding=flt.padding.only(top=20)
    )

    # Создаём основной список напоминаний
    reminder_list = flt.ListView(
        controls=[],
        padding=flt.padding.symmetric(horizontal=10, vertical=20),
        spacing=10,
        height=220
    )

    add_button = flt.IconButton(
        icon=flt.icons.ADD_CIRCLE_OUTLINE,
        on_click=lambda _: open_create_note_editor(page),
        icon_size=42,
        icon_color="#D1D1D1",
    )


    # def switch_to_calendar_page(e):
    #     nonlocal current_page_index
    #     selected_index = int(e.data)
    #     if selected_index == 1:  # Переход на страницу календаря
    #         current_page_index = 1
    #         build_calendar(current_year, current_month)
    #         page_notes.offset = flt.transform.Offset(-2, 0)  # Смещаем заметки влево
    #         page_calendar.offset = flt.transform.Offset(0, 0)  # Перемещаем календарь на видимое место
    #         page_notes.update()
    #         page_calendar.update()
    #     elif selected_index == 0:  # Переход на страницу заметок
    #         current_page_index = 0
    #         page_notes.offset = flt.transform.Offset(0, 0)  # Перемещаем заметки на видимое место
    #         page_calendar.offset = flt.transform.Offset(2, 0)  # Смещаем календарь вправо (вне видимой области)
    #         page_notes.update()
    #         page_calendar.update()

    def switch_to_page(index):
        build_calendar(current_year, current_month)
        current_page_index = index

        if current_page_index == 0:  # Показать заметки
            page_notes.offset = flt.transform.Offset(0, 0)
            page_calendar.offset = flt.transform.Offset(1, 0)
            page.navigation_bar.selected_index = 1
        elif current_page_index == 1:  # Показать календарь
            page_notes.offset = flt.transform.Offset(-1, 0)
            page_calendar.offset = flt.transform.Offset(0, 0)
            page.navigation_bar.selected_index = 0

        page_notes.update()
        page_calendar.update()

    # def on_swipe(e):
    #     # Обрабатываем свайп влево/вправо
    #     if e.global_x < 150 and page.navigation_bar.selected_index == 0:
    #         switch_to_page(1)
    #         # Если прокрутка идет вправо и мы на странице календаря
    #     elif e.global_x > 150 and page.navigation_bar.selected_index == 1:
    #         switch_to_page(0)

    def on_switch(e):
        build_calendar(current_year, current_month)
        current_page_index = int(e.data)
        if current_page_index == 0:
            switch_to_page(0)
        elif current_page_index == 1:
            switch_to_page(1)

        # Генерируем список значений для часов и минут

    hours = [f" {i:02d}" for i in range(24)]
    minutes = [f" {i:02d}" for i in range(60)]

    # Текущие индексы выбранных значений
    selected_hour_index = 0
    selected_minute_index = 0

    # Функции для обновления центрального значения с учетом "прилипания"
    def update_display():
        hour_label_top.value = hours[(selected_hour_index - 1) % len(hours)]
        hour_label_center.value = hours[selected_hour_index]
        hour_label_bottom.value = hours[(selected_hour_index + 1) % len(hours)]

        minute_label_top.value = minutes[(selected_minute_index - 1) % len(minutes)]
        minute_label_center.value = minutes[selected_minute_index]
        minute_label_bottom.value = minutes[(selected_minute_index + 1) % len(minutes)]

        hour_label_top.update()
        hour_label_center.update()
        hour_label_bottom.update()

        minute_label_top.update()
        minute_label_center.update()
        minute_label_bottom.update()

    # Функции для смены значений часов и минут
    def scroll_hour(delta):
        nonlocal selected_hour_index
        selected_hour_index = (selected_hour_index + delta) % len(hours)
        update_display()

    def scroll_minute(delta):
        nonlocal selected_minute_index
        selected_minute_index = (selected_minute_index + delta) % len(minutes)
        update_display()

    # Создаем текстовые поля для часов
    hour_label_top = flt.Text(hours[selected_hour_index - 1], color="#888888", size=20)
    hour_label_center = flt.Text(hours[selected_hour_index], color="#FFFFFF", size=24)
    hour_label_bottom = flt.Text(hours[(selected_hour_index + 1) % len(hours)], color="#888888", size=20)

    # Создаем текстовые поля для минут
    minute_label_top = flt.Text(minutes[selected_minute_index - 1], color="#888888", size=20)
    minute_label_center = flt.Text(minutes[selected_minute_index], color="#FFFFFF", size=24)
    minute_label_bottom = flt.Text(minutes[(selected_minute_index + 1) % len(minutes)], color="#888888", size=20)

    # Контейнер для отображения списка часов с кнопками для навигации
    hours_column = flt.Column(
        controls=[
            flt.IconButton(icon=flt.icons.ARROW_DROP_UP, on_click=lambda e: scroll_hour(-1), icon_color="#D1D1D1"),
            hour_label_top,
            hour_label_center,
            hour_label_bottom,
            flt.IconButton(icon=flt.icons.ARROW_DROP_DOWN, on_click=lambda e: scroll_hour(1), icon_color="#D1D1D1")
        ],
        alignment=flt.MainAxisAlignment.CENTER
    )

    # Контейнер для отображения списка минут с кнопками для навигации
    minutes_column = flt.Column(
        controls=[
            flt.IconButton(icon=flt.icons.ARROW_DROP_UP, on_click=lambda e: scroll_minute(-1), icon_color="#D1D1D1"),
            minute_label_top,
            minute_label_center,
            minute_label_bottom,
            flt.IconButton(icon=flt.icons.ARROW_DROP_DOWN, on_click=lambda e: scroll_minute(1), icon_color="#D1D1D1")
        ],
        alignment=flt.MainAxisAlignment.CENTER
    )

    # Контейнер для всего компонента выбора времени
    time_picker = flt.Row(
        controls=[hours_column, minutes_column],
        alignment=flt.MainAxisAlignment.CENTER
    )

    cont_time_picker = flt.Container(
        content=time_picker,
        bgcolor="#060606",
        border_radius=flt.border_radius.all(10)
    )
    # date = flt.TextField(
    #     color="#D1D1D1",
    #     border_radius=flt.border_radius.all(10),
    #     text_size=14,
    #     bgcolor="#060606",
    #     border_color="#252525",
    #     cursor_color="#D1D1D1",
    #     read_only=True,
    #     width=100
    # )
    def close_bs(e):
        page.close(bottom_sheet)
        bottom_sheet.update()

    def add_value_to_date(year, month, day):
        nonlocal date
        date = f"{day}-{month}-{year}"

    def save_reminder(e):
        if task_name_field.value != "":
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            cursor.execute('INSERT INTO Reminders (task_name, reminder_date, reminder_time) VALUES (?, ?, ?)',
                           (task_name_field.value,
                            date,
                            button_text.value))
            conn.commit()
            conn.close()
            page.close(bottom_sheet)
            page.update(bottom_sheet)
            update_reminder_list_with_filter("This month")

    def update_reminder_list_with_filter(filter_type):
        grouped_reminders = get_filtered_reminders(filter_type)

        reminder_list.controls = create_grouped_reminder_view_with_format(grouped_reminders, filter_type)
        reminder_list.update()

    save_button = flt.ElevatedButton(width=100, text="Save", color="#D1D1D1", bgcolor="#060606", on_click=save_reminder)
    cancel_button = flt.ElevatedButton(width=100, text="Cancel", color="#D1D1D1", bgcolor="#060606", on_click=close_bs)
    task_name_field = flt.TextField(hint_text="Task name", hint_style=flt.TextStyle(color="#9E9E9E"), color="#D1D1D1",
                                  border_radius=flt.border_radius.all(10), text_size=14, bgcolor="#060606",
                                  border_color="#252525", cursor_color="#D1D1D1")

    timer_picker_value_ref = flt.Ref[flt.Text]()

    def handle_timer_picker_change(e):
        # e.data is the selected time in seconds
        timer_picker_value_ref.current.value = time.strftime("%H:%M", time.gmtime(int(e.data)))
        button_time_picker.update()

    cupertino_timer_picker = flt.CupertinoTimerPicker(
        alignment=flt.alignment.center,
        value=3600,
        second_interval=10,
        minute_interval=1,
        mode=flt.CupertinoTimerPickerMode.HOUR_MINUTE,
        on_change=handle_timer_picker_change,
    )

    button_text = flt.Text(
        ref=timer_picker_value_ref,
        value="00:00",
        size=18,
        width=50,
        height=25,
        color="#D1D1D1",
        text_align=flt.TextAlign.CENTER
    )

    def switch_to_bottom_sheet(e):
        page.close(time_bot_picker)
        page.open(bottom_sheet)

    time_bot_picker = flt.CupertinoBottomSheet(
        content=flt.Container(flt.Column([
                flt.IconButton(icon=flt.icons.CHEVRON_LEFT, icon_size=24,
                               on_click=lambda e: switch_to_bottom_sheet(e)),
                cupertino_timer_picker
                ],
            ),
            bgcolor="#252525",
            height=250,
        ),
        height=216,
    )

    button_time_picker = flt.Container(
        bgcolor="#060606",
        width=100,
        height=40,
        border_radius=flt.border_radius.all(20),
        content=button_text,
        alignment=flt.alignment.center,
        on_click=lambda e: page.open(time_bot_picker)
    )

    bottom_sheet = flt.BottomSheet(
        maintain_bottom_view_insets_padding=True,
        content=flt.Container(
            padding=flt.padding.only(bottom=20, top=20, left=20, right=20),
            bgcolor="#252525",
            content=flt.Column(
                tight=True,
                controls=[
                    flt.Text("Schedule a reminder", size=20),
                    task_name_field,
                    # cont_time_picker,
                    flt.Row(
                        controls=[
                            cancel_button,
                            button_time_picker,
                            # date,
                            save_button,
                        ],
                        alignment=flt.MainAxisAlignment.SPACE_BETWEEN,
                    )
                ],
                horizontal_alignment=flt.CrossAxisAlignment.CENTER
            )
        )
    )

    page.navigation_bar = flt.CupertinoNavigationBar(
        selected_index=0,
        bgcolor="#060606",
        inactive_color="#9E9E9E",
        active_color="#D1D1D1",
        icon_size=32,
        height=60,
        on_change=on_switch,
        destinations=[
            flt.NavigationBarDestination(icon=flt.icons.EVENT_NOTE_OUTLINED),
            flt.NavigationBarDestination(icon=flt.icons.CALENDAR_TODAY_OUTLINED),
        ]
    )
    page.navigation_bar.elevation = 10
    page.navigation_bar.indicator_shape = 10
    page.navigation_bar.shadow_color = "#D1D1D1"

    # bottom_bar = flt.Container(
    #     width=375,
    #     height=50,
    #     content=flt.Image(
    #         src="assets/icons/bottom_bar.png",
    #         fit=flt.ImageFit.COVER
    #     ),
    #     expand=True,
    #     bottom=-20,
    #     left=0,
    #     right=0,
    # )

    # bottom_bar = flt.Container(
    #     bgcolor="#76ABAE",
    #     content=flt.Stack(
    #         controls=[
    #             flt.Image(
    #                 src="assets/icons/bottom_bar.png",
    #                 fit=flt.ImageFit.FIT_WIDTH
    #             ),
    #             flt.Row(
    #                 controls=[
    #                     flt.Image(
    #                         src="assets/icons/layers_button.png"
    #                     ),
    #                     flt.Image(
    #                         src="assets/icons/calendar_button.png"
    #                     )
    #                 ]
    #             ),
    #             flt.Image(
    #                 src="assets/icons/add_circle.png",
    #
    #             )
    #         ],
    #         alignment=flt.alignment.bottom_center
    #     ),
    #     alignment=flt.alignment.bottom_center,
    # )

    # page.navigation_bar = flt.BottomAppBar(
    #     content=flt.Container(
    #         bgcolor="#76ABAE",
    #         content=flt.Stack(
    #             controls=[
    #                 flt.Image(
    #                     src="assets/icons/bottom_bar.png"
    #                 )
    #             ]
    #         ),
    #         expand=True
    #     ),
    # )

    # bottom_panel = flt.Image(
    #     src="assets/icons/sub.png",
    #     fit=flt.ImageFit.FILL,
    #     width=page.width,
    #
    # )

    # bottom_panel = flt.Container(
    #     content=flt.Row(
    #         controls=[
    #             flt.ElevatedButton(text="Button 1", on_click=lambda e: print("Button 1 clicked")),
    #             flt.ElevatedButton(text="Button 2", on_click=lambda e: print("Button 2 clicked")),
    #             flt.ElevatedButton(text="Button 3", on_click=lambda e: print("Button 3 clicked")),
    #         ],
    #         alignment=flt.alignment.bottom_center,
    #         spacing=10
    #     ),
    #     bgcolor="#31363F",  # Цвет панели
    #     padding=flt.padding.all(10),
    #     height=60,  # Высота панели
    #     alignment=flt.alignment.bottom_center
    # )

    # bottom_panel = flt.Container(
    #     content=flt.Row(
    #         controls=[
    #             flt.IconButton(icon=flt.icons.LAYERS_OUTLINED, expand=True),
    #             flt.IconButton(icon=flt.icons.CALENDAR_TODAY_OUTLINED, expand=True)
    #         ],
    #         alignment=flt.alignment.bottom_center
    #     ),
    #     alignment=flt.alignment.bottom_center,
    #     bgcolor="#31363F",
    #     height=50
    # )

    header_cont = flt.Container(
            content=header,
            alignment=flt.alignment.top_center,
            padding=flt.padding.only(left=10),
            height=45,
    )

    add_button_cont = flt.Container(
            content=add_button,
            alignment=flt.alignment.bottom_right,
            padding=flt.padding.only(right=15, bottom=40)
    )

    page_notes = flt.Column(
        controls=[
            header_cont,
            note_list,
            add_button_cont
        ],
        offset=flt.transform.Offset(0, 0),
        animate_offset=flt.animation.Animation(300),
    )

    current_year = datetime.now().year
    current_month = datetime.now().month

    mon = flt.Text("mon", width=40, height=30)
    tue = flt.Text("tue", width=40, height=30)
    wed = flt.Text("wed", width=40, height=30)
    thu = flt.Text("thu", width=40, height=30)
    fri = flt.Text(" fri", width=40, height=30)
    sat = flt.Text("sat", width=40, height=30)
    sun = flt.Text("sun", width=40, height=30)

    day_of_week_row = flt.Row(
        controls=(
            mon,
            tue,
            wed,
            thu,
            fri,
            sat,
            sun
        ),
        alignment=flt.MainAxisAlignment.END,
        spacing=10,
        width=365
    )


    # cont_dow = flt.Container(content=day_of_week_row, alignment=flt.alignment.center, margin=10, width=300)
    def build_calendar(year, month):
        # Очистить текущий контент календаря
        calendar_days.controls.clear()

        # Получить дни месяца
        month_days = calendar.monthcalendar(year, month)

        # Генерация кнопок для дней
        for week in month_days:
            row = flt.Row(controls=[], alignment=flt.MainAxisAlignment.CENTER)
            for day in week:
                if day == 0:
                    row.controls.append(flt.Container(width=40, height=40, bgcolor="#252525", border_radius=20,
                                                      opacity=0.5))  # Пустые дни
                else:
                    # Определение дня недели (0 = Понедельник, 6 = Воскресенье)
                    day_of_week = calendar.weekday(year, month, day)
                    # Помечаем субботу и воскресенье
                    is_weekend = day_of_week in [5, 6]
                    row.controls.append(
                        flt.IconButton(
                            bgcolor=flt.colors.RED if is_weekend else "#252525",  # Красный цвет для выходных
                            content=flt.Text(str(day), color="white"),
                            width=40,
                            height=40,
                            on_click=lambda e, y=year, m=month, d=day: (
                            page.open(bottom_sheet), add_value_to_date(y, m, d)),
                        )
                    )
            calendar_days.controls.append(row)
        calendar_days.update()
        month_label.update()

    def change_month(e):
        nonlocal current_month, current_year
        if e.control.data == "prev":
            current_month -= 1
            if current_month == 0:
                current_month = 12
                current_year -= 1
        elif e.control.data == "next":
            current_month += 1
            if current_month == 13:
                current_month = 1
                current_year += 1
        month_label.value = f"{calendar.month_name[current_month]} {current_year}"
        build_calendar(current_year, current_month)

    # Заголовок с переключателями месяцев
    month_label = flt.Text(f"{calendar.month_name[current_month]} {current_year}", size=20, color="#D1D1D1", width=175,
                           text_align=flt.TextAlign.CENTER)
    calendar_navigation = flt.Row(
        controls=[
            flt.IconButton(flt.icons.CHEVRON_LEFT, on_click=change_month, data="prev", icon_color="#9E9E9E"),
            month_label,
            flt.IconButton(flt.icons.CHEVRON_RIGHT, on_click=change_month, data="next", icon_color="#9E9E9E"),
        ],
        alignment=flt.MainAxisAlignment.CENTER
    )

    # Контейнер для дней календаря
    calendar_days = flt.Column()



    page_calendar = flt.Column(
        controls=[
            calendar_navigation,
            day_of_week_row,
            calendar_days,
            reminders_list_filter,
            reminder_list
        ],
        offset=flt.transform.Offset(1, 0),
        animate_offset=flt.animation.Animation(300),
    )

    # gesture_detector = flt.GestureDetector(
    #     content=flt.Stack([page_notes, page_calendar]),
    #     on_pan_update=on_swipe
    # )

    page.controls.clear()
    page.add(
        flt.Stack([page_notes, page_calendar])
        # gesture_detector
        # bottom_panel
        )
    # page.vertical_alignment = "end"
    # page.padding = 0
    page.update()
    update_reminder_list_with_filter("This month")