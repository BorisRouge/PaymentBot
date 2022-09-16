import psycopg2
from datetime import datetime
from .logger import get_logger


log = get_logger()


class Database:
    """Менеджер базы данных."""
    def __init__(self, db_conf: str):
        self.db_conf = db_conf
        self.start_up()


    def start_up(self):
        """Проверка наличия и инициализация создания таблиц."""
        con = psycopg2.connect(self.db_conf)
        cur = con.cursor()
        try:
            cur.execute("""SELECT * FROM users""")
            log.warning("Таблица users - OK")
        except psycopg2.Error:
            log.warning("Таблицы users не существует. Создается...")
            con.rollback()
            self.create_table_users()
        try:
            cur.execute("""SELECT * FROM ledgers""")
            log.warning("Таблица ledgers - OK")
        except psycopg2.Error:
            log.warning("Таблицы ledgers не существует. Создается...")
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
                banned BOOLEAN DEFAULT false,
                PRIMARY KEY(user_id)
                );"""
            )
            con.commit()
            log.warning("Таблица users создана.")
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
            log.warning("Таблица ledgers создана.")
        except psycopg2.Error:
            pass


    def deposit(self, user_id:int, amount:int, bill_id:int):
        """Пополнение баланса."""
        con = psycopg2.connect(self.db_conf)
        cur = con.cursor()
        try:
            dt=datetime.now().isoformat(sep=' ', timespec="seconds")
            new_balance = self.user_info(user_id)[1] + amount
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
            log.info(f'Баланс пользователя {user_id} пополнен ' 
                    +f'на сумму {amount} руб. Текущий баланс: {new_balance} руб.'
                    )
        except psycopg2.DatabaseError as e:
            log.error(f'Ошибка при проведении операции пополнения: {e}')
            return False


    def user_info(self, user_id: int):
        """Проверка наличия пользователя в базе.
        Возращает текущий баланс счета или ложное значение."""

        con = psycopg2.connect(self.db_conf)
        cur = con.cursor()
        try:
            cur.execute(
                        f"""SELECT *
                            FROM users
                            WHERE user_id = '{user_id}';"""
            )
            user_data = cur.fetchone()
            if user_data == None:
                raise TypeError            
            log.info('Успешный запрос данных о пользователе.')
            return user_data

        except (psycopg2.Error, TypeError) as e:
            log.error('При поиске в базе данных '
                     +'не найден идентификатор пользователя.', e
                     )
            return False


    def user_create(self, user_id: int):
        """Создание пользователя с указанным идентификатором."""
        con = psycopg2.connect(self.db_conf)
        cur = con.cursor()
        cur.execute(
                        f"""INSERT INTO users(user_id)
                         VALUES({user_id});"""
        )
        con.commit()
        con.close()
        log.info(f'Пользователь {user_id} внесен в базу данных.')

    def user_update(self, user_id: int, new_balance: int):
        """Изменение баланса пользователя с указанным идентификатором."""
        con = psycopg2.connect(self.db_conf)
        cur = con.cursor()
        cur.execute(
                    f"""UPDATE users
                        SET balance = {new_balance}
                        WHERE user_id = {user_id};"""
        )
        con.commit()
        con.close()
        log.info(f'Баланс пользователя {user_id} '
               + f'изменен на значение: {new_balance}')

    def user_ban(self, user_id: int):
        """Блокировка пользователя с указанным идентификатором."""
        con = psycopg2.connect(self.db_conf)
        cur = con.cursor()
        cur.execute(
                    f"""UPDATE users
                        SET banned = TRUE
                        WHERE user_id = {user_id};"""
        )
        con.commit()
        con.close()
        log.info(f'Пользователь {user_id} был заблокирован.')


    def user_get_all(self):
        """Выгрузка данных о всех пользователях."""
        con = psycopg2.connect(self.db_conf)
        cur = con.cursor()
        cur.execute("""SELECT * FROM users""")
        all_users = cur.fetchall()
        con.close()
        log.info('Произведена выгрузка данных о всех пользователях.')
        return all_users
        