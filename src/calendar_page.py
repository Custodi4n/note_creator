import flet as flt
import calendar
from datetime import datetime

def calendar_screen(page):
    current_year = datetime.now().year
    current_month = datetime.now().month

    def build_calendar(year, month):
        calendar_days.controls.clear()

        month_days = calendar.monthcalendar(year, month)

        for week in month_days:
            row = flt.Row(controls=[], alignment=flt.MainAxisAlignment.CENTER)
            for day in week:
                if day == 0:
                    row.controls.append(flt.Container(width=40, height=40))
                else:
                    day_of_week = calendar.weekday(year, month, day)

                    is_weekend = day_of_week in [5, 6]
                    row.controls.append(
                        flt.IconButton(
                            bgcolor=flt.colors.RED if is_weekend else "#252525",
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

    month_label = flt.Text(f"{calendar.month_name[current_month]} {current_year}", size=20, color="#D1D1D1", width=175, text_align=flt.TextAlign.CENTER)
    calendar_navigation = flt.Row(
        controls=[
            flt.IconButton(flt.icons.CHEVRON_LEFT, on_click=change_month, data="prev", icon_color="#9E9E9E"),
            month_label,
            flt.IconButton(flt.icons.CHEVRON_RIGHT, on_click=change_month, data="next", icon_color="#9E9E9E"),
        ],
        alignment=flt.MainAxisAlignment.CENTER
    )

    calendar_days = flt.Column()
    selected_day = flt.Text()

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

    page.add(calendar_navigation, calendar_days, selected_day)

    build_calendar(current_year, current_month)

    page.update()