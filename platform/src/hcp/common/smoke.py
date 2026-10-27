"""Three nonpatient constants exercise the installed wheel and Delta transactions."""

import argparse
import json
import re
import sys
from importlib.metadata import PackageNotFoundError, version


def run(spark, table):
    if not re.fullmatch(r"hc_(dev|test)\._foundation_probe\.wheel_smoke", table):
        raise ValueError("Smoke writes are restricted to the dedicated fixture table")
    spark.sql(
        f"CREATE TABLE IF NOT EXISTS {table} (id BIGINT, value STRING) USING DELTA"
    )
    # Append a distinct sentinel so time travel proves an older state, rather
    # than merely re-reading the latest table under a version qualifier.
    spark.sql(f"INSERT INTO {table} VALUES (3, 'append-sentinel')")
    appended_version = spark.sql(f"DESCRIBE HISTORY {table} LIMIT 1").first().version
    spark.sql(f"DELETE FROM {table} WHERE id = 3")
    merge = (
        f"MERGE INTO {table} AS target "
        "USING (SELECT id, concat('fixture-', CAST(id AS STRING)) AS value "
        "FROM range(3)) AS source ON target.id = source.id "
        "WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED THEN INSERT *"
    )
    spark.sql(merge)
    spark.sql(merge)
    rows = spark.table(table).orderBy("id").collect()
    if [(r.id, r.value) for r in rows] != [(i, f"fixture-{i}") for i in range(3)]:
        raise AssertionError("Delta wheel smoke reconciliation failed")
    version = spark.sql(f"DESCRIBE HISTORY {table} LIMIT 1").first().version
    assert spark.sql(f"SELECT * FROM {table} VERSION AS OF {version}").count() == 3
    assert (
        spark.sql(
            f"SELECT * FROM {table} VERSION AS OF {appended_version} WHERE id = 3"
        ).count()
        == 1
    )
    return {
        "status": "PASS",
        "rows": 3,
        "version": version,
        "append_version": appended_version,
        "historical_sentinel_rows": 1,
        "replay_idempotent": True,
        "table": table,
    }


def main():
    from pyspark.sql import SparkSession

    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", choices=["hc_dev", "hc_test"], required=True)
    args = parser.parse_args()
    spark = SparkSession.builder.getOrCreate()
    result = run(spark, args.catalog + "._foundation_probe.wheel_smoke")
    packages = {}
    for name in ["intellify-healthcare-platform", "pyspark", "delta-spark"]:
        try:
            packages[name] = version(name)
        except PackageNotFoundError:
            packages[name] = "runtime-managed"
    print(json.dumps(result | {"python": sys.version, "packages": packages}))


if __name__ == "__main__":
    main()
