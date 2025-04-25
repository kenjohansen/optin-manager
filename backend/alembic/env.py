from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models and set target_metadata for autogenerate support
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
from app.core.database import Base
import app.models.auth_user, app.models.optin, app.models.customization, app.models.message, app.models.message_template, app.models.user, app.models.verification_code, app.models.consent

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Get the database URL from environment or use the default
    import os
    url = os.getenv("DATABASE_URL", "sqlite:///./optin_manager.db")
    
    # Override the URL in the config
    config.set_main_option("sqlalchemy.url", url)
    
    # Detect database type and configure accordingly
    schema = None
    is_sqlite = url.startswith("sqlite")
    
    if url.startswith("postgresql"):
        schema = "optin_manager"
        
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=schema,
        include_schemas=True if schema else False,
        default_schema_name=schema if schema else None,
        render_as_batch=is_sqlite,
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Get the database URL from environment or use the default
    import os
    db_url = os.getenv("DATABASE_URL", "sqlite:///./optin_manager.db")
    
    # Override the URL in the config
    config.set_main_option("sqlalchemy.url", db_url)
    
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Detect SQLite and configure accordingly
        is_sqlite = db_url.startswith("sqlite")
        
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # SQLite doesn't support certain operations
            render_as_batch=is_sqlite,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
