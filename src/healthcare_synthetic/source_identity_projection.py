"""Pure identity-format examples for source integration tests, not vendor-certified exports."""


def patient_identity_record(row):
    return {"MRN": row["mrn"], "NameComponentText": "^".join((row["family_name"].upper(), row["given_name"].upper(), (row["middle_name"] or "").upper())),
            "BirthDate": row["birth_date"], "AdministrativeSex": row["administrative_sex"], "SourceVersion": row["source_record_id"]}


def workday_identity_record(row, workers, centers):
    manager = row["manager_worker_id"]
    references = {r["worker_id"]: r["employee_number"] for r in workers}
    centers_by_id = {r["cost_center_id"]: r for r in centers}
    return {"EmployeeID": row["employee_number"], "DisplayName": f"{row['family_name'].upper()}, {row['given_name']}",
            "ManagerEmployeeID": references[manager] if manager else None, "Role": row["role"], "FTE": row["fte"],
            "CostCenterReference": "WO-" + centers_by_id[row["cost_center_id"]]["cost_center_code"],
            "EffectiveDate": row["valid_from"][:10], "ExtractVersion": row["source_record_id"], "KnownFrom": row["known_from"]}


def axiom_center_record(row):
    return {"CostCenterReference": "AX-" + row["cost_center_code"], "CostCenterName": row["cost_center_name"], "FacilityReference": row["facility_id"]}
