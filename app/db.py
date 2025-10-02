import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///local.db")

# Ajustes por dialeto (MySQL/Postgres/SQLite)
engine_kwargs = {
    "pool_pre_ping": True,   # evita conexões zumbis
}

# MySQL: pode precisar aumentar timeout ou passar ssl se for nuvem
if DATABASE_URL.startswith("mysql"):
    # Exemplo de ajustes opcionais:
    # engine_kwargs["connect_args"] = {"ssl": {"ssl_disabled": True}}
    # engine_kwargs["pool_recycle"] = 280
    pass

# Postgres na nuvem normalmente exige sslmode=require na URL
# Ex.: postgresql+psycopg2://user:pass@host:5432/db?sslmode=require

engine = create_engine(DATABASE_URL, **engine_kwargs)

db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base()
Base.query = db_session.query_property()


def init_db(app=None):
    # Se quiser logar SQLs para debug local:
    # import logging
    # logging.basicConfig()
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    pass
