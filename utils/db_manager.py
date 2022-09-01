import psycopg2
from datetime import datetime


class Database:
    def __init__(self, db_conf: str):
        self.db_conf = db_conf
        self.start_up()


    def start_up(self): # выглядит как гавнич
        """Проверка наличия и инициализация создания таблиц."""
        con = psycopg2.connect(self.db_conf)
        cur = con.cursor()
        try:
            cur.execute("""SELECT * FROM users""")
            print("Таблица users существует")
        except psycopg2.Error:
            print("Таблицы users не существует. Создается...")
            con.rollback()
            self.create_table_users()
        try:
            cur.execute("""SELECT * FROM ledgers""")
            print("Таблица ledgers существует")
        except psycopg2.Error:
            print("Таблицы ledgers не существует. Создается...")
            con.rollback()
            self.create_table_ledgers()
        con.close()


    def create_table_users(self):
        """Создать таблицу пользователей."""
        con = psycopg2.connect(self.db_conf)
        cur = con.cursor()
        try:
            cur.execute(
                """CREATE TABLE users (
                user_id BIGINT,
                balance INT DEFAULT 0,
                PRIMARY KEY(user_id)
                );"""
            )
            con.commit()
            print("Таблица users создана.")
        except psycopg2.Error:
            con.rollback()


    def create_table_ledgers(self):
        """Создать таблицу учетной книги."""
        con = psycopg2.connect(self.db_conf)
        cur = con.cursor()
        try:
            cur.execute(
                """CREATE TABLE ledgers (
                user_id BIGINT,
                amount INT,
                bill_id BIGINT,
                timestamp TIMESTAMP,
                CONSTRAINT fk_user
                    FOREIGN KEY(user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
                );"""
            )
            con.commit()
            print("Таблица ledgers создана.")
        except psycopg2.Error:
            pass


    def deposit(self, user_id:int, amount:int, bill_id:int):
        """Пополнение баланса."""
        con = psycopg2.connect(self.db_conf)
        cur = con.cursor()
        try:
            dt=datetime.now().isoformat(sep=' ', timespec="seconds")
            new_balance = self.user_info(user_id) + amount
            cur.execute(
                            f"""INSERT INTO ledgers
                            (user_id, amount, bill_id, timestamp)
                            VALUES({user_id},{amount},{bill_id},'{dt}');"""
            )
            cur.execute(
                            f"""UPDATE users
                            SET balance = {new_balance}
                            WHERE user_id = {user_id};"""
            )
            con.commit()
            con.close()
            print('deposit procedure complete')
        except psycopg2.DatabaseError as e:
            print(f'deposit procedure error: {e}')
            return False

    def user_info(self, user_id: int):
        """Проверка наличия пользователя в базе.
        Возращает текущий баланс счета или ложное значение."""
        con = psycopg2.connect(self.db_conf)
        cur = con.cursor()
        try:
            cur.execute(
                        f"""SELECT user_id, balance
                            FROM users
                            WHERE user_id = '{user_id}';"""
            )

            balance = cur.fetchone()[1]
            print('user info procedure successful')
            return balance
        except (psycopg2.Error, TypeError) as e:
            print(e)
            return False


    def user_create(self, user_id: int):
        """Создание пользователя с указанным идентификатором. """
        con = psycopg2.connect(self.db_conf)
        cur = con.cursor()
        print(user_id)
        cur.execute(
                        f"""INSERT INTO users(user_id)
                         VALUES({user_id});"""
        )
        con.commit()
        con.close()