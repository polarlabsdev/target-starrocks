"""Starrocks target sink class, which handles writing streams."""

from __future__ import annotations

import typing as t

import sqlalchemy as sa
from singer_sdk.connectors import SQLConnector
from singer_sdk.sinks import SQLSink


class StarrocksConnector(SQLConnector):
    """The connector for Starrocks."""

    max_varchar_length = 65535

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

    # The following 3 methods are hacks to get around issues with the starrocks dialect
    # unable to create tables in an Iceberg catalog. There's nothing wrong with the
    # tables created, however there are 2 main issues:
    # 1. The dialect does not check the existence of tables correctly and fails with a
    #    ProgrammingError when checking if a table exists.
    # 2. The dialect insists on VARCHARS having a length, which is not actually required
    #    however Meltano SDK by default does not set a length for all VARCHARs.
    #    so instead we force it.
    def table_exists(
        self,
        full_table_name: str | SQLConnector.FullyQualifiedName
    ) -> bool:
        """Determine if the target table already exists.

        Args:
            full_table_name: the target table name.

        Returns:
            True if table exists, False if not, None if unsure or undetectable.
        """
        _, schema_name, table_name = self.parse_full_table_name(full_table_name)

        try:
            table_exists_result = sa.inspect(self._engine).has_table(
                table_name, schema_name
            )
        except sa.exc.ProgrammingError:
            self.logger.info(
                "ANNOYING TABLE CREATION ERROR IS STILL OCCURING WHEN "
                "CHECKING IF TABLE EXISTS."
            )
            table_exists_result = False

        return table_exists_result

    def create_empty_table(
        self,
        full_table_name: str | SQLConnector.FullyQualifiedName,
        schema: dict,
        primary_keys: t.Sequence[str] | None = None,  # noqa: ARG002
        partition_keys: list[str] | None = None,
        as_temp_table: bool = False,  # noqa: FBT001, FBT002
    ) -> None:
        """Create an empty target table.

        Args:
            full_table_name: the target table name.
            schema: the JSON schema for the new table.
            primary_keys: list of key properties.
            partition_keys: list of partition keys.
            as_temp_table: True to create a temp table.

        Raises:
            NotImplementedError: if temp tables are unsupported and as_temp_table=True.
            RuntimeError: if a variant schema is passed with no properties defined.
        """
        if as_temp_table:
            msg = "Temporary tables are not supported."
            raise NotImplementedError(msg)

        _ = partition_keys  # Not supported in generic implementation.

        _, schema_name, table_name = self.parse_full_table_name(full_table_name)
        meta = sa.MetaData(schema=schema_name)
        columns: list[sa.Column] = []

        try:
            properties: dict = schema["properties"]
        except KeyError as e:
            msg = f"Schema for '{full_table_name}' does not define properties: {schema}"
            raise RuntimeError(msg) from e
        for property_name, property_jsonschema in properties.items():
            columns.append(
                sa.Column(
                    property_name,
                    self.to_sql_type(property_jsonschema),
                ),
            )

        _ = sa.Table(table_name, meta, *columns)
        meta.create_all(self._engine, checkfirst=False)

    def to_sql_type(self, jsonschema_type: dict) -> sa.types.TypeEngine:
        """Return a JSON Schema representation of the provided type.

        By default will call `typing.to_sql_type()`.

        Developers may override this method to accept additional input argument types,
        to support non-standard types, or to provide custom typing logic.
        If overriding this method, developers should call the default implementation
        from the base class for all unhandled cases.

        Args:
            jsonschema_type: The JSON Schema representation of the source type.

        Returns:
            The SQLAlchemy type representation of the data type.
        """
        sql_type = self.jsonschema_to_sql.to_sql_type(jsonschema_type)

        if type(sql_type) is sa.types.VARCHAR and sql_type.length is None:
            # Set a default length for VARCHAR if not specified
            # else StarRocks dialect will throw an error
            sql_type = sa.types.VARCHAR(self.max_varchar_length)

        return sql_type


class StarrocksSink(SQLSink):
    """Starrocks target sink class."""

    connector_class = StarrocksConnector
