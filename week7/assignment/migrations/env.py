import os
import sys
from logging.config import fileConfig

from alembic import context
from flask import current_app

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.extensions import db
from app import models  # noqa: F401

target_metadata = db.metadata

def get_engine():
    return current_app.extensions["migrate"].db.engine

def run_migrations_offline():
    context.configure(url=str(get_engine().url), target_metadata=target_metadata,
                      literal_binds=True, compare_type=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    with get_engine().connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
