# Native source engineering review sample

Implementation phase: 7.

Twenty-seven deterministic strata: eight source systems, twelve Axiom archetypes and seven explicit value/state counterexamples. The baseline first-record strata retain legitimate zeros; the additional preregistered nonzero/comparable/zero-budget strata prevent a first-row zero bias. These are synthetic records. Complete round-trip controls, typed dictionaries and all fault outcomes are reviewed alongside these samples.

## EHR-native-layout

```json
{
  "review_case": "EHR-native-layout",
  "file_id": "012a53741c2b84c95a34320b67762762cd8e093332a1b5c6c9b3cacd718c756a",
  "path": "valid/ehr/patient/2025-11.jsonl",
  "mode": "EVENT_ARCHIVE",
  "available_at": "2025-11-28T07:00:00Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "MessageID": "EHR-PATIENT_VERSION-c37baf459fe9d64fcf6f2be6",
    "Record": {
      "AddressLine": "3451 Meadowlark Road Apt 18",
      "AdministrativeSex": "F",
      "AuditKnowledgeClosedAt": "\\N",
      "BirthDate": "04/26/1976",
      "City": "Springfield",
      "DeceasedAt": "\\N",
      "EffectiveTime": "20251115060000+0000",
      "ExtractVersion": "3",
      "FirstName": "Patricia",
      "GenderIdentity": "\\N",
      "GenerationRunId": "master-9aa8405de00cd355060ac1aa",
      "KnownFrom": "20251118060000+0000",
      "LastName": "Sanders",
      "MRN": "MRN-00009451",
      "MiddleName": "Mary",
      "PatientReference": "MRN-00009451",
      "PatientVersionId": "EHR-PATIENT_VERSION-c37baf459fe9d64fcf6f2be6",
      "PostalCode": "62704",
      "PreferredLanguage": "en",
      "RaceEthnicity": "White, non-Hispanic",
      "RecordedAt": "20251118060000+0000",
      "SourceAvailableAt": "20251118070000+0000",
      "SourceRecordId": "patient_2ad10d4eae44b3d017e944f53ee49116/v3",
      "SourceSystem": "EHR_REGISTRATION",
      "StateCode": "IL",
      "Suffix": "\\N",
      "TestEmail": "patriciacollins.e49116@patients.example",
      "TestPhone": "+1-217-555-0100",
      "ValidTo": "\\N"
    },
    "SchemaVersion": "synthetic-source-1",
    "SourceAvailableAt": "2025-11-18T07:00:00Z",
    "SourceSequence": 1
  }
}
```

## WORKDAY-native-layout

```json
{
  "review_case": "WORKDAY-native-layout",
  "file_id": "0731a47e4896c788f0b3c400cb16c066e550db77885ef5958deedb49a1132b8e",
  "path": "valid/workday/worker-assignment/2024-01-05-070000.csv",
  "mode": "IMMUTABLE_VERSION_DELTA",
  "available_at": "2024-01-05T07:00:00Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "AssignmentReference": "WORKDAY-WORKER_ASSIGNMENT-13e1685e9fd22938ed181e42",
    "EmployeeID": "EMP-300006",
    "EmployeeNumber": "EMP-300006",
    "FirstName": "Jack",
    "LastName": "Rodriguez",
    "BirthDate": "06/15/1963",
    "FacilityId": "WORKDAY-FACILITY-0c05765e9024317b9a9e4ec9",
    "HomeLocationId": "WORKDAY-HOME_LOCATION-7e797ff6d7a26e6157a99545",
    "CostCenterReference": "WO-HSP-SPR-MEDICINE",
    "ManagerEmployeeID": "EMP-300001",
    "Role": "PHYSICIAN",
    "Specialty": "Internal Medicine",
    "CredentialCode": "MD",
    "CredentialValidFrom": "07/01/2022",
    "CredentialValidTo": "07/01/2024",
    "WorkerType": "EMPLOYEE",
    "Fte": "1.000000",
    "HourlyCostRate": "171.73",
    "Currency": "USD",
    "HireDate": "03/01/2020",
    "TerminationDate": "\\N",
    "ExtractVersion": "2",
    "EffectiveTime": "12/15/2022 06:00:00 +0000",
    "ValidTo": "01/01/2024 06:00:00 +0000",
    "KnownFrom": "01/05/2024 06:00:00 +0000",
    "AuditKnowledgeClosedAt": "\\N",
    "SourceSystem": "WORKDAY",
    "SourceRecordId": "worker_0f321e9e3b7cfc3e14d2aa742caead21/v2",
    "RecordedAt": "01/05/2024 06:00:00 +0000",
    "SourceAvailableAt": "01/05/2024 07:00:00 +0000",
    "GenerationRunId": "master-5d3d5e0464055ee4d8d26e6d"
  }
}
```

## ADT_BED-native-layout

```json
{
  "review_case": "ADT_BED-native-layout",
  "file_id": "0047832a99a6ca6cb688275eba9420a7d85ccc327ad869e5737e23028cad5d6e",
  "path": "valid/adt-bed/bed-event/2025-11.jsonl",
  "mode": "EVENT_ARCHIVE",
  "available_at": "2025-11-30T23:20:07Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "MessageID": "ADT_BED-BED_EVENT-a4b4bea6f8b4cbd7e401c5d9",
    "Record": {
      "BedReference": "ADT_BED-BED_LOCATION-39edd07ba9b420a87f272d41",
      "CorrectionReference": "\\N",
      "DeliveryAt": "20251103052113+0000",
      "EffectiveTime": "20251103052000+0000",
      "EncounterVersionId": "\\N",
      "EventType": "READY",
      "GenerationRunId": "operations-9fbd04d15b06b3e4147daf46",
      "MessageControlID": "ADT_BED-BED_EVENT-a4b4bea6f8b4cbd7e401c5d9",
      "OccupancyState": "EMPTY",
      "Reason": "CLEANING_COMPLETED",
      "RecordedAt": "20251103052013+0000",
      "Reserved": "N",
      "Sequence": "893",
      "ServiceState": "IN_SERVICE",
      "SourceAvailableAt": "20251103052113+0000",
      "SourceRecordId": "bed_event_001b6e6b104b14c0ff90dbbb9d76788c",
      "SourceSystem": "ADT_BED",
      "StaffingEnabled": "Y",
      "TransferGroupId": "\\N"
    },
    "SchemaVersion": "synthetic-source-1",
    "SourceAvailableAt": "2025-11-03T05:21:13Z",
    "SourceSequence": 1
  }
}
```

## ROSTER_TIME-native-layout

```json
{
  "review_case": "ROSTER_TIME-native-layout",
  "file_id": "0eeb85f0e97a131da7855079c90b4bf1d6ea20acb2611e96602c5d3629fe2a6f",
  "path": "valid/roster-time/staff-shift/2025-01.csv",
  "mode": "IMMUTABLE_VERSION_DELTA",
  "available_at": "2025-01-31T23:04:12Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "ShiftVersionId": "ROSTER_TIME-SHIFT_VERSION-d9100818a706100a7835c6d6",
    "ShiftId": "ROSTER_TIME-SHIFT-e2484ffecbec765efbcc55c2",
    "AssignmentReference": "ROSTER_TIME-WORKER_ASSIGNMENT-e754788a2b9119ed523883d9",
    "LocationId": "ROSTER_TIME-LOCATION-01ce23ef204e6ff58c8ad1ab",
    "CostCenterReference": "ROSTER_TIME-COST_CENTER-d2ab06f37d13ce40773c9866",
    "ShiftType": "WORK",
    "PlannedStart": "20250107190900+0000",
    "PlannedEnd": "20250107202400+0000",
    "ActualStart": "20250107190900+0000",
    "ActualEnd": "20250107202400+0000",
    "WorkedHours": "1.250000",
    "ProductiveHours": "1.000000",
    "PaidNonproductiveHours": "0.250000",
    "UnpaidBreakHours": "0.000000",
    "OvertimeHours": "0.000000",
    "LoadedCost": "67.29",
    "Currency": "USD",
    "PostingGroupKey": "ROSTER_TIME-POSTING_GROUP-24b77859076967ce7b261746",
    "AttendanceStatus": "WORKED",
    "ExtractVersion": "1",
    "KnownFrom": "20250107205400+0000",
    "AuditKnowledgeClosedAt": "\\N",
    "SourceSystem": "ROSTER_TIME",
    "SourceRecordId": "circulator/facility_7990133218ef060b178c3cf8a0825f76/2025-01-07/1/v1",
    "RecordedAt": "20250107205400+0000",
    "SourceAvailableAt": "20250107215400+0000",
    "GenerationRunId": "resources-26840013fc95a08b44ea975b"
  }
}
```

## SUPPLY_PHARMACY-native-layout

```json
{
  "review_case": "SUPPLY_PHARMACY-native-layout",
  "file_id": "003436a60709e9cc88d9390f969e3ada2f3a54e6b21873edb6dd7668db1fe9c3",
  "path": "valid/supply-pharmacy/inventory-movement/2025-06.csv",
  "mode": "ADDITIVE_TRANSACTION",
  "available_at": "2025-06-30T19:25:00Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "MovementId": "SUPPLY_PHARMACY-MOVEMENT-583649515d2db2ef2353895a",
    "LocationId": "SUPPLY_PHARMACY-LOCATION-754d1493e412c31ce94e920d",
    "CatalogItemId": "SUPPLY_PHARMACY-CATALOG_ITEM-77bede38b11d5837f7d48a07",
    "LotId": "SUPPLY_PHARMACY-LOT-82a5edb080b14f758326a5b5",
    "MovementType": "CONSUME",
    "OccurredAt": "20250620031600+0000",
    "QuantityBase": "-10.000000",
    "UnitCost": "0.390000",
    "ExtendedCost": "-3.90",
    "ExpiresOn": "05/19/2026",
    "TransferGroupId": "\\N",
    "ConsumptionGroupKey": "SUPPLY_PHARMACY-CONSUMPTION_GROUP-072d28c90f27dfa32fe854bc",
    "NonpatientWasteBase": "0.000000",
    "ReversesMovementId": "\\N",
    "PostingGroupKey": "SUPPLY_PHARMACY-POSTING_GROUP-58aa36757953b98f979e813a",
    "Currency": "USD",
    "SourceSystem": "INVENTORY_PHARMACY",
    "SourceRecordId": "daily-issue/consumption_bba4bd49005f4a77711417f8c7aade84",
    "RecordedAt": "20250620060000+0000",
    "SourceAvailableAt": "20250620070000+0000",
    "GenerationRunId": "resources-c54d06844d794b1ed8ff7bb9"
  }
}
```

## REVENUE_CYCLE-native-layout

```json
{
  "review_case": "REVENUE_CYCLE-native-layout",
  "file_id": "0115ba76be85cd9fc12bad380ad28aa284d15fd9b30ecbc384433f094fbdd3dc",
  "path": "valid/revenue-cycle/claim-event/2024-07.csv",
  "mode": "ADDITIVE_TRANSACTION",
  "available_at": "2024-07-31T23:38:00Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "ClaimEventId": "REVENUE_CYCLE-CLAIM_EVENT-410ae8852519f300fc60fe05",
    "ClaimId": "REVENUE_CYCLE-CLAIM-c722f2f8384faee81bcbebf4",
    "ClaimLineId": "\\N",
    "DenialCatalogId": "\\N",
    "ReversesClaimEventId": "\\N",
    "EventType": "SUBMITTED",
    "AttemptNo": "1",
    "OccurredAt": "20240722211100+0000",
    "ContractualAdjustmentDelta": "0.00",
    "PayerLiabilityDelta": "0.00",
    "PatientLiabilityDelta": "0.00",
    "CashDelta": "0.00",
    "WriteoffDelta": "0.00",
    "RecognizedRevenueDelta": "0.00",
    "ArDelta": "234.43",
    "PostingGroupKey": "REVENUE_CYCLE-POSTING_GROUP-e1ebffd9dbf950e8ce655784",
    "Currency": "USD",
    "SourceSystem": "RCM_REMITTANCE",
    "SourceRecordId": "claim_8a9fee4819d72182ed25a62f2facc859/0/SUBMITTED",
    "RecordedAt": "20240724061100+0000",
    "SourceAvailableAt": "20240724061100+0000",
    "GenerationRunId": "financial-d9e198b6e9a7a5f97a7a652e"
  }
}
```

## FINANCE_ERP-native-layout

```json
{
  "review_case": "FINANCE_ERP-native-layout",
  "file_id": "16e6e1bc9ab1e0ccbed9fc8dc225eaf39f52f460159ed70bbc84b32183bfad6b",
  "path": "valid/finance-erp/financial-posting/2023-07.csv",
  "mode": "ADDITIVE_TRANSACTION",
  "available_at": "2023-07-31T05:00:00Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "PostingId": "FINANCE_ERP-POSTING-ea9707064c63e4f946da74bb",
    "JournalId": "FINANCE_ERP-JOURNAL-e1a4ad8fb583ea4ec2dd43a6",
    "LineNo": "3",
    "FacilityId": "FINANCE_ERP-FACILITY-0c05765e9024317b9a9e4ec9",
    "CostCenterReference": "FINANCE_ERP-COST_CENTER-3a5a1286daaa325e69cb3ea4",
    "Account": "FINANCE_ERP-ACCOUNT_CATALOG-92e88ca83a36fdb957de3f21",
    "PostingDate": "07/24/2023",
    "ServiceFrom": "07/21/2023",
    "ServiceTo": "07/24/2023",
    "DebitAmount": "0.00",
    "CreditAmount": "7400.00",
    "Currency": "USD",
    "SourceDomain": "REVENUE",
    "SourceGroupKey": "FINANCE_ERP-SOURCE_GROUP-af4674aebb1eec7ae5fd519d",
    "AllocationPoolKey": "\\N",
    "EligibleForAllocation": "N",
    "ReversesPostingId": "\\N",
    "KnownFrom": "20230726050000+0000",
    "SourceSystem": "SYNTHETIC_GL",
    "SourceRecordId": "journal_8e1aa4c6094e21d70fe7b5495edf8be8/3",
    "RecordedAt": "20230726050000+0000",
    "SourceAvailableAt": "20230726050000+0000",
    "GenerationRunId": "financial-781025ba2048d11921f325f3"
  }
}
```

## AXIOM-native-layout

```json
{
  "review_case": "AXIOM-native-layout",
  "file_id": "00a9ba837ed774f45c4ff15881d8d8aaff38e2622fb43b4d06eadbb212cce23b",
  "path": "valid/axiom/finance-monthly/37baeb3356f0468e25bd1d16.csv",
  "mode": "APPEND_VINTAGE",
  "available_at": "2024-12-20T18:00:00Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "FinanceRecordReference": "AXIOM-FINANCE_RECORD-9e49dc540ea29d2eb2aa710f",
    "FacilityId": "AXIOM-FACILITY-a411b48d72552bbfbf97c22c",
    "CostCenterReference": "AX-HSP-RFD-ADMINISTRATION",
    "Account": "\\N",
    "MeasureCode": "PATIENT_DAYS",
    "Period": "07/01/2025",
    "Scenario": "BUDGET",
    "Version": "BUDGET-2025-ORIGINAL",
    "Publication": "20241220180000+0000",
    "Amount": "\\N",
    "Quantity": "580.320000",
    "Unit": "patient_days",
    "ReportID": "AXIOM-SYNTHETIC-FINANCIAL_STATISTICS",
    "OriginalFileID": "AXIOM/FINANCIAL_STATISTICS/BUDGET/BUDGET-2025-ORIGINAL/2025-07-01",
    "SupersedesVintageId": "\\N",
    "SourceSystem": "AXIOM",
    "SourceRecordId": "cost_center_7d935ea992b528c00f1af0d0bc3e9f72/PATIENT_DAYS/2025-07-01/BUDGET/BUDGET-2025-ORIGINAL/patient_days",
    "RecordedAt": "20241220180000+0000",
    "SourceAvailableAt": "20241220180000+0000",
    "GenerationRunId": "financial-07b19c0caf42f20b8319ff0f"
  }
}
```

## axiom-actual-long

```json
{
  "review_case": "axiom-actual-long",
  "file_id": "0379304df693d94de00c69cbe56c4a6b09fcb324f21c47b418cf49bcf74eccf4",
  "path": "valid/axiom/finance-monthly/46dc1c7e75244d8589d0bba7.csv",
  "mode": "REPLACE_DECLARED_SCOPE_VERSION",
  "available_at": "2025-11-06T00:00:00Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "FinanceRecordReference": "AXIOM-FINANCE_RECORD-d32a4d1c89446b320d1d56a0",
    "FacilityId": "AXIOM-FACILITY-46ec4c6a19dc7c49e495a217",
    "CostCenterReference": "AX-HSP-PEO-SURGERY",
    "Account": "AX-LABOR_POOL",
    "MeasureCode": "ACCOUNT_AMOUNT",
    "Period": "10/01/2025",
    "Scenario": "ACTUAL",
    "Version": "ACTUAL-2025-10-01",
    "Publication": "20251106000000+0000",
    "Amount": "0.00",
    "Quantity": "\\N",
    "Unit": "USD",
    "ReportID": "AXIOM-SYNTHETIC-FINANCIAL_PNL",
    "OriginalFileID": "AXIOM/FINANCIAL_PNL/ACTUAL/ACTUAL-2025-10-01/2025-10-01",
    "SupersedesVintageId": "\\N",
    "SourceSystem": "AXIOM",
    "SourceRecordId": "cost_center_1a57763be3fc2320e074ed5aa9a855e7/LABOR_POOL/2025-10-01/ACTUAL/ACTUAL-2025-10-01/USD",
    "RecordedAt": "20251106000000+0000",
    "SourceAvailableAt": "20251106000000+0000",
    "GenerationRunId": "financial-07b19c0caf42f20b8319ff0f"
  }
}
```

## axiom-actual-wide-months

```json
{
  "review_case": "axiom-actual-wide-months",
  "file_id": "8c0672d629b2f0bb8e24627576428dd35f46f751c46ce1948eeb7ceddc6f109f",
  "path": "valid/axiom/reports/actual-wide-months.csv",
  "mode": "DERIVED_MIRROR",
  "available_at": "2026-01-10T00:00:00Z",
  "mirrored_scalar_facts": 12,
  "native_record": {
    "Year": "2023",
    "CostCenter": "cost_center_08b112d0165f81b84313cd9f50749172",
    "Account": "catalog_096258c2d3dac3894d9950fb291bf480",
    "Measure": "ACCOUNT_AMOUNT",
    "Unit": "USD",
    "P01": "0.00",
    "P01Record": "finance_record_c2f4c5d807b1ad8c41f792b0b565b1c0",
    "P02": "0.00",
    "P02Record": "finance_record_f8b0d012602ed57c7c5c74d8567c134c",
    "P03": "0.00",
    "P03Record": "finance_record_5fcf5cf84ea0c0a9c96d1dc9659790c1",
    "P04": "0.00",
    "P04Record": "finance_record_0d51a840305d5297dbaa57fe1e418dc0",
    "P05": "0.00",
    "P05Record": "finance_record_8c5229b61ddbcdbfb1611740de5d2449",
    "P06": "0.00",
    "P06Record": "finance_record_14ee22d4ccee5ec1464e80be0f7cb30e",
    "P07": "0.00",
    "P07Record": "finance_record_b1c550e1862af1ca4d1fddafb78e2103",
    "P08": "0.00",
    "P08Record": "finance_record_b8787de10ecf97d91aaa1714885c4f65",
    "P09": "0.00",
    "P09Record": "finance_record_a4920abb7ce4be486b34eedec30dffbd",
    "P10": "0.00",
    "P10Record": "finance_record_b4dbfee2d31c26168b940311dff626a4",
    "P11": "0.00",
    "P11Record": "finance_record_79c717e65197e986dca2a34f747b45d5",
    "P12": "0.00",
    "P12Record": "finance_record_b4fe6778b8590c3045d08f4bfc01f6d7"
  }
}
```

## axiom-actual-with-adjustments

```json
{
  "review_case": "axiom-actual-with-adjustments",
  "file_id": "c1db3ee5f05d66872ec258710de711c6a18bfb2393fecdaa9a04221b77bba481",
  "path": "valid/axiom/reports/actual-with-adjustments.csv",
  "mode": "DERIVED_MIRROR",
  "available_at": "2026-01-10T00:00:00Z",
  "mirrored_scalar_facts": 2,
  "native_record": {
    "Period": "2025-12-01",
    "CostCenter": "cost_center_ede90e24a661c450df8de75587c9e8b2",
    "Account": "catalog_b41384d66339e2b541f86750ee0754dc",
    "Measure": "ACCOUNT_AMOUNT",
    "Unit": "USD",
    "OriginalRecord": "finance_record_f82e0bec6fa1470a4298563e9fc348f1",
    "ReplacementRecord": "finance_record_00dbd797cdf749b7140a91568ef9225e",
    "OriginalValue": "0.00",
    "Adjustment": "0.00",
    "ReportedValue": "0.00"
  }
}
```

## axiom-budget-original

```json
{
  "review_case": "axiom-budget-original",
  "file_id": "0a705db6071bfc3fec0f4351852fdc3ba5b5fcf85929ae47680c172567037072",
  "path": "valid/axiom/finance-monthly/c5bc809a23054e29f47389b3.csv",
  "mode": "APPEND_VINTAGE",
  "available_at": "2022-12-20T18:00:00Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "FinanceRecordReference": "AXIOM-FINANCE_RECORD-0387979e43fe7bf15c33869f",
    "FacilityId": "AXIOM-FACILITY-0c05765e9024317b9a9e4ec9",
    "CostCenterReference": "AX-HSP-SPR-FACILITIES",
    "Account": "AX-DRUG_POOL",
    "MeasureCode": "ACCOUNT_AMOUNT",
    "Period": "04/01/2023",
    "Scenario": "BUDGET",
    "Version": "BUDGET-2023-ORIGINAL",
    "Publication": "20221220180000+0000",
    "Amount": "0.00",
    "Quantity": "\\N",
    "Unit": "USD",
    "ReportID": "AXIOM-SYNTHETIC-FINANCIAL_PNL",
    "OriginalFileID": "AXIOM/FINANCIAL_PNL/BUDGET/BUDGET-2023-ORIGINAL/2023-04-01",
    "SupersedesVintageId": "\\N",
    "SourceSystem": "AXIOM",
    "SourceRecordId": "cost_center_7ea3c0bcab8be893a8f82a4d1d50ce74/DRUG_POOL/2023-04-01/BUDGET/BUDGET-2023-ORIGINAL/USD",
    "RecordedAt": "20221220180000+0000",
    "SourceAvailableAt": "20221220180000+0000",
    "GenerationRunId": "financial-07b19c0caf42f20b8319ff0f"
  }
}
```

## axiom-budget-revised

```json
{
  "review_case": "axiom-budget-revised",
  "file_id": "11e072f803fb6c404cae4dbf0b44e9cbe90fd6d6bd2f99b2b7a093f352ffc5a3",
  "path": "valid/axiom/finance-monthly/62e36000da0075832fd24eb6.csv",
  "mode": "APPEND_VINTAGE",
  "available_at": "2024-06-20T17:00:00Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "FinanceRecordReference": "AXIOM-FINANCE_RECORD-2f150ca7182c22ba26acc053",
    "FacilityId": "AXIOM-FACILITY-0c05765e9024317b9a9e4ec9",
    "CostCenterReference": "AX-HSP-SPR-ENVIRONMENTAL",
    "Account": "AX-OVERHEAD_POOL",
    "MeasureCode": "ACCOUNT_AMOUNT",
    "Period": "12/01/2024",
    "Scenario": "BUDGET",
    "Version": "BUDGET-2024-MIDYEAR",
    "Publication": "20240620170000+0000",
    "Amount": "0.00",
    "Quantity": "\\N",
    "Unit": "USD",
    "ReportID": "AXIOM-SYNTHETIC-FINANCIAL_PNL",
    "OriginalFileID": "AXIOM/FINANCIAL_PNL/BUDGET/BUDGET-2024-MIDYEAR/2024-12-01",
    "SupersedesVintageId": "BUDGET-2024-ORIGINAL",
    "SourceSystem": "AXIOM",
    "SourceRecordId": "cost_center_ede90e24a661c450df8de75587c9e8b2/OVERHEAD_POOL/2024-12-01/BUDGET/BUDGET-2024-MIDYEAR/USD",
    "RecordedAt": "20240620170000+0000",
    "SourceAvailableAt": "20240620170000+0000",
    "GenerationRunId": "financial-07b19c0caf42f20b8319ff0f"
  }
}
```

## axiom-forecast-amount

```json
{
  "review_case": "axiom-forecast-amount",
  "file_id": "07a582f089f82db83d79efc7535634379428c629601ee675a111815d732ab4db",
  "path": "valid/axiom/finance-monthly/d852df6e88c0bc1d0d5d816d.csv",
  "mode": "APPEND_VINTAGE",
  "available_at": "2024-12-20T18:00:00Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "FinanceRecordReference": "AXIOM-FINANCE_RECORD-9c6060d79f7788fea65ce80c",
    "FacilityId": "AXIOM-FACILITY-0c05765e9024317b9a9e4ec9",
    "CostCenterReference": "AX-HSP-SPR-MEDICINE",
    "Account": "AX-LABOR_POOL",
    "MeasureCode": "ACCOUNT_AMOUNT",
    "Period": "02/01/2025",
    "Scenario": "FORECAST",
    "Version": "FORECAST-2025-01-01",
    "Publication": "20241220180000+0000",
    "Amount": "215469.21",
    "Quantity": "\\N",
    "Unit": "USD",
    "ReportID": "AXIOM-SYNTHETIC-FINANCIAL_PNL",
    "OriginalFileID": "AXIOM/FINANCIAL_PNL/FORECAST/FORECAST-2025-01-01/2025-02-01",
    "SupersedesVintageId": "\\N",
    "SourceSystem": "AXIOM",
    "SourceRecordId": "cost_center_68ea4703e95fc8f06b1d9407840569cb/LABOR_POOL/2025-02-01/FORECAST/FORECAST-2025-01-01/USD",
    "RecordedAt": "20241220180000+0000",
    "SourceAvailableAt": "20241220180000+0000",
    "GenerationRunId": "financial-07b19c0caf42f20b8319ff0f"
  }
}
```

## axiom-forecast-drivers

```json
{
  "review_case": "axiom-forecast-drivers",
  "file_id": "dceeecedc739b8dbbfebbed282e1da39bd0daa732fc20d80b5c3ad8a9851264b",
  "path": "valid/axiom/reports/forecast-drivers.csv",
  "mode": "DERIVED_MIRROR",
  "available_at": "2026-01-10T00:00:00Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "FinanceRecord": "finance_record_004adee4567cb09eed2e492d379f72d3",
    "Publication": "2025-09-19T17:00:00Z",
    "Period": "2025-10-01",
    "CalendarDays": "31",
    "MonthlyAmount": "231461.46",
    "DailyPlanRate": "7466.498710",
    "Unit": "USD/calendar_day",
    "Basis": "DERIVED_FROM_ACCEPTED_FORECAST_NOT_A_CAUSAL_FEATURE"
  }
}
```

## axiom-statistics-volume

```json
{
  "review_case": "axiom-statistics-volume",
  "file_id": "00a9ba837ed774f45c4ff15881d8d8aaff38e2622fb43b4d06eadbb212cce23b",
  "path": "valid/axiom/finance-monthly/37baeb3356f0468e25bd1d16.csv",
  "mode": "APPEND_VINTAGE",
  "available_at": "2024-12-20T18:00:00Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "FinanceRecordReference": "AXIOM-FINANCE_RECORD-9e49dc540ea29d2eb2aa710f",
    "FacilityId": "AXIOM-FACILITY-a411b48d72552bbfbf97c22c",
    "CostCenterReference": "AX-HSP-RFD-ADMINISTRATION",
    "Account": "\\N",
    "MeasureCode": "PATIENT_DAYS",
    "Period": "07/01/2025",
    "Scenario": "BUDGET",
    "Version": "BUDGET-2025-ORIGINAL",
    "Publication": "20241220180000+0000",
    "Amount": "\\N",
    "Quantity": "580.320000",
    "Unit": "patient_days",
    "ReportID": "AXIOM-SYNTHETIC-FINANCIAL_STATISTICS",
    "OriginalFileID": "AXIOM/FINANCIAL_STATISTICS/BUDGET/BUDGET-2025-ORIGINAL/2025-07-01",
    "SupersedesVintageId": "\\N",
    "SourceSystem": "AXIOM",
    "SourceRecordId": "cost_center_7d935ea992b528c00f1af0d0bc3e9f72/PATIENT_DAYS/2025-07-01/BUDGET/BUDGET-2025-ORIGINAL/patient_days",
    "RecordedAt": "20241220180000+0000",
    "SourceAvailableAt": "20241220180000+0000",
    "GenerationRunId": "financial-07b19c0caf42f20b8319ff0f"
  }
}
```

## axiom-statistics-workforce

```json
{
  "review_case": "axiom-statistics-workforce",
  "file_id": "01a81c81c7de7b7822229ea1f1ef86a27dda16d547c9c9c45e7d3e238535de27",
  "path": "valid/axiom/finance-monthly/ff7408817a64e5839f0e009d.csv",
  "mode": "REPLACE_DECLARED_SCOPE_VERSION",
  "available_at": "2024-02-06T00:00:00Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "FinanceRecordReference": "AXIOM-FINANCE_RECORD-cb6315648144a7bca7dde9c3",
    "FacilityId": "AXIOM-FACILITY-a411b48d72552bbfbf97c22c",
    "CostCenterReference": "AX-HSP-RFD-SURGERY",
    "Account": "\\N",
    "MeasureCode": "FTE",
    "Period": "01/01/2024",
    "Scenario": "ACTUAL",
    "Version": "ACTUAL-2024-01-01",
    "Publication": "20240206000000+0000",
    "Amount": "\\N",
    "Quantity": "0.000000",
    "Unit": "FTE",
    "ReportID": "AXIOM-SYNTHETIC-FINANCIAL_STATISTICS",
    "OriginalFileID": "AXIOM/FINANCIAL_STATISTICS/ACTUAL/ACTUAL-2024-01-01/2024-01-01",
    "SupersedesVintageId": "\\N",
    "SourceSystem": "AXIOM",
    "SourceRecordId": "cost_center_b7b7769b78c862a466158356e2450adf/FTE/2024-01-01/ACTUAL/ACTUAL-2024-01-01/FTE",
    "RecordedAt": "20240206000000+0000",
    "SourceAvailableAt": "20240206000000+0000",
    "GenerationRunId": "financial-07b19c0caf42f20b8319ff0f"
  }
}
```

## axiom-variance-comparison

```json
{
  "review_case": "axiom-variance-comparison",
  "file_id": "35fae3d56026413725c7ead3a1c7922dec7ee3145a98c6c55a60b1953200cdd0",
  "path": "valid/axiom/reports/variance-comparison.csv",
  "mode": "DERIVED_MIRROR",
  "available_at": "2026-01-10T00:00:00Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "ActualRecord": "finance_record_000086b2c8f79abe8ed5ed13ebef7e51",
    "BudgetRecord": "\\N",
    "Actual": "0.00",
    "Budget": "\\N",
    "Variance": "\\N",
    "VariancePercent": "\\N",
    "ComparisonState": "NO_BUDGET",
    "Unit": "USD"
  }
}
```

## axiom-account-mapping

```json
{
  "review_case": "axiom-account-mapping",
  "file_id": "8e2dd47231bd362f01bc582d3bd48794a7a610f06d39dc52a43f8b087e140950",
  "path": "valid/axiom/reports/account-mapping.csv",
  "mode": "DERIVED_MIRROR",
  "available_at": "2026-01-10T00:00:00Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "Account": "AX-OVERHEAD_DIRECT",
    "CanonicalAccount": "catalog_096258c2d3dac3894d9950fb291bf480",
    "Description": "overhead direct expense",
    "Class": "EXPENSE",
    "NormalBalance": "DEBIT"
  }
}
```

## axiom-center-mapping

```json
{
  "review_case": "axiom-center-mapping",
  "file_id": "1a270b2e503d532a76517baab0e423b96695d3e26ed343d69c11cca25c2cc13c",
  "path": "valid/axiom/reports/center-mapping.csv",
  "mode": "DERIVED_MIRROR",
  "available_at": "2026-01-10T00:00:00Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "CostCenter": "AX-HSP-SPR-PHARMACY",
    "CanonicalCostCenter": "cost_center_08b112d0165f81b84313cd9f50749172",
    "Description": "Pharmacy",
    "Facility": "facility_a6a95cfdcf7df4bfa7fe88c206195c24",
    "Parent": "cost_center_c013afac2864ae48f3b64f1905e361e3"
  }
}
```

## nonzero-actual

```json
{
  "review_case": "nonzero-actual",
  "file_id": "0379304df693d94de00c69cbe56c4a6b09fcb324f21c47b418cf49bcf74eccf4",
  "path": "valid/axiom/finance-monthly/46dc1c7e75244d8589d0bba7.csv",
  "mode": "REPLACE_DECLARED_SCOPE_VERSION",
  "available_at": "2025-11-06T00:00:00Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "FinanceRecordReference": "AXIOM-FINANCE_RECORD-01d80eaa896a345cf6a644dd",
    "FacilityId": "AXIOM-FACILITY-0c05765e9024317b9a9e4ec9",
    "CostCenterReference": "AX-HSP-SPR-SURGERY",
    "Account": "AX-CONTRA_REVENUE",
    "MeasureCode": "ACCOUNT_AMOUNT",
    "Period": "10/01/2025",
    "Scenario": "ACTUAL",
    "Version": "ACTUAL-2025-10-01",
    "Publication": "20251106000000+0000",
    "Amount": "246408.10",
    "Quantity": "\\N",
    "Unit": "USD",
    "ReportID": "AXIOM-SYNTHETIC-FINANCIAL_PNL",
    "OriginalFileID": "AXIOM/FINANCIAL_PNL/ACTUAL/ACTUAL-2025-10-01/2025-10-01",
    "SupersedesVintageId": "\\N",
    "SourceSystem": "AXIOM",
    "SourceRecordId": "cost_center_2e630aee9f11fa16e57314a0d7b9abf9/CONTRA_REVENUE/2025-10-01/ACTUAL/ACTUAL-2025-10-01/USD",
    "RecordedAt": "20251106000000+0000",
    "SourceAvailableAt": "20251106000000+0000",
    "GenerationRunId": "financial-07b19c0caf42f20b8319ff0f"
  }
}
```

## nonzero-revised-budget

```json
{
  "review_case": "nonzero-revised-budget",
  "file_id": "11e072f803fb6c404cae4dbf0b44e9cbe90fd6d6bd2f99b2b7a093f352ffc5a3",
  "path": "valid/axiom/finance-monthly/62e36000da0075832fd24eb6.csv",
  "mode": "APPEND_VINTAGE",
  "available_at": "2024-06-20T17:00:00Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "FinanceRecordReference": "AXIOM-FINANCE_RECORD-dbcb0aea5a1e18b214ffea7d",
    "FacilityId": "AXIOM-FACILITY-a411b48d72552bbfbf97c22c",
    "CostCenterReference": "AX-HSP-RFD-HR",
    "Account": "AX-LABOR_POOL",
    "MeasureCode": "ACCOUNT_AMOUNT",
    "Period": "12/01/2024",
    "Scenario": "BUDGET",
    "Version": "BUDGET-2024-MIDYEAR",
    "Publication": "20240620170000+0000",
    "Amount": "29758.40",
    "Quantity": "\\N",
    "Unit": "USD",
    "ReportID": "AXIOM-SYNTHETIC-FINANCIAL_PNL",
    "OriginalFileID": "AXIOM/FINANCIAL_PNL/BUDGET/BUDGET-2024-MIDYEAR/2024-12-01",
    "SupersedesVintageId": "BUDGET-2024-ORIGINAL",
    "SourceSystem": "AXIOM",
    "SourceRecordId": "cost_center_71f95c51a9d0dae6252355152e3f642f/LABOR_POOL/2024-12-01/BUDGET/BUDGET-2024-MIDYEAR/USD",
    "RecordedAt": "20240620170000+0000",
    "SourceAvailableAt": "20240620170000+0000",
    "GenerationRunId": "financial-07b19c0caf42f20b8319ff0f"
  }
}
```

## nonzero-workforce-statistic

```json
{
  "review_case": "nonzero-workforce-statistic",
  "file_id": "01a81c81c7de7b7822229ea1f1ef86a27dda16d547c9c9c45e7d3e238535de27",
  "path": "valid/axiom/finance-monthly/ff7408817a64e5839f0e009d.csv",
  "mode": "REPLACE_DECLARED_SCOPE_VERSION",
  "available_at": "2024-02-06T00:00:00Z",
  "mirrored_scalar_facts": 1,
  "native_record": {
    "FinanceRecordReference": "AXIOM-FINANCE_RECORD-98b3b6dce05cc156c7c68c64",
    "FacilityId": "AXIOM-FACILITY-46ec4c6a19dc7c49e495a217",
    "CostCenterReference": "AX-HSP-PEO-MEDICINE",
    "Account": "\\N",
    "MeasureCode": "FTE",
    "Period": "01/01/2024",
    "Scenario": "ACTUAL",
    "Version": "ACTUAL-2024-01-01",
    "Publication": "20240206000000+0000",
    "Amount": "\\N",
    "Quantity": "19.841467",
    "Unit": "FTE",
    "ReportID": "AXIOM-SYNTHETIC-FINANCIAL_STATISTICS",
    "OriginalFileID": "AXIOM/FINANCIAL_STATISTICS/ACTUAL/ACTUAL-2024-01-01/2024-01-01",
    "SupersedesVintageId": "\\N",
    "SourceSystem": "AXIOM",
    "SourceRecordId": "cost_center_f28b9e300754f62f24c73d76aa4275b1/FTE/2024-01-01/ACTUAL/ACTUAL-2024-01-01/FTE",
    "RecordedAt": "20240206000000+0000",
    "SourceAvailableAt": "20240206000000+0000",
    "GenerationRunId": "financial-07b19c0caf42f20b8319ff0f"
  }
}
```

## nonzero-wide-history

```json
{
  "review_case": "nonzero-wide-history",
  "file_id": "8c0672d629b2f0bb8e24627576428dd35f46f751c46ce1948eeb7ceddc6f109f",
  "path": "valid/axiom/reports/actual-wide-months.csv",
  "mode": "DERIVED_MIRROR",
  "available_at": "2026-01-10T00:00:00Z",
  "mirrored_scalar_facts": 12,
  "native_record": {
    "Year": "2023",
    "CostCenter": "cost_center_08b112d0165f81b84313cd9f50749172",
    "Account": "catalog_77cb988bb7f4ee120716a9a0846099a3",
    "Measure": "ACCOUNT_AMOUNT",
    "Unit": "USD",
    "P01": "656.25",
    "P01Record": "finance_record_cf8cbc973f04878314a5c626763e0e17",
    "P02": "820.00",
    "P02Record": "finance_record_601ea3ac24eea9cd7d234c34a169d036",
    "P03": "1017.50",
    "P03Record": "finance_record_a6d8c263563c801fbbf67d5def35d181",
    "P04": "990.00",
    "P04Record": "finance_record_a6e20240bb468437092b5ee58d7ebd15",
    "P05": "1040.00",
    "P05Record": "finance_record_fc31d4a6b6056c9403b58bf23264b3f8",
    "P06": "777.50",
    "P06Record": "finance_record_80633cd291870edcbfcdd76649ff0152",
    "P07": "721.25",
    "P07Record": "finance_record_cfddc1190b7112d53c8244ebeda4b2e0",
    "P08": "886.25",
    "P08Record": "finance_record_0931717f2e7db86d285ae42dbf54d71e",
    "P09": "615.00",
    "P09Record": "finance_record_80e9a326770679ba18e4d040f0f23b4c",
    "P10": "662.50",
    "P10Record": "finance_record_533683f7eb2808cec1b6f040bd4ea7ef",
    "P11": "1208.75",
    "P11Record": "finance_record_498e277c0884189d786dc4ce07d36da0",
    "P12": "352.50",
    "P12Record": "finance_record_b6d565cc0ae24f6500fad458b4244869"
  }
}
```

## nonzero-final-close-confirmation

```json
{
  "review_case": "nonzero-final-close-confirmation",
  "file_id": "c1db3ee5f05d66872ec258710de711c6a18bfb2393fecdaa9a04221b77bba481",
  "path": "valid/axiom/reports/actual-with-adjustments.csv",
  "mode": "DERIVED_MIRROR",
  "available_at": "2026-01-10T00:00:00Z",
  "mirrored_scalar_facts": 2,
  "native_record": {
    "Period": "2025-12-01",
    "CostCenter": "cost_center_3337062e2276c29de2f8fe16fab5e0c5",
    "Account": "",
    "Measure": "PATIENT_DAYS",
    "Unit": "patient_days",
    "OriginalRecord": "finance_record_135c3828086b46aa73ac42ae9e15109e",
    "ReplacementRecord": "finance_record_01301d4d77830a9a73b6ac54521d6acf",
    "OriginalValue": "28.120833",
    "Adjustment": "0.000000",
    "ReportedValue": "28.120833"
  }
}
```

## comparable-budget-variance

```json
{
  "review_case": "comparable-budget-variance",
  "file_id": "35fae3d56026413725c7ead3a1c7922dec7ee3145a98c6c55a60b1953200cdd0",
  "path": "valid/axiom/reports/variance-comparison.csv",
  "mode": "DERIVED_MIRROR",
  "available_at": "2026-01-10T00:00:00Z",
  "mirrored_scalar_facts": 2,
  "native_record": {
    "ActualRecord": "finance_record_00269617e90b6f63d2d9de4178ec5c3a",
    "BudgetRecord": "finance_record_0d1f997da9ddde3899633c6f130a17b3",
    "Actual": "465182.50",
    "Budget": "480150.38",
    "Variance": "-14967.88",
    "VariancePercent": "-3.117332",
    "ComparisonState": "COMPARABLE",
    "Unit": "USD"
  }
}
```

## explicit-zero-budget

```json
{
  "review_case": "explicit-zero-budget",
  "file_id": "35fae3d56026413725c7ead3a1c7922dec7ee3145a98c6c55a60b1953200cdd0",
  "path": "valid/axiom/reports/variance-comparison.csv",
  "mode": "DERIVED_MIRROR",
  "available_at": "2026-01-10T00:00:00Z",
  "mirrored_scalar_facts": 2,
  "native_record": {
    "ActualRecord": "finance_record_000a94846bb71e8dec89a46f835c5d56",
    "BudgetRecord": "finance_record_e1fe16c0552d33b6c3885d418a02435f",
    "Actual": "0.00",
    "Budget": "0.00",
    "Variance": "0.00",
    "VariancePercent": "\\N",
    "ComparisonState": "ZERO_BUDGET",
    "Unit": "USD"
  }
}
```
