"""Verify the isolated Spark runtime with actual SQL and Delta round trips."""

from __future__ import annotations

import importlib.metadata
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"
    os.environ["PYSPARK_PYTHON"] = str(Path(__import__("sys").executable))
    os.environ["PYSPARK_DRIVER_PYTHON"] = os.environ["PYSPARK_PYTHON"]
    report = {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "checks": {},
        "versions": {
            p: importlib.metadata.version(p)
            for p in ["pyspark", "delta-spark", "mlflow", "databricks-sdk", "openai"]
        },
    }
    spark = None
    try:
        from delta import configure_spark_with_delta_pip
        from pyspark.sql import SparkSession

        builder = (
            SparkSession.builder.master("local[2]")
            .appName("healthcare-runtime-readiness")
            .config("spark.ui.enabled", "false")
            .config("spark.sql.shuffle.partitions", "2")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config(
                "spark.sql.catalog.spark_catalog",
                "org.apache.spark.sql.delta.catalog.DeltaCatalog",
            )
            .config("spark.sql.session.timeZone", "UTC")
        )
        spark = configure_spark_with_delta_pip(builder).getOrCreate()
        actual = spark.sql("SELECT SUM(id) AS total FROM range(10)").first()["total"]
        if actual != 45:
            raise ValueError("Spark SQL did not return the expected sum")
        report["checks"]["spark_sql"] = "PASS"
        path = ROOT / "output/platform-readiness/runtime-delta"
        spark.range(3).write.format("delta").mode("overwrite").save(str(path))
        spark.range(3, 5).write.format("delta").mode("append").save(str(path))
        if spark.read.format("delta").load(str(path)).count() != 5:
            raise ValueError("Delta current version count differs")
        if (
            spark.read.format("delta").option("versionAsOf", 0).load(str(path)).count()
            != 3
        ):
            raise ValueError("Delta versioned read differs")
        report["checks"]["delta_write_append_time_travel"] = "PASS"
    except Exception as error:  # noqa: BLE001 - CLI boundary records failure and cleanup
        report["error"] = str(error)[-3000:]
    finally:
        if spark is not None:
            spark.stop()
    report["status"] = (
        "PASS"
        if len(report["checks"]) == 2
        and all(v == "PASS" for v in report["checks"].values())
        else "FAIL"
    )
    destination = ROOT / "output/platform-readiness/local-runtime.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
