"""Linux local fixture; never submits a cloud workload."""

import pytest
from hcp.common.smoke import run


def test_replay_and_delta_time_travel(tmp_path):
    from delta import configure_spark_with_delta_pip
    from pyspark.sql import SparkSession

    builder = (
        SparkSession.builder.master("local[2]")
        .appName("hcp-shared-library-test")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .config("spark.sql.warehouse.dir", str(tmp_path / "warehouse"))
        .config("spark.ui.enabled", "false")
    )
    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    try:
        # OSS Spark has a two-part catalog. The wrapper translates only the
        # exact authorized UC fixture name; production validation stays intact.
        spark.sql("CREATE DATABASE IF NOT EXISTS _foundation_probe")

        class LocalCatalog:
            def sql(self, query):
                return spark.sql(
                    query.replace("hc_test._foundation_probe.", "_foundation_probe.")
                )

            def table(self, table):
                return spark.table(
                    table.replace("hc_test._foundation_probe.", "_foundation_probe.")
                )

        first = run(LocalCatalog(), "hc_test._foundation_probe.wheel_smoke")
        second = run(LocalCatalog(), "hc_test._foundation_probe.wheel_smoke")
        assert first["rows"] == second["rows"] == 3
        assert first["historical_sentinel_rows"] == 1
        assert second["replay_idempotent"] is True
        assert second["version"] > first["version"]
        with pytest.raises(ValueError):
            run(LocalCatalog(), "hc_prod.silver.patient")
    finally:
        spark.sql("DROP TABLE IF EXISTS _foundation_probe.wheel_smoke")
        spark.stop()
