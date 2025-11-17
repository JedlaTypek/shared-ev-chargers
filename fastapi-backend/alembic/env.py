# env.py
from logging.config import fileConfig

# Odebráno engine_from_config a pool, protože je nepotřebujeme
# Místo toho importujeme create_engine
from sqlalchemy import create_engine

from alembic import context

from app.db.schema import Base
# TADY JE ZMĚNA: Importujeme váš config s aliasem 'app_config',
# aby se "nepobil" s Alembic proměnnou 'config'
from app.core.config import config as app_config

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
# Tato proměnná 'config' je teď čistě jen pro Alembic
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata # Ponecháno jen jednou

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        # TADY JE ZMĚNA: Použijeme URL z vaší app_config
        url=app_config.db_url, 
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )


def run_migrations_online() -> None:
    """Run migrations in 'online' mode' using FastAPI config."""
    
    # TADY JE ZMĚNA: Vytvoříme engine z app_config.db_url
    # 'create_engine' a 'app_config' jsou už naimportované nahoře
    connectable = create_engine(app_config.db_url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,          # porovnávání změn typů
            compare_server_default=True # porovnávání defaultů
        )

        with context.begin_transaction():
            context.run_migrations()



if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()