"""Starrocks target class."""

from __future__ import annotations

from singer_sdk import typing as th
from singer_sdk.target_base import SQLTarget

from target_starrocks.sinks import (
    StarrocksSink,
)


class TargetStarrocks(SQLTarget):
    """Sample target for Starrocks."""

    name = "target-starrocks"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "host",
            th.StringType,
            required=True,
            description="StarRocks cluster FE host or IP address.",
        ),
        th.Property(
            "port",
            th.IntegerType,
            required=True,
            default=9030,
            description="StarRocks cluster FE query port (typically 9030).",
        ),
        th.Property(
            "user",
            th.StringType,
            required=True,
            description="Username for StarRocks connection.",
        ),
        th.Property(
            "password",
            th.StringType,
            required=True,
            secret=True,
            description="Password for StarRocks connection.",
        ),
        th.Property(
            "catalog",
            th.StringType,
            required=True,
            description="Target Iceberg catalog in StarRocks",
        ),
        th.Property(
            "warehouse",
            th.StringType,
            required=True,
            description="Target Iceberg warehouse in StarRocks",
        ),
    ).to_dict()

    default_sink_class = StarrocksSink


if __name__ == "__main__":
    TargetStarrocks.cli()
