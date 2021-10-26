from aiogram.utils.callback_data import CallbackData

direction_callback = CallbackData("direction", "direction_name", "template_text")

search_type_callback = CallbackData("search_type", "search_name")

request_save_callback = CallbackData("request_save", "user_answer")

deadline_year_callback = CallbackData("call_dead_year", "year_value")

deadline_month_callback = CallbackData("call_dead_month", "month_value")

page_changer_callback = CallbackData("call_change_page", "change_status", "current_page")

page_num_callback = CallbackData("call_num_page", "page_status")

user_order_callback = CallbackData("call_user_orders", "order_id")

confirm_deletion_callback = CallbackData("confirm_deletion", "confirm_answer")

confirm_deletion_request_callback = CallbackData("confirm_request_deletion", "confirm_answer_of_request")

user_request_callback = CallbackData("call_user_requests", "request_id", "request_name")

set_user_order_callback = CallbackData("set_user_order", "order_id")

edition_choice_callback = CallbackData("edit_order", "edit_name", "order_id")

get_user_order_callback = CallbackData("get_order_of_user", "order_id")

review_callback = CallbackData("review", "review_id")

insert_review_callback = CallbackData("insert_rev_id")
