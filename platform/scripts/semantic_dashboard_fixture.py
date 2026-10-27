"""Nonpatient metric/dashboard fixture; no embedded publisher credentials."""

METRIC = "hc_test.semantic.hcp_foundation_metric"
SOURCE = "hc_test.gold.app_authorization_fixture"
QUERY = f"SELECT facility_id, MEASURE(fixture_count) AS fixture_count FROM {METRIC} GROUP BY facility_id ORDER BY facility_id"
CREATE_METRIC = f"""CREATE VIEW {METRIC} WITH METRICS LANGUAGE YAML AS
$$
version: 1.1
source: {SOURCE}
filter: hc_ops.security.facility_allowed(source.facility_id)
dimensions:
  - name: facility_id
    expr: source.facility_id
measures:
  - name: fixture_count
    expr: COUNT(*)
$$"""


def definition():
    return {
        "datasets": [
            {
                "name": "fixture",
                "displayName": "Nonpatient scoped count",
                "queryLines": [QUERY],
            }
        ],
        "pages": [
            {
                "name": "scope",
                "displayName": "Authorization fixture",
                "pageType": "PAGE_TYPE_CANVAS",
                "layout": [
                    {
                        "widget": {
                            "name": "scope-table",
                            "queries": [
                                {
                                    "name": "main_query",
                                    "query": {
                                        "datasetName": "fixture",
                                        "fields": [
                                            {
                                                "name": "facility_id",
                                                "expression": "`facility_id`",
                                            },
                                            {
                                                "name": "fixture_count",
                                                "expression": "`fixture_count`",
                                            },
                                        ],
                                        "disaggregated": True,
                                    },
                                }
                            ],
                            "spec": {
                                "version": 2,
                                "widgetType": "table",
                                "encodings": {
                                    "columns": [
                                        {
                                            "fieldName": "facility_id",
                                            "displayName": "Facility",
                                        },
                                        {
                                            "fieldName": "fixture_count",
                                            "displayName": "Fixture count",
                                        },
                                    ]
                                },
                                "frame": {
                                    "showTitle": True,
                                    "title": "Authorized facility only",
                                },
                            },
                        },
                        "position": {"x": 0, "y": 0, "width": 12, "height": 5},
                    }
                ],
            }
        ],
    }
