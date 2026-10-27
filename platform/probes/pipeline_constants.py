"""Lakeflow capability fixture: three constants, with no healthcare sources."""

from pyspark import pipelines as dp
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()


@dp.materialized_view(name="pipeline_constants")
def pipeline_constants():
    return spark.range(3).selectExpr("id", "concat('fixture-', id) AS value")
