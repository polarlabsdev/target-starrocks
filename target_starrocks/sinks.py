"""Starrocks target sink class, which handles writing streams."""

from __future__ import annotations

from singer_sdk.connectors import SQLConnector
from singer_sdk.sinks import SQLSink


class StarrocksConnector(SQLConnector):
    """The connector for Starrocks."""

    def get_sqlalchemy_url(self, config: dict) -> str:
        """Generates a SQLAlchemy URL for Starrocks.

        Args:
            config: The configuration for the connector.
        """
        # Ensure that the sqlalchemy-starrocks dialect is installed.
        # The URL format is typically: starrocks://user:password@host:port/database
        # If using a specific catalog, config['database'] should be in the
        # format 'catalog_name.database_name'.
        return (
            f"starrocks://{config['user']}:{config['password']}"
            f"@{config['host']}:{config['port']}/{config['catalog']}.{config['warehouse']}"
        )


class StarrocksSink(SQLSink):
    """Starrocks target sink class."""

    connector_class = StarrocksConnector
