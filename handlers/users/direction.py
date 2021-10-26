import base64
import logging
import math
from datetime import date, timedelta

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery

from config import dbName, admin_id
from handlers.Encode.IdGenerator import encrypt_val
from handlers.keyboards.inline.choiseButtons import choiceDirection, reply_keyboards, choice_request_save, \
    choice_month_current_year_deadline, choice_month_of_next_year_deadline, \
    create_change_page_buttons, create_user_order_buttons, create_confirm_deletion_buttons, create_user_request_buttons, \
    create_confirm_user_request_buttons, create_order_edit_choice, \
    choice_year_of_deadline, choice_search_type_buttons, cancel_reply_keyboard, reviewButtonCreator, \
    payment_reply_keyboard

from Database.dbConnection import SQLither
from loader import dp, bot
from aiogram.dispatcher.filters.state import State, StatesGroup

db = SQLither(dbName)


class Form(StatesGroup):
    userDirection = State()
    title = State()
    description = State()
    payment = State()
    dead_year = State()
    dead_month = State()
    dead_day = State()
    dead_time = State()
    key_wrd = State()
    current_page = State()
    action_name = State()
    order_id = State()
    some_id = State()
    review_id = State()
    review_text = State()


def message_generator(orders):
    msg_results = []
    msg = ""

    for order in orders:
        deadline_time = str(order[5]).split(":")
        pay_tag = "kzt"
        if order[3] == "Договорная":
            pay_tag = ""
        info_text = f"{str(order[6])}||{str(order[0])}"
        msg_results.append(f"\n\n \U0001F468\U0000200D\U0001F4BB <strong>{order[1].upper()}</strong>"
                           f"\n\n<b><i>Описание заказа:</i></b> \n <i>{order[2]}</i> "
                           f"\n\n Дата сдачи работы: <code>{order[4]}</code>"
                           f"\n Время сдачи работы: <code>{deadline_time[0]}:{deadline_time[1]}</code>"
                           f"\n Оплата за заказ: <code>{order[3]} {pay_tag}</code>"
                           f"\n\n Отклик Id: /{str(encrypt_val(info_text))}\n"
                           )

    for result in msg_results:
        msg += result
    return msg


def message_generator_for_fetchone(order):
    pay_tag = "kzt"
    if order[3] == "Договорная":
        pay_tag = ""

    deadline_time = str(order[5]).split(":")
    msg = f"\n\n<b>{str(order[1]).upper()}</b> " \
          f"\n\n<b><i>Описание заказа:</i></b> \n <i>{order[2]}</i> " \
          f"\n\n Дата сдачи работы: <code>{order[4]}</code>" \
          f"\n Время сдачи работы: <code>{deadline_time[0]}:{deadline_time[1]}</code>" \
          f"\n Оплата за заказ: <code>{order[3]} {pay_tag}</code>\n\n"

    return msg


def user_order_temp_creator(order_id):
    order_temp = db.select_order_by_id(order_id)
    pay_tag = "kzt"
    if order_temp[3] == "Договорная":
        pay_tag = ""
    deadline_time = str(order_temp[5]).split(":")
    msg = f"\n\n<b>{str(order_temp[1]).upper()}</b>" \
          f"\n\n<b><i>Описание заказа:</i></b> \n <i>{str(order_temp[2])[0:150]}...</i>" \
          f"\n Дата сдачи работы: <code>{order_temp[4]}</code>" \
          f"\n Время сдачи работы: <code>{deadline_time[0]}:{deadline_time[1]}</code>" \
          f"\n Оплата за заказ: <code>{order_temp[3]} {pay_tag}</code>\n\n"

    return msg


@dp.message_handler(Command(["start", "setuser"]))
async def show_directions(message: Message, state: FSMContext):
    try:
        await state.reset_state(True)
        db.create_order_table()
        db.create_request_table()
        db.create_review_table()
        if message.text == "/start":
            await message.answer(
                text=f"\U0001F44B Привет, я фриланс бот, я помогу вам найти исполнителя для вашей работы, а также, дам возможность выполнять работы тех, кто нуждается в помощи.\n\n<b>Для этого сначала выбери свой путь:</b>",
                reply_markup=choiceDirection)
        else:
            await message.answer(text="Какой путь хотите выбрать:", reply_markup=choiceDirection)
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.message_handler(Command("showreq"))
async def showRequests(message: Message):
    try:
        if message.chat.id == admin_id:
            requests = db.select_all_request()
            if len(requests) != 0:
                for req in requests:
                    await message.answer(text=f"\n{req}")
            else:
                await message.answer(text="Empty")
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.message_handler(Command("showorder"))
async def showOrders(message: Message):
    try:
        if message.chat.id == admin_id:
            db.cur.execute("Select * from orders")
            orders = db.cur.fetchall()
            if len(orders) != 0:
                for order in orders:
                    await message.answer(text=f"\n{order}")
            else:
                await message.answer(text="Empty")
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.message_handler(Command('delorderbyid'))
async def setOrderId(message: Message):
    try:
        if message.chat.id == admin_id:
            await Form.order_id.set()
            await message.answer(text="Id order:")
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.message_handler(state=Form.order_id)
async def deleteOrder(message: Message, state: FSMContext):
    try:
        if message.chat.id == admin_id:
            db.delete_user_order(message.text)
            await message.answer("Deleted!!!")
            await state.finish()
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.message_handler(Command(["deleteorder", "editorder", "myorders"]))
async def select_orders_list_to_delete(message: Message, state: FSMContext):
    try:
        await state.reset_state(True)
        if message.text == "/deleteorder":
            action_text = "Какой заказ вы хотите удалить?"
            action_name = "delete_order"
        elif message.text == "/editorder":
            action_text = "Какой заказ вы хотите редактировать?"
            action_name = "edit_order"
        else:
            action_text = "Выберите заказ, который вы хотите просмотреть. \n Ваши заказы:"
            action_name = "get_order"
        user_orders = db.select_user_order(message.chat.id)
        if len(user_orders) > 0:
            await message.answer(text=f"{action_text}",
                                 reply_markup=create_user_order_buttons(user_orders, action_name))
        else:
            await message.answer(text="В данный момент у вас нет никаких заказов!!!")
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.callback_query_handler(text_contains="get_order_of_user")
async def get_user_order_by_id(call: CallbackQuery):
    try:
        await call.answer(cache_time=60)
        order_id = int(call.data.split(":")[1])
        order = db.select_order_by_id(order_id)
        await call.message.delete()
        await call.message.answer(text=f"{message_generator_for_fetchone(order)}", reply_markup=reply_keyboards)
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.callback_query_handler(text_contains="call_user_orders")
async def confirm_deletion_of_order(call: CallbackQuery):
    try:
        await call.answer(cache_time=60)
        order_id = int(call.data.split(":")[1])
        await call.message.edit_text(text=f"Вы выбрали:{user_order_temp_creator(order_id)} \n\n <b>Вы уверены?</b>")
        await call.message.edit_reply_markup(reply_markup=create_confirm_deletion_buttons(order_id))
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.callback_query_handler(text_contains="confirm_deletion")
async def delete_order(call: CallbackQuery):
    try:
        await call.answer(cache_time=60)
        answer = call.data.split(":")[1]
        if answer == "cancel":
            await call.message.delete()
            await call.message.answer(text=f"Удаление заказа отменилось.\n Что я ещё могу для вас сделать?")
        else:
            db.cur.execute(f"Delete from reviews where order_id = '{int(answer)}'")
            db.conn.commit()
            db.delete_user_order(int(answer))
            await call.message.delete()
            await call.message.answer(text=f"Ваш заказ успешно удален.\n Что я еще могу для вас сделать?")
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.callback_query_handler(text_contains="set_user_order")
async def show_set_order_choice(call: CallbackQuery):
    try:
        await call.answer(cache_time=60)
        await call.message.delete()
        order_id = call.data.split(":")[1]
        await call.message.answer(
            text=f"Вы выбрали: \n {user_order_temp_creator(order_id)}\n\n Что вы хотите изменить в этом заказе?",
            reply_markup=create_order_edit_choice(order_id))
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.callback_query_handler(text_contains="edit_order")
async def edit_order(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer(cache_time=60)
        call_data = call.data.split(":")
        act = call_data[1]
        await call.message.edit_reply_markup(reply_markup=None)
        async with state.proxy() as data:
            data['action_name'] = "Update"
            data['order_id'] = call_data[2]
        if act == "Title":
            await Form.title.set()
            await call.message.answer(text="Напишите новый зоголовок для заказа:", reply_markup=cancel_reply_keyboard)
        elif act == "Description":
            await Form.description.set()
            await call.message.answer(text="Напишите новое описание для заказа:", reply_markup=cancel_reply_keyboard)
        elif act == "Dead_date":
            await call.message.answer(text="Укажите новую дату сдачи работы:", reply_markup=choice_year_of_deadline)
        elif act == "Dead_time":
            await Form.dead_time.set()
            await call.message.answer(text="Укажите новое время сдачи работы:", reply_markup=cancel_reply_keyboard)
        elif act == "Payment":
            await Form.payment.set()
            await call.message.answer(text="Напишите новую цену для оплаты заказа:",
                                      reply_markup=payment_reply_keyboard)
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.message_handler(Command("deleterequest"))
async def select_user_request(message: Message):
    try:
        requests = db.select_request_by_chat_id(message.chat.id)
        if len(requests) > 0:
            await message.answer(text="Какой запрос вы хотите удалить:",
                                 reply_markup=create_user_request_buttons(requests))
        else:
            await message.answer(text="У вас нет никаких запросов!")
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.callback_query_handler(text_contains="call_user_requests")
async def confirm_deletion_of_request(call: CallbackQuery):
    try:
        await call.answer(cache_time=60)
        call_data = call.data.split(":")
        await call.message.edit_text(text=f"Вы выбрали {call_data[2]}. \n Вы уверены?")
        await call.message.edit_reply_markup(reply_markup=create_confirm_user_request_buttons(int(call_data[1])))
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.callback_query_handler(text_contains="confirm_request_deletion")
async def delete_user_request(call: CallbackQuery):
    try:
        await call.answer(cache_time=60)
        call_answer = call.data.split(":")[1]
        if call_answer == "cancel":
            await call.message.delete()
            await call.message.answer(text=f"Удаление запроса отменено.\n Что я еще могу для вас сделать?")
        else:
            db.deletion_request_by_id(int(call_answer))
            await call.message.delete()
            await call.message.answer(text="Ваш запрос успешно удален.\n Что я еще могу для вас сделать?")
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.callback_query_handler(text_contains="direction")
async def direct_to_freelance(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer(cache_time=60)
        await call.message.edit_reply_markup(reply_markup=None)
        callback_data = call.data
        logging.info(f"call = {callback_data}")
        async with state.proxy() as data:
            data['userDirection'] = callback_data.split(":")[1]

            if data['userDirection'] == "order":
                user_orders = db.select_user_order(call.message.chat.id)
                if len(user_orders) <= 7:
                    data['action_name'] = "Insert"
                    await Form.title.set()
                    await call.message.answer(
                        text="Если хотите отменить заказ, нажмите 'Отмена'. \n\n<b>Напишите краткий зоговолок к заказу:</b>",
                        reply_markup=cancel_reply_keyboard)
                else:
                    await call.message.answer(text="Количество ваших заказов достигло максимума, удалите лишнее:",
                                              reply_markup=create_user_order_buttons(user_orders, "delete_order"))
            else:
                await call.message.answer(text="Выберите способ поиска:", reply_markup=choice_search_type_buttons)
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.callback_query_handler(text_contains="search_type")
async def search_by_choosing_method(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer(cache_time=60)
        search = call.data.split(":")[1]
        if search == "Recommendation":
            async with state.proxy() as data:
                data['key_wrd'] = "rec_all_order"
                data['current_page'] = 0
                await state.finish()
                orders = db.get_order_by_limit(0, 2)
                if len(orders) != 0:
                    await call.message.delete()
                    await call.message.answer(text=f"{message_generator(orders)}",
                                              reply_markup=create_change_page_buttons(data['key_wrd'],
                                                                                      data['current_page']))
                else:
                    await call.message.answer(text=f"Пока нет никаких заказов!!!")

        else:
            async with state.proxy() as data:
                data["current_page"] = 0
                await state.finish()
                await Form.key_wrd.set()
                await call.message.answer(
                    text=f"Для поиска, напишите ключевые слова к заказу (Например: 'java'):")
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.message_handler(state=Form.key_wrd)
async def search_by_keyword(message: Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['key_wrd'] = message.text
            await state.finish()
            db.delete_order_over_deadline()
            start_num = int(data['current_page']) * 2
            orders = db.select_order(str(data['key_wrd']).lower(), start_num)
            if len(orders) != 0:
                await message.answer(text=f"{message_generator(orders)}",
                                     reply_markup=create_change_page_buttons(data['key_wrd'], data['current_page']))
            else:
                await message.answer(text="В данный момент нет заказов по этому запросу, "
                                          "Если вы хотите, мы можем сохранить ваш запрос и отправить вам информацию о новых заказах, которые поступят по данному запросу"
                                          "\n Вы этого хотите?(Да/нет)", reply_markup=choice_request_save)
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.callback_query_handler(text_contains="call_change_page")
async def change_page_by_buttons(call: CallbackQuery, state: FSMContext):
    try:
        async with state.proxy() as data:
            call_data = call.data.split(":")
            if data['key_wrd'] != "rec_all_order":
                total_page_num = math.ceil(db.select_order_count(str(data['key_wrd']).lower())[0] / 2)
            else:
                total_page_num = math.ceil(len(db.select_orders_for_rec()) / 2)

            if int(total_page_num) - 1 > 0:
                if data['current_page'] == int(total_page_num) - 1:
                    if call_data[1] == "next":
                        data['current_page'] = int(call_data[2])
                    else:
                        data['current_page'] = int(call_data[2]) - 1
                elif data['current_page'] == 0:
                    if call_data[1] == "next":
                        data['current_page'] = int(call_data[2]) + 1
                    else:
                        data['current_page'] = int(call_data[2])
                else:
                    if call_data[1] == "next":
                        data['current_page'] = int(call_data[2]) + 1
                    else:
                        data['current_page'] = int(call_data[2]) - 1
            else:
                if call_data[1] == "next":
                    data['current_page'] = int(call_data[2])
                else:
                    data['current_page'] = int(call_data[2])

            start_num = int(data['current_page']) * 2

            if data['key_wrd'] != "rec_all_order":
                orders = db.select_order(str(data['key_wrd']).lower(), start_num)
            else:
                orders = db.get_order_by_limit(start_num, 2)

            await call.message.delete()
            await call.message.answer(text=f"{message_generator(orders)}",
                                      reply_markup=create_change_page_buttons(data['key_wrd'], data['current_page']))
    except KeyError:
        await call.message.answer(text="Меню бота устарело. Повторите попытку заново.")
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.callback_query_handler(text_contains="call_num_page")
async def change_page_by_num(call: CallbackQuery, state: FSMContext):
    try:
        async with state.proxy() as data:
            if data['key_wrd'] != "rec_all_order":
                total_page_num = math.ceil(db.select_order_count(str(data['key_wrd']).lower())[0] / 2)
            else:
                total_page_num = math.ceil(len(db.select_orders_for_rec()) / 2)

            page_status = call.data.split(":")[1]
            if page_status == "start":
                data['current_page'] = 0
            elif page_status == "last":
                data['current_page'] = math.ceil((total_page_num - 1) / 2)

            start = data['current_page'] * 2

            if data['key_wrd'] != "rec_all_order":
                orders = db.select_order(str(data['key_wrd']).lower(), start)
            else:
                orders = db.get_order_by_limit(start, 2)

            await call.message.delete()
            await call.message.answer(text=f"{message_generator(orders)}",
                                      reply_markup=create_change_page_buttons(data['key_wrd'], data['current_page']))
    except KeyError:
        await call.message.answer(text="Меню бота устарело. Повторите попытку заново.")
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.callback_query_handler(text_contains="insert_rev_id")
async def insert_review_id(call: CallbackQuery):
    try:
        await call.message.delete_reply_markup()
        await Form.review_id.set()
        await call.message.answer(text="На какую заказу вы хотите откликнуться? Отправьте отклик id:", reply_markup=cancel_reply_keyboard)
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.message_handler(state=Form.review_id)
async def insert_review_message(message: Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            if message.text != "Отмена":
                data['review_id'] = message.text[1:]
                await state.finish()
                await Form.review_text.set()
                await message.answer(text="Напишите текст отклика:", reply_markup=cancel_reply_keyboard)
            else:
                await state.finish()
                await message.answer(text="Ваш отклик отменен. \n Что я еще могу для вас сделать?",
                                     reply_markup=reply_keyboards)
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.callback_query_handler(text_contains="review")
async def call_rev_id(call: CallbackQuery, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['review_id'] = call.data.split(":")[1]
            await state.finish()
            await Form.review_text.set()
            await call.message.delete_reply_markup()
            await call.message.answer("Напиши текст отклика:", reply_markup=cancel_reply_keyboard)
    except KeyError:
        await call.message.answer(text="Меню бота устарело. Повторите попытку заново.")
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.message_handler(state=Form.review_text)
async def insert_review_message(message: Message, state: FSMContext):
    try:
        if message.text != "Отмена":
            async with state.proxy() as data:
                if message.chat.username is not None:
                    data['review_text'] = message.text
                    f_name = f'@{message.chat.username}'
                    info = str(base64.b64decode(str(data['review_id']).replace('_', '=')).decode('utf-8')).split("||")
                    if info[0].isdecimal():
                        db.cur.execute(f"Select * from orders where chat_id = {int(info[0])} and id = {int(info[1])}")
                        pubs = db.cur.fetchone()
                        if len(pubs) > 0:
                            db.cur.execute("Insert into reviews values(?,?,?,?)",
                                           (int(info[0]), int(info[1]), f_name, message.text))
                            db.cur.execute(f"Select * from reviews where chat_id='{info[0]}' and order_id ='{info[1]}'")
                            reviews = db.cur.fetchall()
                            review_result = ""
                            for review in reviews:
                                review_result += f"\n{review[2]}:\n <b>Отклик:</b>  <i>{review[3]}</i>\n"
                            await bot.send_message(chat_id=pubs[6],
                                                   text=f"Вам к заказу <b>{pubs[1].upper()}</b>"
                                                        f"\n Оставили отклик:\n"
                                                        f"{review_result}\n"
                                                   )

                            await state.finish()
                            await message.answer(text=f"Ваш отклик к заказу '{str(pubs[1]).upper()}' отправлен. Ждите ответа заказчика.", reply_markup=reply_keyboards)
                        else:
                            await state.finish()
                            await message.answer(text="Неверный отклик id, повторите попытку.",
                                                 reply_markup=reply_keyboards)
                    else:
                        await state.finish()
                        await message.answer(text="Неверный отклик id, повторите попытку.", reply_markup=reply_keyboards)
                else:
                    await state.finish()
                    await message.answer_photo(
                        photo="https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/35084360882/original/6y7V9KClxBkpq8DyHFIjIRwyOygqIEFYqQ.png?1591612555",
                        caption="Пожалуйста, для начала установите свое пользовательское имя в телеграм. Без этого, заказчик не сможет найти вас по отклику.",
                        reply_markup=reply_keyboards)

        else:
            await state.finish()
            await message.answer(text="Вы отменили отклик. \n Что я еще могу для вас сделать?",
                                 reply_markup=reply_keyboards)
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.callback_query_handler(text_contains="request_save")
async def save_request(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer(cache_time=60)
        await call.message.edit_reply_markup(reply_markup=None)
        async with state.proxy() as data:
            call_name = call.data.split(":")[1]
            if call_name == "Yes":
                if int(db.get_number_of_requests(call.message.chat.id)[0]) <= 10:
                    deadline_date = date.today() + timedelta(days=3)
                    db.insert_request(chat_id=call.message.chat.id, request_text=data['key_wrd'],
                                      deadline_date=deadline_date)
                    await call.message.answer(
                        text="Отлично, ваш запрос сохранен на сервере и будет удален через 3 дня, ждите новых заказов.",
                        reply_markup=reply_keyboards)
                else:
                    await call.message.answer(
                        text="Каждый пользователь может сохранить не более 10-ти запросов, пожалуйста удалите ненужные и повторите попытку заново.",
                        reply_markup=reply_keyboards
                    )
            else:
                await call.message.answer(
                    text="Ваш запрос не сохранен. Попробуйте найти заказ по другим ключевым словам.",
                    reply_markup=reply_keyboards)
    except KeyError:
        await call.message.answer(text="Меню бота устарело. Повторите попытку заново.")
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.message_handler(state=Form.title)
async def write_title(message: Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            if message.text != "Отмена":
                if len(message.text) > 2:
                    data['title'] = message.text
                    if data['action_name'] == "Insert":
                        await Form.description.set()
                        await message.answer(
                            text="Если хотите отменить заказ, нажмите 'Отмена'.\n\n<b>Напишите описание заказа:</b>",
                            reply_markup=cancel_reply_keyboard)
                    else:
                        db.update_order(data['order_id'], data['title'], "Title")
                        await message.answer(
                            text="Ваш заказ успешно отредактирован. \n Что я еще могу для вас сделать?",
                            reply_markup=reply_keyboards)
                        await state.finish()
                else:
                    await Form.title.set()
                    await message.answer(
                        text="Заголовок должен состоять минимум из 3-х букв. Отправьте запрос повторно:")
            else:
                await state.finish()
                await message.answer(text="Вы отменили заказ. \n Что я еще могу для вас сделать?",
                                     reply_markup=reply_keyboards)
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.message_handler(state=Form.description)
async def write_description(message: Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            if message.text != "Отмена":
                if len(message.text) > 20:
                    data['description'] = message.text
                    if data['action_name'] == "Insert":
                        await state.finish()
                        await message.answer(text="<b>Выберите год сдачи работы:</b>",
                                             reply_markup=choice_year_of_deadline)
                    else:
                        db.update_order(data['order_id'], data['description'], "Description")
                        await message.answer(
                            text="Ваш заказ успешно отредактирован. \n Что я еще могу для вас сделать?",
                            reply_markup=reply_keyboards)
                        await state.finish()
                else:
                    await Form.description.set()
                    await message.answer(
                        text="Описание должно состоять минимум из 20-ти букв. Отправьте запрос повторно:")
            else:
                await state.finish()
                await message.answer(text="Вы отменили заказ. \n Что я еще могу для вас сделать?",
                                     reply_markup=reply_keyboards)
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.callback_query_handler(text_contains="call_dead_year")
async def write_dead_year(call: CallbackQuery, state: FSMContext):
    try:
        async with state.proxy() as data:
            year = call.data.split(":")
            data['dead_year'] = year[1]
            await call.message.edit_text(text="Выберите месяц сдачи работы:")
            if int(year[1]) == date.today().year:
                await state.finish()
                await call.message.edit_reply_markup(reply_markup=choice_month_current_year_deadline)
            else:
                await state.finish()
                await call.message.edit_reply_markup(reply_markup=choice_month_of_next_year_deadline)
    except KeyError:
        await call.message.answer(text="Меню бота устарело. Повторите попытку заново.")
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.callback_query_handler(text_contains="call_dead_month")
async def write_dead_month(call: CallbackQuery, state: FSMContext):
    try:
        async with state.proxy() as data:
            await call.message.edit_reply_markup(reply_markup=None)
            month = call.data.split(":")[1]
            data['dead_month'] = month
            await Form.dead_day.set()
            await call.message.answer(
                text="Если хотите отменить заказ, нажмите 'Отмена'.\n\n<b>Напишите день сдачи работы(1-31):</b>",
                reply_markup=cancel_reply_keyboard)
    except KeyError:
        await call.message.answer(text="Меню бота устарело. Повторите попытку заново.")
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.message_handler(state=Form.dead_day)
async def write_dead_day(message: Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            if message.text != "Отмена":
                if message.text.isdecimal():
                    day = int(message.text)
                    if 1 <= day <= 31:
                        check = int(data['dead_year']) == date.today().year and int(
                            data['dead_month']) == date.today().month
                        if check:
                            if day >= date.today().day:
                                data['dead_day'] = day
                                if data['action_name'] == "Insert":
                                    await Form.dead_time.set()
                                    await message.answer(
                                        text="Если хотите отменить заказ, нажмите 'Отмена'.\n\n<b>Укажите время сдачи работы(ЧЧ:ММ):</b>",
                                        reply_markup=cancel_reply_keyboard)
                                else:
                                    new_value = f"{data['dead_year']}-{data['dead_month']}-{data['dead_day']}"
                                    db.update_order(int(data['order_id']), new_value, "Dead_date")
                                    await message.answer(
                                        text="Ваш заказ успешно отредактирован. \n Что я еще могу для вас сделать?",
                                        reply_markup=reply_keyboards)
                                    await state.finish()
                            else:
                                await Form.dead_day.set()
                                await message.answer(
                                    text="Неправильно введена дата сдачи работы. Повторите попытку заново.")
                        else:
                            if data['action_name'] == "Insert":
                                data['dead_day'] = day
                                await Form.dead_time.set()
                                await message.answer(
                                    text="Если хотите отменить заказ, нажмите 'Отмена'.\n<b>Укажите время сдачи работы(ЧЧ:ММ):</b>",
                                    reply_markup=cancel_reply_keyboard)
                            else:
                                new_value = f"{data['dead_year']}-{data['dead_month']}-{day}"
                                db.update_order(int(data['order_id']), new_value, "Dead_date")
                                await message.answer(
                                    text="Ваш заказ успешно отредактирован. \n Что я еще могу для вас сделать?",
                                    reply_markup=reply_keyboards)
                                await state.finish()
                    else:
                        await Form.dead_day.set()
                        await message.answer(text="Неправильно введена дата сдачи работы. Повторите попытку заново.")
                else:
                    await Form.dead_day.set()
                    await message.answer(
                        text="Ответ должен состоять только из цифр от 1 до 31. Повторите попытку заново.")
            else:
                await state.finish()
                await message.answer(text="Вы отменили заказ. \n Что я еще могу для вас сделать?",
                                     reply_markup=reply_keyboards)
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.message_handler(state=Form.dead_time)
async def write_dead_time(message: Message, state: FSMContext):
    try:
        if message.text != "Отмена":
            async with state.proxy() as data:
                if ":" in message.text:
                    time_arr = message.text.split(":")
                    if len(time_arr) == 2:
                        if time_arr[0].isdecimal() and time_arr[1].isdecimal():
                            hour = int(time_arr[0])
                            minute = int(time_arr[1])
                            check = 0 <= hour <= 24 and 0 <= minute <= 60
                            if check:
                                if data['action_name'] == "Insert":
                                    data['dead_time'] = message.text
                                    await Form.payment.set()
                                    await message.answer(
                                        text="Если хотите отменить заказ, нажмите 'Отмена'.\n\n<b>Укажите оплату за заказ(в kzt):</b>",
                                        reply_markup=payment_reply_keyboard)
                                else:
                                    db.update_order(data['order_id'], message.text, "Dead_time")
                                    await message.answer(
                                        text="Ваш заказ успешно отредактирован. \n Что я еще могу для вас сделать?",
                                        reply_markup=reply_keyboards)
                                    await state.finish()
                            else:
                                await Form.dead_time.set()
                                await message.answer(
                                    text="Неправильно введено время сдачи работы. Повторите попытку заново.")
                        else:
                            await Form.dead_time.set()
                            await message.answer(
                                text="Неправильный формат отправления ответа(ЧЧ:ММ). Повторите попытку заново.")
                    else:
                        await Form.dead_time.set()
                        await message.answer(
                            text="Неправильный формат отправления ответа(ЧЧ:ММ). Повторите попытку заново.")
                else:
                    await Form.dead_time.set()
                    await message.answer(
                        text="Неправильный формат отправления ответа(ЧЧ:ММ). Повторите попытку заново.")

        else:
            await state.finish()
            await message.answer(text="Вы отменили заказ. \n Что я еще могу для вас сделать?",
                                 reply_markup=reply_keyboards)
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))


@dp.message_handler(state=Form.payment)
async def write_title(message: Message, state: FSMContext):
    try:
        if message.text != "Отмена":
            async with state.proxy() as data:
                if message.text.isdecimal() or message.text == "Договорная":
                    data['payment'] = message.text
                    if data['action_name'] == "Insert":
                        chat_id = message.chat.id
                        await message.answer(text=f"Ваш заказ успешно сохранен. Ждите исполнителя вашего заказа.",
                                             reply_markup=reply_keyboards)
                        await state.finish()

                        date_deadline = f"{data['dead_year']}-{data['dead_month']}-{data['dead_day']}"
                        db.insert_order(data['title'], data['description'], data['payment'], date_deadline,
                                        data['dead_time'],
                                        chat_id, str(data['title']).lower(), str(data['description']).lower())

                        db.delete_requests_over_deadline(date_today=date.today())

                        if db.has_request():
                            requests = db.select_all_request()
                            for request in requests:
                                row = db.select_last_order()
                                if row[1].lower().find(request[0].lower()) != -1 or row[2].lower().find(
                                        request[0].lower()) != -1:
                                    chats = db.select_chat_id_by_request()
                                    for chat in chats:
                                        if chat[1] == request[0]:
                                            order = db.select_last_order()
                                            deadline_time = str(order[5]).split(":")
                                            info_text = f"{str(order[6])}||{str(order[0])}"
                                            await bot.send_message(chat_id=chat[0],
                                                                   text=f"К нам поступил новый заказ по вашему запросу(<b>{request[0]}</b>), просмотрите:")
                                            await bot.send_message(chat_id=chat[0], text=f"<b>{order[1]}</b>"
                                                                                         f"\n\nОписание заказа: \n {order[2]} "
                                                                                         f"\n\n Дата сдачи работы: {order[4]}"
                                                                                         f"\n Время сдачи работы: {deadline_time[0]} : {deadline_time[1]}"
                                                                                         f"\n Оплата за заказ: {order[3]}",
                                                                   reply_markup=reviewButtonCreator(
                                                                       encrypt_val(info_text)))
                    else:
                        db.update_order(data['order_id'], data['payment'], "Payment")
                        await message.answer(
                            text="Ваш заказ успешно отредактирован. \n Что я еще могу для вас сделать?",
                            reply_markup=reply_keyboards)
                        await state.finish()
                else:
                    await Form.payment.set()
                    await message.answer(text="Оплата должна состоять только из цифр. Повторите попытку заново.")

        else:
            await state.finish()
            await message.answer(text="Вы отменили заказ. \n Что я еще могу для вас сделать?",
                                 reply_markup=reply_keyboards)
    except Exception as e:
        error_file = open("error.txt", "a")
        error_file.write('\n' + str(e))
