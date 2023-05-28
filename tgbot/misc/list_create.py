from openpyxl import Workbook
from openpyxl.styles import Font
import os


async def create_excel(ticket_list, period):
    wb = Workbook()
    ws = wb.active
    ws.append(
        (
            'Номер',
            'Дата-время',
            'ID пользователя',
            'Username пользователя',
            "Ветка",
            'ФИО пользователя',
            'Телефон',
            'Метод телефона',
            'Уровень 1',
            'Уровень 2',
            'Обращение',
            'Кол-во медиа'
        )
    )
    ft = Font(bold=True)
    for row in ws['A1:T1']:
        for cell in row:
            cell.font = ft

    for ticket in ticket_list:
        create_datetime = ticket["create_timestamp"].strftime("%d.%m.%Y %H:%M")
        username = f"@{ticket['username']}" if ticket["username"] else "---"
        branch = ticket['branch'] if ticket["branch"] else "---"
        full_name = ticket['full_name'] if ticket["full_name"] else "---"
        phone_number = ticket['phone_number'] if ticket["phone_number"] else "---"
        phone_method = ticket['phone_method'] if ticket["phone_method"] else "---"
        level_1 = ticket['level_1'] if ticket["level_1"] else "---"
        ws.append(
            (
                ticket['id'],
                create_datetime,
                ticket['user_id'],
                username,
                branch,
                full_name,
                phone_number,
                phone_method,
                level_1,
                ticket['level_2'],
                ticket['petition'],
                len(ticket['media'])
            )
        )

    wb.save(f'{os.getcwd()}/{period}_tickets.xlsx')
