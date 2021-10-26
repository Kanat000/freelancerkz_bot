import sqlite3
from datetime import date


class SQLither:
    def __init__(self, database):
        self.conn = sqlite3.connect(database)
        self.cur = self.conn.cursor()

    def create_order_table(self):
        self.cur.execute('Create Table if not exists orders('
                         'id integer PRIMARY KEY AUTOINCREMENT NOT NULL,'
                         'title varchar(255),'
                         'description Text,'
                         'payment int,'
                         'dead_date date,'
                         'dead_time Time,'
                         'chat_id int,'
                         'check_title varchar(255),'
                         'check_description Text'
                         ')'
                         )

    def create_request_table(self):
        self.cur.execute('Create Table if not exists requests('
                         'id integer PRIMARY KEY AUTOINCREMENT NOT NULL,'
                         'chat_id varchar(255),'
                         'request VARCHAR,'
                         'deadline_date Date'
                         ')')

    def create_review_table(self):
        self.cur.execute('Create Table if not exists reviews('
                         'chat_id int,'
                         'order_id int,'
                         'review_sender varchar,'
                         'review_msg text'
                         ')')

    def insert_order(self, title, description, payment, dead_date, dead_time, chat_id, low_title, low_description):
        self.cur.execute(
            "Insert into orders(title,description,payment,dead_date,dead_time,chat_id,check_title, check_description) "
            "values(?,?,?,?,?,?,?,?);",
            (title, description, payment, dead_date, dead_time, chat_id, low_title, low_description))
        self.conn.commit()

    def select_order(self, key_word, start_num):
        self.cur.execute(
            f"Select * From orders where check_title Like '%{key_word}%' or check_description Like '%{key_word}%' limit {start_num}, 2;")
        return self.cur.fetchall()

    def get_order_by_limit(self, start, limit):
        self.cur.execute(f"Select * from orders limit {start}, {limit}")
        return self.cur.fetchall()

    def select_order_count(self, key_word):
        self.cur.execute(
            f"Select count(id) From orders where check_title Like '%{key_word}%' or check_description Like '%{key_word}%';")
        return self.cur.fetchone()

    def select_user_order(self, chat_id):
        self.cur.execute(f"Select * from orders where chat_id='{chat_id}'")
        return self.cur.fetchall()

    def delete_user_order(self, order_id):
        self.cur.execute(
            f"Delete from orders where id = '{order_id}'"
        )
        self.conn.commit()

    def select_order_by_id(self, order_id):
        self.cur.execute(f"Select * from orders where id = '{order_id}'")
        return self.cur.fetchone()

    def select_last_order(self):
        self.cur.execute("Select * from orders order by id desc limit 1;")
        return self.cur.fetchone()

    def select_orders_for_rec(self):
        self.cur.execute("Select * from orders order by dead_date Asc;")
        return self.cur.fetchall()

    def delete_order_over_deadline(self):
        today_date = date.today()
        self.cur.execute(f"Delete from orders where dead_date < '{today_date}'")
        self.conn.commit()

    def update_order(self, order_id, new_value, action_name):
        if action_name == "Title":
            self.cur.execute(f"Update orders set title='{new_value}', check_title='{str(new_value).lower()}' where id = '{order_id}'")
        elif action_name == "Description":
            self.cur.execute(f"Update orders set description='{new_value}', check_description='{str(new_value).lower()}' where id='{order_id}'")
        elif action_name == "Dead_date":
            self.cur.execute(f"Update orders set dead_date='{new_value}' where id='{order_id}'")
        elif action_name == "Dead_time":
            self.cur.execute(f"Update orders set dead_time='{new_value}' where id='{order_id}'")
        elif action_name == "Payment":
            self.cur.execute(f"Update orders set payment='{new_value}' where id='{order_id}'")
        self.conn.commit()

    def insert_request(self, chat_id, request_text, deadline_date):
        self.cur.execute(
            f"Insert into requests(chat_id,request,deadline_date) values('{chat_id}','{request_text}','{deadline_date}');")
        self.conn.commit()

    def has_request(self):
        return bool(self.cur.execute("Select request from requests;"))

    def select_all_request(self):
        self.cur.execute("Select request from requests;")
        return self.cur.fetchall()

    def select_chat_id_by_request(self):
        self.cur.execute(f"Select chat_id, request from requests;")
        return self.cur.fetchall()

    def select_request_by_chat_id(self, chat_id):
        self.cur.execute(f"Select * from requests where chat_id = {chat_id}")
        return self.cur.fetchall()

    def deletion_request_by_id(self, request_id):
        self.cur.execute(f"Delete from requests where id = '{request_id}';")
        self.conn.commit()

    def delete_requests_over_deadline(self, date_today):
        self.cur.execute(f"Delete from requests where deadline_date < '{date_today}'")

    def select_date(self):
        self.cur.execute(f"Select request, deadline_date from requests")
        return self.cur.fetchall()

    def get_number_of_requests(self, chatId):
        self.cur.execute(f"Select count(id) from requests where chat_id = '{chatId}'")
        return self.cur.fetchone()

    def close_db(self):
        self.cur.close()
