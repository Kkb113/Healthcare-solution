"""Three nonpatient constants exercise the installed wheel and Delta transactions."""

import argparse
import json
import re


def run(spark, table):
    if not re.fullmatch(r"hc_(dev|test)\._foundation_probe\.wheel_smoke", table):
        raise ValueError("Smoke writes are restricted to the dedicated fixture table")
    spark.sql(
        f"CREATE TABLE IF NOT EXISTS {table} (id BIGINT, value STRING) USING DELTA"
    )
    spark.sql(
        f"MERGE INTO {table} AS target "
        "USING (SELECT id, concat('fixture-', CAST(id AS STRING)) AS value "
        "FROM range(3)) AS source ON target.id = source.id "
        "WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED THEN INSERT *"
    )
    rows = spark.table(table).orderBy("id").collect()
    if [(r.id, r.value) for r in rows] != [(i, f"fixture-{i}") for i in range(3)]:
        raise AssertionError("Delta wheel smoke reconciliation failed")
    version = spark.sql(f"DESCRIBE HISTORY {table} LIMIT 1").first().version
    assert spark.sql(f"SELECT * FROM {table} VERSION AS OF {version}").count() == 3
    return {"status": "PASS", "rows": 3, "version": version, "table": table}


def main():
    from pyspark.sql import SparkSession

    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", choices=["hc_dev", "hc_test"], required=True)
    args = parser.parse_args()
    spark = SparkSession.builder.getOrCreate()
    print(json.dumps(run(spark, args.catalog + "._foundation_probe.wheel_smoke")))


if __name__ == "__main__":
    main()
