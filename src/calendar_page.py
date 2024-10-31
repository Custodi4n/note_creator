import flet as flt
import calendar
from datetime import datetime
import copy
# from calendar_custom import CustomCalendar
def calendar_screen(page):
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
                    row.controls.append(flt.Container(width=40, height=40, bgcolor="#252525", border_radius=20, opacity=0.5))  # Пустые дни
                else:
                    # Определение дня недели (0 = Понедельник, 6 = Воскресенье)
                    day_of_week = calendar.weekday(year, month, day)

                    # Помечаем субботу и воскресенье
                    is_weekend = day_of_week in [5, 6]
                    row.controls.append(
                        flt.IconButton(
                            # icon=ft.icons.STAR_BORDER if day == 15 else None,  # Пример со звездочкой на 15 число
                            # icon_color="black" if day == 15 else None,
                            bgcolor=flt.colors.RED if is_weekend else "#252525",  # Красный цвет для выходных
                            content=flt.Text(str(day), color="white"),
                            width=40,
                            height=40,
                            on_click=lambda e, d=day: select_day(d),
                        )
                    )
            calendar_days.controls.append(row)
        page.update()

    def select_day(day):
        selected_day.value = f"Selected day: {day}"
        page.update()

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
    month_label = flt.Text(f"{calendar.month_name[current_month]} {current_year}", size=20, color="#D1D1D1", width=175, text_align=flt.TextAlign.CENTER)
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
    # Вывод выбранного дня
    selected_day = flt.Text()

    # my_calendar2 = CustomCalendar(width=250,
    #                               bgcolor="#282c35",
    #                               hover_color="#34d409",
    #                               font_color="#ffffff",
    #                               font_color_accent="#000000",
    #                               accent_color="#f9c629",
    #                               header_font_color="#ffffff")

    def switch_to_main_page(e):
        from main_page import main_screen
        selected_index = int(e.data)
        if selected_index == 0:
            page.clean()
            main_screen(page)

    page.navigation_bar = flt.CupertinoNavigationBar(
        selected_index=1,
        bgcolor="#060606",
        inactive_color="#9E9E9E",
        active_color="#D1D1D1",
        icon_size=32,
        height=60,
        on_change=lambda e: switch_to_main_page(e),
        destinations=[
            flt.NavigationBarDestination(icon=flt.icons.EVENT_NOTE_OUTLINED),
            flt.NavigationBarDestination(icon=flt.icons.CALENDAR_TODAY_OUTLINED),
        ]
    )
    page.navigation_bar.elevation = 10
    page.navigation_bar.indicator_shape = 10
    page.navigation_bar.shadow_color = "#D1D1D1"

    page.add(calendar_navigation, day_of_week_row, calendar_days, selected_day)
    # page.add(my_calendar2)

    # Инициализация календаря
    build_calendar(current_year, current_month)

    page.update()