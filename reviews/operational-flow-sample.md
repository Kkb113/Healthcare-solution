# Operational patient-flow review

Phase 4: user-designated synthetic operational plausibility review. Times are UTC. No licensed clinical endorsement.
Admission care includes monitored boarding; only physical licensed-bed intervals contribute to bed occupancy.

## Case 1: Mary Rosado

Birth 1927-02-13; recorded sex F; Prairie Creek Community Hospital; strata: BOARDING_OVER_DAY, BOARDING_OVER_HOUR, ED, MAINTENANCE_SEASON, PRIVATE_ISOLATION, TRANSFER, UNMET_EXTERNAL_TRANSFER, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_c43fdd49f4a48d53c94aae476b0db9ca; episode episode_f1aa8403fa750367bbd2d5259e471b8f; acuity 3; 2024-07-30T19:23:00Z arrival; 2024-07-30T19:23:00Z decision; 2024-07-30T19:38:00Z admission; 2024-07-31T19:38:00Z end; TRANSFER.
Time from admission/opening to first placement: 24.000 hours.
- Source operational note @ 2024-07-30T19:38:00Z: Placement assessment for Mary Rosado, age 97: suspected transmissible respiratory illness; isolation-capable private room requested. Recorded at 2024-07-30T19:38:00Z.
- Source operational note @ 2024-07-31T19:38:00Z: Placement disposition for encounter encounter_c43fdd49f4a48d53c94aae476b0db9ca: external transfer at 2024-07-31T19:38:00Z after 24 hours from inpatient admission awaiting a compatible bed. Cause: COMPATIBLE_CAPACITY_EXHAUSTED,ISOLATION_COHORT_REQUIRED,MAINTENANCE_REDUCED_CAPACITY. Receiving care and later outcome are outside the modeled network.

## Case 2: Sarah Scott

Birth 1976-12-22; recorded sex F; Oakwood Community Hospital; strata: CARRY_IN, DIRECT, HOME, ICU_STEPDOWN, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_0ab04fb6e025466792462e6bbaaa4e01; episode episode_510261ad5fbba25ec71424753ab47515; acuity 2; 2022-12-30T00:00:00Z arrival; 2022-12-30T00:00:00Z decision; 2022-12-30T00:15:00Z admission; 2023-01-07T22:00:00Z end; HOME.
Time from admission/opening to first placement: 0.000 hours.
- ICU-R03-B1: 2023-01-01T06:00:00Z to 2023-01-03T06:00:00Z, 48.000 hours.
- SURG-R02-B2: 2023-01-03T06:00:00Z to 2023-01-07T22:00:00Z, 112.000 hours.
- 2023-01-01T06:00:00Z OPENING: OBSERVED_OPENING_CENSUS; transfer none; delivered 2023-01-01T12:01:18Z.
- 2023-01-03T06:00:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_9d1c42b2e0bda12a6a324c33064039b5; delivered 2023-01-03T06:01:08Z.
- 2023-01-03T06:00:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_9d1c42b2e0bda12a6a324c33064039b5; delivered 2023-01-03T06:01:09Z.
- 2023-01-07T22:00:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-01-07T22:01:29Z.

## Case 3: David Jenkins

Birth 1968-08-22; recorded sex M; Riverbend Community Hospital; strata: DEATH, DIRECT, ICU, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_2beb21e58d68d6b4ba5f4d17e3b8e6ec; episode episode_97a92c47236ae39fcc27e5c717c1dbe2; acuity 1; 2025-12-22T09:00:00Z arrival; 2025-12-22T09:00:00Z decision; 2025-12-22T09:15:00Z admission; 2025-12-23T12:00:00Z end; DEATH.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R01-B1: 2025-12-22T09:25:00Z to 2025-12-23T12:00:00Z, 26.583 hours.
- 2025-12-22T09:25:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2025-12-22T09:26:26Z.
- 2025-12-23T12:00:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-12-23T12:00:37Z.

## Case 4: Ashley Graham

Birth 1980-07-02; recorded sex F; Riverbend Community Hospital; strata: ELECTIVE, OPEN, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_9d383afdddb6fb2e0b98fc2ed5a03b8a; episode episode_dc31f512cdeccba8a021ac343c36320a; acuity 2; 2025-12-29T14:32:00Z arrival; 2025-12-29T14:32:00Z decision; 2025-12-29T14:47:00Z admission; CENSORED end; OPEN.
Time from admission/opening to first placement: 0.167 hours.
- SURG-R05-B1: 2025-12-29T14:57:00Z to 2026-01-01T06:00:00Z, 63.050 hours.
- 2025-12-29T14:57:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2025-12-29T14:58:25Z.

## Case 5: Daniel Fraser

Birth 1991-04-09; recorded sex M; Riverbend Community Hospital; strata: BOARDING_OVER_HOUR, HOME, SITE_TRANSFER, TRANSFER, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_524caf10670e581a7e2de4cf9a8681e8; episode episode_1406b05306bd7e8cb261b877cf28af98; acuity 2; 2024-02-21T16:17:00Z arrival; 2024-02-21T16:17:00Z decision; 2024-02-21T16:32:00Z admission; 2024-03-05T19:47:00Z end; HOME.
Time from admission/opening to first placement: 19.033 hours.
- MED-R04-B1: 2024-02-22T11:34:00Z to 2024-03-05T19:47:00Z, 296.217 hours.
- 2024-02-22T11:34:00Z OCCUPY: SITE_TRANSFER_IN; transfer site_transfer_6377d923b5280be347018d08543cf24a; delivered 2024-02-22T11:34:45Z.
- 2024-03-05T19:47:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-03-05T19:48:14Z.
- Source operational note @ 2024-02-21T16:32:00Z: Transfer coordination for encounter encounter_524caf10670e581a7e2de4cf9a8681e8: accepted continuation at HSP-PEO; receiving arrival is observed at 2024-02-21T16:17:00Z. Later care outcome is not yet established.

## Case 6: Lewis Silva

Birth 1968-10-17; recorded sex M; Prairie Creek Community Hospital; strata: DIRECT, MAINTENANCE_SEASON, TRANSFER, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_59d47bed7966a23a9f22eee1a10e9263; episode episode_57ba065c9b668bc0ba5d5ce06c39546a; acuity 2; 2024-06-18T05:37:00Z arrival; 2024-06-18T05:37:00Z decision; 2024-06-18T05:52:00Z admission; 2024-06-22T13:37:00Z end; TRANSFER.
Time from admission/opening to first placement: 0.167 hours.
- MED-R02-B1: 2024-06-18T06:02:00Z to 2024-06-22T13:37:00Z, 103.583 hours.
- 2024-06-18T06:02:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2024-06-18T06:02:25Z.
- 2024-06-22T13:37:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-06-22T13:37:35Z.

## Case 7: Paul Beil

Birth 1970-11-18; recorded sex M; Riverbend Community Hospital; strata: ELECTIVE, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_fe36b5874cf82d165897a6fe74d7249c; episode episode_c0ac8a4bf5e41de2b1fb8a2c856e2eb3; acuity 3; 2025-03-17T12:00:00Z arrival; 2025-03-17T12:00:00Z decision; 2025-03-17T12:15:00Z admission; 2025-03-21T18:00:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- SURG-R03-B1: 2025-03-17T12:25:00Z to 2025-03-21T18:00:00Z, 101.583 hours.
- 2025-03-17T12:25:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED,ELECTIVE_MORNING_SLOT_REQUIRED; transfer none; delivered 2025-03-17T12:25:36Z.
- 2025-03-21T18:00:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-03-21T18:01:02Z.

## Case 8: Kelly Williams

Birth 1968-12-20; recorded sex M; Riverbend Community Hospital; strata: ELECTIVE, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_290a2c7aba8b812c235c46c2f1311911; episode episode_76f7a127d55f49fc6c17a077562cc940; acuity 2; 2023-09-14T15:20:00Z arrival; 2023-09-14T15:20:00Z decision; 2023-09-14T15:35:00Z admission; 2023-09-17T06:20:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- SURG-R05-B1: 2023-09-14T15:45:00Z to 2023-09-17T06:20:00Z, 62.583 hours.
- 2023-09-14T15:45:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-09-14T15:46:21Z.
- 2023-09-17T06:20:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-09-17T06:21:26Z.

## Case 9: Sonia Carmichael

Birth 1955-01-16; recorded sex F; Oakwood Community Hospital; strata: ELECTIVE, HOME, ICU_STEPDOWN, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_48d2ff74226c862269d0c845ad969d45; episode episode_40b2a5b3fb094a36ea7de6070916bf03; acuity 2; 2025-07-08T15:16:00Z arrival; 2025-07-08T15:16:00Z decision; 2025-07-08T15:31:00Z admission; 2025-07-13T04:16:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R01-B1: 2025-07-08T15:41:00Z to 2025-07-10T04:12:00Z, 36.517 hours.
- SURG-R05-B1: 2025-07-10T04:12:00Z to 2025-07-13T04:16:00Z, 72.067 hours.
- 2025-07-08T15:41:00Z OCCUPY: FIRST_PLACEMENT;WARD_OVERFLOW_ICU; transfer none; delivered 2025-07-08T15:42:04Z.
- 2025-07-10T04:12:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_69b9351d4046a3093144a625f45b31cc; delivered 2025-07-10T04:12:34Z.
- 2025-07-10T04:12:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_69b9351d4046a3093144a625f45b31cc; delivered 2025-07-10T04:13:27Z.
- 2025-07-13T04:16:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-07-13T04:16:41Z.

## Case 10: Mary Harding

Birth 1945-10-07; recorded sex F; Prairie Creek Community Hospital; strata: ED, HOME, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_62be3156dc2e8453b68206a1416b4d18; episode episode_e0f304f14da070571ffb784e28fcdc8a; acuity 3; 2023-11-08T09:09:00Z arrival; 2023-11-08T09:09:00Z decision; 2023-11-08T09:24:00Z admission; 2023-11-13T04:09:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R05-B1: 2023-11-08T09:34:00Z to 2023-11-13T04:09:00Z, 114.583 hours.
- 2023-11-08T09:34:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-11-08T09:35:31Z.
- 2023-11-13T04:09:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-11-13T04:10:52Z.

## Case 11: Timothy York-Long

Birth 1945-10-18; recorded sex M; Oakwood Community Hospital; strata: BOARDING_OVER_HOUR, ED, TRANSFER, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_9e2cff02bb88ce0c44a80f92d1b54743; episode episode_c2b8c44efb3f9e15628aa6b6b272a8e9; acuity 2; 2023-02-27T15:04:00Z arrival; 2023-02-27T15:04:00Z decision; 2023-02-27T15:19:00Z admission; 2023-03-05T16:45:00Z end; TRANSFER.
Time from admission/opening to first placement: 16.850 hours.
- SURG-R04-B1: 2023-02-28T08:10:00Z to 2023-03-05T16:45:00Z, 128.583 hours.
- 2023-02-28T08:10:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED; transfer none; delivered 2023-02-28T08:11:17Z.
- 2023-03-05T16:45:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-03-05T16:45:44Z.

## Case 12: Robert Peach

Birth 1941-01-20; recorded sex M; Oakwood Community Hospital; strata: ELECTIVE, HOME, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_ba5b42b70a2d40e53d42c053a05b3ea9; episode episode_618fa0ffc9a8880f5a37d736d3fba659; acuity 3; 2025-03-10T15:37:00Z arrival; 2025-03-10T15:37:00Z decision; 2025-03-10T15:52:00Z admission; 2025-03-14T04:37:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- SURG-R01-B2: 2025-03-10T16:02:00Z to 2025-03-14T04:37:00Z, 84.583 hours.
- 2025-03-10T16:02:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2025-03-10T16:02:26Z.
- 2025-03-14T04:37:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-03-14T04:37:40Z.

## Case 13: Sammy Pacheco

Birth 1944-10-19; recorded sex M; Riverbend Community Hospital; strata: ELECTIVE, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_560c58ad2cea00d6445fa882dd25f5cd; episode episode_689c50fd2c754ef9368bf817f4ea60eb; acuity 3; 2023-10-03T15:33:00Z arrival; 2023-10-03T15:33:00Z decision; 2023-10-03T15:48:00Z admission; 2023-10-08T16:33:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- SURG-R03-B2: 2023-10-03T15:58:00Z to 2023-10-08T16:33:00Z, 120.583 hours.
- 2023-10-03T15:58:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-10-03T15:58:55Z.
- 2023-10-08T16:33:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-10-08T16:33:39Z.

## Case 14: William McArthur

Birth 1947-12-19; recorded sex M; Riverbend Community Hospital; strata: ELECTIVE, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_3490ea5fcd767952b9daf17991a7adb8; episode episode_dff837355f4d63d10ee4a33c2a092b0f; acuity 3; 2025-09-15T14:33:00Z arrival; 2025-09-15T14:33:00Z decision; 2025-09-15T14:48:00Z admission; 2025-09-20T11:33:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R03-B2: 2025-09-15T14:58:00Z to 2025-09-20T11:33:00Z, 116.583 hours.
- 2025-09-15T14:58:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2025-09-15T14:58:45Z.
- 2025-09-20T11:33:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-09-20T11:33:28Z.

## Case 15: William Taylor

Birth 1994-07-18; recorded sex M; Oakwood Community Hospital; strata: ELECTIVE, HOME, ICU_STEPDOWN, MAINTENANCE_SEASON, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_cc4c9b86e386366b21499a29a481b39a; episode episode_5e167870736dac4b605a381409b17691; acuity 3; 2024-07-22T15:36:00Z arrival; 2024-07-22T15:36:00Z decision; 2024-07-22T15:51:00Z admission; 2024-07-26T15:36:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R02-B1: 2024-07-22T16:01:00Z to 2024-07-23T06:24:00Z, 14.383 hours.
- SURG-R04-B2: 2024-07-23T06:24:00Z to 2024-07-26T15:36:00Z, 81.200 hours.
- 2024-07-22T16:01:00Z OCCUPY: FIRST_PLACEMENT;WARD_OVERFLOW_ICU; transfer none; delivered 2024-07-22T16:01:56Z.
- 2024-07-23T06:24:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_40c00941bfd820f3487fba3c17ba88b0; delivered 2024-07-23T06:25:22Z.
- 2024-07-23T06:24:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_40c00941bfd820f3487fba3c17ba88b0; delivered 2024-07-23T06:24:44Z.
- 2024-07-26T15:36:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-07-26T15:37:02Z.

## Case 16: Maria Cole

Birth 1972-03-13; recorded sex F; Prairie Creek Community Hospital; strata: ELECTIVE, HOME, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_50e5b649ecd305b815e940b77fc6cbff; episode episode_40f633945cc96005698a680eadadf2a7; acuity 2; 2024-12-09T13:00:00Z arrival; 2024-12-09T13:00:00Z decision; 2024-12-09T13:15:00Z admission; 2024-12-14T14:00:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R01-B2: 2024-12-09T13:25:00Z to 2024-12-14T14:00:00Z, 120.583 hours.
- 2024-12-09T13:25:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED,ELECTIVE_MORNING_SLOT_REQUIRED; transfer none; delivered 2024-12-09T13:26:15Z.
- 2024-12-14T14:00:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-12-14T14:01:13Z.

## Case 17: Andrea Pham

Birth 1978-04-14; recorded sex F; Oakwood Community Hospital; strata: ED, HOME, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_83fb2dd95a4e8bc0cbdeb8a7a4a42d24; episode episode_63992e4dbf25272d9b89e55fb3cab603; acuity 3; 2023-12-03T19:52:00Z arrival; 2023-12-03T19:52:00Z decision; 2023-12-03T20:07:00Z admission; 2023-12-09T05:52:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R02-B2: 2023-12-03T20:17:00Z to 2023-12-09T05:52:00Z, 129.583 hours.
- 2023-12-03T20:17:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-12-03T20:18:14Z.
- 2023-12-09T05:52:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-12-09T05:53:15Z.

## Case 18: Mary Thomas

Birth 1936-06-19; recorded sex F; Oakwood Community Hospital; strata: BOARDING_OVER_DAY, BOARDING_OVER_HOUR, ED, TRANSFER, UNMET_EXTERNAL_TRANSFER, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_517c546d8ae404f4537f75d49996bc4a; episode episode_9613362799099be45fa1412ad4b8b7d5; acuity 3; 2024-04-16T16:18:00Z arrival; 2024-04-16T16:18:00Z decision; 2024-04-16T16:33:00Z admission; 2024-04-17T16:33:00Z end; TRANSFER.
Time from admission/opening to first placement: 24.000 hours.
- Source operational note @ 2024-04-17T16:33:00Z: Placement disposition for encounter encounter_517c546d8ae404f4537f75d49996bc4a: external transfer at 2024-04-17T16:33:00Z after 24 hours from inpatient admission awaiting a compatible bed. Cause: COMPATIBLE_CAPACITY_EXHAUSTED. Receiving care and later outcome are outside the modeled network.

## Case 19: Caleb Cavazos

Birth 1985-10-11; recorded sex F; Riverbend Community Hospital; strata: ED, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_7dba787685a535d7845b8aaedaa2107d; episode episode_bbfd583d2c835f62564d06de3c3b0f64; acuity 2; 2023-03-10T19:08:00Z arrival; 2023-03-10T19:08:00Z decision; 2023-03-10T19:23:00Z admission; 2023-03-16T10:08:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R04-B1: 2023-03-10T19:33:00Z to 2023-03-16T10:08:00Z, 134.583 hours.
- 2023-03-10T19:33:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-03-10T19:33:51Z.
- 2023-03-16T10:08:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-03-16T10:09:55Z.

## Case 20: Gary Pulido

Birth 1954-08-09; recorded sex M; Oakwood Community Hospital; strata: ELECTIVE, HOME, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_1b5ab02a1972cdfe5c51058ae17f7c02; episode episode_d85ab4279b6ae49b78642f8c26b538c3; acuity 2; 2025-02-24T15:54:00Z arrival; 2025-02-24T15:54:00Z decision; 2025-02-24T16:09:00Z admission; 2025-02-28T17:54:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R03-B1: 2025-02-24T16:19:00Z to 2025-02-28T17:54:00Z, 97.583 hours.
- 2025-02-24T16:19:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED; transfer none; delivered 2025-02-24T16:20:16Z.
- 2025-02-28T17:54:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-02-28T17:55:35Z.

## Case 21: Irene Wilson

Birth 1944-10-17; recorded sex F; Prairie Creek Community Hospital; strata: ELECTIVE, HOME, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_c43e284da69179b452f0f6048f04d856; episode episode_8eda18d8caaa0886b3c2c1e7c2623ec2; acuity 2; 2024-12-24T13:00:00Z arrival; 2024-12-24T13:00:00Z decision; 2024-12-24T13:15:00Z admission; 2025-01-05T08:00:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- SURG-R03-B1: 2024-12-24T13:25:00Z to 2025-01-05T08:00:00Z, 282.583 hours.
- 2024-12-24T13:25:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED,ELECTIVE_MORNING_SLOT_REQUIRED; transfer none; delivered 2024-12-24T13:26:25Z.
- 2025-01-05T08:00:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-01-05T08:00:38Z.

## Case 22: Mary Wilson

Birth 1963-10-14; recorded sex F; Riverbend Community Hospital; strata: ED, HOME, ICU_STEPDOWN, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_8a909bf24100784a0cf5967102aa663a; episode episode_3f6ce069e6f064bd12c9446e1c7f3533; acuity 2; 2025-04-11T09:28:00Z arrival; 2025-04-11T09:28:00Z decision; 2025-04-11T09:43:00Z admission; 2025-04-15T14:28:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R01-B1: 2025-04-11T09:53:00Z to 2025-04-13T09:53:00Z, 48.000 hours.
- SURG-R02-B2: 2025-04-13T09:53:00Z to 2025-04-15T14:28:00Z, 52.583 hours.
- 2025-04-11T09:53:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2025-04-11T09:54:18Z.
- 2025-04-13T09:53:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_bde01e2dc170da9d63a0419f24bb314a; delivered 2025-04-13T09:54:09Z.
- 2025-04-13T09:53:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_bde01e2dc170da9d63a0419f24bb314a; delivered 2025-04-13T09:53:19Z.
- 2025-04-15T14:28:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-04-15T14:28:22Z.

## Case 23: Mary Shaw-Metzler

Birth 1963-02-18; recorded sex UNKNOWN; Oakwood Community Hospital; strata: BOARDING_OVER_HOUR, ED, HOME, ICU_STEPDOWN, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_fc153f848f88a423db1f0e6085c6e88d; episode episode_3d542d10688e6a4e9fb917ef16130b5d; acuity 3; 2025-02-08T00:38:00Z arrival; 2025-02-08T00:38:00Z decision; 2025-02-08T00:53:00Z admission; 2025-02-12T16:43:00Z end; HOME.
Time from admission/opening to first placement: 1.250 hours.
- ICU-R01-B1: 2025-02-08T02:08:00Z to 2025-02-10T15:09:00Z, 61.017 hours.
- MED-R01-B1: 2025-02-10T15:09:00Z to 2025-02-12T16:43:00Z, 49.567 hours.
- 2025-02-08T02:08:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED;WARD_OVERFLOW_ICU;PRIVATE_ROOM_PLACEMENT; transfer none; delivered 2025-02-08T02:09:18Z.
- 2025-02-10T15:09:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_542f1c53b6c87a79540cf6d0b9560656; delivered 2025-02-10T15:10:31Z.
- 2025-02-10T15:09:00Z OCCUPY: INTERNAL_STEPDOWN_IN;PRIVATE_ROOM_PLACEMENT; transfer ward_transfer_542f1c53b6c87a79540cf6d0b9560656; delivered 2025-02-10T15:09:55Z.
- 2025-02-12T16:43:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-02-12T16:43:36Z.

## Case 24: David Garrido

Birth 1958-12-19; recorded sex M; Riverbend Community Hospital; strata: ED, HOME, ICU_STEPDOWN, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_90ccd8f5d9873c5cea02cbb3d917804f; episode episode_5158074d7f53398159180d4fd7ad61b2; acuity 2; 2023-12-10T06:22:00Z arrival; 2023-12-10T06:22:00Z decision; 2023-12-10T06:37:00Z admission; 2023-12-16T22:22:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R04-B1: 2023-12-10T06:47:00Z to 2023-12-12T06:47:00Z, 48.000 hours.
- SURG-R03-B2: 2023-12-12T06:47:00Z to 2023-12-16T22:22:00Z, 111.583 hours.
- 2023-12-10T06:47:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-12-10T06:47:17Z.
- 2023-12-12T06:47:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_2c71b73a9b20de25842ad6bf6291fd28; delivered 2023-12-12T06:47:57Z.
- 2023-12-12T06:47:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_2c71b73a9b20de25842ad6bf6291fd28; delivered 2023-12-12T06:48:09Z.
- 2023-12-16T22:22:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-12-16T22:23:35Z.

## Case 25: Tricia Giordano

Birth 1961-06-06; recorded sex F; Riverbend Community Hospital; strata: ELECTIVE, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_6bc36d4bc3b2b96b9393f8b3a33352a4; episode episode_380ca193111d749963ce0de9f034ccb5; acuity 3; 2025-01-27T13:00:00Z arrival; 2025-01-27T13:00:00Z decision; 2025-01-27T13:15:00Z admission; 2025-02-01T14:00:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R01-B1: 2025-01-27T13:25:00Z to 2025-02-01T14:00:00Z, 120.583 hours.
- 2025-01-27T13:25:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED,ELECTIVE_MORNING_SLOT_REQUIRED; transfer none; delivered 2025-01-27T13:25:45Z.
- 2025-02-01T14:00:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-02-01T14:01:11Z.

## Case 26: Cynthia Abraham

Birth 1952-12-24; recorded sex F; Prairie Creek Community Hospital; strata: ED, HOME, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_e0dbf5120dc224c90023d77acd98b374; episode episode_49c2ebabc14ef0aa84ef84eb4e9176cd; acuity 3; 2024-09-15T01:42:00Z arrival; 2024-09-15T01:42:00Z decision; 2024-09-15T01:57:00Z admission; 2024-09-19T20:42:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- SURG-R02-B1: 2024-09-15T02:07:00Z to 2024-09-19T20:42:00Z, 114.583 hours.
- 2024-09-15T02:07:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2024-09-15T02:08:09Z.
- 2024-09-19T20:42:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-09-19T20:43:23Z.

## Case 27: Arthur Caudle

Birth 1950-07-18; recorded sex M; Riverbend Community Hospital; strata: ED, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_190a81cc646667ebd0ab77001015e1a7; episode episode_2514689f05a6bfda85a94cb31971d82b; acuity 3; 2023-05-29T19:03:00Z arrival; 2023-05-29T19:03:00Z decision; 2023-05-29T19:18:00Z admission; 2023-06-03T05:03:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R05-B1: 2023-05-29T19:28:00Z to 2023-06-03T05:03:00Z, 105.583 hours.
- 2023-05-29T19:28:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-05-29T19:29:19Z.
- 2023-06-03T05:03:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-06-03T05:04:48Z.

## Case 28: Bert Doyle

Birth 1932-02-19; recorded sex M; Oakwood Community Hospital; strata: ELECTIVE, HOME, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_ee4d238e8f97d18646d8bc014b9194a0; episode episode_224690f96d2b88ec5e2a7e5d0c35309d; acuity 3; 2025-09-17T13:53:00Z arrival; 2025-09-17T13:53:00Z decision; 2025-09-17T14:08:00Z admission; 2025-09-20T16:53:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- SURG-R02-B2: 2025-09-17T14:18:00Z to 2025-09-20T16:53:00Z, 74.583 hours.
- 2025-09-17T14:18:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2025-09-17T14:18:59Z.
- 2025-09-20T16:53:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-09-20T16:53:58Z.

## Case 29: Amanda Cheng

Birth 1984-10-29; recorded sex F; Prairie Creek Community Hospital; strata: ED, HOME, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_0a5b334613f33a4cd1a496c7ce4606a8; episode episode_b6682ca8c62d070b857369531911968d; acuity 3; 2025-09-15T17:43:00Z arrival; 2025-09-15T17:43:00Z decision; 2025-09-15T17:58:00Z admission; 2025-09-20T06:43:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- SURG-R03-B2: 2025-09-15T18:08:00Z to 2025-09-20T06:43:00Z, 108.583 hours.
- 2025-09-15T18:08:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2025-09-15T18:09:42Z.
- 2025-09-20T06:43:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-09-20T06:44:18Z.

## Case 30: Kristin Alvarez

Birth 1989-10-04; recorded sex F; Riverbend Community Hospital; strata: ED, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_880fbba989ad6db86c18ede80838b946; episode episode_01f925399f6f4d59f5490adc21dc3476; acuity 2; 2023-09-19T00:28:00Z arrival; 2023-09-19T00:28:00Z decision; 2023-09-19T00:43:00Z admission; 2023-09-25T03:28:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R04-B1: 2023-09-19T00:53:00Z to 2023-09-25T03:28:00Z, 146.583 hours.
- 2023-09-19T00:53:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-09-19T00:54:33Z.
- 2023-09-25T03:28:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-09-25T03:28:40Z.

## Case 31: Daniel Jankowski

Birth 1955-03-23; recorded sex M; Prairie Creek Community Hospital; strata: ELECTIVE, HOME, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_8eef922d5ee6736c03f70526a2330247; episode episode_8f66f7e077e0dcf60190b74a29a5456b; acuity 2; 2024-01-30T18:10:00Z arrival; 2024-01-30T18:10:00Z decision; 2024-01-30T18:25:00Z admission; 2024-02-04T08:10:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- SURG-R01-B1: 2024-01-30T18:35:00Z to 2024-02-04T08:10:00Z, 109.583 hours.
- 2024-01-30T18:35:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED,ELECTIVE_MORNING_SLOT_REQUIRED; transfer none; delivered 2024-01-30T18:36:17Z.
- 2024-02-04T08:10:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-02-04T08:10:49Z.

## Case 32: Caitlin Kelly

Birth 1996-12-18; recorded sex F; Oakwood Community Hospital; strata: ED, HOME, ICU_STEPDOWN, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_d46d6e65790d1f637222eb9bb4ae1cb3; episode episode_1d34aaeef8ad131c688dbf1b495df682; acuity 3; 2024-01-08T22:08:00Z arrival; 2024-01-08T22:08:00Z decision; 2024-01-08T22:23:00Z admission; 2024-01-14T19:08:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R02-B1: 2024-01-08T22:33:00Z to 2024-01-12T04:43:00Z, 78.167 hours.
- MED-R04-B2: 2024-01-12T04:43:00Z to 2024-01-14T19:08:00Z, 62.417 hours.
- 2024-01-08T22:33:00Z OCCUPY: FIRST_PLACEMENT;WARD_OVERFLOW_ICU; transfer none; delivered 2024-01-08T22:33:55Z.
- 2024-01-12T04:43:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_0a2dfb65af2101c5d4ac9b10e0864cec; delivered 2024-01-12T04:43:46Z.
- 2024-01-12T04:43:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_0a2dfb65af2101c5d4ac9b10e0864cec; delivered 2024-01-12T04:44:37Z.
- 2024-01-14T19:08:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-01-14T19:09:49Z.

## Case 33: Kelly Kiser

Birth 1976-10-05; recorded sex F; Riverbend Community Hospital; strata: ELECTIVE, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_466435bb3510cc0bd27c936958a191f9; episode episode_be1a9cb2c1c05a126f5984d2ff74e39e; acuity 2; 2023-04-12T13:07:00Z arrival; 2023-04-12T13:07:00Z decision; 2023-04-12T13:22:00Z admission; 2023-04-16T17:07:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R01-B1: 2023-04-12T13:32:00Z to 2023-04-16T17:07:00Z, 99.583 hours.
- 2023-04-12T13:32:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-04-12T13:33:27Z.
- 2023-04-16T17:07:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-04-16T17:07:57Z.

## Case 34: Lindsay Dixon

Birth 1993-11-20; recorded sex F; Oakwood Community Hospital; strata: ELECTIVE, HOME, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_14eacd7e404e8f928088d72c0efcf46c; episode episode_86a23354806070b6330ebdaa1a2bfa57; acuity 3; 2024-02-27T19:44:00Z arrival; 2024-02-27T19:44:00Z decision; 2024-02-27T19:59:00Z admission; 2024-03-04T00:44:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- SURG-R05-B2: 2024-02-27T20:09:00Z to 2024-03-04T00:44:00Z, 124.583 hours.
- 2024-02-27T20:09:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED,ELECTIVE_MORNING_SLOT_REQUIRED; transfer none; delivered 2024-02-27T20:10:31Z.
- 2024-03-04T00:44:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-03-04T00:44:19Z.

## Case 35: Susie Roberts

Birth 1930-11-08; recorded sex F; Oakwood Community Hospital; strata: ELECTIVE, HOME, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_208e1fad5309309c0383c445d5255eb7; episode episode_54f56da6d88952988d89a22dab81bcec; acuity 2; 2025-09-02T15:12:00Z arrival; 2025-09-02T15:12:00Z decision; 2025-09-02T15:27:00Z admission; 2025-09-07T07:12:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R01-B1: 2025-09-02T15:37:00Z to 2025-09-07T07:12:00Z, 111.583 hours.
- 2025-09-02T15:37:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2025-09-02T15:38:51Z.
- 2025-09-07T07:12:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-09-07T07:13:04Z.

## Case 36: Teri Cantrell

Birth 1971-08-30; recorded sex F; Prairie Creek Community Hospital; strata: ED, HOME, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_6c7fb6b298110349bc1770270bfaec1c; episode episode_5ac252ebb905cb3affe6c3b084164477; acuity 3; 2024-05-20T12:12:00Z arrival; 2024-05-20T12:12:00Z decision; 2024-05-20T12:27:00Z admission; 2024-05-25T11:12:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R03-B2: 2024-05-20T12:37:00Z to 2024-05-25T11:12:00Z, 118.583 hours.
- 2024-05-20T12:37:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2024-05-20T12:37:52Z.
- 2024-05-25T11:12:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-05-25T11:12:32Z.

## Case 37: Kimberly Brickner

Birth 1982-03-07; recorded sex F; Oakwood Community Hospital; strata: ELECTIVE, HOME, ICU_STEPDOWN, MAINTENANCE_SEASON, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_815922da9a2b677c929bb1acb4c1451b; episode episode_3b4f3b267d5436ff8df7f89178ab48ef; acuity 3; 2024-07-05T12:00:00Z arrival; 2024-07-05T12:00:00Z decision; 2024-07-05T12:15:00Z admission; 2024-07-09T13:00:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R03-B1: 2024-07-05T12:25:00Z to 2024-07-06T04:41:00Z, 16.267 hours.
- SURG-R03-B1: 2024-07-06T04:41:00Z to 2024-07-09T13:00:00Z, 80.317 hours.
- 2024-07-05T12:25:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED,ELECTIVE_MORNING_SLOT_REQUIRED,MAINTENANCE_REDUCED_CAPACITY;WARD_OVERFLOW_ICU; transfer none; delivered 2024-07-05T12:25:32Z.
- 2024-07-06T04:41:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_41cbf82cbb718d60593fc220f10515c9; delivered 2024-07-06T04:41:54Z.
- 2024-07-06T04:41:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_41cbf82cbb718d60593fc220f10515c9; delivered 2024-07-06T04:41:47Z.
- 2024-07-09T13:00:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-07-09T13:00:30Z.

## Case 38: Thomas Clouse

Birth 1949-06-16; recorded sex M; Oakwood Community Hospital; strata: ED, HOME, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_926601a1d9637795c3a9389f842bd096; episode episode_107c5c11195c04fbf99d493075b07e96; acuity 3; 2025-05-22T11:57:00Z arrival; 2025-05-22T11:57:00Z decision; 2025-05-22T12:12:00Z admission; 2025-05-28T01:57:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- SURG-R02-B1: 2025-05-22T12:22:00Z to 2025-05-28T01:57:00Z, 133.583 hours.
- 2025-05-22T12:22:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2025-05-22T12:23:27Z.
- 2025-05-28T01:57:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-05-28T01:59:01Z.

## Case 39: Gail Keeler

Birth 1963-01-16; recorded sex F; Prairie Creek Community Hospital; strata: ELECTIVE, HOME, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_f2d913696730f30498fb7d78f960cbed; episode episode_65e89f1a1058f18ca6d54401a7547d88; acuity 3; 2023-03-03T13:00:00Z arrival; 2023-03-03T13:00:00Z decision; 2023-03-03T13:15:00Z admission; 2023-03-07T17:00:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- SURG-R02-B1: 2023-03-03T13:25:00Z to 2023-03-07T17:00:00Z, 99.583 hours.
- 2023-03-03T13:25:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED,ELECTIVE_MORNING_SLOT_REQUIRED; transfer none; delivered 2023-03-03T13:26:31Z.
- 2023-03-07T17:00:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-03-07T17:00:26Z.

## Case 40: John Yi

Birth 1964-02-08; recorded sex F; Oakwood Community Hospital; strata: ELECTIVE, HOME, ICU_STEPDOWN, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_8d77c2c654ebcbc3e279d6f75a99e09b; episode episode_e9fb41f3de707d277a85cfc496503eea; acuity 2; 2025-09-29T15:17:00Z arrival; 2025-09-29T15:17:00Z decision; 2025-09-29T15:32:00Z admission; 2025-10-03T02:17:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R02-B1: 2025-09-29T15:42:00Z to 2025-09-30T12:43:00Z, 21.017 hours.
- MED-R05-B2: 2025-09-30T12:43:00Z to 2025-10-03T02:17:00Z, 61.567 hours.
- 2025-09-29T15:42:00Z OCCUPY: FIRST_PLACEMENT;WARD_OVERFLOW_ICU; transfer none; delivered 2025-09-29T15:42:44Z.
- 2025-09-30T12:43:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_8ba22dcc7d34a9d2d3e2e2a90925111a; delivered 2025-09-30T12:44:26Z.
- 2025-09-30T12:43:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_8ba22dcc7d34a9d2d3e2e2a90925111a; delivered 2025-09-30T12:43:45Z.
- 2025-10-03T02:17:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-10-03T02:17:53Z.

## Case 41: Joel Douglas

Birth 1991-11-21; recorded sex M; Riverbend Community Hospital; strata: ED, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_b1540cd8a6eaeba3b91a834bdafbcde5; episode episode_a18008a39ba6b5952b4961096e1d2de2; acuity 2; 2025-09-07T13:16:00Z arrival; 2025-09-07T13:16:00Z decision; 2025-09-07T13:31:00Z admission; 2025-09-11T07:16:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R03-B1: 2025-09-07T13:41:00Z to 2025-09-11T07:16:00Z, 89.583 hours.
- 2025-09-07T13:41:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2025-09-07T13:42:02Z.
- 2025-09-11T07:16:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-09-11T07:17:29Z.

## Case 42: Ralph Bills

Birth 1969-08-10; recorded sex M; Riverbend Community Hospital; strata: ELECTIVE, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_79bc1894296f5eb0616d228ba2816e01; episode episode_e5e4af8deed10e2bfe36eb2bddf1ed80; acuity 2; 2023-03-01T14:28:00Z arrival; 2023-03-01T14:28:00Z decision; 2023-03-01T14:43:00Z admission; 2023-03-04T20:28:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R05-B1: 2023-03-01T14:53:00Z to 2023-03-04T20:28:00Z, 77.583 hours.
- 2023-03-01T14:53:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-03-01T14:53:30Z.
- 2023-03-04T20:28:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-03-04T20:29:55Z.

## Case 43: Barbara Parke

Birth 1945-03-12; recorded sex F; Riverbend Community Hospital; strata: BOARDING_OVER_HOUR, ED, HOME, ICU_STEPDOWN, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_bbd089e66881e0a7e2711ca187282583; episode episode_e48e9b105abe086a94f2d717b2cba844; acuity 3; 2023-04-27T10:36:00Z arrival; 2023-04-27T10:36:00Z decision; 2023-04-27T10:51:00Z admission; 2023-05-02T03:04:00Z end; HOME.
Time from admission/opening to first placement: 15.633 hours.
- ICU-R02-B1: 2023-04-28T02:29:00Z to 2023-04-28T14:29:00Z, 12.000 hours.
- SURG-R01-B2: 2023-04-28T14:29:00Z to 2023-05-02T03:04:00Z, 84.583 hours.
- 2023-04-28T02:29:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED;WARD_OVERFLOW_ICU; transfer none; delivered 2023-04-28T02:30:25Z.
- 2023-04-28T14:29:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_b23caee7638281ad172bfa6aadd92c40; delivered 2023-04-28T14:30:25Z.
- 2023-04-28T14:29:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_b23caee7638281ad172bfa6aadd92c40; delivered 2023-04-28T14:29:09Z.
- 2023-05-02T03:04:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-05-02T03:05:19Z.

## Case 44: Steven Mix

Birth 1954-08-19; recorded sex M; Riverbend Community Hospital; strata: BOARDING_OVER_DAY, BOARDING_OVER_HOUR, ED, HOME, ICU_STEPDOWN, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_ee16c2629ec74bc539752cb728496e56; episode episode_56ae13430b1088f3ae1d9e738f045cce; acuity 3; 2024-02-09T17:40:00Z arrival; 2024-02-09T17:40:00Z decision; 2024-02-09T17:55:00Z admission; 2024-02-14T16:20:00Z end; HOME.
Time from admission/opening to first placement: 23.833 hours.
- ICU-R01-B1: 2024-02-10T17:45:00Z to 2024-02-11T10:59:00Z, 17.233 hours.
- MED-R01-B1: 2024-02-11T10:59:00Z to 2024-02-14T16:20:00Z, 77.350 hours.
- 2024-02-10T17:45:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED;WARD_OVERFLOW_ICU; transfer none; delivered 2024-02-10T17:46:39Z.
- 2024-02-11T10:59:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_bc3906685fe9ecf3044b15f65c7952cb; delivered 2024-02-11T11:00:13Z.
- 2024-02-11T10:59:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_bc3906685fe9ecf3044b15f65c7952cb; delivered 2024-02-11T11:00:05Z.
- 2024-02-14T16:20:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-02-14T16:21:41Z.

## Case 45: Sylvia Shelton

Birth 1935-07-03; recorded sex F; Riverbend Community Hospital; strata: ELECTIVE, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_b8e01db8d84d1db62ac4c5c23e66ecac; episode episode_ccfdf9bec3be3ff0f0bc83588279ac96; acuity 3; 2025-06-16T13:12:00Z arrival; 2025-06-16T13:12:00Z decision; 2025-06-16T13:27:00Z admission; 2025-06-20T16:12:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R05-B1: 2025-06-16T13:37:00Z to 2025-06-20T16:12:00Z, 98.583 hours.
- 2025-06-16T13:37:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2025-06-16T13:37:28Z.
- 2025-06-20T16:12:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-06-20T16:12:21Z.

## Case 46: Haley Hyer

Birth 1992-11-30; recorded sex F; Oakwood Community Hospital; strata: ELECTIVE, HOME, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_280b2a79f3272085edc2b9743a815057; episode episode_7ae9fda2f72abbb2e81014f93153ab51; acuity 3; 2025-03-27T13:08:00Z arrival; 2025-03-27T13:08:00Z decision; 2025-03-27T13:23:00Z admission; 2025-04-01T03:08:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R02-B2: 2025-03-27T13:33:00Z to 2025-04-01T03:08:00Z, 109.583 hours.
- 2025-03-27T13:33:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2025-03-27T13:34:10Z.
- 2025-04-01T03:08:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-04-01T09:08:32Z.

## Case 47: Paula Hicks

Birth 1944-05-09; recorded sex F; Riverbend Community Hospital; strata: ED, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_c8463fd5101fe3c87e317d3d70e64ee6; episode episode_b3b51ee3fc94fd8ffd99e191618aa3e5; acuity 3; 2024-09-16T02:24:00Z arrival; 2024-09-16T02:24:00Z decision; 2024-09-16T02:39:00Z admission; 2024-09-20T11:24:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R04-B2: 2024-09-16T02:49:00Z to 2024-09-20T11:24:00Z, 104.583 hours.
- 2024-09-16T02:49:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2024-09-16T02:50:21Z.
- 2024-09-20T11:24:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-09-20T11:24:58Z.

## Case 48: Calvin Reed

Birth 1941-06-22; recorded sex M; Oakwood Community Hospital; strata: ED, HOME, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_1710d58cb5f2de42debf8851b8555b75; episode episode_235382102e1d5ab98565386749fcf03e; acuity 3; 2025-05-15T22:29:00Z arrival; 2025-05-15T22:29:00Z decision; 2025-05-15T22:44:00Z admission; 2025-05-20T23:29:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R05-B1: 2025-05-15T22:54:00Z to 2025-05-20T23:29:00Z, 120.583 hours.
- 2025-05-15T22:54:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2025-05-16T04:54:54Z.
- 2025-05-20T23:29:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-05-20T23:29:15Z.

## Case 49: Arthur Goldsmith

Birth 1961-09-01; recorded sex M; Prairie Creek Community Hospital; strata: BOARDING_OVER_DAY, BOARDING_OVER_HOUR, DIRECT, TRANSFER, UNMET_EXTERNAL_TRANSFER, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_ba5941d51fb3be5a7d0bdbffea06d520; episode episode_661e1f62535797268df4aa70f102d87c; acuity 3; 2023-06-28T04:57:00Z arrival; 2023-06-28T04:57:00Z decision; 2023-06-28T05:12:00Z admission; 2023-06-29T05:12:00Z end; TRANSFER.
Time from admission/opening to first placement: 24.000 hours.
- Source operational note @ 2023-06-29T05:12:00Z: Placement disposition for encounter encounter_ba5941d51fb3be5a7d0bdbffea06d520: external transfer at 2023-06-29T05:12:00Z after 24 hours from inpatient admission awaiting a compatible bed. Cause: COMPATIBLE_CAPACITY_EXHAUSTED. Receiving care and later outcome are outside the modeled network.

## Case 50: William Hostetler

Birth 1926-09-05; recorded sex M; Oakwood Community Hospital; strata: ED, HOME, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_126e52412064bf22d936d05d96f6d840; episode episode_46a1a39b1980865ca5801c1f35a03273; acuity 2; 2024-10-30T15:32:00Z arrival; 2024-10-30T15:32:00Z decision; 2024-10-30T15:47:00Z admission; 2024-11-07T02:32:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R04-B1: 2024-10-30T15:57:00Z to 2024-11-07T02:32:00Z, 178.583 hours.
- 2024-10-30T15:57:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2024-10-30T15:57:25Z.
- 2024-11-07T02:32:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-11-07T02:32:38Z.

## Case 51: Michael Cartwright

Birth 1981-10-06; recorded sex M; Riverbend Community Hospital; strata: ED, HOME, ICU_STEPDOWN, PRIVATE_ISOLATION, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_252ad409a9990aba1ce024e77231bb05; episode episode_0036c30b8803550e381fda71539617f1; acuity 2; 2024-05-03T05:47:00Z arrival; 2024-05-03T05:47:00Z decision; 2024-05-03T06:02:00Z admission; 2024-05-10T08:47:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R01-B1: 2024-05-03T06:12:00Z to 2024-05-08T13:51:00Z, 127.650 hours.
- SURG-R01-B1: 2024-05-08T13:51:00Z to 2024-05-10T08:47:00Z, 42.933 hours.
- 2024-05-03T06:12:00Z OCCUPY: FIRST_PLACEMENT;PRIVATE_ISOLATION_PLACEMENT; transfer none; delivered 2024-05-03T06:13:33Z.
- 2024-05-08T13:51:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_3e999e55c6adb5f92c28352f73734f2d; delivered 2024-05-08T13:52:30Z.
- 2024-05-08T13:51:00Z OCCUPY: INTERNAL_STEPDOWN_IN;PRIVATE_ISOLATION_PLACEMENT; transfer ward_transfer_3e999e55c6adb5f92c28352f73734f2d; delivered 2024-05-08T13:51:29Z.
- 2024-05-10T08:47:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-05-10T08:47:44Z.
- Source operational note @ 2024-05-03T06:02:00Z: Placement assessment for Michael Cartwright, age 42: suspected transmissible respiratory illness; isolation-capable private room requested. Recorded at 2024-05-03T06:02:00Z.

## Case 52: Katie Anderson

Birth 1925-07-07; recorded sex F; Prairie Creek Community Hospital; strata: BOARDING_OVER_HOUR, ED, HOME, ICU_STEPDOWN, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_30d6da83d4e841b5af5f06b7673c4e13; episode episode_d30a357a64d057eeeafb37b7f7cd2f2f; acuity 3; 2023-09-15T14:02:00Z arrival; 2023-09-15T14:02:00Z decision; 2023-09-15T14:17:00Z admission; 2023-09-20T16:27:00Z end; HOME.
Time from admission/opening to first placement: 10.583 hours.
- ICU-R03-B1: 2023-09-16T00:52:00Z to 2023-09-16T12:52:00Z, 12.000 hours.
- MED-R03-B1: 2023-09-16T12:52:00Z to 2023-09-20T16:27:00Z, 99.583 hours.
- 2023-09-16T00:52:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED;WARD_OVERFLOW_ICU; transfer none; delivered 2023-09-16T00:53:11Z.
- 2023-09-16T12:52:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_975cc1e1fac93957c118e180c477fa63; delivered 2023-09-16T12:54:01Z.
- 2023-09-16T12:52:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_975cc1e1fac93957c118e180c477fa63; delivered 2023-09-16T12:52:52Z.
- 2023-09-20T16:27:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-09-20T16:27:43Z.

## Case 53: Lawrence Castor

Birth 1944-01-06; recorded sex X; Riverbend Community Hospital; strata: ED, HOME, ICU_STEPDOWN, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_a551fe44f01e0cf167a279541490e620; episode episode_0227be964d24567795447ba652be768f; acuity 2; 2023-05-09T22:16:00Z arrival; 2023-05-09T22:16:00Z decision; 2023-05-09T22:31:00Z admission; 2023-05-15T10:16:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R01-B1: 2023-05-09T22:41:00Z to 2023-05-12T17:36:00Z, 66.917 hours.
- SURG-R05-B1: 2023-05-12T17:36:00Z to 2023-05-15T10:16:00Z, 64.667 hours.
- 2023-05-09T22:41:00Z OCCUPY: FIRST_PLACEMENT;WARD_OVERFLOW_ICU;PRIVATE_ROOM_PLACEMENT; transfer none; delivered 2023-05-09T22:42:47Z.
- 2023-05-12T17:36:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_cb430aa199b4297291dff8689397b67c; delivered 2023-05-12T17:37:54Z.
- 2023-05-12T17:36:00Z OCCUPY: INTERNAL_STEPDOWN_IN;PRIVATE_ROOM_PLACEMENT; transfer ward_transfer_cb430aa199b4297291dff8689397b67c; delivered 2023-05-12T17:37:28Z.
- 2023-05-15T10:16:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-05-15T10:16:55Z.

## Case 54: Jeffrey Wallace

Birth 1978-02-16; recorded sex M; Riverbend Community Hospital; strata: ED, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_fc121d16c85899c1654c0251f8313b24; episode episode_a8a06f1b800e7873cca5554d4c60d51c; acuity 3; 2025-11-28T21:55:00Z arrival; 2025-11-28T21:55:00Z decision; 2025-11-28T22:10:00Z admission; 2025-12-03T10:55:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R05-B2: 2025-11-28T22:20:00Z to 2025-12-03T10:55:00Z, 108.583 hours.
- 2025-11-28T22:20:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2025-11-28T22:21:00Z.
- 2025-12-03T10:55:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-12-03T10:56:17Z.

## Case 55: Jason Young

Birth 1982-03-21; recorded sex M; Riverbend Community Hospital; strata: ED, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_772e42fb3efc2b35beb0e4acf21a55a3; episode episode_95bdc8e1389d75001eea7146744002e2; acuity 2; 2023-06-16T15:56:00Z arrival; 2023-06-16T15:56:00Z decision; 2023-06-16T16:11:00Z admission; 2023-06-21T06:56:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R04-B2: 2023-06-16T16:21:00Z to 2023-06-21T06:56:00Z, 110.583 hours.
- 2023-06-16T16:21:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-06-16T16:21:27Z.
- 2023-06-21T06:56:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-06-21T06:57:26Z.

## Case 56: Karen Hetzel

Birth 1968-06-05; recorded sex F; Prairie Creek Community Hospital; strata: BOARDING_OVER_HOUR, DIRECT, HOME, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_e080a4020b4a5fd1935420df16e005d0; episode episode_a2b5c54b897bede61b849e131ff0db16; acuity 3; 2025-04-04T20:44:00Z arrival; 2025-04-04T20:44:00Z decision; 2025-04-04T20:59:00Z admission; 2025-04-10T17:46:00Z end; HOME.
Time from admission/opening to first placement: 3.200 hours.
- MED-R05-B1: 2025-04-05T00:11:00Z to 2025-04-10T17:46:00Z, 137.583 hours.
- 2025-04-05T00:11:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED; transfer none; delivered 2025-04-05T00:11:54Z.
- 2025-04-10T17:46:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-04-10T17:46:31Z.

## Case 57: Gerald Barrera

Birth 1949-11-12; recorded sex M; Oakwood Community Hospital; strata: ELECTIVE, HOME, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_628f27562f7ee5e18e94acfd222eba70; episode episode_8343709f0d1d23224333f43303dc938c; acuity 3; 2024-09-05T13:46:00Z arrival; 2024-09-05T13:46:00Z decision; 2024-09-05T14:01:00Z admission; 2024-09-09T02:46:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R01-B1: 2024-09-05T14:11:00Z to 2024-09-09T02:46:00Z, 84.583 hours.
- 2024-09-05T14:11:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2024-09-05T14:12:48Z.
- 2024-09-09T02:46:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-09-09T02:47:07Z.

## Case 58: Ronald Tang

Birth 1955-01-24; recorded sex M; Riverbend Community Hospital; strata: BOARDING_OVER_HOUR, ED, HOME, ICU_STEPDOWN, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_ce4bee1e1dd36604bde1a9eda331130f; episode episode_8d5295ff192e06b76d0688f6a6af5cd6; acuity 3; 2025-04-22T20:24:00Z arrival; 2025-04-22T20:24:00Z decision; 2025-04-22T20:39:00Z admission; 2025-04-26T23:50:00Z end; HOME.
Time from admission/opening to first placement: 6.600 hours.
- ICU-R02-B1: 2025-04-23T03:15:00Z to 2025-04-24T21:45:00Z, 42.500 hours.
- SURG-R03-B2: 2025-04-24T21:45:00Z to 2025-04-26T23:50:00Z, 50.083 hours.
- 2025-04-23T03:15:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED;WARD_OVERFLOW_ICU; transfer none; delivered 2025-04-23T03:15:21Z.
- 2025-04-24T21:45:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_c6ebafc814365a46ddbb88bb061ee233; delivered 2025-04-24T21:46:20Z.
- 2025-04-24T21:45:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_c6ebafc814365a46ddbb88bb061ee233; delivered 2025-04-24T21:45:29Z.
- 2025-04-26T23:50:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-04-26T23:51:01Z.

## Case 59: Gary Figueroa

Birth 1968-11-06; recorded sex M; Prairie Creek Community Hospital; strata: ED, HOME, ICU_STEPDOWN, MAINTENANCE_SEASON, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_7833f9cd111cadcb1ba79acd743599e5; episode episode_870129f286c0111dc999a9ed6d452f4c; acuity 2; 2024-07-05T22:21:00Z arrival; 2024-07-05T22:21:00Z decision; 2024-07-05T22:36:00Z admission; 2024-07-09T13:21:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R04-B1: 2024-07-05T22:46:00Z to 2024-07-07T22:46:00Z, 48.000 hours.
- MED-R02-B2: 2024-07-07T22:46:00Z to 2024-07-09T13:21:00Z, 38.583 hours.
- 2024-07-05T22:46:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2024-07-05T22:47:07Z.
- 2024-07-07T22:46:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_daf8720dc1adeebd25a641720ad6d214; delivered 2024-07-07T22:47:39Z.
- 2024-07-07T22:46:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_daf8720dc1adeebd25a641720ad6d214; delivered 2024-07-07T22:47:34Z.
- 2024-07-09T13:21:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-07-09T13:22:42Z.

## Case 60: Monica Roberts

Birth 1986-08-18; recorded sex F; Oakwood Community Hospital; strata: BOARDING_OVER_DAY, BOARDING_OVER_HOUR, ED, TRANSFER, UNMET_EXTERNAL_TRANSFER, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_230563913789c19c37c4586f9fade3f6; episode episode_99d2bbf856d76b3257dac2136f9f1979; acuity 2; 2024-02-27T01:09:00Z arrival; 2024-02-27T01:09:00Z decision; 2024-02-27T01:24:00Z admission; 2024-02-28T01:24:00Z end; TRANSFER.
Time from admission/opening to first placement: 24.000 hours.
- Source operational note @ 2024-02-28T01:24:00Z: Placement disposition for encounter encounter_230563913789c19c37c4586f9fade3f6: external transfer at 2024-02-28T01:24:00Z after 24 hours from inpatient admission awaiting a compatible bed. Cause: COMPATIBLE_CAPACITY_EXHAUSTED. Receiving care and later outcome are outside the modeled network.

## Case 61: Robin Neubauer

Birth 1961-06-26; recorded sex F; Prairie Creek Community Hospital; strata: ED, HOME, ICU_STEPDOWN, MAINTENANCE_SEASON, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_4c63342d3c6b0d4b058614934a124e72; episode episode_3c54d56bea2b7124b3e19e9993c2caf5; acuity 2; 2024-07-14T10:50:00Z arrival; 2024-07-14T10:50:00Z decision; 2024-07-14T11:05:00Z admission; 2024-07-19T06:50:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R01-B1: 2024-07-14T11:15:00Z to 2024-07-15T12:41:00Z, 25.433 hours.
- MED-R04-B2: 2024-07-15T12:41:00Z to 2024-07-19T06:50:00Z, 90.150 hours.
- 2024-07-14T11:15:00Z OCCUPY: FIRST_PLACEMENT;WARD_OVERFLOW_ICU; transfer none; delivered 2024-07-14T11:16:30Z.
- 2024-07-15T12:41:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_8cf9a8bc94f6749f940c9b22926dfd86; delivered 2024-07-15T12:41:27Z.
- 2024-07-15T12:41:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_8cf9a8bc94f6749f940c9b22926dfd86; delivered 2024-07-15T12:42:19Z.
- 2024-07-19T06:50:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-07-19T06:50:48Z.

## Case 62: Janice Arnold

Birth 1972-04-16; recorded sex F; Prairie Creek Community Hospital; strata: ED, HOME, ICU_STEPDOWN, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_e27154c7b6b433be63b9464f284a50e6; episode episode_8e24eaf17d56b628aec9310a6cba0423; acuity 3; 2023-06-15T18:57:00Z arrival; 2023-06-15T18:57:00Z decision; 2023-06-15T19:12:00Z admission; 2023-06-21T14:57:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R01-B1: 2023-06-15T19:22:00Z to 2023-06-16T07:22:00Z, 12.000 hours.
- SURG-R03-B1: 2023-06-16T07:22:00Z to 2023-06-21T14:57:00Z, 127.583 hours.
- 2023-06-15T19:22:00Z OCCUPY: FIRST_PLACEMENT;WARD_OVERFLOW_ICU; transfer none; delivered 2023-06-15T19:23:58Z.
- 2023-06-16T07:22:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_6bbc9f101008268b7ecbf485faafabd8; delivered 2023-06-16T07:23:14Z.
- 2023-06-16T07:22:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_6bbc9f101008268b7ecbf485faafabd8; delivered 2023-06-16T07:23:26Z.
- 2023-06-21T14:57:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-06-21T14:57:35Z.

## Case 63: Natalie Moreno

Birth 1960-04-28; recorded sex F; Riverbend Community Hospital; strata: ED, HOME, ICU_STEPDOWN, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_250210d3039a09100f448e1cc721b06f; episode episode_f1840755230ad203d93a7fca27a9d1a5; acuity 3; 2025-05-27T17:55:00Z arrival; 2025-05-27T17:55:00Z decision; 2025-05-27T18:10:00Z admission; 2025-06-01T13:55:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R02-B1: 2025-05-27T18:20:00Z to 2025-05-28T07:41:00Z, 13.350 hours.
- MED-R03-B1: 2025-05-28T07:41:00Z to 2025-06-01T13:55:00Z, 102.233 hours.
- 2025-05-27T18:20:00Z OCCUPY: FIRST_PLACEMENT;WARD_OVERFLOW_ICU; transfer none; delivered 2025-05-27T18:21:31Z.
- 2025-05-28T07:41:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_6943293db98c22e0a359c11c62c4aa5e; delivered 2025-05-28T07:42:09Z.
- 2025-05-28T07:41:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_6943293db98c22e0a359c11c62c4aa5e; delivered 2025-05-28T07:42:59Z.
- 2025-06-01T13:55:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-06-01T13:55:45Z.

## Case 64: Roy Estevez

Birth 1946-03-08; recorded sex F; Oakwood Community Hospital; strata: ED, HOME, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_ad21658c910a57903e7088ac105ab612; episode episode_10338aa16f3719cbecbd231cdb7ca269; acuity 3; 2023-06-12T20:53:00Z arrival; 2023-06-12T20:53:00Z decision; 2023-06-12T21:08:00Z admission; 2023-06-17T18:53:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- SURG-R02-B2: 2023-06-12T21:18:00Z to 2023-06-17T18:53:00Z, 117.583 hours.
- 2023-06-12T21:18:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-06-12T21:18:14Z.
- 2023-06-17T18:53:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-06-17T18:54:34Z.

## Case 65: Richard Albano

Birth 1940-03-04; recorded sex M; Oakwood Community Hospital; strata: ELECTIVE, HOME, ICU_STEPDOWN, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_6f92d550e240c18fda80624a9cc90ecc; episode episode_2bfe618cc3d93013d69d778762c0f3f6; acuity 3; 2023-05-19T12:00:00Z arrival; 2023-05-19T12:00:00Z decision; 2023-05-19T12:15:00Z admission; 2023-05-24T05:00:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R02-B1: 2023-05-19T12:25:00Z to 2023-05-20T08:05:00Z, 19.667 hours.
- MED-R03-B1: 2023-05-20T08:05:00Z to 2023-05-24T05:00:00Z, 92.917 hours.
- 2023-05-19T12:25:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED,ELECTIVE_MORNING_SLOT_REQUIRED;WARD_OVERFLOW_ICU; transfer none; delivered 2023-05-19T12:26:38Z.
- 2023-05-20T08:05:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_d8f1e34d7613d547dbb61b1d5ff80d7a; delivered 2023-05-20T08:05:28Z.
- 2023-05-20T08:05:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_d8f1e34d7613d547dbb61b1d5ff80d7a; delivered 2023-05-20T08:06:51Z.
- 2023-05-24T05:00:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-05-24T05:00:59Z.

## Case 66: Christine Bonilla

Birth 1968-03-16; recorded sex F; Oakwood Community Hospital; strata: ELECTIVE, HOME, ICU_STEPDOWN, MAINTENANCE_SEASON, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_be252d5c5c2764a1bef2d37724c7a168; episode episode_d4c0e17fb2b411fd087760754fe2a286; acuity 3; 2024-06-07T14:29:00Z arrival; 2024-06-07T14:29:00Z decision; 2024-06-07T14:44:00Z admission; 2024-06-11T17:29:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R02-B1: 2024-06-07T14:54:00Z to 2024-06-08T02:54:00Z, 12.000 hours.
- SURG-R03-B1: 2024-06-08T02:54:00Z to 2024-06-11T17:29:00Z, 86.583 hours.
- 2024-06-07T14:54:00Z OCCUPY: FIRST_PLACEMENT;WARD_OVERFLOW_ICU; transfer none; delivered 2024-06-07T14:55:26Z.
- 2024-06-08T02:54:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_2d821b2c4dc39b02c5ffd5c213fef7b6; delivered 2024-06-08T02:54:55Z.
- 2024-06-08T02:54:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_2d821b2c4dc39b02c5ffd5c213fef7b6; delivered 2024-06-08T02:55:32Z.
- 2024-06-11T17:29:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-06-11T17:29:58Z.

## Case 67: Jessica Kelly

Birth 1981-09-24; recorded sex F; Riverbend Community Hospital; strata: BOARDING_OVER_HOUR, ED, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_886c6042a5f94075be7611623f7a8d6f; episode episode_44c808d8dc0f0304fad48d38400b5ac5; acuity 2; 2024-03-02T07:01:00Z arrival; 2024-03-02T07:01:00Z decision; 2024-03-02T07:16:00Z admission; 2024-03-07T11:33:00Z end; HOME.
Time from admission/opening to first placement: 4.700 hours.
- SURG-R02-B1: 2024-03-02T11:58:00Z to 2024-03-07T11:33:00Z, 119.583 hours.
- 2024-03-02T11:58:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED; transfer none; delivered 2024-03-02T11:59:25Z.
- 2024-03-07T11:33:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-03-07T11:34:31Z.

## Case 68: Lauren Kitchens

Birth 1996-09-12; recorded sex F; Oakwood Community Hospital; strata: BOARDING_OVER_HOUR, ED, HOME, ICU_STEPDOWN, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_6f147319d1d4bfdc612ad38d68f218dc; episode episode_2a2ae88b0342b298177817af6a34899e; acuity 2; 2024-04-19T18:46:00Z arrival; 2024-04-19T18:46:00Z decision; 2024-04-19T19:01:00Z admission; 2024-04-26T00:39:00Z end; HOME.
Time from admission/opening to first placement: 5.050 hours.
- ICU-R01-B1: 2024-04-20T00:04:00Z to 2024-04-21T21:24:00Z, 45.333 hours.
- MED-R01-B1: 2024-04-21T21:24:00Z to 2024-04-26T00:39:00Z, 99.250 hours.
- 2024-04-20T00:04:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED;WARD_OVERFLOW_ICU; transfer none; delivered 2024-04-20T00:04:32Z.
- 2024-04-21T21:24:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_84ddb164d2e7570771fbeaa378fcf48d; delivered 2024-04-21T21:24:58Z.
- 2024-04-21T21:24:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_84ddb164d2e7570771fbeaa378fcf48d; delivered 2024-04-21T21:24:55Z.
- 2024-04-26T00:39:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-04-26T00:40:52Z.

## Case 69: Ronald Thomas

Birth 1943-05-11; recorded sex M; Oakwood Community Hospital; strata: ED, HOME, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_4244dd05482ad33f9f2720bfc394421e; episode episode_41e85edae242be74c050877becca69f2; acuity 2; 2025-01-23T02:03:00Z arrival; 2025-01-23T02:03:00Z decision; 2025-01-23T02:18:00Z admission; 2025-01-29T02:03:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R03-B1: 2025-01-23T02:28:00Z to 2025-01-29T02:03:00Z, 143.583 hours.
- 2025-01-23T02:28:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2025-01-23T02:28:47Z.
- 2025-01-29T02:03:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-01-29T02:04:34Z.

## Case 70: Sandra Burge

Birth 1948-06-11; recorded sex F; Riverbend Community Hospital; strata: ED, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_cd8caf4f701bfb3ae6f7e33de43bb748; episode episode_35c83bf5041ac590ff466193700868d1; acuity 2; 2024-08-12T02:25:00Z arrival; 2024-08-12T02:25:00Z decision; 2024-08-12T02:40:00Z admission; 2024-08-16T23:25:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- SURG-R02-B2: 2024-08-12T02:50:00Z to 2024-08-16T23:25:00Z, 116.583 hours.
- 2024-08-12T02:50:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2024-08-12T02:50:50Z.
- 2024-08-16T23:25:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-08-16T23:26:05Z.

## Case 71: John Stark

Birth 1940-07-09; recorded sex M; Oakwood Community Hospital; strata: ELECTIVE, HOME, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_e17d574f22e9eb5fc9f886c6d6cba405; episode episode_adb0b5f885012f0175b2467e2560ec35; acuity 2; 2024-03-21T14:02:00Z arrival; 2024-03-21T14:02:00Z decision; 2024-03-21T14:17:00Z admission; 2024-03-25T17:02:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R03-B2: 2024-03-21T14:27:00Z to 2024-03-25T17:02:00Z, 98.583 hours.
- 2024-03-21T14:27:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED,ELECTIVE_MORNING_SLOT_REQUIRED; transfer none; delivered 2024-03-21T14:27:47Z.
- 2024-03-25T17:02:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-03-25T23:03:20Z.

## Case 72: Catherine Singh

Birth 1955-06-25; recorded sex UNKNOWN; Prairie Creek Community Hospital; strata: DIRECT, ICU_STEPDOWN, TRANSFER, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_b9e76ff76701eda14ea73fa949b42f6d; episode episode_0a9844fb1ab9a52ca3460e2ed660d757; acuity 3; 2025-09-05T06:13:00Z arrival; 2025-09-05T06:13:00Z decision; 2025-09-05T06:28:00Z admission; 2025-09-10T12:13:00Z end; TRANSFER.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R01-B1: 2025-09-05T06:38:00Z to 2025-09-06T07:49:00Z, 25.183 hours.
- SURG-R03-B1: 2025-09-06T07:49:00Z to 2025-09-10T12:13:00Z, 100.400 hours.
- 2025-09-05T06:38:00Z OCCUPY: FIRST_PLACEMENT;WARD_OVERFLOW_ICU;PRIVATE_ROOM_PLACEMENT; transfer none; delivered 2025-09-05T06:39:05Z.
- 2025-09-06T07:49:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_0dbf71db926b8993701459e40a46bca3; delivered 2025-09-06T07:50:19Z.
- 2025-09-06T07:49:00Z OCCUPY: INTERNAL_STEPDOWN_IN;PRIVATE_ROOM_PLACEMENT; transfer ward_transfer_0dbf71db926b8993701459e40a46bca3; delivered 2025-09-06T07:49:43Z.
- 2025-09-10T12:13:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-09-10T12:13:42Z.

## Case 73: Roberto Leigh

Birth 1962-10-08; recorded sex M; Prairie Creek Community Hospital; strata: ED, HOME, ICU_STEPDOWN, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_02b26fadea2281a61726104888e4fafb; episode episode_7f5bf0a12cd425f517e81fe6d96b95d7; acuity 2; 2023-02-16T20:15:00Z arrival; 2023-02-16T20:15:00Z decision; 2023-02-16T20:30:00Z admission; 2023-02-24T02:15:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R01-B1: 2023-02-16T20:40:00Z to 2023-02-18T20:40:00Z, 48.000 hours.
- MED-R04-B1: 2023-02-18T20:40:00Z to 2023-02-24T02:15:00Z, 125.583 hours.
- 2023-02-16T20:40:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-02-16T20:41:54Z.
- 2023-02-18T20:40:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_e0e0cf71f5d1eda7ce1b0120c3d1491f; delivered 2023-02-18T20:41:57Z.
- 2023-02-18T20:40:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_e0e0cf71f5d1eda7ce1b0120c3d1491f; delivered 2023-02-18T20:41:28Z.
- 2023-02-24T02:15:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-02-24T02:15:23Z.

## Case 74: Rebecca Smith

Birth 1946-01-30; recorded sex F; Riverbend Community Hospital; strata: ELECTIVE, HOME, ICU_STEPDOWN, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_e2e54ab139977edbfe84ba4e84929e89; episode episode_1d1d730134f1f574534df7bd2cd4eae1; acuity 2; 2024-02-27T13:00:00Z arrival; 2024-02-27T13:00:00Z decision; 2024-02-27T13:15:00Z admission; 2024-03-02T11:00:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R03-B1: 2024-02-27T13:25:00Z to 2024-02-28T22:07:00Z, 32.700 hours.
- MED-R02-B2: 2024-02-28T22:07:00Z to 2024-03-02T11:00:00Z, 60.883 hours.
- 2024-02-27T13:25:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED,ELECTIVE_MORNING_SLOT_REQUIRED;WARD_OVERFLOW_ICU; transfer none; delivered 2024-02-27T13:26:28Z.
- 2024-02-28T22:07:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_f7319a7fe7d1435a4aaf99d962766284; delivered 2024-02-28T22:08:49Z.
- 2024-02-28T22:07:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_f7319a7fe7d1435a4aaf99d962766284; delivered 2024-02-28T22:08:41Z.
- 2024-03-02T11:00:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-03-02T11:01:05Z.

## Case 75: Mitchell Barrett

Birth 1963-03-11; recorded sex M; Riverbend Community Hospital; strata: BOARDING_OVER_HOUR, ED, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_536fb2550d3ddfe3871cbc96da94c496; episode episode_f9d14dea371b861ae822e39d7adb1fcc; acuity 2; 2024-01-26T14:32:00Z arrival; 2024-01-26T14:32:00Z decision; 2024-01-26T14:47:00Z admission; 2024-02-02T15:22:00Z end; HOME.
Time from admission/opening to first placement: 23.000 hours.
- MED-R04-B1: 2024-01-27T13:47:00Z to 2024-02-02T15:22:00Z, 145.583 hours.
- 2024-01-27T13:47:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED; transfer none; delivered 2024-01-27T13:48:36Z.
- 2024-02-02T15:22:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-02-02T15:22:59Z.

## Case 76: Jessica McCarthy

Birth 1983-08-03; recorded sex F; Riverbend Community Hospital; strata: ELECTIVE, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_24e869fb1e86ab0d1bd4056b8d14e4d4; episode episode_8004c0c337bebef544f44112a1581443; acuity 2; 2024-05-31T14:01:00Z arrival; 2024-05-31T14:01:00Z decision; 2024-05-31T14:16:00Z admission; 2024-06-04T16:01:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- SURG-R04-B2: 2024-05-31T14:26:00Z to 2024-06-04T16:01:00Z, 97.583 hours.
- 2024-05-31T14:26:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2024-05-31T14:26:41Z.
- 2024-06-04T16:01:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-06-04T16:01:45Z.

## Case 77: James Piotrowski

Birth 1937-06-22; recorded sex M; Oakwood Community Hospital; strata: ELECTIVE, HOME, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_246ea855c2fc52e785e5e5b9fc03396a; episode episode_d5fc31d6e8fc8fa8a6ab4ee7388dfa96; acuity 3; 2023-01-30T13:57:00Z arrival; 2023-01-30T13:57:00Z decision; 2023-01-30T14:12:00Z admission; 2023-02-03T02:57:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R02-B2: 2023-01-30T14:22:00Z to 2023-02-03T02:57:00Z, 84.583 hours.
- 2023-01-30T14:22:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-01-30T14:22:23Z.
- 2023-02-03T02:57:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-02-03T02:58:01Z.

## Case 78: Cara Johnson

Birth 1989-05-06; recorded sex F; Oakwood Community Hospital; strata: DIRECT, HOME, ICU_STEPDOWN, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_f1b48b9e9748a6ece03e6c9acd674a26; episode episode_f2a3278f0e3bf34491b80fcc3204b8d5; acuity 3; 2025-11-21T09:38:00Z arrival; 2025-11-21T09:38:00Z decision; 2025-11-21T09:53:00Z admission; 2025-11-27T16:38:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R02-B1: 2025-11-21T10:03:00Z to 2025-11-21T22:03:00Z, 12.000 hours.
- MED-R01-B1: 2025-11-21T22:03:00Z to 2025-11-27T16:38:00Z, 138.583 hours.
- 2025-11-21T10:03:00Z OCCUPY: FIRST_PLACEMENT;WARD_OVERFLOW_ICU; transfer none; delivered 2025-11-21T10:04:30Z.
- 2025-11-21T22:03:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_c7c7ca8b3a9c32456f5cfe4eedcd56c7; delivered 2025-11-21T22:03:30Z.
- 2025-11-21T22:03:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_c7c7ca8b3a9c32456f5cfe4eedcd56c7; delivered 2025-11-21T22:04:32Z.
- 2025-11-27T16:38:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-11-27T16:39:09Z.

## Case 79: Ronald McCrary

Birth 1930-08-29; recorded sex M; Prairie Creek Community Hospital; strata: ELECTIVE, HOME, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_e989a9ecf1774361fa5dc910a5f1d189; episode episode_44a1d4aa484393d96127dda89adf9f59; acuity 2; 2023-02-20T13:53:00Z arrival; 2023-02-20T13:53:00Z decision; 2023-02-20T14:08:00Z admission; 2023-02-23T15:53:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R04-B2: 2023-02-20T14:18:00Z to 2023-02-23T15:53:00Z, 73.583 hours.
- 2023-02-20T14:18:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-02-20T14:19:09Z.
- 2023-02-23T15:53:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-02-23T15:53:42Z.

## Case 80: Betty Jackson

Birth 1950-01-11; recorded sex F; Riverbend Community Hospital; strata: ELECTIVE, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_b77bfc1da2dd67ee9929358cfec78ce6; episode episode_e49fc7114868de9bbf338655aa7c7c68; acuity 3; 2023-11-13T14:13:00Z arrival; 2023-11-13T14:13:00Z decision; 2023-11-13T14:28:00Z admission; 2023-11-16T18:13:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R02-B2: 2023-11-13T14:38:00Z to 2023-11-16T18:13:00Z, 75.583 hours.
- 2023-11-13T14:38:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-11-13T14:39:36Z.
- 2023-11-16T18:13:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-11-16T18:13:42Z.

## Case 81: Anthony Yoon

Birth 1975-02-18; recorded sex M; Prairie Creek Community Hospital; strata: ED, HOME, ICU_STEPDOWN, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_1e091c696cb5fc3a143f6a5c8c02069a; episode episode_8de18fecfe5e53ebf7d4087d4567e9a1; acuity 2; 2025-07-10T12:50:00Z arrival; 2025-07-10T12:50:00Z decision; 2025-07-10T13:05:00Z admission; 2025-07-15T18:50:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R02-B1: 2025-07-10T13:15:00Z to 2025-07-11T01:15:00Z, 12.000 hours.
- SURG-R01-B2: 2025-07-11T01:15:00Z to 2025-07-15T18:50:00Z, 113.583 hours.
- 2025-07-10T13:15:00Z OCCUPY: FIRST_PLACEMENT;WARD_OVERFLOW_ICU; transfer none; delivered 2025-07-10T13:15:44Z.
- 2025-07-11T01:15:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_043359203649c05bcf77e59272dbe746; delivered 2025-07-11T01:16:34Z.
- 2025-07-11T01:15:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_043359203649c05bcf77e59272dbe746; delivered 2025-07-11T01:16:01Z.
- 2025-07-15T18:50:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-07-15T18:51:42Z.

## Case 82: Gary Trainor

Birth 1955-01-02; recorded sex M; Prairie Creek Community Hospital; strata: ED, HOME, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_604262640464f9e172d2c1b9bd3b2f35; episode episode_c156b66b5aac2a7dccd7285bcdd28b3f; acuity 3; 2025-07-28T02:08:00Z arrival; 2025-07-28T02:08:00Z decision; 2025-07-28T02:23:00Z admission; 2025-08-03T00:08:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R05-B2: 2025-07-28T02:33:00Z to 2025-08-03T00:08:00Z, 141.583 hours.
- 2025-07-28T02:33:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2025-07-28T02:34:00Z.
- 2025-08-03T00:08:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-08-03T00:09:33Z.

## Case 83: Nancy Solomon

Birth 1955-03-13; recorded sex F; Riverbend Community Hospital; strata: ELECTIVE, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_c08cae189ea31470fe7f78795c47aa83; episode episode_b6a0dd7e34506be5187672233a01ed8b; acuity 2; 2023-05-01T14:23:00Z arrival; 2023-05-01T14:23:00Z decision; 2023-05-01T14:38:00Z admission; 2023-05-05T14:23:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R03-B1: 2023-05-01T14:48:00Z to 2023-05-05T14:23:00Z, 95.583 hours.
- 2023-05-01T14:48:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-05-01T14:48:47Z.
- 2023-05-05T14:23:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-05-05T14:24:23Z.

## Case 84: Roberta Reynolds

Birth 1957-03-03; recorded sex F; Riverbend Community Hospital; strata: BOARDING_OVER_DAY, BOARDING_OVER_HOUR, DIRECT, TRANSFER, UNMET_EXTERNAL_TRANSFER, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_264dcff01138db8fa100cae1864006f7; episode episode_618454c0dfe0a4cf0cf0e54c6a25e293; acuity 3; 2024-02-13T06:34:00Z arrival; 2024-02-13T06:34:00Z decision; 2024-02-13T06:49:00Z admission; 2024-02-14T06:49:00Z end; TRANSFER.
Time from admission/opening to first placement: 24.000 hours.
- Source operational note @ 2024-02-14T06:49:00Z: Placement disposition for encounter encounter_264dcff01138db8fa100cae1864006f7: external transfer at 2024-02-14T06:49:00Z after 24 hours from inpatient admission awaiting a compatible bed. Cause: COMPATIBLE_CAPACITY_EXHAUSTED. Receiving care and later outcome are outside the modeled network.

## Case 85: Helen Canchola

Birth 1931-10-28; recorded sex F; Riverbend Community Hospital; strata: ED, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_331c75cdae02dfd6bbde845b96bac36c; episode episode_54c76bad38078271f6e20f8728b386c9; acuity 3; 2023-08-19T15:06:00Z arrival; 2023-08-19T15:06:00Z decision; 2023-08-19T15:21:00Z admission; 2023-08-25T10:06:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R02-B2: 2023-08-19T15:31:00Z to 2023-08-25T10:06:00Z, 138.583 hours.
- 2023-08-19T15:31:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-08-19T15:31:45Z.
- 2023-08-25T10:06:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-08-25T10:06:37Z.

## Case 86: Nathan McCune

Birth 1975-11-02; recorded sex M; Prairie Creek Community Hospital; strata: ELECTIVE, HOME, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_d24ad007e02771541f3efe5925dea3e4; episode episode_46792e4a38deab0553b9aee77bc180ad; acuity 2; 2025-03-24T14:54:00Z arrival; 2025-03-24T14:54:00Z decision; 2025-03-24T15:09:00Z admission; 2025-03-27T20:54:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R02-B2: 2025-03-24T15:19:00Z to 2025-03-27T20:54:00Z, 77.583 hours.
- 2025-03-24T15:19:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2025-03-24T15:20:20Z.
- 2025-03-27T20:54:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-03-27T20:55:21Z.

## Case 87: John Cothran

Birth 1932-10-03; recorded sex M; Riverbend Community Hospital; strata: ED, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_1dec3809c61bd405be20c6263718dc69; episode episode_86ac4e6841829f1773a73a332a69d10d; acuity 2; 2024-09-29T04:02:00Z arrival; 2024-09-29T04:02:00Z decision; 2024-09-29T04:17:00Z admission; 2024-10-03T19:02:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- SURG-R01-B1: 2024-09-29T04:27:00Z to 2024-10-03T19:02:00Z, 110.583 hours.
- 2024-09-29T04:27:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2024-09-29T04:27:35Z.
- 2024-10-03T19:02:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-10-03T19:02:57Z.

## Case 88: Gary Maurer

Birth 1950-10-14; recorded sex M; Oakwood Community Hospital; strata: ELECTIVE, HOME, ICU_STEPDOWN, MAINTENANCE_SEASON, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_c39f97efc4ed3cb7cae697ae4f4db316; episode episode_727ebf5d74474623a7db131c840780fb; acuity 3; 2024-07-30T16:37:00Z arrival; 2024-07-30T16:37:00Z decision; 2024-07-30T16:52:00Z admission; 2024-08-03T19:37:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R03-B1: 2024-07-30T17:02:00Z to 2024-08-01T06:23:00Z, 37.350 hours.
- MED-R02-B2: 2024-08-01T06:23:00Z to 2024-08-03T19:37:00Z, 61.233 hours.
- 2024-07-30T17:02:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED,MAINTENANCE_REDUCED_CAPACITY;WARD_OVERFLOW_ICU; transfer none; delivered 2024-07-30T17:02:46Z.
- 2024-08-01T06:23:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_b0e1207c9919e011ecdb7c80392d8e0e; delivered 2024-08-01T06:23:52Z.
- 2024-08-01T06:23:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_b0e1207c9919e011ecdb7c80392d8e0e; delivered 2024-08-01T06:23:47Z.
- 2024-08-03T19:37:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-08-03T19:37:50Z.

## Case 89: Heather Loomis

Birth 1971-03-06; recorded sex F; Prairie Creek Community Hospital; strata: BOARDING_OVER_HOUR, ED, HOME, ICU_STEPDOWN, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_422678c0633f5a17150061ea1848915d; episode episode_c1eda42c169dd01560b5385f166476fe; acuity 2; 2024-02-15T19:04:00Z arrival; 2024-02-15T19:04:00Z decision; 2024-02-15T19:19:00Z admission; 2024-02-21T18:21:00Z end; HOME.
Time from admission/opening to first placement: 5.450 hours.
- ICU-R03-B1: 2024-02-16T00:46:00Z to 2024-02-17T09:11:00Z, 32.417 hours.
- SURG-R03-B2: 2024-02-17T09:11:00Z to 2024-02-21T18:21:00Z, 105.167 hours.
- 2024-02-16T00:46:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED;WARD_OVERFLOW_ICU; transfer none; delivered 2024-02-16T00:46:38Z.
- 2024-02-17T09:11:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_4abf5ff59fc0c06a74b937c5f8209a68; delivered 2024-02-17T09:12:25Z.
- 2024-02-17T09:11:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_4abf5ff59fc0c06a74b937c5f8209a68; delivered 2024-02-17T09:12:16Z.
- 2024-02-21T18:21:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-02-21T18:22:55Z.

## Case 90: Mark Williams

Birth 1974-10-25; recorded sex M; Prairie Creek Community Hospital; strata: ELECTIVE, HOME, ICU_STEPDOWN, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_42e54026cf9559d22552b8832bf92fe2; episode episode_a86789d78d64301901da7b62dca02bf3; acuity 2; 2023-08-23T17:29:00Z arrival; 2023-08-23T17:29:00Z decision; 2023-08-23T17:44:00Z admission; 2023-08-27T18:29:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R02-B1: 2023-08-23T17:54:00Z to 2023-08-24T13:56:00Z, 20.033 hours.
- MED-R02-B1: 2023-08-24T13:56:00Z to 2023-08-27T18:29:00Z, 76.550 hours.
- 2023-08-23T17:54:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED;WARD_OVERFLOW_ICU; transfer none; delivered 2023-08-23T17:55:48Z.
- 2023-08-24T13:56:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_6d20b2985aff55b9ec5294a35952153a; delivered 2023-08-24T13:56:41Z.
- 2023-08-24T13:56:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_6d20b2985aff55b9ec5294a35952153a; delivered 2023-08-24T13:57:53Z.
- 2023-08-27T18:29:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-08-27T18:29:12Z.

## Case 91: James Weeks

Birth 1942-12-30; recorded sex M; Riverbend Community Hospital; strata: ED, HOME, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_21914b3011efa967e107356cc2ccb81b; episode episode_aed2dd60d250f09e240630ee4a72c371; acuity 2; 2023-04-24T13:58:00Z arrival; 2023-04-24T13:58:00Z decision; 2023-04-24T14:13:00Z admission; 2023-04-30T20:58:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- SURG-R03-B2: 2023-04-24T14:23:00Z to 2023-04-30T20:58:00Z, 150.583 hours.
- 2023-04-24T14:23:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-04-24T14:24:33Z.
- 2023-04-30T20:58:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-04-30T20:59:17Z.

## Case 92: James Hassan

Birth 1946-02-10; recorded sex X; Oakwood Community Hospital; strata: ELECTIVE, HOME, ICU_STEPDOWN, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_59404689c66bc3639e60d7f3e4f205b0; episode episode_89cb84fa1fc9fdfb7bf254e0aa859495; acuity 2; 2025-10-17T14:11:00Z arrival; 2025-10-17T14:11:00Z decision; 2025-10-17T14:26:00Z admission; 2025-10-20T21:11:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R02-B1: 2025-10-17T14:36:00Z to 2025-10-18T17:05:00Z, 26.483 hours.
- MED-R04-B1: 2025-10-18T17:05:00Z to 2025-10-20T21:11:00Z, 52.100 hours.
- 2025-10-17T14:36:00Z OCCUPY: FIRST_PLACEMENT;WARD_OVERFLOW_ICU;PRIVATE_ROOM_PLACEMENT; transfer none; delivered 2025-10-17T14:37:01Z.
- 2025-10-18T17:05:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_3f0d81239479fefbabb9edcc5b4fa179; delivered 2025-10-18T17:06:00Z.
- 2025-10-18T17:05:00Z OCCUPY: INTERNAL_STEPDOWN_IN;PRIVATE_ROOM_PLACEMENT; transfer ward_transfer_3f0d81239479fefbabb9edcc5b4fa179; delivered 2025-10-18T17:06:11Z.
- 2025-10-20T21:11:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-10-20T21:12:28Z.

## Case 93: David Partida

Birth 1969-02-10; recorded sex M; Prairie Creek Community Hospital; strata: ELECTIVE, HOME, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_e1822481ce38dba55278e45f51131d3e; episode episode_8ad881b43e5018b474ca1e23d14dd366; acuity 2; 2024-03-28T12:00:00Z arrival; 2024-03-28T12:00:00Z decision; 2024-03-28T12:15:00Z admission; 2024-04-01T05:00:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R01-B2: 2024-03-28T12:25:00Z to 2024-04-01T05:00:00Z, 88.583 hours.
- 2024-03-28T12:25:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED,ELECTIVE_MORNING_SLOT_REQUIRED; transfer none; delivered 2024-03-28T12:25:30Z.
- 2024-04-01T05:00:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-04-01T05:01:42Z.

## Case 94: Justin Gao

Birth 1986-11-17; recorded sex M; Prairie Creek Community Hospital; strata: BOARDING_OVER_DAY, BOARDING_OVER_HOUR, ED, PRIVATE_ISOLATION, TRANSFER, UNMET_EXTERNAL_TRANSFER, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_ee6ad6382654b6cc3a92d1f38af70296; episode episode_f31ea8eac0005bcb0e2856de6ae7aafc; acuity 2; 2024-02-21T14:48:00Z arrival; 2024-02-21T14:48:00Z decision; 2024-02-21T15:03:00Z admission; 2024-02-22T15:03:00Z end; TRANSFER.
Time from admission/opening to first placement: 24.000 hours.
- Source operational note @ 2024-02-21T15:03:00Z: Placement assessment for Justin Gao, age 37: suspected transmissible respiratory illness; isolation-capable private room requested. Recorded at 2024-02-21T15:03:00Z.
- Source operational note @ 2024-02-22T15:03:00Z: Placement disposition for encounter encounter_ee6ad6382654b6cc3a92d1f38af70296: external transfer at 2024-02-22T15:03:00Z after 24 hours from inpatient admission awaiting a compatible bed. Cause: COMPATIBLE_CAPACITY_EXHAUSTED,ICU_STABILIZATION_REQUIRED. Receiving care and later outcome are outside the modeled network.

## Case 95: Stephanie Williams

Birth 1987-11-29; recorded sex F; Riverbend Community Hospital; strata: BOARDING_OVER_HOUR, DIRECT, HOME, ICU, PRIVATE_ISOLATION, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_ec3d5fb315ab23b30241b02ac056e305; episode episode_75cde67ac764be4e7dcea8429eb372b4; acuity 3; 2024-01-02T22:04:00Z arrival; 2024-01-02T22:04:00Z decision; 2024-01-02T22:19:00Z admission; 2024-01-09T08:41:00Z end; HOME.
Time from admission/opening to first placement: 5.783 hours.
- ICU-R01-B1: 2024-01-03T04:06:00Z to 2024-01-09T08:41:00Z, 148.583 hours.
- 2024-01-03T04:06:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED,ISOLATION_COHORT_REQUIRED;WARD_OVERFLOW_ICU;PRIVATE_ISOLATION_PLACEMENT; transfer none; delivered 2024-01-03T04:06:21Z.
- 2024-01-09T08:41:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2024-01-09T08:42:27Z.
- Source operational note @ 2024-01-02T22:19:00Z: Placement assessment for Stephanie Williams, age 36: suspected transmissible respiratory illness; isolation-capable private room requested. Recorded at 2024-01-02T22:19:00Z.

## Case 96: Veronica Marion

Birth 1999-12-18; recorded sex F; Oakwood Community Hospital; strata: ED, HOME, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_40ed0f8b43bd638459ea57b86dafe78e; episode episode_a1c8ae34456e091bac93c2db904ff3b2; acuity 2; 2025-07-07T00:45:00Z arrival; 2025-07-07T00:45:00Z decision; 2025-07-07T01:00:00Z admission; 2025-07-12T04:45:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R02-B2: 2025-07-07T01:10:00Z to 2025-07-12T04:45:00Z, 123.583 hours.
- 2025-07-07T01:10:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2025-07-07T01:10:45Z.
- 2025-07-12T04:45:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2025-07-12T04:46:42Z.

## Case 97: Leonard Rowden

Birth 1948-11-04; recorded sex M; Oakwood Community Hospital; strata: ED, HOME, ICU_STEPDOWN, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_aa529f9f588ef4b78238142927c7f952; episode episode_59ecad505ae398574ba5042ad11026a6; acuity 2; 2023-05-20T03:36:00Z arrival; 2023-05-20T03:36:00Z decision; 2023-05-20T03:51:00Z admission; 2023-05-24T15:56:00Z end; HOME.
Time from admission/opening to first placement: 0.500 hours.
- ICU-R03-B1: 2023-05-20T04:21:00Z to 2023-05-22T04:21:00Z, 48.000 hours.
- MED-R01-B2: 2023-05-22T04:21:00Z to 2023-05-24T15:56:00Z, 59.583 hours.
- 2023-05-20T04:21:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED,ICU_STABILIZATION_REQUIRED; transfer none; delivered 2023-05-20T04:22:39Z.
- 2023-05-22T04:21:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_1d0a29a26299dc7b6977eefb45db1c1b; delivered 2023-05-22T04:22:49Z.
- 2023-05-22T04:21:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_1d0a29a26299dc7b6977eefb45db1c1b; delivered 2023-05-22T04:21:58Z.
- 2023-05-24T15:56:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-05-24T15:57:52Z.

## Case 98: Michael Ingram

Birth 1954-07-18; recorded sex M; Oakwood Community Hospital; strata: ELECTIVE, HOME, ICU_STEPDOWN, facility_7990133218ef060b178c3cf8a0825f76.
Encounter encounter_7504ba5dbd325bc4aeed95c30a261261; episode episode_52a3366e680f165a084c0255651a33d5; acuity 2; 2023-11-01T13:42:00Z arrival; 2023-11-01T13:42:00Z decision; 2023-11-01T13:57:00Z admission; 2023-11-05T10:42:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- ICU-R03-B1: 2023-11-01T14:07:00Z to 2023-11-03T06:58:00Z, 40.850 hours.
- SURG-R03-B2: 2023-11-03T06:58:00Z to 2023-11-05T10:42:00Z, 51.733 hours.
- 2023-11-01T14:07:00Z OCCUPY: FIRST_PLACEMENT_AFTER_WAIT:COMPATIBLE_CAPACITY_EXHAUSTED;WARD_OVERFLOW_ICU; transfer none; delivered 2023-11-01T14:07:48Z.
- 2023-11-03T06:58:00Z VACATE: INTERNAL_STEPDOWN_OUT; transfer ward_transfer_cb7fb63a0d5ae7a48c147563c0614f8d; delivered 2023-11-03T06:58:57Z.
- 2023-11-03T06:58:00Z OCCUPY: INTERNAL_STEPDOWN_IN; transfer ward_transfer_cb7fb63a0d5ae7a48c147563c0614f8d; delivered 2023-11-03T06:59:16Z.
- 2023-11-05T10:42:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-11-05T10:43:40Z.

## Case 99: Monica Bigler

Birth 1999-11-01; recorded sex F; Riverbend Community Hospital; strata: BOARDING_OVER_DAY, BOARDING_OVER_HOUR, ED, TRANSFER, UNMET_EXTERNAL_TRANSFER, facility_a56f2c2e3a76834b7a766c6ba89f7afe.
Encounter encounter_0b15e25336f90057bafaa12c88ce4ff1; episode episode_bb3546f626cb24e8c3bb40e083911893; acuity 3; 2024-03-21T22:36:00Z arrival; 2024-03-21T22:36:00Z decision; 2024-03-21T22:51:00Z admission; 2024-03-22T22:51:00Z end; TRANSFER.
Time from admission/opening to first placement: 24.000 hours.
- Source operational note @ 2024-03-22T22:51:00Z: Placement disposition for encounter encounter_0b15e25336f90057bafaa12c88ce4ff1: external transfer at 2024-03-22T22:51:00Z after 24 hours from inpatient admission awaiting a compatible bed. Cause: COMPATIBLE_CAPACITY_EXHAUSTED. Receiving care and later outcome are outside the modeled network.

## Case 100: Douglas Moreno

Birth 1979-06-25; recorded sex M; Prairie Creek Community Hospital; strata: ELECTIVE, HOME, facility_a6a95cfdcf7df4bfa7fe88c206195c24.
Encounter encounter_0d0f1ade71b0c6ed9cc707f387771178; episode episode_82726e853a839bb5f49f2d37262c8ba3; acuity 3; 2023-12-18T15:12:00Z arrival; 2023-12-18T15:12:00Z decision; 2023-12-18T15:27:00Z admission; 2023-12-22T16:12:00Z end; HOME.
Time from admission/opening to first placement: 0.167 hours.
- MED-R05-B2: 2023-12-18T15:37:00Z to 2023-12-22T16:12:00Z, 96.583 hours.
- 2023-12-18T15:37:00Z OCCUPY: FIRST_PLACEMENT; transfer none; delivered 2023-12-18T15:38:23Z.
- 2023-12-22T16:12:00Z VACATE: OBSERVED_CARE_END; transfer none; delivered 2023-12-22T16:13:09Z.

## Capacity and source correction review

- ICU-R01-B1 (location_8b117e98d2d91b78772532bf72fcf9e3): 2023-01-03T07:01:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_9d6dcab581bbb03100a2daf0bf855a66.
- ICU-R01-B1 (location_05d8b9f3f9d04c571f9c0e104b127173): 2023-01-03T07:02:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_857d7ded1439590862f50ea203edf89a.
- ICU-R01-B1 (location_9de65a63bc536eb7257560506e59c386): 2023-01-03T07:03:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_f37aed1f64a737fea0fc0a5e725a8d77.
- ICU-R04-B1 (location_d102d3155e8feb62a4eba333378462af): 2023-01-03T07:03:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_0380d576aad6239338bc9afedff7112a.
- ICU-R04-B1 (location_b387dd0bb588d2a2d64139b1a2f5975c): 2023-01-03T07:06:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_8b44ac7c4cc2bdf9830a2458a22ed53f.
- ICU-R03-B1 (location_c9ea5395f2cf2cb82ec26babd719740e): 2023-01-03T07:08:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_97f69315a38132c65da03ed545f014b6.
- ICU-R01-B1 (location_8b117e98d2d91b78772532bf72fcf9e3): 2023-01-03T07:16:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R02-B1 (location_c6d793c93d843ba35e0b355f5e64f26f): 2023-01-03T07:16:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_ec338f74756dff48747863e0adee090e.
- ICU-R01-B1 (location_05d8b9f3f9d04c571f9c0e104b127173): 2023-01-03T07:17:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R01-B1 (location_9de65a63bc536eb7257560506e59c386): 2023-01-03T07:18:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R04-B1 (location_d102d3155e8feb62a4eba333378462af): 2023-01-03T07:18:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R04-B1 (location_b387dd0bb588d2a2d64139b1a2f5975c): 2023-01-03T07:21:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R02-B1 (location_db311c7fdb45c7057d3ca6c5990ddfe2): 2023-01-03T07:21:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_b392d9ce43d9463b28350f8faeb73ce7.
- ICU-R04-B1 (location_87fd2b6476c332bb86ac3387365e6ef5): 2023-01-03T07:23:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_fd05a1ba82c84668ff4d0cba3a898dd7.
- ICU-R03-B1 (location_c9ea5395f2cf2cb82ec26babd719740e): 2023-01-03T07:23:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R03-B1 (location_efdda3b2a94df13b9317c6d32ec5fb41): 2023-01-03T07:23:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_eea6824df2be78699b75d7e899806b1d.
- ICU-R03-B1 (location_d1ce5e083547b29599bcce98ddb16f2d): 2023-01-03T07:26:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_b09e2ed21e82aca34dcea221e0c8330d.
- ICU-R02-B1 (location_c6d793c93d843ba35e0b355f5e64f26f): 2023-01-03T07:31:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R02-B1 (location_db311c7fdb45c7057d3ca6c5990ddfe2): 2023-01-03T07:36:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R04-B1 (location_87fd2b6476c332bb86ac3387365e6ef5): 2023-01-03T07:38:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R03-B1 (location_efdda3b2a94df13b9317c6d32ec5fb41): 2023-01-03T07:38:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R03-B1 (location_d1ce5e083547b29599bcce98ddb16f2d): 2023-01-03T07:41:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R01-B1 (location_1ef5a9db41ae73fac806607303e00a28): 2023-01-04T05:00:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_edfefc3c6e12096c5c6b321a94168720.
- SURG-R01-B1 (location_1ef5a9db41ae73fac806607303e00a28): 2023-01-04T05:15:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R03-B2 (location_a89c4fe86776f8953ceb045ab4a0d738): 2023-01-04T11:14:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_4534482db4b6a0223aa28a61a2400893.
- MED-R03-B2 (location_a89c4fe86776f8953ceb045ab4a0d738): 2023-01-04T11:29:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R04-B2 (location_5bd5a9145130b6a7f3f7d64f0ae1b07a): 2023-01-04T13:27:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_d2543d6407f37b1f7627922b4b3c86a8.
- SURG-R04-B2 (location_5bd5a9145130b6a7f3f7d64f0ae1b07a): 2023-01-04T13:42:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R02-B1 (location_96198727c3af8384181d5574cffd55d2): 2023-01-04T16:12:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_6c982a9255c2af6146ace40b55e08bca.
- ICU-R02-B1 (location_96198727c3af8384181d5574cffd55d2): 2023-01-04T16:27:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R02-B2 (location_0390bc1f7211b056fc235812aeeb2b2c): 2023-01-04T22:05:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_35442932e931ae80fb65d67e336b0732.
- SURG-R02-B2 (location_0390bc1f7211b056fc235812aeeb2b2c): 2023-01-04T22:20:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R04-B1 (location_52c768c54855f1180306335168bc2f88): 2023-01-05T01:05:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_16b56aa7d692c597ce2ae19cde13e0c7.
- MED-R04-B1 (location_52c768c54855f1180306335168bc2f88): 2023-01-05T01:20:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R04-B2 (location_d105989be0147691b4c7bfbcbc4d7e32): 2023-01-05T11:29:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_fde1e4657d88eacfc48c875c79d7252e.
- MED-R04-B2 (location_d105989be0147691b4c7bfbcbc4d7e32): 2023-01-05T11:44:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R04-B2 (location_d0efc1f0b72fe4bf780059e14b5421f3): 2023-01-05T16:20:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_4056bb8fb0fc4c72d81afa05f7e5ef8b.
- SURG-R04-B2 (location_d0efc1f0b72fe4bf780059e14b5421f3): 2023-01-05T16:35:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R04-B1 (location_75040bf573390196e12442a9fd363feb): 2023-01-05T18:17:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_8719c6dff9e82948f9b8dcfeeb93748c.
- SURG-R02-B2 (location_00438655256908a53eb0df2679bb6a91): 2023-01-05T18:20:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_34ea6d0faec96bc3c00269358399bff2.
- MED-R04-B1 (location_75040bf573390196e12442a9fd363feb): 2023-01-05T18:32:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R02-B2 (location_00438655256908a53eb0df2679bb6a91): 2023-01-05T18:35:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R05-B1 (location_78063ac49b3826812656bc1c46a8a0f6): 2023-01-05T19:04:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_2a2f2eedb670a2bc149419b2ca0e0258.
- SURG-R05-B1 (location_78063ac49b3826812656bc1c46a8a0f6): 2023-01-05T19:19:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R01-B1 (location_8b117e98d2d91b78772532bf72fcf9e3): 2023-01-06T03:50:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_7433c8c926f90fbe2df07cd33ffdc676.
- ICU-R01-B1 (location_8b117e98d2d91b78772532bf72fcf9e3): 2023-01-06T04:05:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R04-B1 (location_6880ba3dc60367e38e2afbc737f05e7c): 2023-01-06T04:18:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_a8aea1337c4e1893ed4e6468d73732c7.
- SURG-R04-B1 (location_6880ba3dc60367e38e2afbc737f05e7c): 2023-01-06T04:33:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R01-B1 (location_05d8b9f3f9d04c571f9c0e104b127173): 2023-01-06T05:09:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_a895ae02dc67a6154713ea8648d631c7.
- MED-R02-B1 (location_8168ca706d0df4c97842006697510bb0): 2023-01-06T05:17:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_1ac5897be73bfd4b03a41787d9d286d6.
- SURG-R02-B1 (location_8e501cbeef106a89f0864afbc81a5d2f): 2023-01-06T05:21:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_847b400a8b52ca0bb5b77f9fdf128a45.
- ICU-R01-B1 (location_05d8b9f3f9d04c571f9c0e104b127173): 2023-01-06T05:24:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R02-B1 (location_8168ca706d0df4c97842006697510bb0): 2023-01-06T05:32:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R02-B1 (location_8e501cbeef106a89f0864afbc81a5d2f): 2023-01-06T05:36:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R02-B2 (location_0b1c0d9e80edd1fa301ddf0174a3a23f): 2023-01-06T06:26:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_a118890a61ef31172834bf0b79b611bb.
- MED-R02-B2 (location_0b1c0d9e80edd1fa301ddf0174a3a23f): 2023-01-06T06:41:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R04-B2 (location_06721c718818ad3665e923b23e34ff12): 2023-01-06T07:11:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_6533cb627c8756eae4d4fe00d202132c.
- MED-R04-B2 (location_06721c718818ad3665e923b23e34ff12): 2023-01-06T07:26:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R02-B1 (location_96198727c3af8384181d5574cffd55d2): 2023-01-06T08:53:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_ea457e00173090707549250128332c4e.
- ICU-R02-B1 (location_96198727c3af8384181d5574cffd55d2): 2023-01-06T09:08:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R04-B2 (location_65f8c6430871d15d8c804f5b1dd1acba): 2023-01-06T10:30:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_65af03f9182086f41990d578a7b10027.
- MED-R04-B2 (location_65f8c6430871d15d8c804f5b1dd1acba): 2023-01-06T10:45:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R05-B2 (location_07314bcb33b8a2f0ca2a06cac413a95f): 2023-01-06T14:02:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_bf853b1fa6a556f2a10ffb79331b49f7.
- MED-R05-B2 (location_07314bcb33b8a2f0ca2a06cac413a95f): 2023-01-06T14:17:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R01-B1 (location_12df24a3232ee95c3f230388290e8f92): 2023-01-06T14:18:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_9da5fa863eed8a7148e66260a60fd2e7.
- MED-R01-B1 (location_12df24a3232ee95c3f230388290e8f92): 2023-01-06T14:33:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R02-B2 (location_e3247a7caadaa3230e75062700081fef): 2023-01-06T17:07:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_6ff7c75157995203d94fadc659c0ef74.
- MED-R02-B2 (location_e3247a7caadaa3230e75062700081fef): 2023-01-06T17:22:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R02-B2 (location_2487a9099ce9481c10cddd42fe9c9d06): 2023-01-06T19:25:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_473832a856bfc7025785b2c0c5de6981.
- MED-R02-B2 (location_2487a9099ce9481c10cddd42fe9c9d06): 2023-01-06T19:40:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R01-B1 (location_df7673692728c4305c643cbf570ab7a1): 2023-01-06T21:03:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_5068ff047b8c293c807618b206679e44.
- SURG-R01-B1 (location_df7673692728c4305c643cbf570ab7a1): 2023-01-06T21:18:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R03-B2 (location_530cf07f9ec025336417912c9988254f): 2023-01-06T22:17:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_8bf293661339b507e37efb3d0a4e10c3.
- SURG-R03-B2 (location_530cf07f9ec025336417912c9988254f): 2023-01-06T22:32:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R05-B1 (location_2b9e2c82fe191f115ed6e64fa428bae3): 2023-01-06T23:12:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_fa8e1e074de3133d2b260e851031331c.
- SURG-R05-B1 (location_2b9e2c82fe191f115ed6e64fa428bae3): 2023-01-06T23:27:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R05-B2 (location_74f466c3508e8323ce6d4d2cbc134a20): 2023-01-07T00:09:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_8844f4844fd2b1fb931c7d0af384479e.
- SURG-R05-B2 (location_74f466c3508e8323ce6d4d2cbc134a20): 2023-01-07T00:24:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R05-B2 (location_ea58eefadbc574d707438951616ec85f): 2023-01-07T01:30:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_4716e5e47aa247930a3c4c1abf2253c0.
- MED-R05-B2 (location_ea58eefadbc574d707438951616ec85f): 2023-01-07T01:45:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R02-B1 (location_48ad36d4261763ef1d4987004c8dda42): 2023-01-07T02:13:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_1ea1941bb33554ec69eb125d8f857359.
- MED-R02-B1 (location_48ad36d4261763ef1d4987004c8dda42): 2023-01-07T02:28:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R04-B1 (location_60f180784cd4bdcf24b93fdd148fd906): 2023-01-07T06:22:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_341866fe071b4dad20e748138ac068db.
- SURG-R04-B1 (location_60f180784cd4bdcf24b93fdd148fd906): 2023-01-07T06:37:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R05-B1 (location_8f68eaaee92401a7696f1433368e0e31): 2023-01-07T12:16:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_6b15d149c28191252827547131ab3938.
- MED-R05-B1 (location_8f68eaaee92401a7696f1433368e0e31): 2023-01-07T12:31:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R01-B1 (location_d3d4912c75cd03032a7ed02b8c60a16f): 2023-01-07T13:12:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_824a166a2f599feddbc7c7be6252900f.
- MED-R01-B1 (location_d3d4912c75cd03032a7ed02b8c60a16f): 2023-01-07T13:27:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R03-B1 (location_b0b190657eaec3fb1fe1bfacc3d5dbf4): 2023-01-07T14:10:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_76f00dac13e2faaf2a8591573dccd86f.
- MED-R03-B1 (location_b0b190657eaec3fb1fe1bfacc3d5dbf4): 2023-01-07T14:25:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R05-B2 (location_3b05e0bf75ecccc8a1f16c4aff1c142a): 2023-01-07T15:02:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_279b4e451932c7dea880f565e32ef8c7.
- SURG-R05-B2 (location_3b05e0bf75ecccc8a1f16c4aff1c142a): 2023-01-07T15:17:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R01-B1 (location_05d8b9f3f9d04c571f9c0e104b127173): 2023-01-07T15:25:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_02d5de2436a72dbc40ce9e779766d11a.
- MED-R03-B1 (location_1eec75f78a0008a5add8af863305c3c7): 2023-01-07T15:25:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_d6210f1108103dc0fdeec66a56011d01.
- ICU-R01-B1 (location_05d8b9f3f9d04c571f9c0e104b127173): 2023-01-07T15:40:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R03-B1 (location_1eec75f78a0008a5add8af863305c3c7): 2023-01-07T15:40:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R02-B1 (location_db311c7fdb45c7057d3ca6c5990ddfe2): 2023-01-07T16:03:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_e641f546099eeaaeb9821a82dbfea5b3.
- ICU-R02-B1 (location_db311c7fdb45c7057d3ca6c5990ddfe2): 2023-01-07T16:18:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R02-B1 (location_c8eabf541e783386bc8faec9f2f28d3e): 2023-01-07T17:30:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_ecc8c7567d5f9a1ea1b2cbd9aa1f1857.
- SURG-R02-B1 (location_c8eabf541e783386bc8faec9f2f28d3e): 2023-01-07T17:45:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R02-B1 (location_96198727c3af8384181d5574cffd55d2): 2023-01-07T17:55:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_592bd720b576d384fb5062dfa26e9082.
- ICU-R02-B1 (location_96198727c3af8384181d5574cffd55d2): 2023-01-07T18:10:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R05-B1 (location_943752092d54ed5cc767419c4e972f44): 2023-01-07T20:00:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_f535fa5be65a2c8ab6e27b3e4da79325.
- MED-R05-B1 (location_943752092d54ed5cc767419c4e972f44): 2023-01-07T20:15:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R03-B1 (location_3aa43fdc2a28c82519d9f11cf203dc00): 2023-01-07T21:29:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_3e7d75838da55d41aefa561078edd491.
- SURG-R03-B1 (location_3aa43fdc2a28c82519d9f11cf203dc00): 2023-01-07T21:44:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R02-B2 (location_320d59365dd7a10ff3a420240d5e51c6): 2023-01-07T23:16:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_cf0ab0363c3d3c52e4afcf34a5ad3bea.
- SURG-R04-B1 (location_afb8e0028c27f2f4eb74b3db103a6f02): 2023-01-07T23:21:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_93d8ab70a72609fca40b7ca907a909a7.
- SURG-R02-B2 (location_320d59365dd7a10ff3a420240d5e51c6): 2023-01-07T23:31:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R04-B1 (location_afb8e0028c27f2f4eb74b3db103a6f02): 2023-01-07T23:36:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R01-B1 (location_7970af2187f47c6b8c3a41ffa2bb2692): 2023-01-08T10:22:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_6a9747e4382a1648681f3f8c9eef2ea5.
- SURG-R01-B1 (location_7970af2187f47c6b8c3a41ffa2bb2692): 2023-01-08T10:37:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R03-B2 (location_96e1a210cd26be5eb1e03bdd63f3a12b): 2023-01-08T11:07:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_59a0bc21c87a0d938e83a4b497f45130.
- SURG-R03-B2 (location_96e1a210cd26be5eb1e03bdd63f3a12b): 2023-01-08T11:22:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R05-B1 (location_e036befe3516e17e39b77384432a248b): 2023-01-08T14:16:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_dc41730e847f4ba3bd4f9c92ebc11207.
- SURG-R05-B1 (location_e036befe3516e17e39b77384432a248b): 2023-01-08T14:31:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R02-B1 (location_44af35c09ab1d449b2ec7c95249ecb1f): 2023-01-08T15:20:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_226f5bf2eab2202b0d43db8cd2a7350a.
- MED-R02-B1 (location_44af35c09ab1d449b2ec7c95249ecb1f): 2023-01-08T15:35:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R01-B2 (location_cc192e378df8c18c16099778749e3307): 2023-01-08T16:02:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_2b489389852cf343dbbd59e8da935ea9.
- SURG-R01-B2 (location_cc192e378df8c18c16099778749e3307): 2023-01-08T16:17:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R03-B1 (location_dd1ec7ff6c29788da9c5887e3e7b4021): 2023-01-08T16:22:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_b1c68cdf2015377c6072273494a15890.
- SURG-R03-B1 (location_dd1ec7ff6c29788da9c5887e3e7b4021): 2023-01-08T16:37:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R02-B1 (location_77d177e58b033943c41708041fd1a70e): 2023-01-08T17:29:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_700bbf906a6f16ce8d2980afe2007bd0.
- SURG-R02-B1 (location_77d177e58b033943c41708041fd1a70e): 2023-01-08T17:44:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R03-B2 (location_1fc650d4a6c4641384c74e0f00ffe590): 2023-01-08T21:22:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_7a7152a289f2b187f5952a670209346d.
- SURG-R03-B2 (location_72ef9856cd2764312d0cfab0ee44219a): 2023-01-08T21:27:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_db77056b1c3a92e2eeaeaebd63d8299f.
- MED-R03-B2 (location_1fc650d4a6c4641384c74e0f00ffe590): 2023-01-08T21:37:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R03-B2 (location_72ef9856cd2764312d0cfab0ee44219a): 2023-01-08T21:42:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R01-B1 (location_4c9c64d5ccaa4007781c4249fb0c177a): 2023-01-09T00:04:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_31f84b8b57c271ce9e88cafc9f1a41d6.
- MED-R01-B1 (location_4c9c64d5ccaa4007781c4249fb0c177a): 2023-01-09T00:19:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R01-B2 (location_03b3641a5f36a8c96911aa2ff3e876ec): 2023-01-09T02:14:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_8e190095bc9403e47f58d9b48014b23f.
- SURG-R01-B2 (location_03b3641a5f36a8c96911aa2ff3e876ec): 2023-01-09T02:29:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R03-B1 (location_437e2dd2bf8d07ef858a308416d3a1e5): 2023-01-09T05:29:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_71ed5da40c13ee946189065b051cc643.
- SURG-R03-B1 (location_437e2dd2bf8d07ef858a308416d3a1e5): 2023-01-09T05:44:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R05-B2 (location_310140d85d72827bb5a74dd055f89863): 2023-01-09T12:08:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_b66fba810aebbff0cb5c4c962985c9d3.
- SURG-R05-B2 (location_310140d85d72827bb5a74dd055f89863): 2023-01-09T12:23:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R03-B1 (location_377f2461a9b41271f0ac3eb0955753bc): 2023-01-09T14:22:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_2d9f4d17a5985173f46a15ac9c17e3b4.
- MED-R03-B1 (location_377f2461a9b41271f0ac3eb0955753bc): 2023-01-09T14:37:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R04-B2 (location_5bd5a9145130b6a7f3f7d64f0ae1b07a): 2023-01-09T16:33:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_3df5479b15cc948a21a329a86ad5c3de.
- SURG-R04-B2 (location_5bd5a9145130b6a7f3f7d64f0ae1b07a): 2023-01-09T16:48:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R05-B2 (location_baee22b979d0566715db157b479905f3): 2023-01-09T19:08:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_e396553d718db8e66da5f36489d79e89.
- MED-R05-B2 (location_baee22b979d0566715db157b479905f3): 2023-01-09T19:23:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R03-B2 (location_c83b04349ecf3d3783fca63562ebfbe3): 2023-01-09T19:25:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_ba1be1d00f201d0c151ad575763ac81e.
- MED-R03-B2 (location_c83b04349ecf3d3783fca63562ebfbe3): 2023-01-09T19:40:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R04-B1 (location_52c768c54855f1180306335168bc2f88): 2023-01-09T22:59:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_8bee41e0df76959910e6691980c1ce72.
- MED-R04-B1 (location_52c768c54855f1180306335168bc2f88): 2023-01-09T23:14:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R05-B1 (location_222109436f4a3f95df53908c73f6339c): 2023-01-10T00:05:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_50bc05869aea827251f9d3ec8d76eaed.
- MED-R05-B1 (location_222109436f4a3f95df53908c73f6339c): 2023-01-10T00:20:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R01-B2 (location_a419604a10ccb5c27e56d74f08c83dc3): 2023-01-10T04:40:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_5d7cd70617f601f759fd8ac531c08bcb.
- SURG-R01-B2 (location_a419604a10ccb5c27e56d74f08c83dc3): 2023-01-10T04:55:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R02-B1 (location_8168ca706d0df4c97842006697510bb0): 2023-01-10T09:00:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_0cdb031a75d28e517eb2a93f704221e0.
- MED-R02-B1 (location_8168ca706d0df4c97842006697510bb0): 2023-01-10T09:15:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R04-B1 (location_60f180784cd4bdcf24b93fdd148fd906): 2023-01-10T09:24:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_7f70b974adfda0c036b791736fbf8918.
- SURG-R04-B1 (location_60f180784cd4bdcf24b93fdd148fd906): 2023-01-10T09:39:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R04-B2 (location_3ebcb02c79d1b91e763a2500e026e29a): 2023-01-10T10:05:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_d36e64a18db267a98fa4b4f866a671b5.
- SURG-R04-B2 (location_3ebcb02c79d1b91e763a2500e026e29a): 2023-01-10T10:20:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R03-B2 (location_a89c4fe86776f8953ceb045ab4a0d738): 2023-01-10T11:09:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_6d9c3bf6d1845e874c9fb5e98536a068.
- MED-R03-B2 (location_a89c4fe86776f8953ceb045ab4a0d738): 2023-01-10T11:24:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R01-B1 (location_8b117e98d2d91b78772532bf72fcf9e3): 2023-01-10T12:19:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_dc0504bbbe5fcc44cdde7acaa1c60be9.
- ICU-R01-B1 (location_8b117e98d2d91b78772532bf72fcf9e3): 2023-01-10T12:34:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R04-B2 (location_65f8c6430871d15d8c804f5b1dd1acba): 2023-01-10T14:28:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_58657b77279d298ef7b58415782ada33.
- SURG-R01-B1 (location_1ef5a9db41ae73fac806607303e00a28): 2023-01-10T14:33:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_7dd8d3b61a9761694b92de0818cf29c4.
- MED-R04-B2 (location_65f8c6430871d15d8c804f5b1dd1acba): 2023-01-10T14:43:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R01-B1 (location_1ef5a9db41ae73fac806607303e00a28): 2023-01-10T14:48:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R04-B1 (location_6880ba3dc60367e38e2afbc737f05e7c): 2023-01-10T15:45:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_57ceda14b06e65b3a22940b6a7d55892.
- SURG-R04-B1 (location_6880ba3dc60367e38e2afbc737f05e7c): 2023-01-10T16:00:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R04-B1 (location_f927c33204fa4952a0f3ecb39d2d2748): 2023-01-10T19:16:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_eb6330c84583d2a27d9015bad04e32c1.
- MED-R04-B1 (location_f927c33204fa4952a0f3ecb39d2d2748): 2023-01-10T19:31:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R01-B2 (location_5d54a577dd8429101baa06dc23f6c9eb): 2023-01-11T00:07:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_ea69aac231ba9441a7e639e49ee759ef.
- MED-R01-B2 (location_5d54a577dd8429101baa06dc23f6c9eb): 2023-01-11T00:22:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R04-B1 (location_75040bf573390196e12442a9fd363feb): 2023-01-11T08:40:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_ea86178c4ef735d53402b7a0993f5535.
- MED-R04-B1 (location_75040bf573390196e12442a9fd363feb): 2023-01-11T08:55:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R05-B1 (location_2b9e2c82fe191f115ed6e64fa428bae3): 2023-01-11T12:27:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_8ec1334caaaedf6fb34b24896f5ac32e.
- SURG-R05-B1 (location_2b9e2c82fe191f115ed6e64fa428bae3): 2023-01-11T12:42:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R04-B2 (location_06721c718818ad3665e923b23e34ff12): 2023-01-11T13:15:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_155acf13c9adc8d2e2f4008efa74928f.
- MED-R04-B2 (location_06721c718818ad3665e923b23e34ff12): 2023-01-11T13:30:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R02-B2 (location_e3247a7caadaa3230e75062700081fef): 2023-01-11T17:55:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_f50d00eed244e7df4e0c150acfbf2a58.
- MED-R02-B2 (location_e3247a7caadaa3230e75062700081fef): 2023-01-11T18:10:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R02-B1 (location_8e501cbeef106a89f0864afbc81a5d2f): 2023-01-11T19:24:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_7336a84529010aef6e94ec0da1d1eb86.
- SURG-R02-B1 (location_8e501cbeef106a89f0864afbc81a5d2f): 2023-01-11T19:39:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R02-B2 (location_2487a9099ce9481c10cddd42fe9c9d06): 2023-01-11T21:49:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_ab4b75346303a7506ddb254dd40062a1.
- MED-R02-B2 (location_2487a9099ce9481c10cddd42fe9c9d06): 2023-01-11T22:04:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R02-B2 (location_00438655256908a53eb0df2679bb6a91): 2023-01-11T22:37:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_c4d2a7e7070af740e9125ad7ccc03d1c.
- SURG-R02-B2 (location_00438655256908a53eb0df2679bb6a91): 2023-01-11T22:52:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R01-B1 (location_8b117e98d2d91b78772532bf72fcf9e3): 2023-01-12T00:07:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_28d8793dc9c5e8f2a4318a915753c597.
- ICU-R01-B1 (location_8b117e98d2d91b78772532bf72fcf9e3): 2023-01-12T00:22:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R05-B1 (location_78063ac49b3826812656bc1c46a8a0f6): 2023-01-12T10:30:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_b6488bb65b8442c02691e4dc42ee6111.
- SURG-R05-B1 (location_78063ac49b3826812656bc1c46a8a0f6): 2023-01-12T10:45:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R04-B2 (location_d0efc1f0b72fe4bf780059e14b5421f3): 2023-01-12T11:14:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_1734253f8fb69c1c6a42149409a893d8.
- SURG-R04-B2 (location_d0efc1f0b72fe4bf780059e14b5421f3): 2023-01-12T11:29:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R01-B1 (location_12df24a3232ee95c3f230388290e8f92): 2023-01-12T15:15:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_30bc6b38e5a1d970919ee46fc4119578.
- MED-R01-B1 (location_12df24a3232ee95c3f230388290e8f92): 2023-01-12T15:30:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- ICU-R01-B1 (location_05d8b9f3f9d04c571f9c0e104b127173): 2023-01-12T15:33:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_36e31cc4240a644a9b0826143474f7cf.
- ICU-R01-B1 (location_05d8b9f3f9d04c571f9c0e104b127173): 2023-01-12T15:48:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R02-B2 (location_0390bc1f7211b056fc235812aeeb2b2c): 2023-01-12T17:11:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_db65e385b59c9d9e8ca2c99fa316892a.
- SURG-R02-B2 (location_0390bc1f7211b056fc235812aeeb2b2c): 2023-01-12T17:26:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R02-B2 (location_320d59365dd7a10ff3a420240d5e51c6): 2023-01-12T21:37:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_06b14e4211f0997f3282722d78763444.
- SURG-R02-B2 (location_320d59365dd7a10ff3a420240d5e51c6): 2023-01-12T21:52:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R05-B2 (location_07314bcb33b8a2f0ca2a06cac413a95f): 2023-01-13T00:31:00Z CORRECTION CORRECTED_CLEAN_READY_SERVICE_STATUS; service IN_SERVICE; staffing True; reserved False; corrects bed_event_99288041957ddd974520a94a783f87dc.
- MED-R05-B2 (location_07314bcb33b8a2f0ca2a06cac413a95f): 2023-01-13T00:46:00Z RELEASE BED_HOLD_CANCELLED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R04-B1 (location_f927c33204fa4952a0f3ecb39d2d2748): 2024-06-01T21:34:00Z STAFF_CHANGE PLANNED_MAINTENANCE_STAFF_DISABLED; service IN_SERVICE; staffing False; reserved False; corrects none.
- MED-R04-B1 (location_f927c33204fa4952a0f3ecb39d2d2748): 2024-06-01T21:34:00Z SERVICE_CHANGE PLANNED_EMPTY_BED_MAINTENANCE; service OUT_OF_SERVICE; staffing False; reserved False; corrects none.
- MED-R04-B1 (location_75040bf573390196e12442a9fd363feb): 2024-06-02T20:00:00Z STAFF_CHANGE PLANNED_MAINTENANCE_STAFF_DISABLED; service IN_SERVICE; staffing False; reserved False; corrects none.
- MED-R04-B1 (location_75040bf573390196e12442a9fd363feb): 2024-06-02T20:00:00Z SERVICE_CHANGE PLANNED_EMPTY_BED_MAINTENANCE; service OUT_OF_SERVICE; staffing False; reserved False; corrects none.
- MED-R04-B1 (location_52c768c54855f1180306335168bc2f88): 2024-06-03T03:21:00Z STAFF_CHANGE PLANNED_MAINTENANCE_STAFF_DISABLED; service IN_SERVICE; staffing False; reserved False; corrects none.
- MED-R04-B1 (location_52c768c54855f1180306335168bc2f88): 2024-06-03T03:21:00Z SERVICE_CHANGE PLANNED_EMPTY_BED_MAINTENANCE; service OUT_OF_SERVICE; staffing False; reserved False; corrects none.
- MED-R05-B1 (location_943752092d54ed5cc767419c4e972f44): 2024-06-09T09:00:00Z STAFF_CHANGE PLANNED_MAINTENANCE_STAFF_DISABLED; service IN_SERVICE; staffing False; reserved False; corrects none.
- MED-R05-B1 (location_943752092d54ed5cc767419c4e972f44): 2024-06-09T09:00:00Z SERVICE_CHANGE PLANNED_EMPTY_BED_MAINTENANCE; service OUT_OF_SERVICE; staffing False; reserved False; corrects none.
- MED-R05-B1 (location_222109436f4a3f95df53908c73f6339c): 2024-06-09T10:10:00Z STAFF_CHANGE PLANNED_MAINTENANCE_STAFF_DISABLED; service IN_SERVICE; staffing False; reserved False; corrects none.
- MED-R05-B1 (location_222109436f4a3f95df53908c73f6339c): 2024-06-09T10:10:00Z SERVICE_CHANGE PLANNED_EMPTY_BED_MAINTENANCE; service OUT_OF_SERVICE; staffing False; reserved False; corrects none.
- MED-R05-B1 (location_8f68eaaee92401a7696f1433368e0e31): 2024-06-09T13:43:00Z STAFF_CHANGE PLANNED_MAINTENANCE_STAFF_DISABLED; service IN_SERVICE; staffing False; reserved False; corrects none.
- MED-R05-B1 (location_8f68eaaee92401a7696f1433368e0e31): 2024-06-09T13:43:00Z SERVICE_CHANGE PLANNED_EMPTY_BED_MAINTENANCE; service OUT_OF_SERVICE; staffing False; reserved False; corrects none.
- SURG-R04-B1 (location_afb8e0028c27f2f4eb74b3db103a6f02): 2024-06-16T14:45:00Z STAFF_CHANGE PLANNED_MAINTENANCE_STAFF_DISABLED; service IN_SERVICE; staffing False; reserved False; corrects none.
- SURG-R04-B1 (location_afb8e0028c27f2f4eb74b3db103a6f02): 2024-06-16T14:45:00Z SERVICE_CHANGE PLANNED_EMPTY_BED_MAINTENANCE; service OUT_OF_SERVICE; staffing False; reserved False; corrects none.
- SURG-R04-B1 (location_60f180784cd4bdcf24b93fdd148fd906): 2024-06-17T12:55:00Z STAFF_CHANGE PLANNED_MAINTENANCE_STAFF_DISABLED; service IN_SERVICE; staffing False; reserved False; corrects none.
- SURG-R04-B1 (location_60f180784cd4bdcf24b93fdd148fd906): 2024-06-17T12:55:00Z SERVICE_CHANGE PLANNED_EMPTY_BED_MAINTENANCE; service OUT_OF_SERVICE; staffing False; reserved False; corrects none.
- SURG-R04-B1 (location_6880ba3dc60367e38e2afbc737f05e7c): 2024-06-18T15:00:00Z STAFF_CHANGE PLANNED_MAINTENANCE_STAFF_DISABLED; service IN_SERVICE; staffing False; reserved False; corrects none.
- SURG-R04-B1 (location_6880ba3dc60367e38e2afbc737f05e7c): 2024-06-18T15:00:00Z SERVICE_CHANGE PLANNED_EMPTY_BED_MAINTENANCE; service OUT_OF_SERVICE; staffing False; reserved False; corrects none.
- SURG-R05-B1 (location_e036befe3516e17e39b77384432a248b): 2024-06-23T12:56:00Z STAFF_CHANGE PLANNED_MAINTENANCE_STAFF_DISABLED; service IN_SERVICE; staffing False; reserved False; corrects none.
- SURG-R05-B1 (location_e036befe3516e17e39b77384432a248b): 2024-06-23T12:56:00Z SERVICE_CHANGE PLANNED_EMPTY_BED_MAINTENANCE; service OUT_OF_SERVICE; staffing False; reserved False; corrects none.
- SURG-R05-B1 (location_2b9e2c82fe191f115ed6e64fa428bae3): 2024-06-25T13:42:00Z STAFF_CHANGE PLANNED_MAINTENANCE_STAFF_DISABLED; service IN_SERVICE; staffing False; reserved False; corrects none.
- SURG-R05-B1 (location_2b9e2c82fe191f115ed6e64fa428bae3): 2024-06-25T13:42:00Z SERVICE_CHANGE PLANNED_EMPTY_BED_MAINTENANCE; service OUT_OF_SERVICE; staffing False; reserved False; corrects none.
- SURG-R05-B1 (location_78063ac49b3826812656bc1c46a8a0f6): 2024-06-26T08:43:00Z STAFF_CHANGE PLANNED_MAINTENANCE_STAFF_DISABLED; service IN_SERVICE; staffing False; reserved False; corrects none.
- SURG-R05-B1 (location_78063ac49b3826812656bc1c46a8a0f6): 2024-06-26T08:43:00Z SERVICE_CHANGE PLANNED_EMPTY_BED_MAINTENANCE; service OUT_OF_SERVICE; staffing False; reserved False; corrects none.
- MED-R04-B1 (location_75040bf573390196e12442a9fd363feb): 2024-08-21T20:00:00Z SERVICE_CHANGE MAINTENANCE_COMPLETE; service IN_SERVICE; staffing False; reserved False; corrects none.
- MED-R04-B1 (location_75040bf573390196e12442a9fd363feb): 2024-08-21T20:00:00Z STAFF_CHANGE STAFFED_CAPACITY_RESTORED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R04-B1 (location_52c768c54855f1180306335168bc2f88): 2024-08-22T03:21:00Z SERVICE_CHANGE MAINTENANCE_COMPLETE; service IN_SERVICE; staffing False; reserved False; corrects none.
- MED-R04-B1 (location_52c768c54855f1180306335168bc2f88): 2024-08-22T03:21:00Z STAFF_CHANGE STAFFED_CAPACITY_RESTORED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R04-B1 (location_f927c33204fa4952a0f3ecb39d2d2748): 2024-08-22T21:34:00Z SERVICE_CHANGE MAINTENANCE_COMPLETE; service IN_SERVICE; staffing False; reserved False; corrects none.
- MED-R04-B1 (location_f927c33204fa4952a0f3ecb39d2d2748): 2024-08-22T21:34:00Z STAFF_CHANGE STAFFED_CAPACITY_RESTORED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R05-B1 (location_943752092d54ed5cc767419c4e972f44): 2024-08-28T09:00:00Z SERVICE_CHANGE MAINTENANCE_COMPLETE; service IN_SERVICE; staffing False; reserved False; corrects none.
- MED-R05-B1 (location_943752092d54ed5cc767419c4e972f44): 2024-08-28T09:00:00Z STAFF_CHANGE STAFFED_CAPACITY_RESTORED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R05-B1 (location_222109436f4a3f95df53908c73f6339c): 2024-08-28T10:10:00Z SERVICE_CHANGE MAINTENANCE_COMPLETE; service IN_SERVICE; staffing False; reserved False; corrects none.
- MED-R05-B1 (location_222109436f4a3f95df53908c73f6339c): 2024-08-28T10:10:00Z STAFF_CHANGE STAFFED_CAPACITY_RESTORED; service IN_SERVICE; staffing True; reserved False; corrects none.
- MED-R05-B1 (location_8f68eaaee92401a7696f1433368e0e31): 2024-08-28T13:43:00Z SERVICE_CHANGE MAINTENANCE_COMPLETE; service IN_SERVICE; staffing False; reserved False; corrects none.
- MED-R05-B1 (location_8f68eaaee92401a7696f1433368e0e31): 2024-08-28T13:43:00Z STAFF_CHANGE STAFFED_CAPACITY_RESTORED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R04-B1 (location_afb8e0028c27f2f4eb74b3db103a6f02): 2024-09-04T14:45:00Z SERVICE_CHANGE MAINTENANCE_COMPLETE; service IN_SERVICE; staffing False; reserved False; corrects none.
- SURG-R04-B1 (location_afb8e0028c27f2f4eb74b3db103a6f02): 2024-09-04T14:45:00Z STAFF_CHANGE STAFFED_CAPACITY_RESTORED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R04-B1 (location_60f180784cd4bdcf24b93fdd148fd906): 2024-09-05T12:55:00Z SERVICE_CHANGE MAINTENANCE_COMPLETE; service IN_SERVICE; staffing False; reserved False; corrects none.
- SURG-R04-B1 (location_60f180784cd4bdcf24b93fdd148fd906): 2024-09-05T12:55:00Z STAFF_CHANGE STAFFED_CAPACITY_RESTORED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R04-B1 (location_6880ba3dc60367e38e2afbc737f05e7c): 2024-09-06T15:00:00Z SERVICE_CHANGE MAINTENANCE_COMPLETE; service IN_SERVICE; staffing False; reserved False; corrects none.
- SURG-R04-B1 (location_6880ba3dc60367e38e2afbc737f05e7c): 2024-09-06T15:00:00Z STAFF_CHANGE STAFFED_CAPACITY_RESTORED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R05-B1 (location_e036befe3516e17e39b77384432a248b): 2024-09-11T12:56:00Z SERVICE_CHANGE MAINTENANCE_COMPLETE; service IN_SERVICE; staffing False; reserved False; corrects none.
- SURG-R05-B1 (location_e036befe3516e17e39b77384432a248b): 2024-09-11T12:56:00Z STAFF_CHANGE STAFFED_CAPACITY_RESTORED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R05-B1 (location_2b9e2c82fe191f115ed6e64fa428bae3): 2024-09-13T13:42:00Z SERVICE_CHANGE MAINTENANCE_COMPLETE; service IN_SERVICE; staffing False; reserved False; corrects none.
- SURG-R05-B1 (location_2b9e2c82fe191f115ed6e64fa428bae3): 2024-09-13T13:42:00Z STAFF_CHANGE STAFFED_CAPACITY_RESTORED; service IN_SERVICE; staffing True; reserved False; corrects none.
- SURG-R05-B1 (location_78063ac49b3826812656bc1c46a8a0f6): 2024-09-14T08:43:00Z SERVICE_CHANGE MAINTENANCE_COMPLETE; service IN_SERVICE; staffing False; reserved False; corrects none.
- SURG-R05-B1 (location_78063ac49b3826812656bc1c46a8a0f6): 2024-09-14T08:43:00Z STAFF_CHANGE STAFFED_CAPACITY_RESTORED; service IN_SERVICE; staffing True; reserved False; corrects none.
