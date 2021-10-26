import base64
import math
from datetime import date

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, \
    KeyboardButton

from Database.dbConnection import SQLither
from config import dbName
from handlers.keyboards.inline.callbackDatas import direction_callback, request_save_callback, deadline_year_callback, \
    deadline_month_callback, page_changer_callback, page_num_callback, user_order_callback, confirm_deletion_callback, \
    user_request_callback, confirm_deletion_request_callback, set_user_order_callback, edition_choice_callback, \
    get_user_order_callback, search_type_callback, review_callback, insert_review_callback

db_conn = SQLither(dbName)

choiceDirection = InlineKeyboardMarkup(row_width=2)

freelanceDirect = InlineKeyboardButton(text="Фрилансер", callback_data=direction_callback.new(
    direction_name="freelance", template_text="фрилансера"
))
choiceDirection.insert(freelanceDirect)

orderDirect = InlineKeyboardButton(text="Заказчик", callback_data=direction_callback.new(
    direction_name="order", template_text="заказчика"
))
choiceDirection.insert(orderDirect)


def reviewButtonCreator(review_id):
    review_inline = InlineKeyboardMarkup(row_width=1)
    review_inline.insert(
        InlineKeyboardButton(text="Оставить отзыв", callback_data=review_callback.new(
            review_id=review_id
        ))
    )
    return review_inline


choice_search_type_buttons = InlineKeyboardMarkup(row_width=1)
choice_search_type_buttons.insert(
    InlineKeyboardButton(text="Рекомендации", callback_data=search_type_callback.new(
        search_name="Recommendation"
    ))
)
choice_search_type_buttons.insert(
    InlineKeyboardButton(text="Искать по ключевым словам", callback_data=search_type_callback.new(
        search_name="By_Keyword"
    ))
)

choice_request_save = InlineKeyboardMarkup(row_width=2)
choice_request_save.insert(InlineKeyboardButton(text="Да", callback_data=request_save_callback.new(
    user_answer="Yes"
)))
choice_request_save.insert(InlineKeyboardButton(text="Нет", callback_data=request_save_callback.new(
    user_answer="No"
)))
reply_keyboards = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
reply_keyboards.insert(
    KeyboardButton(text="/setuser")
)
reply_keyboards.insert(
    KeyboardButton(text="/deleteorder")
)
reply_keyboards.insert(
    KeyboardButton(text="/deleterequest")
)
reply_keyboards.insert(
    KeyboardButton(text="/editorder")
)
reply_keyboards.insert(
    KeyboardButton(text="/myorders")
)
cancel_reply_keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
cancel_reply_keyboard.insert(
    KeyboardButton(text="Отмена")
)
payment_reply_keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
payment_reply_keyboard.insert(
    KeyboardButton(text="Договорная")
)
payment_reply_keyboard.insert(
    KeyboardButton(text="Отмена")
)
choice_year_of_deadline = InlineKeyboardMarkup(row_width=2)
choice_year_of_deadline.insert(
    InlineKeyboardButton(text=f"{date.today().year}", callback_data=deadline_year_callback.new(
        year_value=f"{date.today().year}"
    )))
choice_year_of_deadline.insert(
    InlineKeyboardButton(text=f"{date.today().year + 1}", callback_data=deadline_year_callback.new(
        year_value=f"{date.today().year + 1}"
    )))

choice_month_current_year_deadline = InlineKeyboardMarkup(row_width=2)
for i in range(date.today().month, 13):
    choice_month_current_year_deadline.insert(
        InlineKeyboardButton(text=f"{i}", callback_data=deadline_month_callback.new(
            month_value=f"{i}"
        )))

choice_month_of_next_year_deadline = InlineKeyboardMarkup(row_width=3)
for i in range(1, 13):
    choice_month_of_next_year_deadline.insert(
        InlineKeyboardButton(text=f"{i}", callback_data=deadline_month_callback.new(
            month_value=f"{i}"
        )))


def create_change_page_buttons(key_wrd, current_page):
    choices_change_page = InlineKeyboardMarkup(row_width=5)
    if key_wrd != "rec_all_order":
        order_num = db_conn.select_order_count(key_wrd)[0]
    else:
        order_num = len(db_conn.select_orders_for_rec())
    start_page = 1
    last_page = math.ceil(order_num / 2)
    btn_previous = InlineKeyboardButton(text="prev", callback_data=page_changer_callback.new(
        change_status="previous", current_page=f"{current_page}"
    ))
    current_page_button = InlineKeyboardButton(text=f"{current_page + 1}", callback_data=page_num_callback.new(
        page_status="current"
    ))
    start_page_button = InlineKeyboardButton(text=f"{start_page}", callback_data=page_num_callback.new(
        page_status="start"
    ))
    last_page_button = InlineKeyboardButton(text=f"{last_page}", callback_data=page_num_callback.new(
        page_status="last"
    ))
    btn_next = InlineKeyboardButton(text="next", callback_data=page_changer_callback.new(
        change_status="next", current_page=f"{current_page}"
    ))
    review_btn = InlineKeyboardButton(text="Оставить отклик", callback_data=insert_review_callback.new())
    choices_change_page.insert(start_page_button)
    choices_change_page.insert(btn_previous)
    choices_change_page.insert(current_page_button)
    choices_change_page.insert(btn_next)
    choices_change_page.insert(last_page_button)
    choices_change_page.insert(review_btn)
    return choices_change_page


def create_user_order_buttons(user_orders, action_name):
    choice_user_order = InlineKeyboardMarkup()
    if len(user_orders) < 5:
        choice_user_order.row_width = 1
    else:
        choice_user_order.row_width = 2

    if action_name == "delete_order":
        callback_name = user_order_callback
    elif action_name == "edit_order":
        callback_name = set_user_order_callback
    else:
        callback_name = get_user_order_callback
    for user_order in user_orders:
        if len(str(user_order[1])) > 15 and len(user_orders) >= 5:
            choice_user_order.insert(
                InlineKeyboardButton(text=f"{str(user_order[1])[0:15]}", callback_data=callback_name.new(
                    order_id=f"{user_order[0]}"
                ))
            )
        elif len(str(user_order[1])) > 30 and len(user_orders) >= 5:
            choice_user_order.insert(
                InlineKeyboardButton(text=f"{str(user_order[1])[0:30]}", callback_data=callback_name.new(
                    order_id=f"{user_order[0]}"
                ))
            )
        else:
            choice_user_order.insert(
                InlineKeyboardButton(text=f"{str(user_order[1])}", callback_data=callback_name.new(
                    order_id=f"{user_order[0]}"
                ))
            )
    return choice_user_order


def create_confirm_deletion_buttons(order_id):
    choice_confirm_deletion = InlineKeyboardMarkup(row_width=2)
    choice_confirm_deletion.insert(
        InlineKeyboardButton(text="Да, я уверен(-а)", callback_data=confirm_deletion_callback.new(
            confirm_answer=f"{order_id}"
        ))
    )
    choice_confirm_deletion.insert(
        InlineKeyboardButton(text="Отмена", callback_data=confirm_deletion_callback.new(
            confirm_answer=f"cancel"
        ))
    )
    return choice_confirm_deletion


def create_user_request_buttons(user_requests):
    choice_user_request = InlineKeyboardMarkup(row_width=2)

    for user_request in user_requests:
        choice_user_request.insert(
            InlineKeyboardButton(text=f"{user_request[2]}", callback_data=user_request_callback.new(
                request_id=f"{user_request[0]}", request_name=f"{user_request[2]}"
            ))
        )
    return choice_user_request


def create_confirm_user_request_buttons(request_id):
    choice_confirm_user_request = InlineKeyboardMarkup(row_width=2)
    choice_confirm_user_request.insert(
        InlineKeyboardButton(text="Да, я уверен(-а)", callback_data=confirm_deletion_request_callback.new(
            confirm_answer_of_request=f"{request_id}"
        ))
    )

    choice_confirm_user_request.insert(
        InlineKeyboardButton(text="Отмена", callback_data=confirm_deletion_request_callback.new(
            confirm_answer_of_request="cancel"
        )))

    return choice_confirm_user_request


def create_order_edit_choice(order_id):
    choice_order_edit = InlineKeyboardMarkup(row_width=2)
    edit_order_buttons = [
        ["Зоголовок", "Title"],
        ["Описание", "Description"],
        ["Дата сдачи работы", "Dead_date"],
        ["Время сдачи работы", "Dead_time"],
        ["Оплата", "Payment"]
    ]
    for edit_order_button in edit_order_buttons:
        choice_order_edit.insert(
            InlineKeyboardButton(text=f"{edit_order_button[0]}", callback_data=edition_choice_callback.new(
                edit_name=f"{edit_order_button[1]}", order_id=f"{order_id}"
            ))
        )
    return choice_order_edit
