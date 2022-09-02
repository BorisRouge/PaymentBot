from dataclasses import dataclass
from environs import Env


@dataclass
class Database:
    # db: str
    # user: str
    # password: str
    con_data: str


@dataclass
class Telegram:
    telegram_bot_token: str
    admin: str

@dataclass
class Qiwi:
    qiwi_secret_key: str


@dataclass
class Settings:
    database: Database
    telegram: Telegram
    qiwi: Qiwi



def get_config(path: str = None):
    """Получение переменных из указанной среды."""
    env = Env()
    env.read_env(path)
    return Settings(
        database=Database(f"""dbname={env.str('DB')}
                          user={env.str('DBUSER')}
                          password={env.str('DBPASS')}""",
                         ),
        telegram=Telegram(telegram_bot_token=env.str('TELEGRAM_BOT_TOKEN'),
                          admin=env.str('TELEGRAM_ADMINS'),
                         ),
        qiwi=Qiwi(qiwi_secret_key=env.str('QIWI_SECRET_KEY')),

    )