# Longitudinal clinical journey review

Selected synthetic records are deliberate review mirrors. Timings remain provisional until resource integration. This is a synthetic plausibility review, not a clinical endorsement.

## Journey 1: Gale Wright

Stable patient: patient_00a7b488c29f948ed144f865407aa710; birth date 1945-02-15; strata: acuity/2, acuity/3, acuity/4, acuity/5, age/65-79, age/80+, carry/False, long-stay/False, long-stay/True, outcome/HOME, outcome/TRANSFER, pathway/I509, pathway/J189, pathway/R079, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- OPD 2023-04-14T17:57:00Z to 2023-04-14T19:50:00Z; acuity 5; HOME; diagnosis I509; episode episode_0bed64e0d8641480641596e1c25bd59e; predecessor none.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.
  Treatment evidence: Furosemide 140 mg PO NOT_DONE.

  OP_NOTE @ 2023-04-14T19:50:00Z: Care assessment: Gale Wright, age 78. Interval follow-up for worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 97.43 % (record clinical_event_a215b16d5bc0529dbb77ec4d69a86f32). Heart rate: 86.70 /min (record clinical_event_af3eebb5385653dec502f16358786309). Previously recorded problems: Heart failure, unspecified; Hyperlipidemia, unspecified. Furosemide 140 mg withheld; recorded allergy requires review (record clinical_event_d56765862f4381a73ee81440598d3363). Continue assessment as results become available. Follow-up completion is not established by this document.
- OPD 2023-11-01T16:55:00Z to 2023-11-01T18:37:00Z; acuity 3; HOME; diagnosis R079; episode episode_03e92a42c6633d9f2b7174d3c199c20a; predecessor encounter_version_3a7b3ffff71f67e4a1a6304f88bbf543.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2023-11-01T18:37:00Z: Encounter review: Gale Wright, age 78. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.78 % (record clinical_event_3756805a188722d7f7dae962c783453e). Heart rate: 73.35 /min (record clinical_event_fd178050c86e9f9a147fa1384e3f8aeb). Troponin I: 4.88 ng/L (record clinical_event_a097a85a7c0c0b606cbc34ae8630bf97). Previously recorded problems: Heart failure, unspecified; Hyperlipidemia, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2025-02-16T04:49:00Z to 2025-02-16T07:35:00Z; acuity 4; HOME; diagnosis R1010; episode episode_310fb2d4a25eca2c905bde252e8d2e82; predecessor encounter_version_5e4c65de04d8b6e971582435b26e6488.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2025-02-16T07:35:00Z: Patient review: Gale Wright, age 80. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.86 % (record clinical_event_a19e0c2157a32e72a9de1c3b0432a13f). Heart rate: 104.25 /min (record clinical_event_8a495b5f55d9f0bf53bb95e7258edac2). Previously recorded problems: Heart failure, unspecified; Hyperlipidemia, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2025-04-23T22:46:00Z to 2025-04-24T00:36:00Z; acuity 5; HOME; diagnosis R079; episode episode_388d4ce58a75ac3069d8e6bf849214d5; predecessor encounter_version_a7930d56a9ef461bf25bac8cc02ef5a2.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-04-24T00:36:00Z: Care assessment: Gale Wright, age 80. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 96.18 % (record clinical_event_3453cc1f99662aa4258a72bbfcc4e1cf). Heart rate: 102.25 /min (record clinical_event_01c4ade4a439fbe71ab15065851781f8). Troponin I: 4.16 ng/L (record clinical_event_53c71a6417b078cd807af58d4ed5500e). Previously recorded problems: Heart failure, unspecified; Hyperlipidemia, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2025-07-11T10:33:00Z to 2025-07-11T14:33:00Z; acuity 3; TRANSFER; diagnosis J189; episode episode_79c9c3e348fbbe047ef530ea7dba5677; predecessor encounter_version_18c62e6df116932b2cbe6af161ea716d.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-07-11T14:33:00Z: Interval assessment: Gale Wright, age 80. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Oxygen saturation: 95.46 % (record clinical_event_37d738eb65e4e8049f2f9da6f897adbc). Heart rate: 110.25 /min (record clinical_event_a78155e042fd9af1111f7829ac7e5b77). White blood cell count: 16.73 10*3/uL (record clinical_event_a9229d70d5e434a6b8afe3cef1eed300). Previously recorded problems: Heart failure, unspecified; Hyperlipidemia, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- IPD 2025-07-11T14:33:00Z to 2025-07-17T15:33:00Z; acuity 3; HOME; diagnosis J189; episode episode_79c9c3e348fbbe047ef530ea7dba5677; predecessor encounter_version_3d50bdf59f2e281457a523e5a6c409a7.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=13, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Doxycycline 100 mg PO COMPLETED; Doxycycline 100 mg PO COMPLETED.

  PROGRESS_NOTE @ 2025-07-11T18:33:00Z: Patient review: Gale Wright, age 80. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Body temperature: 38.07 Cel (record clinical_event_b3b6a922f97071cec80fdd6129e80920). Oxygen saturation: 95.55 % (record clinical_event_f94ca7f6bfb6a11913d545700f2578cb). White blood cell count: 13.23 10*3/uL (record clinical_event_7784909675450b0e20e2f9046f412d8e). C-reactive protein: 71.52 mg/L (record clinical_event_dbd27d77d83d9865e374912a26d6821e). Previously recorded problems: Heart failure, unspecified; Hyperlipidemia, unspecified. Doxycycline 100 mg administered (record clinical_event_9885c81f5aac7ad24895c5a3e6935c59). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-07-17T15:33:00Z: Clinical review: Gale Wright, age 80. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. White blood cell count: 13.23 10*3/uL (record clinical_event_7784909675450b0e20e2f9046f412d8e). White blood cell count: 9.61 10*3/uL (record clinical_event_138982e88013560b2794df3b226627cf). C-reactive protein: 71.52 mg/L (record clinical_event_dbd27d77d83d9865e374912a26d6821e). C-reactive protein: 14.32 mg/L (record clinical_event_43886805ff69199a872dfff5d9efc478). Previously recorded problems: Heart failure, unspecified; Hyperlipidemia, unspecified. Doxycycline 100 mg administered (record clinical_event_51cc1b10ee26a2d40568d1a5874021f3). Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2025-07-26T11:33:00Z to 2025-07-26T15:33:00Z; acuity 3; TRANSFER; diagnosis J189; episode episode_ee35a07c88f1671f14453a18368ac6ad; predecessor encounter_version_8b8c3b8d699a6ce2d14b2a3549a841a7.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2025-07-26T15:33:00Z: Assessment update: Gale Wright, age 80. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Oxygen saturation: 93.24 % (record clinical_event_6f896fb9389ac392386feb70433f90a0). Heart rate: 92.75 /min (record clinical_event_82442ac456cdfe7b1ef5170794402822). Previously recorded problems: Heart failure, unspecified; Hyperlipidemia, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- IPD 2025-07-26T15:33:00Z to 2025-08-10T10:33:00Z; acuity 2; HOME; diagnosis J189; episode episode_ee35a07c88f1671f14453a18368ac6ad; predecessor encounter_version_4ed0d264fbcbf1d74bc6167a82970da6.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=14, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Doxycycline 100 mg PO COMPLETED; Doxycycline 100 mg PO COMPLETED.

  PROGRESS_NOTE @ 2025-07-26T19:33:00Z: Encounter review: Gale Wright, age 80. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Body temperature: 38.54 Cel (record clinical_event_eaa23624f06ca2e47c4d86cf5c9e2d09). Oxygen saturation: 92.67 % (record clinical_event_e2d7a663f600e82733fdb339591ec2f9). White blood cell count: 15.08 10*3/uL (record clinical_event_c71f617d1b5eab239cb1c765fe08326f). C-reactive protein: 115.44 mg/L (record clinical_event_ac2a791b53791217edea1aa3195c77bc). Previously recorded problems: Heart failure, unspecified; Hyperlipidemia, unspecified. Doxycycline 100 mg administered (record clinical_event_e481131edbca5dfd663374208ab9da4c). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-08-10T10:33:00Z: Encounter review: Gale Wright, age 80. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. White blood cell count: 15.08 10*3/uL (record clinical_event_c71f617d1b5eab239cb1c765fe08326f). White blood cell count: 7.45 10*3/uL (record clinical_event_67f2ebc7bdd9e9381327bcb3e740b092). C-reactive protein: 115.44 mg/L (record clinical_event_ac2a791b53791217edea1aa3195c77bc). C-reactive protein: 15.04 mg/L (record clinical_event_916934d45cc9dbf7d12ba64c540ccdc4). Previously recorded problems: Heart failure, unspecified; Hyperlipidemia, unspecified. Doxycycline 100 mg administered (record clinical_event_77b58855a5d125292a4a8d0c848c2384). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 2: Stephanie Johnson

Stable patient: patient_610838e6160c9096ceeaec0ca72765ce; birth date 1975-03-30; strata: acuity/3, acuity/4, acuity/5, age/35-49, age/50-64, carry/False, long-stay/False, outcome/HOME, outcome/LEFT_WITHOUT_SEEN, pathway/J449, pathway/K8010, pathway/R079, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- IPD 2023-03-01T13:56:00Z to 2023-03-06T13:56:00Z; acuity 3; HOME; diagnosis K8010; episode episode_4281ebee2ceea1e47b9fa699d9f256c2; predecessor none.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=11, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2023-03-01T23:56:00Z: Interval assessment: Stephanie Johnson, age 47. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 7.00 1 (record clinical_event_c8c1177f42135fb15ba078415a08befe). Heart rate: 92.25 /min (record clinical_event_78116c2729c7af6749336450aeb4ba95). Hemoglobin: 14.05 g/dL (record clinical_event_bafe910b1ea3f9a5b7bb9e31c360eaa1). Creatinine: 0.99 mg/dL (record clinical_event_6f39c09eebc2b2b1263ba2eb16628476). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_f473ba3f19095111913b131b5dc417a9). Acetaminophen 650 mg administered (record clinical_event_c790dd98212dd50471511d7b6bb33ce2). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-03-06T13:56:00Z: Clinical review: Stephanie Johnson, age 47. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 14.05 g/dL (record clinical_event_bafe910b1ea3f9a5b7bb9e31c360eaa1). Hemoglobin: 13.35 g/dL (record clinical_event_be5ede6abb293f8471d2d64bbf42d1d5). Creatinine: 0.99 mg/dL (record clinical_event_6f39c09eebc2b2b1263ba2eb16628476). Creatinine: 0.97 mg/dL (record clinical_event_f3cba81f89abda2e645a4a1133047996). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Acetaminophen 650 mg administered (record clinical_event_3cc549121df326f6f97857237d0b1b76). Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2024-02-16T21:10:00Z to 2024-02-16T23:06:00Z; acuity 4; HOME; diagnosis J449; episode episode_ee651d0a66bb2136d6eea72454149426; predecessor encounter_version_b9fc203edad04a8496d19911d8a6cef8.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=1.
  Treatment evidence: Prednisone 200 mg PO COMPLETED.

  ED_NOTE @ 2024-02-16T23:06:00Z: Assessment update: Stephanie Johnson, age 48. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 94.89 % (record clinical_event_c65fdbc825abc321bd1110fd2390a02a). Heart rate: 96.00 /min (record clinical_event_5edd97a0109b9dc937032ff2dc791c87). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Prednisone 200 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_b78ef5f753113dec20c505778d1bcc6b). Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2024-03-07T19:58:00Z to 2024-03-07T22:46:00Z; acuity 4; LEFT_WITHOUT_SEEN; diagnosis unassessed; episode episode_b31df9f19fbe0f013f5576f62f028c5e; predecessor encounter_version_7824d9018fecd327ca6a2f97b68206a2.
  Captured evidence: .
- OPD 2024-06-10T18:49:00Z to 2024-06-10T20:00:00Z; acuity 3; HOME; diagnosis J449; episode episode_7e4e02470936c83abf3ab3f1eb1fcf25; predecessor encounter_version_6c14d0edf7939f4d17f7b4485de2a652.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2024-06-10T20:00:00Z: Care assessment: Stephanie Johnson, age 49. Interval follow-up for increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 95.76 % (record clinical_event_18eecca1ccfbb0e685e37c965a121582). Heart rate: 75.45 /min (record clinical_event_c5357f5c61fa71ca0dc74f87829e760d). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.
- OPD 2025-03-18T15:13:00Z to 2025-03-18T16:17:00Z; acuity 3; HOME; diagnosis R079; episode episode_a5cf183f3fd5fbff74044df9285b13a3; predecessor encounter_version_cf2a43c2e5992bd1ed59bffe9c5ca5b8.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2025-03-18T16:17:00Z: Clinical review: Stephanie Johnson, age 49. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.92 % (record clinical_event_edc8f6188fa7bcab2ee0ce5b40abc3b8). Heart rate: 84.90 /min (record clinical_event_249b412947f3acdf011f3da927939e0b). Troponin I: 3.86 ng/L (record clinical_event_fa27c741b88d671b5e740ae31ad5f28b). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2025-11-24T09:48:00Z to 2025-11-24T12:08:00Z; acuity 5; HOME; diagnosis R079; episode episode_8325aa09b8432e5cf1fb921d32d9fb20; predecessor encounter_version_da5f107496547ab669f15bb526ea87f4.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-11-24T12:08:00Z: Clinical review: Stephanie Johnson, age 50. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.05 % (record clinical_event_d3fb2a05c1a0da92776c9a4e54f0bb2f). Heart rate: 98.75 /min (record clinical_event_ddda08e191a643a99b9bafa4a0411dc0). Troponin I: 4.22 ng/L (record clinical_event_68c2a75baf29fb36a53b54f5fac5c13d). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 3: Logan Kitchens

Stable patient: patient_78b24a9b6b24570c0ff306a709f7030b; birth date 1998-04-09; strata: acuity/3, age/18-34, carry/False, outcome/OPEN, pathway/E119, repeat/False, service/IPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- IPD 2025-12-31T07:00:00Z to CENSORED; acuity 3; OPEN; diagnosis E119; episode episode_41312bf5447772c0a9b1ddea6ae9faea; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=4, OBSERVATION=4, ORDER=3, PROCEDURE=1.

  PROGRESS_NOTE @ 2025-12-31T11:00:00Z: Care assessment: Logan Kitchens, age 27. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Capillary glucose: 223.30 mg/dL (record clinical_event_344b1bd08c4c569a9b95264d98781615). Heart rate: 90.75 /min (record clinical_event_4e4f831d7b9f91865428109ac351dd21). Serum glucose: 223.30 mg/dL (record clinical_event_de92c6e160973bb4d7a18d7ee669a80e). Creatinine: 1.05 mg/dL (record clinical_event_7f38575aede75d0d03ac1b36ac12309c). Previously recorded problems: Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 4: David Jenkins

Stable patient: patient_5a1817b0aa14598114c04841b8e9f62f; birth date 1968-08-22; strata: acuity/1, acuity/3, age/50-64, carry/False, long-stay/False, outcome/DEATH, outcome/HOME, pathway/I509, pathway/J189, repeat/True, service/IPD, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- OPD 2025-01-07T20:27:00Z to 2025-01-07T21:53:00Z; acuity 3; HOME; diagnosis J189; episode episode_66eb34fc04c12fcd6b77754a5ed6d539; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2.
  Treatment evidence: Doxycycline 1400 mg PO COMPLETED.

  OP_NOTE @ 2025-01-07T21:53:00Z: Patient review: David Jenkins, age 56. Interval follow-up for cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Oxygen saturation: 97.39 % (record clinical_event_8fffe5035313511f9e8388bb7d92f58b). Heart rate: 82.35 /min (record clinical_event_77ab34ed5029cd47236ee4b930fd8214). White blood cell count: 18.10 10*3/uL (record clinical_event_04e612dc19200ad938dab6673a272176). Prior problem documentation is incomplete; absence of a record does not exclude disease. Doxycycline 1400 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_0768ffac3926a24817b578d780911339). Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2025-12-29T15:00:00Z to 2025-12-30T18:00:00Z; acuity 1; DEATH; diagnosis I509; episode episode_97a92c47236ae39fcc27e5c717c1dbe2; predecessor encounter_version_4b61394d1422d3a5e54407854720f368.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=2, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Furosemide 20 mg PO COMPLETED; Furosemide 20 mg PO COMPLETED.

  PROGRESS_NOTE @ 2025-12-29T19:00:00Z: Patient review: David Jenkins, age 57. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Body weight: 100.77 kg (record clinical_event_98dde35dd86e0eae6ee5e0c05ba73c1a). Oxygen saturation: 92.58 % (record clinical_event_92efc0cc4e50306713be9b3e5fe451ff). Creatinine: 1.13 mg/dL (record clinical_event_929b512157a0994531c58c1fa1400462). Potassium: 4.13 mmol/L (record clinical_event_4f6f54426405c6c778f64b66d1bb9c26). Previously recorded problems: Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_08fa4de3c21be4265142c7e993e9eece). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-12-30T18:00:00Z: Interval assessment: David Jenkins, age 57. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Creatinine: 1.13 mg/dL (record clinical_event_929b512157a0994531c58c1fa1400462). Creatinine: 1.24 mg/dL (record clinical_event_85bb82ad83e854204ad57740b03df08e). Potassium: 4.13 mmol/L (record clinical_event_4f6f54426405c6c778f64b66d1bb9c26). Potassium: 4.32 mmol/L (record clinical_event_04e2bbb8f8b9e44345893126a999067f). Previously recorded problems: Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_d5a1a2e34e87948a38d9360a71cf3185). Observed disposition: DEATH. Follow-up completion is not established by this document.

## Journey 5: Leslie Gold-Velazquez

Stable patient: patient_7d8d0ee7205d04d1c8be10409c462d14; birth date 1955-12-15; strata: acuity/3, acuity/4, acuity/5, age/65-79, allergy-withheld, carry/False, long-stay/False, outcome/HOME, pathway/M1711, pathway/R079, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- ED 2023-02-14T19:15:00Z to 2023-02-14T22:06:00Z; acuity 5; HOME; diagnosis R079; episode episode_7590f659ea6bea8156ae61f4ca84cf9f; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2023-02-14T22:06:00Z: Patient review: Leslie Gold-Velazquez, age 67. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 96.54 % (record clinical_event_cc7c7684fe33d96c277b5ec5277b4831). Heart rate: 113.25 /min (record clinical_event_14721be55af42c329bbcc484f4402c28). Troponin I: 7.46 ng/L (record clinical_event_d115fee64e92f01ebf42d96a91514c4d). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- IPD 2025-05-05T13:08:00Z to 2025-05-09T13:08:00Z; acuity 3; HOME; diagnosis M1711; episode episode_e741183850690e91963688693695d06d; predecessor encounter_version_c3f8cd9c3333fd8ab2be7fc5ad36fafa.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=1, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO NOT_DONE.

  OPERATIVE_NOTE @ 2025-05-05T23:08:00Z: Interval assessment: Leslie Gold-Velazquez, age 69. Presenting concern: right knee osteoarthritis limiting mobility. Working assessment: Unilateral primary osteoarthritis, right knee. Pain numeric rating: 8.00 1 (record clinical_event_83d0c5d070037c7f8d25878adc5f9df7). Mobility assessment: 1.00 1 (record clinical_event_759c4a4f955513282f8f9a68b725e6e8). Hemoglobin: 14.22 g/dL (record clinical_event_b5ed7b4864abba5b8360279ebcacda4b). Creatinine: 1.13 mg/dL (record clinical_event_58dd7a6c29917b7b10ee488ba1645725). Prior problem documentation is incomplete; absence of a record does not exclude disease. Procedure documented: Replacement of Right Knee Joint with Synthetic Substitute, Cemented, Open Approach (record clinical_event_f9f7d6bc19c0c5779966ba9a2e26b073). Acetaminophen 650 mg withheld; recorded allergy requires review (record clinical_event_7bbca1811dba82395e0770b5fde35657). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-05-09T13:08:00Z: Encounter review: Leslie Gold-Velazquez, age 69. Presenting concern: right knee osteoarthritis limiting mobility. Working assessment: Unilateral primary osteoarthritis, right knee. Hemoglobin: 14.22 g/dL (record clinical_event_b5ed7b4864abba5b8360279ebcacda4b). Hemoglobin: 13.52 g/dL (record clinical_event_9cc835ff417933911fe99f85ca49b8b2). Creatinine: 1.13 mg/dL (record clinical_event_58dd7a6c29917b7b10ee488ba1645725). Creatinine: 0.94 mg/dL (record clinical_event_1554b62bd23d13210111d83402ebfd49). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 650 mg withheld; recorded allergy requires review (record clinical_event_7bbca1811dba82395e0770b5fde35657). Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2025-09-01T14:48:00Z to 2025-09-01T16:41:00Z; acuity 4; HOME; diagnosis R079; episode episode_12c44ba273b738f0ddb48b6832522025; predecessor encounter_version_4726340210eae1696305dc8c1e18676c.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2025-09-01T16:41:00Z: Encounter review: Leslie Gold-Velazquez, age 69. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.84 % (record clinical_event_8ec657cf31da4270c6255fb4a1dde2fd). Heart rate: 76.20 /min (record clinical_event_a946fe8cd05d34a9d1425a7b4b3411c7). Troponin I: 5.72 ng/L (record clinical_event_69a6223de0047cd46184331ddd02a5de). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 6: Joan Myers

Stable patient: patient_0b07c0bef7c2ecc19f272d270d45a892; birth date 1923-02-26; strata: acuity/3, acuity/5, age/80+, carry/False, carry/True, long-stay/False, outcome/HOME, pathway/J189, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- OPD 2022-12-21T06:00:00Z to 2022-12-21T08:00:00Z; acuity 5; HOME; diagnosis J189; episode episode_2618a3a498dae9514e585446bfc6e616; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  OP_NOTE @ 2022-12-21T08:00:00Z: Care assessment: Joan Myers, age 99. Interval follow-up for cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Oxygen saturation: 97.21 % (record clinical_event_1965a43075cc62cae10d0f349b7c9c44). Heart rate: 82.65 /min (record clinical_event_8e7bd25c1affba14af07858e4b3c5b7c). Previously recorded problems: Chronic kidney disease, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- IPD 2022-12-28T15:00:00Z to 2023-01-07T13:00:00Z; acuity 3; HOME; diagnosis J189; episode episode_c84578612f4e00781189df7b199f185e; predecessor encounter_version_a29e5239567df8ecb31384a71754a897.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=14, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Doxycycline 100 mg PO COMPLETED; Doxycycline 100 mg PO COMPLETED.

  PROGRESS_NOTE @ 2022-12-28T19:00:00Z: Patient review: Joan Myers, age 99. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Body temperature: 38.22 Cel (record clinical_event_f09980352294f920ed53dbdf883d7f06). Oxygen saturation: 94.80 % (record clinical_event_7078df527b264ebd1fb0b52b3fb9a9f2). White blood cell count: 14.10 10*3/uL (record clinical_event_5cd09515d4ac7d25836676061168107e). C-reactive protein: 82.68 mg/L (record clinical_event_2947e46442fcb4747a78de53d37442ed). Previously recorded problems: Chronic kidney disease, unspecified. Doxycycline 100 mg administered (record clinical_event_70d0fb1ef303306dc942f381713cdd1b). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-01-07T13:00:00Z: Interval assessment: Joan Myers, age 99. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. White blood cell count: 14.10 10*3/uL (record clinical_event_5cd09515d4ac7d25836676061168107e). White blood cell count: 9.34 10*3/uL (record clinical_event_f19869abb49f42c0d018645548dc6883). C-reactive protein: 82.68 mg/L (record clinical_event_2947e46442fcb4747a78de53d37442ed). C-reactive protein: 13.28 mg/L (record clinical_event_2b1aca1600db9c01f980b640145c749b). Previously recorded problems: Chronic kidney disease, unspecified. Doxycycline 100 mg administered (record clinical_event_eb20a7f819f84bf8e156d6f840664c0d). Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2023-12-06T19:26:00Z to 2023-12-06T20:26:00Z; acuity 5; HOME; diagnosis R1010; episode episode_9c8e90a13809412ac1046ac825884487; predecessor encounter_version_155c87c2cbbae3b4d29f72f0780bf245.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2023-12-06T20:26:00Z: Clinical review: Joan Myers, age 100. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.27 % (record clinical_event_d96d59025b68311c0c3ec4b6d7500eda). Heart rate: 74.40 /min (record clinical_event_9354403a7e99e02233c89f5846ce4265). Previously recorded problems: Chronic kidney disease, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2025-01-19T09:26:00Z to 2025-01-19T11:08:00Z; acuity 3; HOME; diagnosis R1010; episode episode_5d48084cf649261d73edeb7a64127887; predecessor encounter_version_119ff68b48fae7dd26f7991cc81d6de0.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2025-01-19T11:08:00Z: Clinical review: Joan Myers, age 101. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 98.91 % (record clinical_event_f50348dec13f8387dc6ce36da7d0b9c5). Heart rate: 99.00 /min (record clinical_event_020632d440cbdafab64fe0390881629a). Hemoglobin: 13.60 g/dL (record clinical_event_0fb40c8390239995c3cdc922c9cfae01). Previously recorded problems: Chronic kidney disease, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- OPD 2025-06-30T17:23:00Z to 2025-06-30T18:59:00Z; acuity 5; HOME; diagnosis R1010; episode episode_c0766e24c923220aeef4dfbc2165ad0d; predecessor encounter_version_cd3950a6d2c88838bac30e275902ce9e.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  OP_NOTE @ 2025-06-30T18:59:00Z: Patient review: Joan Myers, age 102. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.09 % (record clinical_event_16a839028936f3708260db0e6c064f84). Heart rate: 82.80 /min (record clinical_event_2ddf4e249e05d0f21665453ed437777a). Previously recorded problems: Chronic kidney disease, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 7: John Smith

Stable patient: patient_6deb314071c82ead57a301cfd3de1a6c; birth date 1968-03-28; strata: acuity/5, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/I509, repeat/False, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- OPD 2024-04-12T16:32:00Z to 2024-04-12T17:09:00Z; acuity 5; HOME; diagnosis I509; episode episode_fb952845ed5629b39a5f1f128e451be9; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  OP_NOTE @ 2024-04-12T17:09:00Z: Care assessment: John Smith, age 56. Interval follow-up for worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 97.52 % (record clinical_event_853c2a21e5608fa682fac8449db76c7f). Heart rate: 78.60 /min (record clinical_event_b136b788c3e2f75fc8e468760f44b48d). Previously recorded problems: Heart failure, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 8: Thomas Cooper

Stable patient: patient_ca19eed2cdd27678568fa4d3b9caecab; birth date 1974-09-22; strata: acuity/4, age/35-49, carry/False, long-stay/False, outcome/HOME, pathway/R1010, repeat/False, service/ED, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2023-04-09T18:31:00Z to 2023-04-09T21:05:00Z; acuity 4; HOME; diagnosis R1010; episode episode_f52b44bf3119d626bec32aebb60d6172; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2023-04-09T21:05:00Z: Interval assessment: Thomas Cooper, age 48. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 98.94 % (record clinical_event_337bdb7ab2c04a9153a019448adaf36a). Heart rate: 101.75 /min (record clinical_event_0fa78ba43a2a255929b8372c18972424). Hemoglobin: 14.23 g/dL (record clinical_event_6853dd0b57d9e7aa5170445193accb77). Prior problem documentation is incomplete; absence of a record does not exclude disease. The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 9: Erica Hundley

Stable patient: patient_06824aeb919fc49e6e5c5d6223a7da47; birth date 1977-12-04; strata: acuity/2, acuity/3, acuity/4, acuity/5, age/35-49, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/I509, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- ED 2023-02-17T22:54:00Z to 2023-02-18T01:51:00Z; acuity 5; HOME; diagnosis R1010; episode episode_69b53f36db3a2f4053b34846be358362; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2023-02-18T01:51:00Z: Patient review: Erica Hundley, age 45. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 98.97 % (record clinical_event_5582acc59d83c0b7349f189457302209). Heart rate: 104.00 /min (record clinical_event_b49a9de6024053796c30aeeda8b0cdb6). Hemoglobin: 14.49 g/dL (record clinical_event_5a206844d5393ac97d2b148b4f7aaab4). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2023-02-27T21:36:00Z to 2023-02-28T01:36:00Z; acuity 2; TRANSFER; diagnosis I509; episode episode_4f50bb6b9517068bec5fd14e3bad48ed; predecessor encounter_version_e235d0f036bf707b9392a37b9e9fe648.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2023-02-28T01:36:00Z: Interval assessment: Erica Hundley, age 45. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 90.00 % (record clinical_event_4646ca538c35ba08f9b339cd26d8d965). Heart rate: 108.75 /min (record clinical_event_b2543662544ba0c229b72c1c2506aad5). Creatinine: 1.17 mg/dL (record clinical_event_d754c745db386a01b99664e4e9be6099). Previously recorded problems: Heart failure, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- IPD 2023-02-28T01:36:00Z to 2023-03-05T23:36:00Z; acuity 3; HOME; diagnosis I509; episode episode_4f50bb6b9517068bec5fd14e3bad48ed; predecessor encounter_version_223bd47b043406b60e8cbcc5a9538c2d.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=6, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Furosemide 20 mg PO COMPLETED; Furosemide 20 mg PO COMPLETED.

  PROGRESS_NOTE @ 2023-02-28T05:36:00Z: Patient review: Erica Hundley, age 45. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Body weight: 82.58 kg (record clinical_event_72f143a83a49bafa1a11972d5e9303ad). Oxygen saturation: 95.94 % (record clinical_event_76487cc7660701fb350c6dfeae88eddb). Creatinine: 1.13 mg/dL (record clinical_event_992b5eb4cd61c2960e17d9df3e8b05c3). Potassium: 4.43 mmol/L (record clinical_event_4c4429ee7449fe061a8b03659d37b304). Previously recorded problems: Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_d4ed0f1d580f11d779d2ace4da7dd23a). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-03-05T23:36:00Z: Assessment update: Erica Hundley, age 45. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Creatinine: 1.13 mg/dL (record clinical_event_992b5eb4cd61c2960e17d9df3e8b05c3). Creatinine: 0.96 mg/dL (record clinical_event_8892a1e4ac3e104be113818e4d453407). Potassium: 4.43 mmol/L (record clinical_event_4c4429ee7449fe061a8b03659d37b304). Potassium: 4.13 mmol/L (record clinical_event_9d1ce9c6699db954a6e378d7270017ce). Previously recorded problems: Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_f8f20bf0333112aa049446a68f09d973). Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2025-04-23T21:15:00Z to 2025-04-23T22:05:00Z; acuity 4; HOME; diagnosis I509; episode episode_5083eded89e2b60a1ff0e986b1072e84; predecessor encounter_version_672693d97877c06092c7672b8c3901c7.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.
  Treatment evidence: Furosemide 140 mg PO COMPLETED.

  OP_NOTE @ 2025-04-23T22:05:00Z: Assessment update: Erica Hundley, age 47. Interval follow-up for worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 97.68 % (record clinical_event_5028f1f3e3123c760defe27992194e85). Heart rate: 77.40 /min (record clinical_event_b2476cafb8e640d078e79b32fbf1da91). Previously recorded problems: Heart failure, unspecified. Furosemide 140 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_27c4e59af2eaaabb9efde8bdd7dc8143). Continue assessment as results become available. Follow-up completion is not established by this document.
- OPD 2025-07-07T16:54:00Z to 2025-07-07T18:31:00Z; acuity 5; HOME; diagnosis I509; episode episode_7b79069442a3a5c096d0baeefc22018b; predecessor encounter_version_5b66c7a3402af96ef40da3be475f02de.
  Captured evidence: DOCUMENT=1, OBSERVATION=2, ORDER=1, PROCEDURE=1.

  OP_NOTE @ 2025-07-07T18:31:00Z: Care assessment: Erica Hundley, age 47. Interval follow-up for worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 97.73 % (record clinical_event_1eb8b3683781573cf8148d9aeb57459f). Heart rate: 77.70 /min (record clinical_event_ec994c599a0be350f8d2e1008edebe62). Previously recorded problems: Heart failure, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 10: Stephanie Sanchez

Stable patient: patient_c9df370fc5cb0c784cab06988eecc99c; birth date 1992-04-15; strata: acuity/3, age/18-34, carry/False, long-stay/False, outcome/HOME, pathway/R1010, repeat/False, service/ED, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- ED 2023-01-18T03:53:00Z to 2023-01-18T05:34:00Z; acuity 3; HOME; diagnosis R1010; episode episode_f2c3ceffabb9c021215f2fca977b7883; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=3, PROCEDURE=1.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  ED_NOTE @ 2023-01-18T05:34:00Z: Interval assessment: Stephanie Sanchez, age 30. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 96.42 % (record clinical_event_ab15dc9ccb7d1169d992838b521dc01b). Heart rate: 92.50 /min (record clinical_event_f67e7f212f039f427c9c2ccd7545ecc7). Hemoglobin: 14.25 g/dL (record clinical_event_31e8784695c0f8ef6b4780b53154c94a). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_03194953f4103a318b733c2e58328788). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 11: Nancy Ashley

Stable patient: patient_3715541c305a850873392b2d0ef1adbf; birth date 1945-11-12; strata: acuity/2, acuity/3, acuity/4, age/65-79, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/J189, pathway/R079, repeat/True, service/ED, service/IPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- ED 2023-07-07T05:20:00Z to 2023-07-07T09:20:00Z; acuity 2; TRANSFER; diagnosis J189; episode episode_be4838fa4ca57322091f1488b210669b; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2, ORDER=1, PROCEDURE=1.

  ED_NOTE @ 2023-07-07T09:20:00Z: Encounter review: Nancy Ashley, age 77. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Oxygen saturation: 91.08 % (record clinical_event_932cb388b1066f05536e05372f8dfe32). Heart rate: 111.25 /min (record clinical_event_3f3d571889edae96fcb3c83481aba918). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2023-07-07T09:20:00Z to 2023-07-14T07:20:00Z; acuity 3; HOME; diagnosis J189; episode episode_be4838fa4ca57322091f1488b210669b; predecessor encounter_version_0214e49ce3c491f27ba6e93a905b713e.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=14, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Doxycycline 100 mg PO COMPLETED; Doxycycline 100 mg PO COMPLETED.

  PROGRESS_NOTE @ 2023-07-07T13:20:00Z: Patient review: Nancy Ashley, age 77. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Body temperature: 38.38 Cel (record clinical_event_7d36a44f54c9fec5acae511ffe020502). Oxygen saturation: 94.38 % (record clinical_event_afb3d937b7ff6c3ddff9a6c73a97b123). White blood cell count: 15.06 10*3/uL (record clinical_event_65fd77fef412035b906dcfd0e43ba7d2). C-reactive protein: 86.46 mg/L (record clinical_event_5f151c8075465159bad815254b6b20e1). Prior problem documentation is incomplete; absence of a record does not exclude disease. Doxycycline 100 mg administered (record clinical_event_74acc66612805b12022aebc890b2d9dc). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-07-14T07:20:00Z: Assessment update: Nancy Ashley, age 77. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. White blood cell count: 15.06 10*3/uL (record clinical_event_65fd77fef412035b906dcfd0e43ba7d2). White blood cell count: 9.10 10*3/uL (record clinical_event_7de2bccdd2c0fc3630944bb14190b2c1). C-reactive protein: 86.46 mg/L (record clinical_event_5f151c8075465159bad815254b6b20e1). C-reactive protein: 8.56 mg/L (record clinical_event_f906cfaf154c0b75048717c8e44ccf2a). Prior problem documentation is incomplete; absence of a record does not exclude disease. Doxycycline 100 mg administered (record clinical_event_ae242d2a44dc7f1c55fb29d8d7d3820c). Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2023-08-08T03:20:00Z to 2023-08-08T07:20:00Z; acuity 3; TRANSFER; diagnosis J189; episode episode_09112c4908f9c7b53218af0d44d46067; predecessor encounter_version_60cb76c7a09726bf81e0498c727e9721.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2023-08-08T07:20:00Z: Interval assessment: Nancy Ashley, age 77. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Oxygen saturation: 94.83 % (record clinical_event_04bd7fd87caba60d615bb0c9ccd84ec3). Heart rate: 113.50 /min (record clinical_event_339fe4acf63f4d04aee674644cc5c308). White blood cell count: 18.32 10*3/uL (record clinical_event_35f44b80865c5e5c3730f8f4fd2375ed). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2023-08-08T07:20:00Z to 2023-08-15T07:20:00Z; acuity 2; HOME; diagnosis J189; episode episode_09112c4908f9c7b53218af0d44d46067; predecessor encounter_version_23d7eb4af4222c215aa296e78e67e597.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=14, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Doxycycline 100 mg PO COMPLETED; Doxycycline 100 mg PO COMPLETED.

  PROGRESS_NOTE @ 2023-08-08T11:20:00Z: Care assessment: Nancy Ashley, age 77. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Body temperature: 38.46 Cel (record clinical_event_5d1095afdb1688283a6aec872ce2fdac). Oxygen saturation: 90.12 % (record clinical_event_7004c83ed2f45f25ab8a7a176967dbe9). White blood cell count: 15.92 10*3/uL (record clinical_event_77f5c0038e3e7df03c54f237409df8b9). C-reactive protein: 104.82 mg/L (record clinical_event_195cfea3ec6cccbef4f1f7d510da6f1b). Prior problem documentation is incomplete; absence of a record does not exclude disease. Doxycycline 100 mg administered (record clinical_event_238c82e8ec050d5a895289cd2e5001f3). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-08-15T07:20:00Z: Assessment update: Nancy Ashley, age 77. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. White blood cell count: 15.92 10*3/uL (record clinical_event_77f5c0038e3e7df03c54f237409df8b9). White blood cell count: 9.55 10*3/uL (record clinical_event_806ca3957c50525cab4f1547748a49dc). C-reactive protein: 104.82 mg/L (record clinical_event_195cfea3ec6cccbef4f1f7d510da6f1b). C-reactive protein: 13.52 mg/L (record clinical_event_ec581fced0ba8706b169f1801f126abe). Prior problem documentation is incomplete; absence of a record does not exclude disease. Doxycycline 100 mg administered (record clinical_event_e0ce0be6bc724f967b30fdfd1f90b798). Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2023-09-26T13:49:00Z to 2023-09-26T15:42:00Z; acuity 4; HOME; diagnosis R079; episode episode_2e81676ac5ac4abd153a37f9d9cb7e51; predecessor encounter_version_3ab837b0dec7bb5b190e7469cbe5451d.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2023-09-26T15:42:00Z: Clinical review: Nancy Ashley, age 77. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.44 % (record clinical_event_f0e079c0d3e61e2541333f7e290f91ee). Heart rate: 110.50 /min (record clinical_event_5afbdf9a6fd91b0e58ae98a4ca7403f5). Troponin I: 6.62 ng/L (record clinical_event_1a44e0fa9ffd87de4762d2a61d8a6665). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 12: Joseph Stenger

Stable patient: patient_7b953d11727c327897c1950183240cb6; birth date 1968-01-07; strata: acuity/3, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/J449, repeat/False, service/ED, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- ED 2023-03-19T20:38:00Z to 2023-03-19T23:05:00Z; acuity 3; HOME; diagnosis J449; episode episode_1b5f24915a21d98ea30364506aa96166; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2023-03-19T23:05:00Z: Care assessment: Joseph Stenger, age 55. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 94.62 % (record clinical_event_5df31e7f30b7327501e98da7dced1584). Heart rate: 95.00 /min (record clinical_event_110f929b06c65410ea8f4d115b7fb221). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 13: Michele Maxwell

Stable patient: patient_fa957eb56336a21e113858c20f71a77b; birth date 1964-05-11; strata: acuity/4, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/R1010, repeat/False, service/ED, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2023-05-16T03:44:00Z to 2023-05-16T05:59:00Z; acuity 4; HOME; diagnosis R1010; episode episode_5c3243a6100d76acdc9096117bfeb5f0; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2, ORDER=1, PROCEDURE=1.

  ED_NOTE @ 2023-05-16T05:59:00Z: Patient review: Michele Maxwell, age 59. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 98.67 % (record clinical_event_61f85a8130c3b2ab0227d33d28f8e257). Heart rate: 90.50 /min (record clinical_event_d319940bd0ec6fd593df658a0faf2466). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 14: Kimberly Fields

Stable patient: patient_9c3da4dafbe008652e4ce9a65f68e3d6; birth date 1975-09-11; strata: acuity/3, age/35-49, carry/False, long-stay/False, outcome/HOME, pathway/I509, pathway/K8010, pathway/R079, repeat/True, service/IPD, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- OPD 2022-12-26T06:00:00Z to 2022-12-26T08:00:00Z; acuity 3; HOME; diagnosis I509; episode episode_23d4f51064ea6ae49f08c724d8e52c1c; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2.
  Treatment evidence: Furosemide 140 mg PO COMPLETED.

  OP_NOTE @ 2022-12-26T08:00:00Z: Encounter review: Kimberly Fields, age 47. Interval follow-up for worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 97.35 % (record clinical_event_50c2381173543a38ecefb001bad08389). Heart rate: 82.20 /min (record clinical_event_a5e4bde7493a151fb7321a69b8e50d1d). Creatinine: 1.22 mg/dL (record clinical_event_b36df3462926d58deb89f5a78012fd69). Previously recorded problems: Heart failure, unspecified. Furosemide 140 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_17590b93d517136b2514253175e38939). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- OPD 2023-06-13T19:04:00Z to 2023-06-13T19:46:00Z; acuity 3; HOME; diagnosis R079; episode episode_2d2e602edbfa89636a6e02a6d08b4353; predecessor encounter_version_22df1ad676c6119e6dd77ef69ad85de4.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2023-06-13T19:46:00Z: Patient review: Kimberly Fields, age 47. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.01 % (record clinical_event_2328607bed95fbd17ed90ccb730a6718). Heart rate: 83.70 /min (record clinical_event_ccf500fc75c5f8cc4e56c96810ac587b). Previously recorded problems: Heart failure, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2024-04-08T15:06:00Z to 2024-04-13T06:06:00Z; acuity 3; HOME; diagnosis K8010; episode episode_d2ec66ee085befdcbb637c53b4449d18; predecessor encounter_version_7e410386ee42938b69d79425ad970bd4.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=12, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2024-04-09T01:06:00Z: Assessment update: Kimberly Fields, age 48. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 6.00 1 (record clinical_event_b9ec7f9cfd6511113ad4e91c412b8ba1). Heart rate: 103.50 /min (record clinical_event_92cc7fa680eafcd4b7ae183251b55ddb). Hemoglobin: 14.43 g/dL (record clinical_event_76fee5564be6bd68c78f741a9d681138). Creatinine: 1.18 mg/dL (record clinical_event_37070b3078317b6467594be9c4b90019). Previously recorded problems: Heart failure, unspecified. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_8e90c7faf5407f18747e4a076c9ecda1). Acetaminophen 650 mg administered (record clinical_event_6cc4536293d2af23e987b96cf824da53). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2024-04-13T06:06:00Z: Interval assessment: Kimberly Fields, age 48. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 14.43 g/dL (record clinical_event_76fee5564be6bd68c78f741a9d681138). Hemoglobin: 13.73 g/dL (record clinical_event_ed4a3ac80dfc5f89164983daafcfc46d). Creatinine: 1.18 mg/dL (record clinical_event_37070b3078317b6467594be9c4b90019). Creatinine: 1.04 mg/dL (record clinical_event_16959515015cd7e7cde0772cd0411382). Previously recorded problems: Heart failure, unspecified. Acetaminophen 650 mg administered (record clinical_event_16b201d7b8c6d3b83114240fa5b399a9). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 15: Kenneth Ryan

Stable patient: patient_9c1fcb4ea2b3f1d7a9b6500ed70f4288; birth date 1958-08-22; strata: acuity/2, acuity/3, acuity/4, age/65-79, carry/False, long-stay/False, outcome/HOME, pathway/K8010, pathway/R079, repeat/True, service/ED, service/IPD, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- OPD 2023-10-12T17:17:00Z to 2023-10-12T18:42:00Z; acuity 4; HOME; diagnosis R079; episode episode_29e19cbf66f9d73ae1d15246b026f6ee; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2023-10-12T18:42:00Z: Clinical review: Kenneth Ryan, age 65. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.12 % (record clinical_event_f83547e4f2fc296be2658ca4558b2b91). Heart rate: 82.20 /min (record clinical_event_4130dfc46b55fa549dd4e887f6bcdbb4). Troponin I: 5.30 ng/L (record clinical_event_af4da5ed35ff45a9702dc6b4b06d3db6). Previously recorded problems: Essential (primary) hypertension. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2025-02-11T13:57:00Z to 2025-02-15T11:57:00Z; acuity 2; HOME; diagnosis K8010; episode episode_4ece602ef9715d8b36e6c30feb6c1d1a; predecessor encounter_version_305195af16ed7826f7a9ebd66299e86e.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=10, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2025-02-11T23:57:00Z: Encounter review: Kenneth Ryan, age 66. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 5.00 1 (record clinical_event_6ff0848b56c06b675b59fc4af255086b). Heart rate: 111.25 /min (record clinical_event_f6ad66550efca6004d55d59d08dfd962). Hemoglobin: 13.45 g/dL (record clinical_event_2a1a1f19f2169f2829c8b51febe1ed21). Creatinine: 1.24 mg/dL (record clinical_event_25c89625ee0c7d34440d75fda5e72680). Previously recorded problems: Essential (primary) hypertension. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_3bbabc4c44e277e41b117f6c3d3d1e79). Acetaminophen 650 mg administered (record clinical_event_a3713c26eb32581438b5972c4c71c4dc). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-02-15T11:57:00Z: Encounter review: Kenneth Ryan, age 66. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 13.45 g/dL (record clinical_event_2a1a1f19f2169f2829c8b51febe1ed21). Hemoglobin: 12.75 g/dL (record clinical_event_0fac91a28b7e2213eae41649c33ca103). Creatinine: 1.24 mg/dL (record clinical_event_25c89625ee0c7d34440d75fda5e72680). Creatinine: 1.03 mg/dL (record clinical_event_bdb8e06c2943b372f284246d05efa1da). Previously recorded problems: Essential (primary) hypertension. Acetaminophen 650 mg administered (record clinical_event_dedb59fbb733531dfbe18d44d91a5f8a). Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2025-06-18T09:11:00Z to 2025-06-18T12:03:00Z; acuity 3; HOME; diagnosis R079; episode episode_6ba3f0136c0e13f499de3269defaf1ec; predecessor encounter_version_bb90f793d0542b207217be5bc30e657d.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-06-18T12:03:00Z: Care assessment: Kenneth Ryan, age 66. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.38 % (record clinical_event_aba894fa1d5d0cd0dcae2688c4f10d5c). Heart rate: 105.50 /min (record clinical_event_f385880f33ddc068ff603e22b742e1d3). Troponin I: 2.36 ng/L (record clinical_event_d749f001f77647752adcc98afba48274). Previously recorded problems: Essential (primary) hypertension. The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 16: Leroy Cooper

Stable patient: patient_009b5ee1d46f193ce9fa6f150d93b371; birth date 1933-11-06; strata: acuity/3, acuity/4, acuity/5, age/80+, carry/False, long-stay/False, outcome/HOME, pathway/J189, pathway/K8010, pathway/R079, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- OPD 2023-09-19T17:51:00Z to 2023-09-19T18:33:00Z; acuity 4; HOME; diagnosis R1010; episode episode_6a80dd0c94bdc1d29094b762b15992ec; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2023-09-19T18:33:00Z: Assessment update: Leroy Cooper, age 89. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.64 % (record clinical_event_0e1b54fc393fa9c5a73dd5c23a31261a). Heart rate: 72.60 /min (record clinical_event_5b631336a726245e95b0e56a3ddeb9a7). Previously recorded problems: Chronic kidney disease, unspecified; Hyperlipidemia, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2023-12-01T15:35:00Z to 2023-12-06T02:35:00Z; acuity 3; HOME; diagnosis K8010; episode episode_9051b4ba9d94c8ff344d6e79844bfe4d; predecessor encounter_version_45cce9e8222fdbfa200792ccd3e6448a.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=13, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2023-12-02T01:35:00Z: Care assessment: Leroy Cooper, age 90. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 5.00 1 (record clinical_event_c6b677325fac957a0baf9c005a7bb04a). Heart rate: 104.00 /min (record clinical_event_06be7b5e48a6531e9ed95032908fd82a). Hemoglobin: 13.54 g/dL (record clinical_event_e51b0ca51e6a2d971290c2530a65bffe). Creatinine: 1.90 mg/dL (record clinical_event_93af529420ae33575ae7eac0d44e78ef). Previously recorded problems: Chronic kidney disease, unspecified; Hyperlipidemia, unspecified. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_def532749c65f7ca6c43072e291ea8e5). Acetaminophen 650 mg administered (record clinical_event_b1d662ace807560878dbe2fdf3559350). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-12-06T02:35:00Z: Care assessment: Leroy Cooper, age 90. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 13.54 g/dL (record clinical_event_e51b0ca51e6a2d971290c2530a65bffe). Hemoglobin: 12.84 g/dL (record clinical_event_c016c78bc26ee4929fd607dc8017dea0). Creatinine: 1.90 mg/dL (record clinical_event_93af529420ae33575ae7eac0d44e78ef). Creatinine: 1.76 mg/dL (record clinical_event_722cdd74f7c8ae7aa505b745805350c9). Previously recorded problems: Chronic kidney disease, unspecified; Hyperlipidemia, unspecified. Acetaminophen 650 mg administered (record clinical_event_37e0dbab4640486b063fb7e51a367feb). Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2024-01-25T16:04:00Z to 2024-01-25T17:56:00Z; acuity 3; HOME; diagnosis R079; episode episode_76dea9d7324d6bdbd139633a291e758d; predecessor encounter_version_d874b6a5a053642ac3dfeff01fd46970.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2024-01-25T17:56:00Z: Clinical review: Leroy Cooper, age 90. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.84 % (record clinical_event_2908a1cbf60cd06d87cee8f247855a1b). Heart rate: 86.25 /min (record clinical_event_3011d48a2e3e527946182810f42f4b87). Troponin I: 7.82 ng/L (record clinical_event_682411b0b90e742264758f655ee9c7e3). Previously recorded problems: Chronic kidney disease, unspecified; Hyperlipidemia, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2024-06-25T23:39:00Z to 2024-06-26T01:51:00Z; acuity 5; HOME; diagnosis J189; episode episode_739d5dec6e60a231f1c86df971f13e50; predecessor encounter_version_ee084c120b5ef9b00e19c07fef9d4616.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=1.
  Treatment evidence: Doxycycline 1400 mg PO COMPLETED.

  ED_NOTE @ 2024-06-26T01:51:00Z: Clinical review: Leroy Cooper, age 90. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Oxygen saturation: 95.97 % (record clinical_event_345cebc21f37ce5c0b06cc202bb72225). Heart rate: 110.50 /min (record clinical_event_1e7381563152decf0c18b22588ea31c9). Previously recorded problems: Chronic kidney disease, unspecified; Hyperlipidemia, unspecified. Doxycycline 1400 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_9ac836d94fb495f2a6e0848cffcc63a8). The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 17: Rodger Hughes

Stable patient: patient_386e72481dc4f1e696e53f3439c18ae4; birth date 1955-08-28; strata: acuity/2, acuity/3, acuity/4, acuity/5, age/65-79, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/I509, pathway/R079, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2023-02-20T10:40:00Z to 2023-02-20T13:07:00Z; acuity 5; HOME; diagnosis R079; episode episode_56167992fc22b1f45a24e6f10ae76be8; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2023-02-20T13:07:00Z: Encounter review: Rodger Hughes, age 67. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 96.96 % (record clinical_event_85fc1a6d39fe787704520062690b388d). Heart rate: 112.25 /min (record clinical_event_c62da72603504c756cc2d2280b6729b9). Troponin I: 7.82 ng/L (record clinical_event_0429a4675051afcc8fd667759f09519d). Previously recorded problems: Chronic kidney disease, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- OPD 2023-06-12T20:27:00Z to 2023-06-12T21:46:00Z; acuity 3; HOME; diagnosis R1010; episode episode_1089ccd458819770343201c69d8974e6; predecessor encounter_version_36f5ee64f41c96de6e70fae01b6dcc8b.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  OP_NOTE @ 2023-06-12T21:46:00Z: Encounter review: Rodger Hughes, age 67. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.20 % (record clinical_event_10b7083c8b41b4ac61b9e4bcf4fda11a). Heart rate: 82.05 /min (record clinical_event_1e605fd31178f6246910399b851026be). Previously recorded problems: Chronic kidney disease, unspecified. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_48426b663c34d15e433dd0d55b42c243). The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2023-08-09T15:00:00Z to 2023-08-09T19:00:00Z; acuity 3; TRANSFER; diagnosis I509; episode episode_c5bca67ec7b2e3536459571c039810f5; predecessor encounter_version_a7df5bd53a0046c0c995761eaf402502.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.
  Treatment evidence: Furosemide 140 mg PO COMPLETED.

  ED_NOTE @ 2023-08-09T19:00:00Z: Patient review: Rodger Hughes, age 67. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 95.88 % (record clinical_event_83a3403ac7c0e05271419ccda4d3968c). Heart rate: 95.50 /min (record clinical_event_1e200eace318dca1f1df14613e694939). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Furosemide 140 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_2343fca24f194acbbdfc28c368c0aa96). The current assessment may change with further evidence. Follow-up completion is not established by this document.
- IPD 2023-08-09T19:00:00Z to 2023-08-14T17:00:00Z; acuity 3; HOME; diagnosis I509; episode episode_c5bca67ec7b2e3536459571c039810f5; predecessor encounter_version_afcafe7b354e14df130c230b0327b402.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=5, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Furosemide 20 mg PO COMPLETED; Furosemide 20 mg PO COMPLETED.

  PROGRESS_NOTE @ 2023-08-09T23:00:00Z: Interval assessment: Rodger Hughes, age 67. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Body weight: 70.08 kg (record clinical_event_1f0183f0b6258ead16bdd7bde9a43a78). Oxygen saturation: 95.67 % (record clinical_event_15b3103c2e3b4209502bde44d530a0f1). Creatinine: 1.97 mg/dL (record clinical_event_5c75e6db8970e84dfdf0db28eff4c5f1). Potassium: 4.36 mmol/L (record clinical_event_18cc494bb48aefeaec9ef7ee2982ffca). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_04b72014ecefdaff8d629665cb6694d8). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-08-14T17:00:00Z: Clinical review: Rodger Hughes, age 67. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Creatinine: 1.97 mg/dL (record clinical_event_5c75e6db8970e84dfdf0db28eff4c5f1). Creatinine: 1.90 mg/dL (record clinical_event_dc5c29a45e67c45c64a37f62d7c6c0a8). Potassium: 4.36 mmol/L (record clinical_event_18cc494bb48aefeaec9ef7ee2982ffca). Potassium: 4.06 mmol/L (record clinical_event_ce4f11f206fa49ad96c7f7de7ec88f9f). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_48f378397dd767929c7ea0a97975ef35). Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2023-09-05T13:00:00Z to 2023-09-05T17:00:00Z; acuity 2; TRANSFER; diagnosis I509; episode episode_c1f6eaa1581f625c421080214cc3050f; predecessor encounter_version_39f15bd5a43f6cbccebcc0a600ca1121.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2023-09-05T17:00:00Z: Patient review: Rodger Hughes, age 68. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 90.84 % (record clinical_event_20883183dd13e69dee0a13f0a151542f). Heart rate: 95.00 /min (record clinical_event_53ac2d1d2a5c01dd80f14f9113e46bd3). Creatinine: 2.08 mg/dL (record clinical_event_b67cc08977872bc342896b32c542724f). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- IPD 2023-09-05T17:00:00Z to 2023-09-10T23:00:00Z; acuity 2; HOME; diagnosis I509; episode episode_c1f6eaa1581f625c421080214cc3050f; predecessor encounter_version_9472d2c36362ba21932bfb9c7da6cffd.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=6, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Furosemide 20 mg PO COMPLETED; Furosemide 20 mg PO COMPLETED.

  PROGRESS_NOTE @ 2023-09-05T21:00:00Z: Patient review: Rodger Hughes, age 68. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Body weight: 70.15 kg (record clinical_event_6196021c5c50be0e521516b23634d033). Oxygen saturation: 90.42 % (record clinical_event_bc822b26f5c4298cb2111954b9a6af94). Creatinine: 2.03 mg/dL (record clinical_event_c0c33cd270627b661f786b12a479b09e). Potassium: 4.47 mmol/L (record clinical_event_74a1914b4e2ee4c8bb95988e702f2449). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_caa4552aae7d58dad9959468acfa89fb). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-09-10T23:00:00Z: Patient review: Rodger Hughes, age 68. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Creatinine: 2.03 mg/dL (record clinical_event_c0c33cd270627b661f786b12a479b09e). Creatinine: 1.94 mg/dL (record clinical_event_1ad1163f024c3d93fe7d727a44b87739). Potassium: 4.47 mmol/L (record clinical_event_74a1914b4e2ee4c8bb95988e702f2449). Potassium: 4.17 mmol/L (record clinical_event_1af7154cd1245cfd0ac83073e13d984d). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_66ab2b6c72ffc4dfc36211834dcbea08). Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2023-11-10T09:43:00Z to 2023-11-10T12:37:00Z; acuity 4; HOME; diagnosis R1010; episode episode_b7bb0d0874e7ca9eb81083be38728b28; predecessor encounter_version_ed7132764a039273e0bd45fa85ba52fa.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  ED_NOTE @ 2023-11-10T12:37:00Z: Patient review: Rodger Hughes, age 68. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.26 % (record clinical_event_d1d158f00f643f55fb5c5fb659624155). Heart rate: 111.50 /min (record clinical_event_525bf55c55615cfaf2755d6a0c04864e). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_6b97936eed64d933173aa58c737ef4dd). Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2024-09-30T22:56:00Z to 2024-10-01T00:40:00Z; acuity 3; HOME; diagnosis R1010; episode episode_15d52f94d056f6e89f7cdce732c2f466; predecessor encounter_version_86892ec3f6acc18b0c0c47ea8281c324.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=3, PROCEDURE=1.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  ED_NOTE @ 2024-10-01T00:40:00Z: Encounter review: Rodger Hughes, age 69. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.68 % (record clinical_event_33b50423cab42f4f16f3863a14a25dca). Heart rate: 92.25 /min (record clinical_event_a20ca610033def19b55bba2116532e49). Hemoglobin: 14.43 g/dL (record clinical_event_873a7b392702c1a0c01853edc49f113a). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_da585fcb6d0a88a279e04a48599b0eac). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2025-07-12T03:34:00Z to 2025-07-12T05:58:00Z; acuity 5; HOME; diagnosis I509; episode episode_cebfa3c74c18c399176804db8f12b3b6; predecessor encounter_version_da54a34fd955b6783c75d9646b08c780.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2025-07-12T05:58:00Z: Interval assessment: Rodger Hughes, age 69. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 95.10 % (record clinical_event_f8f7f77693ebda913bf6418e9c44327f). Heart rate: 102.50 /min (record clinical_event_c5c562f984555913d12d7851bdb35325). Creatinine: 2.08 mg/dL (record clinical_event_a26c82a90bc0eec2b3bd67e77a59a530). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- OPD 2025-12-09T19:44:00Z to 2025-12-09T21:32:00Z; acuity 5; HOME; diagnosis I509; episode episode_f34ec5bccd99036353d22737574ae80f; predecessor encounter_version_b4fb684f60a34d3c55f49f9ac9a75f37.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=1.
  Treatment evidence: Furosemide 140 mg PO COMPLETED.

  OP_NOTE @ 2025-12-09T21:32:00Z: Assessment update: Rodger Hughes, age 70. Interval follow-up for worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 97.62 % (record clinical_event_d40a27fb008b3b56fe11feaa299da289). Heart rate: 74.40 /min (record clinical_event_af3258130dd4bc0f18de1e3aee294ad7). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Furosemide 140 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_b519dcb72892ef73c39f5fa959608b86). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 18: Sara Watson

Stable patient: patient_68cfe78320c75a90a2e04d0d6204e5c6; birth date 1984-08-08; strata: acuity/4, age/35-49, carry/False, long-stay/False, outcome/HOME, pathway/R1010, repeat/False, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- OPD 2024-01-09T20:49:00Z to 2024-01-09T21:54:00Z; acuity 4; HOME; diagnosis R1010; episode episode_060736e69725a495bfdf941b1651d3c8; predecessor none.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=1.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  OP_NOTE @ 2024-01-09T21:54:00Z: Care assessment: Sara Watson, age 39. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.22 % (record clinical_event_94f2139872d53766db55c1a980fe0a9c). Heart rate: 81.15 /min (record clinical_event_0cdcfbfd029c920e7e9f14cc4866ed89). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_db6edf6fe9972aaa3aa4a0a8c29f30d9). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 19: Mary Hernandez

Stable patient: patient_bfb7e5fead5d35772a387511ea8b8ab4; birth date 1970-04-06; strata: acuity/2, acuity/4, acuity/5, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/E119, pathway/M1711, pathway/R079, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- OPD 2022-12-26T06:00:00Z to 2022-12-26T08:00:00Z; acuity 5; HOME; diagnosis E119; episode episode_330ea7c26d4c973f9596748259e82747; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2022-12-26T08:00:00Z: Care assessment: Mary Hernandez, age 52. Interval follow-up for symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 97.75 % (record clinical_event_ac182201c4ee5433028a50c0cd3ca363). Heart rate: 76.20 /min (record clinical_event_879a86e2ab9e1106b9d4d9468910a0cc). Serum glucose: 316.80 mg/dL (record clinical_event_b78577afd523df1ba453feaf3fa0458a). Previously recorded problems: Chronic kidney disease, unspecified; Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- IPD 2023-06-14T15:06:00Z to 2023-06-18T06:06:00Z; acuity 2; HOME; diagnosis M1711; episode episode_dae6df5e4732d05a31d37b2196f80dea; predecessor encounter_version_e1cb96100f7f58e107d9165807425085.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=12, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2023-06-15T01:06:00Z: Encounter review: Mary Hernandez, age 53. Presenting concern: right knee osteoarthritis limiting mobility. Working assessment: Unilateral primary osteoarthritis, right knee. Pain numeric rating: 5.00 1 (record clinical_event_89093f8fd75bf2eaafc511abf39863d8). Mobility assessment: 2.00 1 (record clinical_event_7277595b409100b55d3d5fbacb268534). Hemoglobin: 14.13 g/dL (record clinical_event_c0104dce17cfcfe172ded689fac0a84e). Creatinine: 2.10 mg/dL (record clinical_event_80a90d479ffae1990aaa8fe477b0b3ef). Previously recorded problems: Chronic kidney disease, unspecified; Type 2 diabetes mellitus without complications. Procedure documented: Replacement of Right Knee Joint with Synthetic Substitute, Cemented, Open Approach (record clinical_event_5989f517b684cb606bb68f4e273e40ed). Acetaminophen 650 mg administered (record clinical_event_fabce12d8b85667e49c4284ac2cd33cb). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-06-18T06:06:00Z: Care assessment: Mary Hernandez, age 53. Presenting concern: right knee osteoarthritis limiting mobility. Working assessment: Unilateral primary osteoarthritis, right knee. Hemoglobin: 14.13 g/dL (record clinical_event_c0104dce17cfcfe172ded689fac0a84e). Hemoglobin: 13.43 g/dL (record clinical_event_f2c618b77b0e2374730a1554416b874c). Creatinine: 2.10 mg/dL (record clinical_event_80a90d479ffae1990aaa8fe477b0b3ef). Creatinine: 1.91 mg/dL (record clinical_event_3791531cfe25eed22372301fcdf66e5e). Previously recorded problems: Chronic kidney disease, unspecified; Type 2 diabetes mellitus without complications. Acetaminophen 650 mg administered (record clinical_event_996e2fc161ccecdd97fa3b4c1a2d37dc). Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2024-01-07T15:38:00Z to 2024-01-07T18:02:00Z; acuity 5; HOME; diagnosis R079; episode episode_4b8158f460add14a72bfb0efbd85190f; predecessor encounter_version_841e8141b6fdcd70993a08a6dbe60a41.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2024-01-07T18:02:00Z: Encounter review: Mary Hernandez, age 53. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 96.39 % (record clinical_event_5536afb335dccaf2df912ba9dc8c156b). Heart rate: 109.00 /min (record clinical_event_742dd9e1e45c9ea3c37d1f916bf41132). Troponin I: 3.50 ng/L (record clinical_event_5bb99f1423d21f0df4e2717ef34466f2). Previously recorded problems: Chronic kidney disease, unspecified; Type 2 diabetes mellitus without complications. Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2024-10-30T19:43:00Z to 2024-10-30T22:37:00Z; acuity 5; HOME; diagnosis R079; episode episode_ccf8fee07e6d0be06492b0d415886126; predecessor encounter_version_3b27388e9dd0cc081c34703857bd5cab.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2024-10-30T22:37:00Z: Interval assessment: Mary Hernandez, age 54. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 98.79 % (record clinical_event_6c5d25ffbde60a37e5772d6dd307d331). Heart rate: 99.25 /min (record clinical_event_a7de2993fef5258f55854859e6e71b7b). Troponin I: 3.26 ng/L (record clinical_event_81401d5e55dd5cc8a267bb5fdbcefaa5). Previously recorded problems: Chronic kidney disease, unspecified; Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2025-02-12T21:59:00Z to 2025-02-13T00:38:00Z; acuity 5; HOME; diagnosis R079; episode episode_7d1c2bd25e4a6de213fe216ce46ae0f7; predecessor encounter_version_7bbfd61d552ea2f248ed5df9dc833d2e.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-02-13T00:38:00Z: Clinical review: Mary Hernandez, age 54. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 98.13 % (record clinical_event_bcf3aaf1a5a0095095a1e0ebb3c98230). Heart rate: 106.25 /min (record clinical_event_4fe1aa2117877b8a774cf32a9a020ba4). Troponin I: 2.60 ng/L (record clinical_event_8be20fc10d3db7d5ff0138a6e0e433fc). Previously recorded problems: Chronic kidney disease, unspecified; Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- OPD 2025-09-29T19:41:00Z to 2025-09-29T21:29:00Z; acuity 4; HOME; diagnosis R1010; episode episode_8e7292bbdec296f5d916b9b9b3169bea; predecessor encounter_version_4b8f797254be2bafc96445b02984ddb6.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2025-09-29T21:29:00Z: Interval assessment: Mary Hernandez, age 55. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.30 % (record clinical_event_1566e08534a73b96105b755a7d569907). Heart rate: 77.40 /min (record clinical_event_dd1d078233a3c60b25400c6700a0b9eb). Hemoglobin: 13.87 g/dL (record clinical_event_6838d12e0883c2d48afd9c9edba3d312). Previously recorded problems: Chronic kidney disease, unspecified; Type 2 diabetes mellitus without complications. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2025-11-28T14:28:00Z to 2025-11-28T17:27:00Z; acuity 4; HOME; diagnosis R1010; episode episode_7d43d7b6e06488dac9853d6d1fa1f62d; predecessor encounter_version_5313d4ccf4fcf5924d450d88c7e164e7.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  ED_NOTE @ 2025-11-28T17:27:00Z: Care assessment: Mary Hernandez, age 55. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.44 % (record clinical_event_d71be7861f1a81ca699544fa5a0f47f2). Heart rate: 113.00 /min (record clinical_event_0bb264667b46565d52016537ee433ce6). Hemoglobin: 14.36 g/dL (record clinical_event_4c5c479cda8ead9a9d2e68abe17f6f9f). Previously recorded problems: Chronic kidney disease, unspecified; Type 2 diabetes mellitus without complications. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_ab816b3dd31e38f4d759d0c1d44564da). The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 20: Isabella Peterson

Stable patient: patient_6d1f9514ff5a2c067fec7dfcc2d4c930; birth date 2000-06-17; strata: acuity/5, age/18-34, carry/False, long-stay/False, outcome/HOME, pathway/R1010, repeat/False, service/OPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- OPD 2025-07-24T18:17:00Z to 2025-07-24T19:18:00Z; acuity 5; HOME; diagnosis R1010; episode episode_0d522d8bbef9dfef5ef344703b2592a2; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  OP_NOTE @ 2025-07-24T19:18:00Z: Patient review: Isabella Peterson, age 25. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.86 % (record clinical_event_42f0499ba7a2bc445f912fe45b3026f4). Heart rate: 84.90 /min (record clinical_event_4f945028b34b42a04f4dfd323b7bb185). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 21: David Wright

Stable patient: patient_5c4bfe9914e880e2c0b2c05379a5b851; birth date 1961-08-02; strata: acuity/4, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/R1010, repeat/False, service/ED, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2024-11-08T05:23:00Z to 2024-11-08T07:46:00Z; acuity 4; HOME; diagnosis R1010; episode episode_281c0d86950a19702846ca5ee815f8f6; predecessor none.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=1.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  ED_NOTE @ 2024-11-08T07:46:00Z: Care assessment: David Wright, age 63. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.71 % (record clinical_event_66f397c3351b67f9dce5389a49ea437a). Heart rate: 112.00 /min (record clinical_event_78c0260529346095bde66c74ef17ed62). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_c708c75ea68e32d369406538b228a7a8). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 22: John Murray

Stable patient: patient_6b31c095e0f0258bc7ef82698d044fe3; birth date 1937-05-09; strata: acuity/5, age/80+, carry/False, long-stay/False, outcome/HOME, pathway/E119, repeat/False, service/ED, site/facility_7990133218ef060b178c3cf8a0825f76.

- ED 2024-01-23T11:47:00Z to 2024-01-23T14:27:00Z; acuity 5; HOME; diagnosis E119; episode episode_021e9918fa9fd900e727700c14f2d103; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2, ORDER=1, PROCEDURE=1.

  ED_NOTE @ 2024-01-23T14:27:00Z: Patient review: John Murray, age 86. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 98.13 % (record clinical_event_fb1ac290e40d75009f7f2259d79fd434). Heart rate: 101.00 /min (record clinical_event_73b7221fce6d6d1f347cb211449222e2). Previously recorded problems: Hyperlipidemia, unspecified; Type 2 diabetes mellitus without complications. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 23: Cassie Piotrowski

Stable patient: patient_0982b7acc7caa5e9092d85734c5d7307; birth date 1980-09-19; strata: acuity/3, acuity/4, acuity/5, age/35-49, carry/False, long-stay/False, outcome/HOME, outcome/LEFT_WITHOUT_SEEN, pathway/J189, pathway/K8010, pathway/R079, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- OPD 2023-09-25T20:28:00Z to 2023-09-25T21:53:00Z; acuity 4; HOME; diagnosis J189; episode episode_dfde44c275b355b0852ee94e4a770caf; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2023-09-25T21:53:00Z: Care assessment: Cassie Piotrowski, age 43. Interval follow-up for cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Oxygen saturation: 97.13 % (record clinical_event_7034c5d4bea91d1c1117eae5fa2eaaed). Heart rate: 83.10 /min (record clinical_event_38621198a2b577edc16ec4d782d6ccc1). White blood cell count: 14.32 10*3/uL (record clinical_event_28b2da21c3fa644571bab1cc9585a691). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2023-12-06T10:01:00Z to 2023-12-06T11:59:00Z; acuity 4; LEFT_WITHOUT_SEEN; diagnosis unassessed; episode episode_8165743273ba8b9f8e10bf97ac6f817b; predecessor encounter_version_a955f672d82a9e4b8903947e2b466a85.
  Captured evidence: .
- ED 2024-05-26T08:19:00Z to 2024-05-26T10:28:00Z; acuity 4; HOME; diagnosis R079; episode episode_ce7d034282cd4c063347d7ebc1093008; predecessor encounter_version_b95fcc1a352dab292e2a991c172b987c.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2024-05-26T10:28:00Z: Interval assessment: Cassie Piotrowski, age 43. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 98.52 % (record clinical_event_2e6ffecaaa7b5270d9b3b0ab063a8248). Heart rate: 110.25 /min (record clinical_event_b3a87b88e8df0901ffd48cbcde0d06f0). Troponin I: 6.62 ng/L (record clinical_event_c3d8d13ea17be25deda1630e6c6379cd). Prior problem documentation is incomplete; absence of a record does not exclude disease. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2024-05-31T20:05:00Z to 2024-05-31T22:35:00Z; acuity 5; HOME; diagnosis R079; episode episode_4ef8d39299fb2f31a20ea9cf7dfc6f12; predecessor encounter_version_63d7a8e29975c83e1a384d427ec21193.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2024-05-31T22:35:00Z: Care assessment: Cassie Piotrowski, age 43. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 98.31 % (record clinical_event_8836775fe9eb47fa543db7d3f819855e). Heart rate: 112.75 /min (record clinical_event_7ff99193d59eeb02de660e7e1c240071). Troponin I: 3.62 ng/L (record clinical_event_2cc2b82e1e4195dda66cf7cb26f9b7ab). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2025-01-12T02:10:00Z to 2025-01-12T04:36:00Z; acuity 5; HOME; diagnosis R079; episode episode_119901b79af0f19f978df2cc8a8deedf; predecessor encounter_version_15dfaf0b368f4079fcc79df3d0430109.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-01-12T04:36:00Z: Care assessment: Cassie Piotrowski, age 44. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.92 % (record clinical_event_01dd5c92776ec66e9cff0e1f254674a4). Heart rate: 103.75 /min (record clinical_event_47fe6f4616eb7f7f8ca9684c22fe49f1). Troponin I: 2.66 ng/L (record clinical_event_173a96cb6049a077b3193c5d6144e5fe). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2025-01-24T13:50:00Z to 2025-01-29T09:50:00Z; acuity 3; HOME; diagnosis K8010; episode episode_40317bac4ed2420c979bf4444402e9bb; predecessor encounter_version_1825f47b014f3bfe3dbe2f2ead024dc4.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=13, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2025-01-24T23:50:00Z: Encounter review: Cassie Piotrowski, age 44. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 8.00 1 (record clinical_event_5a8af79cd6192b5609c47baeb2e9fbc5). Heart rate: 93.25 /min (record clinical_event_3c19c31242c03d0183860f0697f5b06f). Hemoglobin: 14.50 g/dL (record clinical_event_6ac3239d3d469b903af01fe193dc5441). Creatinine: 1.06 mg/dL (record clinical_event_db2d0b9dbc2d8a49d18d946464018d85). Prior problem documentation is incomplete; absence of a record does not exclude disease. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_65accf71696d091cd2e8c22be58f05bb). Acetaminophen 650 mg administered (record clinical_event_0696445ab22da8f6fdfac1d7ff115fa3). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-01-29T09:50:00Z: Patient review: Cassie Piotrowski, age 44. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 14.50 g/dL (record clinical_event_6ac3239d3d469b903af01fe193dc5441). Hemoglobin: 13.80 g/dL (record clinical_event_fdf57b4a9c9583401c3e97f37deec88c). Creatinine: 1.06 mg/dL (record clinical_event_db2d0b9dbc2d8a49d18d946464018d85). Creatinine: 1.03 mg/dL (record clinical_event_ae6b4d62709a5804261fe157b26aa860). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 650 mg administered (record clinical_event_ce3fbb31a1317d818b1549aa4fe6caca). Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2025-03-06T18:38:00Z to 2025-03-06T21:13:00Z; acuity 4; HOME; diagnosis R079; episode episode_d0dd553896e3995e89c6b537d45eecdc; predecessor encounter_version_3090eb6bb22d6c507726a6d11165f27b.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-03-06T21:13:00Z: Encounter review: Cassie Piotrowski, age 44. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 96.18 % (record clinical_event_f4a186f9dd48163b2026af3bd017269f). Heart rate: 100.50 /min (record clinical_event_777291217e30de6d8334910f6d81dc4c). Troponin I: 4.88 ng/L (record clinical_event_292cd716652d1445b338cb12deb5b4ed). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2025-10-28T17:17:00Z to 2025-10-28T20:06:00Z; acuity 3; HOME; diagnosis R079; episode episode_a6023411261b1fba8641cd9c11bcfa92; predecessor encounter_version_11b752c5bae83664b1861462955bfa90.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-10-28T20:06:00Z: Patient review: Cassie Piotrowski, age 45. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 96.63 % (record clinical_event_480aa16c9ab3f6c7596d0bf9e379d8e4). Heart rate: 108.25 /min (record clinical_event_3f103b1f58eb88095215ab5d10f0832c). Troponin I: 2.18 ng/L (record clinical_event_62328787ad596c96cca72bfd04f85ecf). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 24: John Brooks

Stable patient: patient_5825b3cfce7ec6afc2a6f7f064ddba18; birth date 1963-04-25; strata: acuity/5, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/R079, repeat/False, service/ED, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2024-06-17T21:59:00Z to 2024-06-18T00:36:00Z; acuity 5; HOME; diagnosis R079; episode episode_fd79ef785afe33006e959824ff5c03e5; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2024-06-18T00:36:00Z: Encounter review: John Brooks, age 61. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 96.45 % (record clinical_event_b46898a1c371b583c5c8f17e6a8cde7a). Heart rate: 111.00 /min (record clinical_event_3ed8196e490ccd1758c703e95be1ebed). Troponin I: 4.58 ng/L (record clinical_event_18de0bfbeb18a9cb49eeaec8fb42d0e6). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 25: Martin Boston

Stable patient: patient_be09cc526c37de4a69dada0068213d52; birth date 1968-07-09; strata: acuity/3, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/R079, pathway/R1010, repeat/True, service/ED, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2024-07-15T19:58:00Z to 2024-07-15T22:06:00Z; acuity 3; HOME; diagnosis R079; episode episode_d685098341a5390279a542c6806b59bc; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2024-07-15T22:06:00Z: Interval assessment: Martin Boston, age 56. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.38 % (record clinical_event_c35aba18849c29edd1bff5ec1e08230c). Heart rate: 103.50 /min (record clinical_event_4104e2b1814cfd102d837a0f97397bd7). Troponin I: 5.48 ng/L (record clinical_event_84cc067d06776d31ce001816a63db540). Previously recorded problems: Chronic kidney disease, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- OPD 2024-08-12T16:21:00Z to 2024-08-12T17:00:00Z; acuity 3; HOME; diagnosis R1010; episode episode_b88de9077340e4e7f02aa65a4c0f89ac; predecessor encounter_version_6230ce70380ca9be55ea6f2d153355fd.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  OP_NOTE @ 2024-08-12T17:00:00Z: Care assessment: Martin Boston, age 56. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.30 % (record clinical_event_cb53d5dc52499e6987fe538e624e1243). Heart rate: 77.40 /min (record clinical_event_d3ae24219950ab852856c23a20ae19df). Previously recorded problems: Chronic kidney disease, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- OPD 2025-06-16T15:35:00Z to 2025-06-16T17:28:00Z; acuity 3; HOME; diagnosis R1010; episode episode_ce5edb02621bdff758f255d9581f2035; predecessor encounter_version_fa45265fb2310cc25b3f9317555680cd.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  OP_NOTE @ 2025-06-16T17:28:00Z: Clinical review: Martin Boston, age 56. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.26 % (record clinical_event_138459ca12036174a34a53558c144034). Heart rate: 85.50 /min (record clinical_event_7790d4484160f089a4a85b25a4b08641). Hemoglobin: 13.78 g/dL (record clinical_event_6337a6225c36fd41d1f3f85c7a19f76d). Previously recorded problems: Chronic kidney disease, unspecified. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_ccd3fd129db7eb168dbde80585690f91). The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 26: Matthew Haslam

Stable patient: patient_1379f2c65500fa688e8283ba15bf92a3; birth date 1974-10-12; strata: acuity/3, age/35-49, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/J449, repeat/True, service/ED, service/IPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- ED 2024-01-23T11:32:00Z to 2024-01-23T15:32:00Z; acuity 3; TRANSFER; diagnosis J449; episode episode_e440b446f58248a9431daa56f74398bc; predecessor none.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=1.
  Treatment evidence: Prednisone 200 mg PO COMPLETED.

  ED_NOTE @ 2024-01-23T15:32:00Z: Care assessment: Matthew Haslam, age 49. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 93.93 % (record clinical_event_533ba25081f7728d6099c0f70b65a82e). Heart rate: 93.00 /min (record clinical_event_125ad76a1c622da3bdb2aa6347a8a2f9). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Prednisone 200 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_327369b2f8f64e086cd3d5953514632b). Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2024-01-23T15:32:00Z to 2024-01-28T03:32:00Z; acuity 3; HOME; diagnosis J449; episode episode_e440b446f58248a9431daa56f74398bc; predecessor encounter_version_e953af6d5c96a78fe7f3b3d0a16c357b.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=5, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Prednisone 40 mg PO COMPLETED; Prednisone 40 mg PO COMPLETED.

  PROGRESS_NOTE @ 2024-01-23T19:32:00Z: Interval assessment: Matthew Haslam, age 49. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 94.17 % (record clinical_event_5716bcf542e219eef7073c8cd2fe1772). Respiratory rate: 24.40 /min (record clinical_event_92d1ce56a972398128ecdb60afdb65bf). White blood cell count: 14.18 10*3/uL (record clinical_event_aaa34df7cd0a4fe8320020783e0e01b0). Bicarbonate: 29.37 mmol/L (record clinical_event_aa1a391adf5ca67084e9a955a6e943e6). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Prednisone 40 mg administered (record clinical_event_d0dc9a1a5e16a85c00f850b0b84494d2). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2024-01-28T03:32:00Z: Patient review: Matthew Haslam, age 49. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. White blood cell count: 14.18 10*3/uL (record clinical_event_aaa34df7cd0a4fe8320020783e0e01b0). White blood cell count: 8.83 10*3/uL (record clinical_event_eb84827a013dab0675e0b656aa676a97). Bicarbonate: 29.37 mmol/L (record clinical_event_aa1a391adf5ca67084e9a955a6e943e6). Bicarbonate: 28.37 mmol/L (record clinical_event_588b5f3db2ec49e002ff65f930afcf24). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Prednisone 40 mg administered (record clinical_event_de9fb60cd5a25590e5dd89e7ee540049). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 27: Joyce Corrigan

Stable patient: patient_68f49343b4223f3ffefbfdc50d309b52; birth date 1954-05-23; strata: acuity/2, acuity/5, age/65-79, carry/False, long-stay/False, outcome/HOME, pathway/J449, pathway/K8010, pathway/R079, repeat/True, service/ED, service/IPD, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- OPD 2022-12-23T06:00:00Z to 2022-12-23T08:00:00Z; acuity 5; HOME; diagnosis J449; episode episode_ae954fc208de693eca4d0f81ca607763; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2022-12-23T08:00:00Z: Interval assessment: Joyce Corrigan, age 68. Interval follow-up for increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 95.52 % (record clinical_event_b3f6262819ac22a2c448b7d73b4ce2da). Heart rate: 85.50 /min (record clinical_event_d7e3792112baee9b0ebc5348c422f864). White blood cell count: 12.88 10*3/uL (record clinical_event_acb6ecd6953a3295071fde135e798687). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2023-12-01T13:20:00Z to 2023-12-05T21:20:00Z; acuity 2; HOME; diagnosis K8010; episode episode_20c9c0afdbceabafa43263c3ed8d54a8; predecessor encounter_version_9666de62a384a9211f39e8fcd62017b5.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=14, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2023-12-01T23:20:00Z: Assessment update: Joyce Corrigan, age 69. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 5.00 1 (record clinical_event_09911fe80f3d10b87690d2b14dda6acb). Heart rate: 91.25 /min (record clinical_event_1f5b314617887a2a0cc76dd986483474). Hemoglobin: 13.45 g/dL (record clinical_event_26d647c788a312daf7b900123d52abfc). Creatinine: 1.08 mg/dL (record clinical_event_f750000f3e2f2353ca627fbfe96dd586). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_c1286fff26369b372bbba20ad33ee947). Acetaminophen 650 mg administered (record clinical_event_8a103e7c9feef2f046c8fbd9c23890b1). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-12-05T21:20:00Z: Encounter review: Joyce Corrigan, age 69. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 13.45 g/dL (record clinical_event_26d647c788a312daf7b900123d52abfc). Hemoglobin: 12.75 g/dL (record clinical_event_0ddcb152b47210404cb7ae89fb27115c). Creatinine: 1.08 mg/dL (record clinical_event_f750000f3e2f2353ca627fbfe96dd586). Creatinine: 1.06 mg/dL (record clinical_event_d21f8da13faacf6bea2497539d11eb12). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Acetaminophen 650 mg administered (record clinical_event_1fbcc621528e6adf1ad0b333e031575a). Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2024-10-22T18:29:00Z to 2024-10-22T19:50:00Z; acuity 5; HOME; diagnosis R079; episode episode_9a1423697629cbd175aa9d5d24e3916e; predecessor encounter_version_93ff38207684570bf842ec6fdf407cdf.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2024-10-22T19:50:00Z: Assessment update: Joyce Corrigan, age 70. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.67 % (record clinical_event_21c6cc01e3d3b5cbc04347db7993b613). Heart rate: 76.35 /min (record clinical_event_c301aa9af4e0b52e986b5922a5ad1828). Troponin I: 4.58 ng/L (record clinical_event_2cca825e0da9ede402a7902c367d47f1). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2025-01-25T01:30:00Z to 2025-01-25T03:36:00Z; acuity 5; HOME; diagnosis R079; episode episode_1bf2a7535758af3f27b9c13651f5f515; predecessor encounter_version_c1b779a2cc4642b855c7b1a69bc6b57a.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-01-25T03:36:00Z: Patient review: Joyce Corrigan, age 70. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 98.73 % (record clinical_event_3c143ace34c9be925e632251a05e983b). Heart rate: 113.00 /min (record clinical_event_f81844988f2f984b9b026b37fbf7ad58). Troponin I: 2.12 ng/L (record clinical_event_c8d5b22fa706d7c5b7f33bde65fbd6f2). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 28: Glenda Kim

Stable patient: patient_efc27cbc77521bb4677b3a43ec6cee7a; birth date 1941-10-01; strata: acuity/2, acuity/3, acuity/4, age/80+, carry/False, long-stay/False, outcome/HOME, pathway/K8010, pathway/R079, repeat/True, service/IPD, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- OPD 2023-01-18T15:43:00Z to 2023-01-18T16:34:00Z; acuity 3; HOME; diagnosis R079; episode episode_7f3ba4efeb8e491134df44b06b77b186; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2023-01-18T16:34:00Z: Clinical review: Glenda Kim, age 81. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.08 % (record clinical_event_4dcaca565a163d153481fadf362fae66). Heart rate: 82.35 /min (record clinical_event_84bbb2c6dd78397b85a407af2ab17f20). Previously recorded problems: Hyperlipidemia, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- IPD 2024-11-21T14:01:00Z to 2024-11-26T12:01:00Z; acuity 2; HOME; diagnosis K8010; episode episode_f88e94df665266405b2f0c5440c79bed; predecessor encounter_version_4999cc451b77b0f6c2150c3d81e93f9e.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=14, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2024-11-22T00:01:00Z: Assessment update: Glenda Kim, age 83. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 7.00 1 (record clinical_event_f467470fda802a17c32909b872d87f12). Heart rate: 97.25 /min (record clinical_event_7125ae3461613a4fa5b2999f73285b43). Hemoglobin: 14.48 g/dL (record clinical_event_865586265af79ae0cc6c8df6a82e86ea). Creatinine: 0.96 mg/dL (record clinical_event_e32bebd1d410315febb5029a7ff234b4). Previously recorded problems: Hyperlipidemia, unspecified. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_7991f3018b1388f35b5910c6ca30155c). Acetaminophen 650 mg administered (record clinical_event_15e817f24f076378214ee3c6006390ff). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2024-11-26T12:01:00Z: Encounter review: Glenda Kim, age 83. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 14.48 g/dL (record clinical_event_865586265af79ae0cc6c8df6a82e86ea). Hemoglobin: 13.78 g/dL (record clinical_event_f00fd198820d72af6ad7a5e94ff3a555). Creatinine: 0.96 mg/dL (record clinical_event_e32bebd1d410315febb5029a7ff234b4). Creatinine: 0.89 mg/dL (record clinical_event_6580374c235870018a19fcb8342c386e). Previously recorded problems: Hyperlipidemia, unspecified. Acetaminophen 650 mg administered (record clinical_event_ea5a14e3039b85b411fecb91e9d1bc3f). Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2025-12-01T15:17:00Z to 2025-12-01T16:54:00Z; acuity 4; HOME; diagnosis R079; episode episode_95d54a5baae84f855954bf3006dd00b0; predecessor encounter_version_e04abdb50cc3961c5a3cf24a256fd228.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2025-12-01T16:54:00Z: Interval assessment: Glenda Kim, age 84. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.94 % (record clinical_event_d0b8bbdc034c67d8d43a1012048e9235). Heart rate: 81.30 /min (record clinical_event_eebf953f808e3161c24bd9c73a39b2b6). Troponin I: 4.28 ng/L (record clinical_event_b0691b3ac83686bce774621d67c13c4b). Previously recorded problems: Hyperlipidemia, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 29: David Ward

Stable patient: patient_f7f90a0b1743af1218cb2e76090ea1ae; birth date 1975-06-15; strata: acuity/3, acuity/5, age/35-49, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/M1711, pathway/R079, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2023-04-26T04:01:00Z to 2023-04-26T06:31:00Z; acuity 5; HOME; diagnosis R1010; episode episode_c1912315366b1f8ac5cffb4f5ccc9bb7; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2023-04-26T06:31:00Z: Interval assessment: David Ward, age 47. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 98.16 % (record clinical_event_84690ae9f5d7143f3059d23635d87508). Heart rate: 108.50 /min (record clinical_event_6ff4c79d29c980f66d077c112e029feb). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2024-01-17T07:01:00Z to 2024-01-17T09:15:00Z; acuity 3; HOME; diagnosis R079; episode episode_759d106f28be7a2b212e5fae8b6adad0; predecessor encounter_version_2d07c9d4e8f4947ca86a0abc9af5a15b.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2024-01-17T09:15:00Z: Clinical review: David Ward, age 48. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 98.52 % (record clinical_event_0c42ce4b53effc97ff6e7ed8938b06f8). Heart rate: 91.00 /min (record clinical_event_9977fef9bc85fd9da35fb1179539f5ed). Troponin I: 7.34 ng/L (record clinical_event_e294955a97b5aac250961be864473bee). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2025-01-27T14:32:00Z to 2025-01-31T15:32:00Z; acuity 3; HOME; diagnosis M1711; episode episode_ba95aa46a5b71d6c5a2035b7f85bd2e9; predecessor encounter_version_c55cbdd140c057b5b691dcd61d6197ed.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=12, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2025-01-28T00:32:00Z: Care assessment: David Ward, age 49. Presenting concern: right knee osteoarthritis limiting mobility. Working assessment: Unilateral primary osteoarthritis, right knee. Pain numeric rating: 6.00 1 (record clinical_event_69f6c40b0583738f3a143c99dfdb69a3). Mobility assessment: 1.00 1 (record clinical_event_b6aaeb8d3007055194ef449384b6e80c). Hemoglobin: 13.84 g/dL (record clinical_event_953ac9b5b47472eeb4af547a3cd7b5ff). Creatinine: 1.17 mg/dL (record clinical_event_1e349d5c038695cd47608523ea7b86ac). Prior problem documentation is incomplete; absence of a record does not exclude disease. Procedure documented: Replacement of Right Knee Joint with Synthetic Substitute, Cemented, Open Approach (record clinical_event_b0998872ebaff5929c0826f2a7b07322). Acetaminophen 650 mg administered (record clinical_event_f2c31b7b5a093baf19fc69b65485718e). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-01-31T15:32:00Z: Care assessment: David Ward, age 49. Presenting concern: right knee osteoarthritis limiting mobility. Working assessment: Unilateral primary osteoarthritis, right knee. Hemoglobin: 13.84 g/dL (record clinical_event_953ac9b5b47472eeb4af547a3cd7b5ff). Hemoglobin: 13.14 g/dL (record clinical_event_296ea010794adfb1ac2998c45b9c564a). Creatinine: 1.17 mg/dL (record clinical_event_1e349d5c038695cd47608523ea7b86ac). Creatinine: 0.93 mg/dL (record clinical_event_0aaaaa0fb87047ae12eec30f5615831a). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 650 mg administered (record clinical_event_de07b7ea6d7f0995070ecb313c893756). Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2025-08-18T17:19:00Z to 2025-08-18T17:54:00Z; acuity 3; HOME; diagnosis R1010; episode episode_d8c49620e9562151b31a3b9662e78266; predecessor encounter_version_cb9344c9b9b1d0ba077669e2235d07b5.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  OP_NOTE @ 2025-08-18T17:54:00Z: Care assessment: David Ward, age 50. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.95 % (record clinical_event_7b80acc0eabdda9abed87077d2148416). Heart rate: 76.80 /min (record clinical_event_2fbdce85bf1a9e9c740ce9d10174acc3). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 30: Glen Carlson

Stable patient: patient_37cc8a1a790af36dcfab8b1a70579ff3; birth date 1982-01-16; strata: acuity/3, acuity/4, acuity/5, age/35-49, carry/False, long-stay/False, outcome/HOME, pathway/K8010, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- OPD 2023-09-20T16:40:00Z to 2023-09-20T17:39:00Z; acuity 5; HOME; diagnosis R1010; episode episode_bf8bccb34a19e888aaa8c3a6a23a6355; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  OP_NOTE @ 2023-09-20T17:39:00Z: Clinical review: Glen Carlson, age 41. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.17 % (record clinical_event_638b18b1398d419585e549fce10c1d71). Heart rate: 85.35 /min (record clinical_event_f3edd9d88bcd3ba7b789e930359a3cb2). Hemoglobin: 14.35 g/dL (record clinical_event_c56d23dd6a83c79a5e6264e45d7c8a8c). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_bccd45b488554886ad0f3d49f3d1eb2c). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- IPD 2024-07-10T13:43:00Z to 2024-07-15T02:43:00Z; acuity 3; HOME; diagnosis K8010; episode episode_8ae7254eb695f53fe1f99a83db9f0af0; predecessor encounter_version_1c648414dc7f0e9b3e14a653fac5e0d1.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=15, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2024-07-10T23:43:00Z: Encounter review: Glen Carlson, age 42. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 8.00 1 (record clinical_event_79cd8a0a458f13dab1a96cb8014f00da). Heart rate: 111.00 /min (record clinical_event_3d938ca23cef45995bea729a4972a37b). Hemoglobin: 14.17 g/dL (record clinical_event_bd3a464ceda9c8df0472081eb70487f3). Creatinine: 1.04 mg/dL (record clinical_event_3641e4988430126d720fbf3f353fe274). Prior problem documentation is incomplete; absence of a record does not exclude disease. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_9da0d47b2c934e5b096448bc2d12ca08). Acetaminophen 650 mg administered (record clinical_event_10a9835f64cbad4f380b7611c743d1e9). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2024-07-15T02:43:00Z: Care assessment: Glen Carlson, age 42. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 14.17 g/dL (record clinical_event_bd3a464ceda9c8df0472081eb70487f3). Hemoglobin: 13.47 g/dL (record clinical_event_e80092e23324ae617cefce04544c93af). Creatinine: 1.04 mg/dL (record clinical_event_3641e4988430126d720fbf3f353fe274). Creatinine: 0.83 mg/dL (record clinical_event_486da0106f9e25ad0e0c9458c7d5ba3b). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 650 mg administered (record clinical_event_d9a865983e171f310ba0008a5d167d9a). Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2025-07-19T11:33:00Z to 2025-07-19T14:11:00Z; acuity 4; HOME; diagnosis R1010; episode episode_0dd418bacad36a4c8e6b4130b5095fa2; predecessor encounter_version_60410301078593e30cc74eabdc79bbd9.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=1.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  ED_NOTE @ 2025-07-19T14:11:00Z: Encounter review: Glen Carlson, age 43. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.23 % (record clinical_event_b724658b93eb06dd2bd4909c32ebc9ef). Heart rate: 92.00 /min (record clinical_event_d586f3af57441298b8e6ddccb8027ddf). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_dd32c0dcec2ae2a32d72d4368a1e8777). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 31: Ann Sams

Stable patient: patient_b7e27971a36dc50f0f2fb8f433a39b24; birth date 1932-09-15; strata: acuity/3, age/80+, carry/False, long-stay/False, outcome/HOME, pathway/R1010, repeat/False, service/ED, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- ED 2023-05-31T13:53:00Z to 2023-05-31T16:39:00Z; acuity 3; HOME; diagnosis R1010; episode episode_822e70adf2f4a30d697d628c1df3041e; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2023-05-31T16:39:00Z: Clinical review: Ann Sams, age 90. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.50 % (record clinical_event_7f97eb718b489e7692f7f75c182015fe). Heart rate: 98.00 /min (record clinical_event_7beabc653a9f5ee93f837a1dd0213d37). Hemoglobin: 13.82 g/dL (record clinical_event_327fb4b10130d297212a6c119922e374). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 32: Linda Ready

Stable patient: patient_42c79ce56e6bf8c0089e9233c16c2af4; birth date 1956-08-12; strata: acuity/2, acuity/3, acuity/4, age/65-79, carry/False, long-stay/False, outcome/HOME, pathway/K8010, pathway/R079, pathway/R1010, repeat/True, service/ED, service/IPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2023-02-01T08:14:00Z to 2023-02-01T10:08:00Z; acuity 4; HOME; diagnosis R079; episode episode_2499360b1d7739f851328b0d83a4f111; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2023-02-01T10:08:00Z: Clinical review: Linda Ready, age 66. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 96.45 % (record clinical_event_f77af99aa359bc66587894298d8f7cf1). Heart rate: 90.00 /min (record clinical_event_75e9a77d78395578c1a3a473274c5d93). Troponin I: 4.52 ng/L (record clinical_event_a5903366a7219503e48edea428384127). Prior problem documentation is incomplete; absence of a record does not exclude disease. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2025-08-11T13:19:00Z to 2025-08-11T16:15:00Z; acuity 3; HOME; diagnosis R1010; episode episode_d40a2a20175edac678a5f5c0d309d093; predecessor encounter_version_bcd68b83ea8a18115f9ab5f2a9a985b5.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-08-11T16:15:00Z: Clinical review: Linda Ready, age 68. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 98.64 % (record clinical_event_eb90732e975fdeb121cce1c58f5cb871). Heart rate: 114.25 /min (record clinical_event_ab338c8c99d960804d4fa4aeb8880713). Hemoglobin: 14.01 g/dL (record clinical_event_c0ebecb0f881925a3ede722a44cf678a). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2025-12-11T14:14:00Z to 2025-12-14T19:14:00Z; acuity 2; HOME; diagnosis K8010; episode episode_2c53f26b8063f43890f4c828ddbca9ff; predecessor encounter_version_7f0f1f65acc451a5c8827c3c45153562.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=9, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2025-12-12T00:14:00Z: Encounter review: Linda Ready, age 69. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 8.00 1 (record clinical_event_7a92c355ffb40bfddc8485598023244c). Heart rate: 106.00 /min (record clinical_event_7f96eb8f3a96f262cabec223afb4a289). Hemoglobin: 13.99 g/dL (record clinical_event_acfe8f262f2304ae66f5c1baf7b8bda7). Creatinine: 1.02 mg/dL (record clinical_event_254be8a05b36b53130cf13089540e28b). Prior problem documentation is incomplete; absence of a record does not exclude disease. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_b34e78c341e8062d56b454b8c0742b1b). Acetaminophen 650 mg administered (record clinical_event_fc94b0af77399928da3acc697c08b6e4). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-12-14T19:14:00Z: Clinical review: Linda Ready, age 69. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 13.99 g/dL (record clinical_event_acfe8f262f2304ae66f5c1baf7b8bda7). Hemoglobin: 13.29 g/dL (record clinical_event_2943cbcec861cd1e725292b155bb0b32). Creatinine: 1.02 mg/dL (record clinical_event_254be8a05b36b53130cf13089540e28b). Creatinine: 0.86 mg/dL (record clinical_event_2dfff48ab4c097ec1b2d3eff6127c0a9). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 650 mg administered (record clinical_event_6a54ef330618a8ed04fd6bc6a65a9610). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 33: Jeffrey Martinez

Stable patient: patient_3176af2f1eed6a7abec267b80fb4eb2c; birth date 1964-08-22; strata: acuity/5, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/R1010, repeat/False, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- OPD 2023-07-14T21:34:00Z to 2023-07-14T23:06:00Z; acuity 5; HOME; diagnosis R1010; episode episode_2ec8f03928b12cc68480321ad753afa6; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2023-07-14T23:06:00Z: Patient review: Jeffrey Martinez, age 58. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.06 % (record clinical_event_1ec73513ac2cfbc6e568d068d53ade93). Heart rate: 74.55 /min (record clinical_event_894ac3d51616729cd4900c1151fcdb4b). Hemoglobin: 13.81 g/dL (record clinical_event_6e770d467d03b495ebd84362572b3ba2). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 34: Glenn Gulledge

Stable patient: patient_4cd1c14781b748a76325a4854bb48bc3; birth date 1961-12-24; strata: acuity/4, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/R079, repeat/False, service/OPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- OPD 2024-07-22T14:52:00Z to 2024-07-22T16:27:00Z; acuity 4; HOME; diagnosis R079; episode episode_c31899e1e47605079e25b421ca1a9945; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2024-07-22T16:27:00Z: Encounter review: Glenn Gulledge, age 62. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.41 % (record clinical_event_b575f1f0aafcdda772e57b1e600eef48). Heart rate: 78.90 /min (record clinical_event_7fd1208780a25ecdc02eae5860c3388e). Troponin I: 3.86 ng/L (record clinical_event_bd19ed095f2b5ef69c894fe4c4c20e59). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 35: Nettie Gonzalez

Stable patient: patient_df747832044d2aca075b3bc4ffc8b12d; birth date 1938-12-02; strata: acuity/4, age/80+, carry/False, long-stay/False, outcome/HOME, pathway/R079, repeat/False, service/OPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- OPD 2023-12-20T21:24:00Z to 2023-12-20T22:53:00Z; acuity 4; HOME; diagnosis R079; episode episode_24e92d1fda9db1e1534716cf662660ab; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2023-12-20T22:53:00Z: Encounter review: Nettie Gonzalez, age 85. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.54 % (record clinical_event_0c7eec04ee4d740561c8dd5cc903b67b). Heart rate: 84.15 /min (record clinical_event_8c33757954cbaa8c43774781bccf1aa1). Troponin I: 3.68 ng/L (record clinical_event_524361049194bd19ef4e8720baa657e9). Previously recorded problems: Hyperlipidemia, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 36: Erica Meisner

Stable patient: patient_1b7d146a3eba62b0b89cf6a52278879a; birth date 1987-01-04; strata: acuity/5, age/35-49, carry/False, long-stay/False, outcome/HOME, pathway/R079, repeat/False, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- OPD 2025-10-29T17:54:00Z to 2025-10-29T18:35:00Z; acuity 5; HOME; diagnosis R079; episode episode_96a1d598f170717ddfdbc7aac0a0e566; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2025-10-29T18:35:00Z: Patient review: Erica Meisner, age 38. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.78 % (record clinical_event_233db89c68288433864abdbd32e82e7d). Heart rate: 78.90 /min (record clinical_event_9eed6a533cceae59dff344ecd5d85e5c). Prior problem documentation is incomplete; absence of a record does not exclude disease. The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 37: Thomas Espinoza

Stable patient: patient_b4a207e7bd2fb6c74ca02d1f32ddc8bf; birth date 1962-09-21; strata: acuity/5, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/E119, repeat/False, service/ED, site/facility_7990133218ef060b178c3cf8a0825f76.

- ED 2025-04-14T23:44:00Z to 2025-04-15T01:49:00Z; acuity 5; HOME; diagnosis E119; episode episode_a43f9b0fe8cd12b1f81e3e5f2f9592cf; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-04-15T01:49:00Z: Patient review: Thomas Espinoza, age 62. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 96.51 % (record clinical_event_89aff307f3e8b742e3ad1d1f06b08850). Heart rate: 107.75 /min (record clinical_event_d136712f7065815fa096f19a5aa7eae4). Serum glucose: 298.10 mg/dL (record clinical_event_bdeca03f3804d37854f515293ba28f29). Previously recorded problems: Type 2 diabetes mellitus without complications. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 38: Michael Campbell

Stable patient: patient_808a5462a33c32937ac5dea9b059b131; birth date 1975-12-27; strata: acuity/4, acuity/5, age/35-49, carry/False, long-stay/False, outcome/HOME, pathway/R079, pathway/R1010, repeat/True, service/ED, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- OPD 2023-11-22T14:13:00Z to 2023-11-22T15:51:00Z; acuity 4; HOME; diagnosis R079; episode episode_ee47573512fac4f68a8a09e591e9432d; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2023-11-22T15:51:00Z: Assessment update: Michael Campbell, age 47. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.12 % (record clinical_event_dbea456ed24f4f606fbf82d7e6c3b4de). Heart rate: 76.50 /min (record clinical_event_e6eacbd02f583b22b62cdabe3c2ec793). Troponin I: 3.50 ng/L (record clinical_event_c2140779402a2f157811b0f10701f45c). Prior problem documentation is incomplete; absence of a record does not exclude disease. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2025-01-01T02:44:00Z to 2025-01-01T04:37:00Z; acuity 5; HOME; diagnosis R079; episode episode_f3250f2cf47c5c4f17e679003fab4310; predecessor encounter_version_0dcd6a680503eaac130e24713e58a198.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-01-01T04:37:00Z: Care assessment: Michael Campbell, age 49. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.71 % (record clinical_event_2b7662c11de8962a8cf93a6c392ea52b). Heart rate: 108.50 /min (record clinical_event_9eb05992667eebe3a7dc661499821c55). Troponin I: 4.22 ng/L (record clinical_event_5a25bf2bb1192d75099fe335303d9f5d). Prior problem documentation is incomplete; absence of a record does not exclude disease. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- OPD 2025-10-15T21:39:00Z to 2025-10-15T22:29:00Z; acuity 4; HOME; diagnosis R1010; episode episode_566358d56aed87242c9c495f6278012a; predecessor encounter_version_1562afa147cbbdb89c14804ea884cff4.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2025-10-15T22:29:00Z: Encounter review: Michael Campbell, age 49. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.87 % (record clinical_event_45d24f642c30d2ff8fcdf11a3b9f8eda). Heart rate: 82.80 /min (record clinical_event_8c42e2f5a2e910295cd4f5cba88c21f5). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 39: Susan McGregor

Stable patient: patient_fa8c7668d2274518a77e053689222d1d; birth date 1953-03-04; strata: acuity/3, acuity/5, age/65-79, carry/False, long-stay/False, outcome/HOME, pathway/J189, pathway/R079, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- OPD 2023-08-17T21:22:00Z to 2023-08-17T22:05:00Z; acuity 3; HOME; diagnosis R1010; episode episode_082c35dfd39e52c9d9bb5567e2778a75; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2023-08-17T22:05:00Z: Patient review: Susan McGregor, age 70. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.74 % (record clinical_event_22fe92f6d30ce5495d4cd8829740efaf). Heart rate: 81.60 /min (record clinical_event_f5a40181cc2391ca6e3e05924288d763). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2024-03-26T05:02:00Z to 2024-03-26T07:47:00Z; acuity 5; HOME; diagnosis R079; episode episode_84c8e24340ba83f3838e5e60ae4a356e; predecessor encounter_version_a6916c577dda73d2eff5962c27867e80.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2024-03-26T07:47:00Z: Patient review: Susan Tingley, age 71. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.56 % (record clinical_event_390268ee90c1acb41b3aa432dafc7653). Heart rate: 112.50 /min (record clinical_event_41bf1143fc3c6ea8741fd822521b60d4). Troponin I: 7.40 ng/L (record clinical_event_a47d59253935fadabdb6beb363307fdd). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2025-06-24T11:10:00Z to 2025-06-30T19:10:00Z; acuity 3; HOME; diagnosis J189; episode episode_20d9fafc210b153b74f4fabfd13e40e4; predecessor encounter_version_2a5283d2b5cbb3c74ca305030e6ec7a5.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=13, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Doxycycline 100 mg PO COMPLETED; Doxycycline 100 mg PO COMPLETED.

  PROGRESS_NOTE @ 2025-06-24T15:10:00Z: Clinical review: Susan Tingley, age 72. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Body temperature: 38.87 Cel (record clinical_event_5a0a87e0dad3262f7e17bddbfe1cf3ac). Oxygen saturation: 94.05 % (record clinical_event_233a4790f6cb4b0afc47c2287fadecea). White blood cell count: 19.01 10*3/uL (record clinical_event_9f03a79c81c3eefca9aa47a364519ae5). C-reactive protein: 136.14 mg/L (record clinical_event_af83ce3a82042546b64fe9dc90fd60f5). Prior problem documentation is incomplete; absence of a record does not exclude disease. Doxycycline 100 mg administered (record clinical_event_8491591b72a66ed1d20160315997ad15). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-06-30T19:10:00Z: Encounter review: Susan Tingley, age 72. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. White blood cell count: 19.01 10*3/uL (record clinical_event_9f03a79c81c3eefca9aa47a364519ae5). White blood cell count: 9.88 10*3/uL (record clinical_event_edd4b637fafb97f711f73ace4056d024). C-reactive protein: 136.14 mg/L (record clinical_event_af83ce3a82042546b64fe9dc90fd60f5). C-reactive protein: 11.04 mg/L (record clinical_event_a3c186d95ab756469985366247879ada). Prior problem documentation is incomplete; absence of a record does not exclude disease. Doxycycline 100 mg administered (record clinical_event_aa2507fd33347aa5d061a898b2b789d7). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 40: Kelly Brice

Stable patient: patient_7b35abef4bfa6622725c33e9afe2352c; birth date 1997-12-03; strata: acuity/2, acuity/3, age/18-34, carry/False, long-stay/False, outcome/HOME, pathway/E119, pathway/R079, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- ED 2024-12-12T01:41:00Z to 2024-12-12T04:14:00Z; acuity 3; HOME; diagnosis R079; episode episode_1e0e2364349be0f8a269e3e13d5661f9; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2024-12-12T04:14:00Z: Clinical review: Kelly Brice, age 27. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 96.48 % (record clinical_event_368d364f2103a9ee798ebd5744712463). Heart rate: 96.75 /min (record clinical_event_a9eac09e3968e10269f0254ee474bc2c). Troponin I: 2.84 ng/L (record clinical_event_4ea98ad945a647fb842c9e17bd8551ae). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- OPD 2024-12-30T17:13:00Z to 2024-12-30T18:59:00Z; acuity 3; HOME; diagnosis R1010; episode episode_ab7ddab7c952c055c5c03d41519f507e; predecessor encounter_version_4b3ce0927163f5aa9e61168c88917cb1.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2024-12-30T18:59:00Z: Interval assessment: Kelly Brice, age 27. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.05 % (record clinical_event_d588f852c4d817faba872ed5769826d2). Heart rate: 86.70 /min (record clinical_event_faf90e2440a72a74762d1cc8177e26c3). Hemoglobin: 14.07 g/dL (record clinical_event_7e829f8fca64f6c9d80ed2e82968403d). Prior problem documentation is incomplete; absence of a record does not exclude disease. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- IPD 2025-11-23T07:30:00Z to 2025-11-27T11:30:00Z; acuity 2; HOME; diagnosis E119; episode episode_af5233432b7253cf565c8beb04fc6897; predecessor encounter_version_98e5a768b9075f2b8a12a6889753b7fd.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, OBSERVATION=4, ORDER=3, PROCEDURE=1.

  PROGRESS_NOTE @ 2025-11-23T11:30:00Z: Clinical review: Kelly Brice, age 27. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Capillary glucose: 321.20 mg/dL (record clinical_event_eef1a78d3cfc72f79059b5a0938e9f2f). Heart rate: 113.00 /min (record clinical_event_ff828bdbd80a5a5a031fce244f180795). Serum glucose: 321.20 mg/dL (record clinical_event_d4ed14ee54e68c84adcdcf756da153a0). Creatinine: 1.18 mg/dL (record clinical_event_25528ec9c1cf2178f9353eae8594b175). Previously recorded problems: Type 2 diabetes mellitus without complications. Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-11-27T11:30:00Z: Patient review: Kelly Brice, age 27. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Serum glucose: 321.20 mg/dL (record clinical_event_d4ed14ee54e68c84adcdcf756da153a0). Serum glucose: 134.50 mg/dL (record clinical_event_c0e6631f3091fdf0f37c3130faa91cb8). Creatinine: 1.18 mg/dL (record clinical_event_25528ec9c1cf2178f9353eae8594b175). Creatinine: 0.95 mg/dL (record clinical_event_16796239b3292acbfbafba6d094784d8). Previously recorded problems: Type 2 diabetes mellitus without complications. Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 41: Jordan Cox

Stable patient: patient_a7b1c7754c6b4c7d78a425b5fde26a18; birth date 1997-02-14; strata: acuity/5, age/18-34, carry/False, long-stay/False, outcome/HOME, pathway/R079, repeat/False, service/ED, site/facility_7990133218ef060b178c3cf8a0825f76.

- ED 2023-04-18T19:35:00Z to 2023-04-18T21:26:00Z; acuity 5; HOME; diagnosis R079; episode episode_b5b0fb561eb556497dfc8ceddbc660b4; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2023-04-18T21:26:00Z: Clinical review: Jordan Cox, age 26. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 98.07 % (record clinical_event_0c13e8c356acbe31312e5a528f092edc). Heart rate: 113.00 /min (record clinical_event_2d4e9b89a1f0cb21075df8f2141a7df7). Troponin I: 3.68 ng/L (record clinical_event_448f37df2278cc57336a4d7ab7a6d6a0). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 42: Craig Howard

Stable patient: patient_add884f1383554340877b4f5341fcae2; birth date 1941-08-26; strata: acuity/2, acuity/3, acuity/4, age/80+, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/I509, pathway/R079, pathway/R1010, repeat/True, service/ED, service/IPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- ED 2023-02-13T08:28:00Z to 2023-02-13T11:03:00Z; acuity 4; HOME; diagnosis R1010; episode episode_64686387e0a53e62f2c55213297700df; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2023-02-13T11:03:00Z: Interval assessment: Craig Howard, age 81. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.38 % (record clinical_event_d9705ae9a0a9e179f2b307298a8b26a5). Heart rate: 114.50 /min (record clinical_event_04c12265542d48559baab4b3af2633b3). Hemoglobin: 14.07 g/dL (record clinical_event_727ef2fb0414e4a3be1d5f72105f45ee). Previously recorded problems: Essential (primary) hypertension. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2023-12-22T20:03:00Z to 2023-12-22T22:33:00Z; acuity 3; HOME; diagnosis R079; episode episode_0fb0b053397b5d6c0ffd6ec3fa9c91d9; predecessor encounter_version_9163d4c8082586a53c7769ecc4365ca1.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2023-12-22T22:33:00Z: Patient review: Craig Howard, age 82. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 96.48 % (record clinical_event_c0d97d2acb2d15292c35e5d2a4603ad0). Heart rate: 104.25 /min (record clinical_event_5dc34c1aa3cd5b283f1bd1bf1849df08). Troponin I: 7.16 ng/L (record clinical_event_64192abf7df82e970c64842d2aaee187). Previously recorded problems: Essential (primary) hypertension. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2025-04-30T11:26:00Z to 2025-04-30T15:26:00Z; acuity 2; TRANSFER; diagnosis I509; episode episode_5432e89ad4dd806e709709270a8c696f; predecessor encounter_version_e8acdc5a885c190dbfa6d4a9a5b6b63c.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2025-04-30T15:26:00Z: Interval assessment: Craig Howard, age 83. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 91.32 % (record clinical_event_a5071b2e679f0b162495608352c326cc). Heart rate: 114.50 /min (record clinical_event_2a19b33e5439c5ae80d55cc88cce8803). Creatinine: 1.19 mg/dL (record clinical_event_f4f7a89e1992cb2310f84eca9fc8a7f9). Previously recorded problems: Essential (primary) hypertension; Heart failure, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- IPD 2025-04-30T15:26:00Z to 2025-05-05T17:26:00Z; acuity 3; HOME; diagnosis I509; episode episode_5432e89ad4dd806e709709270a8c696f; predecessor encounter_version_ed7f633d1154d0c18754f8fd32f2a59e.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=6, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Furosemide 20 mg PO COMPLETED; Furosemide 20 mg PO COMPLETED.

  PROGRESS_NOTE @ 2025-04-30T19:26:00Z: Assessment update: Craig Howard, age 83. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Body weight: 101.98 kg (record clinical_event_9528fec3a6591e7652846c8ebec24d77). Oxygen saturation: 93.60 % (record clinical_event_36aa88d83f460391e64d37ed72f33cc6). Creatinine: 1.24 mg/dL (record clinical_event_7bf0e4b42fb3133860a08e28b3a23b64). Potassium: 4.13 mmol/L (record clinical_event_29e40763a33afabf0d78fb37f4695872). Previously recorded problems: Essential (primary) hypertension; Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_706b90fa65e841b752e9f4d6bff84ad2). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-05-05T17:26:00Z: Assessment update: Craig Howard, age 83. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Creatinine: 1.24 mg/dL (record clinical_event_7bf0e4b42fb3133860a08e28b3a23b64). Creatinine: 1.10 mg/dL (record clinical_event_f28be3dee7f2d980d625d65ed538ee34). Potassium: 4.13 mmol/L (record clinical_event_29e40763a33afabf0d78fb37f4695872). Potassium: 3.83 mmol/L (record clinical_event_70c072a8fb084c031fe5d1cd48763704). Previously recorded problems: Essential (primary) hypertension; Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_50aa6535c7a4e34ea571115d1c9702f1). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 43: Annie Stein

Stable patient: patient_0ab9e27af7196703dd2b2210bcaa21b3; birth date 1971-11-27; strata: acuity/3, acuity/5, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/J449, pathway/K8010, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- OPD 2022-12-25T06:00:00Z to 2022-12-25T08:00:00Z; acuity 5; HOME; diagnosis J449; episode episode_ead5508411d882904cefccd54a1abe36; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  OP_NOTE @ 2022-12-25T08:00:00Z: Assessment update: Annie Stein, age 51. Interval follow-up for increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 95.35 % (record clinical_event_616a3859de7a1635a9bdc36bfcb3200d). Heart rate: 85.95 /min (record clinical_event_78efc064e7bede57858bcbb34c03452a). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified; Hyperlipidemia, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- IPD 2023-03-27T14:04:00Z to 2023-03-31T08:04:00Z; acuity 3; HOME; diagnosis K8010; episode episode_7b527dfe9095bbf47463ddf0c9661492; predecessor encounter_version_f578f6c630265348870e1915a6d02d07.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=8, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2023-03-28T00:04:00Z: Interval assessment: Annie Stein, age 51. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 7.00 1 (record clinical_event_b358f0ddaa0cf97184f1a23e245d4479). Heart rate: 105.75 /min (record clinical_event_f66e558a9309be5b2846618632773b9c). Hemoglobin: 13.48 g/dL (record clinical_event_61337d7ca82dfb702fdde64444f1f54f). Creatinine: 2.18 mg/dL (record clinical_event_b309384927687c91983a68e2a06ae1c1). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified; Hyperlipidemia, unspecified. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_8f499d19999bcbc67a7eda43492862ba). Acetaminophen 650 mg administered (record clinical_event_229bf00821e3648ec0176b333caa1dfb). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-03-31T08:04:00Z: Encounter review: Annie Stein, age 51. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 13.48 g/dL (record clinical_event_61337d7ca82dfb702fdde64444f1f54f). Hemoglobin: 12.78 g/dL (record clinical_event_9093653f5bde850c750de571de14e1b7). Creatinine: 2.18 mg/dL (record clinical_event_b309384927687c91983a68e2a06ae1c1). Creatinine: 2.02 mg/dL (record clinical_event_069b78db49d90f0e8a030d4fb9943be6). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified; Hyperlipidemia, unspecified. Acetaminophen 650 mg administered (record clinical_event_113310c49d5b1057fa044b9f30da0124). Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2025-11-30T07:50:00Z to 2025-11-30T09:56:00Z; acuity 5; HOME; diagnosis R1010; episode episode_f4f7a58b216a5ae1cb1491ec13b19a89; predecessor encounter_version_298f6af62db70007f37df3ea09f5d736.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2025-11-30T09:56:00Z: Care assessment: Annie Stein, age 54. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 96.24 % (record clinical_event_a97ce9535667592af7ce0b7f92f7a9f4). Heart rate: 113.25 /min (record clinical_event_ad3cfdbcf24dac33c383ff0a0c914a05). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified; Hyperlipidemia, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 44: Rose Sparks

Stable patient: patient_00115f1179ab4bc62fe6ab2ba5319a79; birth date 1942-05-09; strata: acuity/3, age/80+, carry/False, long-stay/False, outcome/HOME, pathway/M1711, repeat/False, service/IPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- IPD 2024-05-20T15:49:00Z to 2024-05-24T18:49:00Z; acuity 3; HOME; diagnosis M1711; episode episode_85a6b9cd3d48d12ddb9f163817977eb6; predecessor none.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=9, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2024-05-21T01:49:00Z: Clinical review: Rose Sparks, age 82. Presenting concern: right knee osteoarthritis limiting mobility. Working assessment: Unilateral primary osteoarthritis, right knee. Pain numeric rating: 7.00 1 (record clinical_event_4545fb6e0b8778c858756e4d3ca5a624). Mobility assessment: 2.00 1 (record clinical_event_aa6d2f54a9c0f639b9bd48ea5b948099). Hemoglobin: 14.58 g/dL (record clinical_event_0e4ea393f1cc346c49a35fcad27cf706). Creatinine: 1.13 mg/dL (record clinical_event_58788139d283f2a2c2a54eaa61e6c231). Previously recorded problems: Heart failure, unspecified. Procedure documented: Replacement of Right Knee Joint with Synthetic Substitute, Cemented, Open Approach (record clinical_event_88b19ff5921c59de4e53ac999b24d1fe). Acetaminophen 650 mg administered (record clinical_event_1f7f1d76e675630dcf4240cf1e073d98). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2024-05-24T18:49:00Z: Assessment update: Rose Sparks, age 82. Presenting concern: right knee osteoarthritis limiting mobility. Working assessment: Unilateral primary osteoarthritis, right knee. Hemoglobin: 14.58 g/dL (record clinical_event_0e4ea393f1cc346c49a35fcad27cf706). Hemoglobin: 13.88 g/dL (record clinical_event_f5a2e4b0be6a5dcd440f84f88a0b2ee6). Creatinine: 1.13 mg/dL (record clinical_event_58788139d283f2a2c2a54eaa61e6c231). Creatinine: 0.98 mg/dL (record clinical_event_b07d6cd66a73d32bc057a907c2deb7ab). Previously recorded problems: Heart failure, unspecified. Acetaminophen 650 mg administered (record clinical_event_be6ef58fef5a51237321ef91d5bcc83a). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 45: Shirley Gomez

Stable patient: patient_f0528e8266908cff55562031ece381ba; birth date 1939-07-12; strata: acuity/2, acuity/3, acuity/5, age/80+, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/J449, pathway/R079, pathway/R1010, repeat/True, service/ED, service/IPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2024-10-27T12:42:00Z to 2024-10-27T14:31:00Z; acuity 3; HOME; diagnosis R079; episode episode_c45032f2f6b8e3598defd6d8b394e011; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2024-10-27T14:31:00Z: Care assessment: Shirley Gomez, age 85. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 96.12 % (record clinical_event_bfa16eb9639620618b25fe0c518e8757). Heart rate: 103.50 /min (record clinical_event_5e06a34620b413301772f61c74d3915f). Troponin I: 3.92 ng/L (record clinical_event_66817d3d2aa48e9d07c819720ad512eb). Previously recorded problems: Hyperlipidemia, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2025-06-14T18:47:00Z to 2025-06-14T21:08:00Z; acuity 5; HOME; diagnosis R079; episode episode_4a97aca4a17b65b6190acf280d722b07; predecessor encounter_version_badd298ef039c57ef5b6dc4e29e1dc26.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-06-14T21:08:00Z: Interval assessment: Shirley Gomez, age 85. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 98.37 % (record clinical_event_dd1842b6e7707bccf50aee04086b65c5). Heart rate: 105.50 /min (record clinical_event_86c858b4a5adafc43a12baf73d743f64). Troponin I: 3.98 ng/L (record clinical_event_9dc4fc4288f7fe93b475bd960936573e). Previously recorded problems: Hyperlipidemia, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2025-08-22T07:14:00Z to 2025-08-22T09:47:00Z; acuity 5; HOME; diagnosis R1010; episode episode_4b34475fac746c898a7e043e95cab037; predecessor encounter_version_716b32b37f1c5e14972678ad83a2666b.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=3, PROCEDURE=1.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  ED_NOTE @ 2025-08-22T09:47:00Z: Care assessment: Shirley Gomez, age 86. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 98.64 % (record clinical_event_64b3c681cd85588582b0c77ac4146938). Heart rate: 114.50 /min (record clinical_event_18746b6b50307e98783330359f71f70e). Hemoglobin: 13.76 g/dL (record clinical_event_639136ede2cf7c930d90ef6cbc5e2db6). Previously recorded problems: Hyperlipidemia, unspecified. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_5f30050ee6545f81f79907ff869ac625). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2025-11-20T10:15:00Z to 2025-11-20T14:15:00Z; acuity 2; TRANSFER; diagnosis J449; episode episode_a039e4630ce950c1c203c34d918363ed; predecessor encounter_version_053458d19ebbd125a41158e1cb770a43.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2025-11-20T14:15:00Z: Encounter review: Shirley Gomez, age 86. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 92.19 % (record clinical_event_9c5fc93ed054db86d5d057c114deb14e). Heart rate: 105.50 /min (record clinical_event_b556a4c4290922e2cd3ea45378d03302). White blood cell count: 16.28 10*3/uL (record clinical_event_e0a156488212b5aef23cee5443cd48bf). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Hyperlipidemia, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- IPD 2025-11-20T14:15:00Z to 2025-11-24T10:15:00Z; acuity 3; HOME; diagnosis J449; episode episode_a039e4630ce950c1c203c34d918363ed; predecessor encounter_version_1d0d0cf04849ff629fc34101e691e098.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=4, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Prednisone 40 mg PO COMPLETED; Prednisone 40 mg PO COMPLETED.

  PROGRESS_NOTE @ 2025-11-20T18:15:00Z: Encounter review: Shirley Gomez, age 86. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 95.04 % (record clinical_event_d871e47520996fcc66083d74d14b4bb1). Respiratory rate: 24.60 /min (record clinical_event_adcce31106aa617cd0c28c42a571060e). White blood cell count: 13.90 10*3/uL (record clinical_event_032b7677af8495cb248a468024a04295). Bicarbonate: 28.41 mmol/L (record clinical_event_2aff02a4d2c1b9152b4075fc87ee18bb). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Hyperlipidemia, unspecified. Prednisone 40 mg administered (record clinical_event_740c210aa453207f1e27d18a2d8b03b7). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-11-24T10:15:00Z: Clinical review: Shirley Gomez, age 86. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. White blood cell count: 13.90 10*3/uL (record clinical_event_032b7677af8495cb248a468024a04295). White blood cell count: 7.99 10*3/uL (record clinical_event_61f98c6bdead901ce588b98d89b8924d). Bicarbonate: 28.41 mmol/L (record clinical_event_2aff02a4d2c1b9152b4075fc87ee18bb). Bicarbonate: 27.41 mmol/L (record clinical_event_b3da35e64a0ddc455a99d8e5ef9fbebe). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Hyperlipidemia, unspecified. Prednisone 40 mg administered (record clinical_event_015e20d12a617fe2db916edc97b27dbf). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 46: Tiffany Dale

Stable patient: patient_c4856de604952c18c380d98a9fa683a8; birth date 1978-12-03; strata: acuity/2, acuity/3, acuity/4, acuity/5, age/35-49, carry/False, long-stay/False, outcome/HOME, pathway/E119, pathway/J449, pathway/K8010, pathway/R079, repeat/True, service/ED, service/IPD, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- OPD 2022-12-23T06:00:00Z to 2022-12-23T08:00:00Z; acuity 3; HOME; diagnosis E119; episode episode_1f647fe288a2d3e15062999047958587; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2, ORDER=1, PROCEDURE=1.

  OP_NOTE @ 2022-12-23T08:00:00Z: Interval assessment: Tiffany Dale, age 44. Interval follow-up for symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 97.30 % (record clinical_event_828c5c849bd0ad96a71e0a3ea372d48c). Heart rate: 76.95 /min (record clinical_event_f32ac28facc695151a1fb93c766e0bda). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Type 2 diabetes mellitus without complications. Continue assessment as results become available. Follow-up completion is not established by this document.
- OPD 2023-02-20T15:01:00Z to 2023-02-20T16:18:00Z; acuity 4; HOME; diagnosis R079; episode episode_d364e90d16957ef4c9280f934aca53a6; predecessor encounter_version_c9b9fe488c7f22bf72c669a9241c1f0b.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2023-02-20T16:18:00Z: Clinical review: Tiffany Dale, age 44. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.23 % (record clinical_event_4c653d888747465768b92ce22c9073e4). Heart rate: 72.60 /min (record clinical_event_ed01664109e822aaf766ec0abdffc012). Troponin I: 3.08 ng/L (record clinical_event_4e32f3532998adf67b0b6fc6d6630f37). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Type 2 diabetes mellitus without complications. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2024-06-13T01:49:00Z to 2024-06-13T04:38:00Z; acuity 5; HOME; diagnosis J449; episode episode_cd36e2c27659bad365f4e3bbea36cfd4; predecessor encounter_version_4d9a3870349c52a9485e73cb3bb9b7fb.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2024-06-13T04:38:00Z: Interval assessment: Tiffany Dale, age 45. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 94.11 % (record clinical_event_418b4c12cad3364fc286b48425784a59). Heart rate: 105.00 /min (record clinical_event_79635b31bf5e783b37de84c6305f129b). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- IPD 2025-03-07T15:12:00Z to 2025-03-12T17:12:00Z; acuity 2; HOME; diagnosis K8010; episode episode_0eeb4ed6467292306993519775a0124c; predecessor encounter_version_ae25f382f928e5e4efe38b095fe0318b.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=10, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2025-03-08T01:12:00Z: Patient review: Tiffany Dale, age 46. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 6.00 1 (record clinical_event_db0728b5578fb35aaaa971a87fcd2432). Heart rate: 98.50 /min (record clinical_event_0f2d8d544a500787ff486a528d74fd98). Hemoglobin: 13.66 g/dL (record clinical_event_fea7a955d554e040c9da95662c8c8e52). Creatinine: 1.12 mg/dL (record clinical_event_1ae94e8fbdde9d028b65ea80cd0bf470). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Type 2 diabetes mellitus without complications. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_15ef156d13375f15e7cc323483f86242). Acetaminophen 650 mg administered (record clinical_event_0525649a69f384aff1a0906f74ed689d). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-03-12T17:12:00Z: Interval assessment: Tiffany Dale, age 46. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 13.66 g/dL (record clinical_event_fea7a955d554e040c9da95662c8c8e52). Hemoglobin: 12.96 g/dL (record clinical_event_97ce1a59f302e0e56250561075e40e1c). Creatinine: 1.12 mg/dL (record clinical_event_1ae94e8fbdde9d028b65ea80cd0bf470). Creatinine: 1.03 mg/dL (record clinical_event_29d7543cc34ed39ff0bb4838b17c418c). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Type 2 diabetes mellitus without complications. Acetaminophen 650 mg administered (record clinical_event_a8567e17bb6eb86a632e91f860aabb6b). Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2025-04-16T18:58:00Z to 2025-04-16T20:25:00Z; acuity 5; HOME; diagnosis J449; episode episode_9f2c9c6a3053bf9b81ee5b065ec0e068; predecessor encounter_version_abd2d4fb2e0aeb9b96526815e5dbee55.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2.
  Treatment evidence: Prednisone 200 mg PO COMPLETED.

  OP_NOTE @ 2025-04-16T20:25:00Z: Assessment update: Tiffany Dale, age 46. Interval follow-up for increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 95.41 % (record clinical_event_81ca19f64c6ba723f4dee7d1ed0f187d). Heart rate: 79.80 /min (record clinical_event_860c43b4dee286341340acc7b7fe6af0). White blood cell count: 16.86 10*3/uL (record clinical_event_4aa0fb80adecdb51c5957f827a09d951). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Type 2 diabetes mellitus without complications. Prednisone 200 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_9a2098d3039098751a9ad0f973def5a3). The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 47: Thomas Scott

Stable patient: patient_19b195e0b6876b85127325aa72163a66; birth date 1972-01-11; strata: acuity/4, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/R079, repeat/False, service/ED, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2023-12-28T02:38:00Z to 2023-12-28T04:42:00Z; acuity 4; HOME; diagnosis R079; episode episode_6a17667c3b2a3d5bb0860bacea287b75; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2023-12-28T04:42:00Z: Interval assessment: Thomas Scott, age 51. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 96.12 % (record clinical_event_02ce50539524e1440d9fdbf8d2fdb184). Heart rate: 95.25 /min (record clinical_event_dcd6cddf2ade77283458cf857f483d1b). Troponin I: 3.80 ng/L (record clinical_event_9610df924397041ec1f7e992b7b9caee). Prior problem documentation is incomplete; absence of a record does not exclude disease. The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 48: Shannon Oakes

Stable patient: patient_ec9d3980de13d6a48e1e4d52aa2283d1; birth date 1970-04-13; strata: acuity/2, acuity/3, age/50-64, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/J449, pathway/R1010, repeat/True, service/ED, service/IPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2023-10-08T07:34:00Z to 2023-10-08T09:39:00Z; acuity 3; HOME; diagnosis R1010; episode episode_1c798294e6512b1332fb981588ae5c99; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2023-10-08T09:39:00Z: Interval assessment: Shannon Oakes, age 53. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 96.72 % (record clinical_event_282f4f4db4de0c365b6d55f4645d9944). Heart rate: 94.75 /min (record clinical_event_c6e6f9c6cd4e3046692c3f62e1cdc2c3). Hemoglobin: 14.59 g/dL (record clinical_event_1560ac8fcfe822bce9e3d57457e67138). Previously recorded problems: Heart failure, unspecified; Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2024-03-01T14:17:00Z to 2024-03-01T18:17:00Z; acuity 2; TRANSFER; diagnosis J449; episode episode_d32e5052f145cc60133b0594ea63ce12; predecessor encounter_version_9006a75db36892a1a22a2f68e06314ca.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2024-03-01T18:17:00Z: Interval assessment: Shannon Oakes, age 53. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 92.94 % (record clinical_event_f1e241f7bd9ff307dabe9b14cd8152d9). Heart rate: 96.25 /min (record clinical_event_9af01404314bcada258eb68592c82dd5). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Heart failure, unspecified; Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- IPD 2024-03-01T18:17:00Z to 2024-03-06T18:17:00Z; acuity 3; HOME; diagnosis J449; episode episode_d32e5052f145cc60133b0594ea63ce12; predecessor encounter_version_421638b8e7d99d3f254da5a3eb2265c5.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=5, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Prednisone 40 mg PO COMPLETED; Prednisone 40 mg PO COMPLETED.

  PROGRESS_NOTE @ 2024-03-01T22:17:00Z: Clinical review: Shannon Oakes, age 53. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 93.09 % (record clinical_event_0c2c6c6474339c0c71f55d6c5b345d7d). Respiratory rate: 23.80 /min (record clinical_event_e3f06f0df19edbc62d01b28c4fb06ea1). White blood cell count: 14.00 10*3/uL (record clinical_event_bf26881384d3cb04bf7dc29f4a26c6f8). Bicarbonate: 28.35 mmol/L (record clinical_event_f98451a2b27d4335aadd20d9d328db18). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Heart failure, unspecified; Type 2 diabetes mellitus without complications. Prednisone 40 mg administered (record clinical_event_6662e063fc9e16176f18a606a2199a57). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2024-03-06T18:17:00Z: Assessment update: Shannon Oakes, age 53. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. White blood cell count: 14.00 10*3/uL (record clinical_event_bf26881384d3cb04bf7dc29f4a26c6f8). White blood cell count: 9.82 10*3/uL (record clinical_event_6c23ac19fccb4fff089d183bc0895d3b). Bicarbonate: 28.35 mmol/L (record clinical_event_f98451a2b27d4335aadd20d9d328db18). Bicarbonate: 27.35 mmol/L (record clinical_event_0af285915cd1d7dd0fc09f5bf0e4dfd6). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Heart failure, unspecified; Type 2 diabetes mellitus without complications. Prednisone 40 mg administered (record clinical_event_0fb955bdeaa0665cc7f9e4e7041318c3). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 49: Mariah Kirk

Stable patient: patient_1918cfb7b78e0125e606b0696c1e919b; birth date 2004-09-08; strata: acuity/4, age/18-34, carry/False, long-stay/False, outcome/HOME, pathway/R1010, repeat/False, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- OPD 2024-06-07T19:34:00Z to 2024-06-07T20:12:00Z; acuity 4; HOME; diagnosis R1010; episode episode_e6dc833804a9ebece4776e71d7c42194; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2024-06-07T20:12:00Z: Care assessment: Mariah Kirk, age 19. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.54 % (record clinical_event_9138d5ec84ca6d54d1a8c34a70c7cea7). Heart rate: 76.50 /min (record clinical_event_de54e1a1679a019af2e0b1cc19cdb79e). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 50: Dawn Seidl

Stable patient: patient_aaf74210d448bf2d84e76c4bb2ed981b; birth date 1965-05-15; strata: acuity/3, acuity/4, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/J449, pathway/M1711, repeat/True, service/IPD, service/OPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- OPD 2022-12-22T06:00:00Z to 2022-12-22T08:00:00Z; acuity 4; HOME; diagnosis J449; episode episode_9d8076cb5831bae017e78668e559d724; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  OP_NOTE @ 2022-12-22T08:00:00Z: Assessment update: Dawn Seidl, age 57. Interval follow-up for increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 95.15 % (record clinical_event_9752603b4321de14734259abab32f9cd). Heart rate: 77.70 /min (record clinical_event_2ea01f94de274aaf2727e5c04553f8fb). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- IPD 2023-11-27T15:13:00Z to 2023-12-02T00:13:00Z; acuity 3; HOME; diagnosis M1711; episode episode_44acc3cd17463c26274405c1ca6ed817; predecessor encounter_version_ba59dafe741500241024b6da275333f0.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=11, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2023-11-28T01:13:00Z: Care assessment: Dawn Seidl, age 58. Presenting concern: right knee osteoarthritis limiting mobility. Working assessment: Unilateral primary osteoarthritis, right knee. Pain numeric rating: 7.00 1 (record clinical_event_c77886c8143fa31006491859462e257a). Mobility assessment: 1.00 1 (record clinical_event_10d753bf3cbfa553703c0ff506cc987c). Hemoglobin: 13.40 g/dL (record clinical_event_b5eb0ef18395fc7ef57818d8adca7aa3). Creatinine: 1.23 mg/dL (record clinical_event_5655c730a36a150bf34dcb4c639af7f0). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Type 2 diabetes mellitus without complications. Procedure documented: Replacement of Right Knee Joint with Synthetic Substitute, Cemented, Open Approach (record clinical_event_bf76f3441896b08980464c1dc6d430bd). Acetaminophen 650 mg administered (record clinical_event_eee261b047e31cb647d6c63c2ff22016). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-12-02T00:13:00Z: Clinical review: Dawn Seidl, age 58. Presenting concern: right knee osteoarthritis limiting mobility. Working assessment: Unilateral primary osteoarthritis, right knee. Hemoglobin: 13.40 g/dL (record clinical_event_b5eb0ef18395fc7ef57818d8adca7aa3). Hemoglobin: 12.70 g/dL (record clinical_event_c0134280e80cbc821d5484dbe9f911d9). Creatinine: 1.23 mg/dL (record clinical_event_5655c730a36a150bf34dcb4c639af7f0). Creatinine: 0.99 mg/dL (record clinical_event_b3c6addd2453cfa5d37b8ef392b5e3f9). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Type 2 diabetes mellitus without complications. Acetaminophen 650 mg administered (record clinical_event_af86a3c03c7ad359125cdf0c4f656b6c). Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2025-02-05T20:59:00Z to 2025-02-05T22:27:00Z; acuity 4; HOME; diagnosis J449; episode episode_9d9ce028cd0079b43ca1dc8b2c16534f; predecessor encounter_version_64915a269ba08e548b48f3127fb913d1.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  OP_NOTE @ 2025-02-05T22:27:00Z: Patient review: Dawn Seidl, age 59. Interval follow-up for increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 95.41 % (record clinical_event_6defa25c861add980aa3027d0c3a6508). Heart rate: 76.65 /min (record clinical_event_c48be4a033a6feaf761de635c38c8417). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 51: Glen Zimmerman

Stable patient: patient_41f8c01f792c2612f31fe97005133aa3; birth date 1958-10-08; strata: acuity/3, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/R1010, repeat/False, service/ED, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2023-10-02T11:46:00Z to 2023-10-02T13:26:00Z; acuity 3; HOME; diagnosis R1010; episode episode_492de83720b5e86d96cbdb49132d22c0; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  ED_NOTE @ 2023-10-02T13:26:00Z: Encounter review: Glen Zimmerman, age 64. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.89 % (record clinical_event_977255ca22075aa516449f67f68b22d9). Heart rate: 109.75 /min (record clinical_event_a5eb4efa591ea62ca395124bcc0aec42). Hemoglobin: 14.58 g/dL (record clinical_event_e8cd877a6bbb2b7a17d6f86c8c4216cb). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_37a93ba576e647cc2b9f60dbe93f5b2d). Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 52: Norma Welsh

Stable patient: patient_cfd156b1f037a861b31e1d970e5c98fd; birth date 1946-07-22; strata: acuity/2, acuity/3, acuity/4, acuity/5, age/65-79, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/J189, pathway/J449, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- ED 2023-03-13T06:13:00Z to 2023-03-13T08:53:00Z; acuity 5; HOME; diagnosis J449; episode episode_39be3faf81aa4fed1f39b83ea84ca7d2; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2, ORDER=1, PROCEDURE=1.

  ED_NOTE @ 2023-03-13T08:53:00Z: Encounter review: Norma Welsh, age 76. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 93.93 % (record clinical_event_450691c0014fc0682dc0e6e6f0fc9920). Heart rate: 111.25 /min (record clinical_event_d2e5a0fc96c016c68562bd7f50229dac). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2024-04-10T11:00:00Z to 2024-04-10T15:00:00Z; acuity 2; TRANSFER; diagnosis J189; episode episode_d172a17730b16408383faa87894340d0; predecessor encounter_version_a49fb3ac0599b5a5a3c234cdb7635cfb.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2024-04-10T15:00:00Z: Encounter review: Norma Welsh, age 77. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Oxygen saturation: 90.27 % (record clinical_event_86ccab3683e75476054ac3faf019b0d8). Heart rate: 112.50 /min (record clinical_event_90d2b9e0abc5441ce081477722f21b6b). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2024-04-10T15:00:00Z to 2024-04-17T01:00:00Z; acuity 2; HOME; diagnosis J189; episode episode_d172a17730b16408383faa87894340d0; predecessor encounter_version_8e7222e66f9b7d32e8e178a061017b86.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=13, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Doxycycline 100 mg PO COMPLETED; Doxycycline 100 mg PO COMPLETED.

  PROGRESS_NOTE @ 2024-04-10T19:00:00Z: Assessment update: Norma Welsh, age 77. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Body temperature: 38.25 Cel (record clinical_event_f6adfc056e95b0d67d3ce4661745cb23). Oxygen saturation: 91.41 % (record clinical_event_b1ca526dcdff39479f0dec091622f489). White blood cell count: 13.41 10*3/uL (record clinical_event_95d96cdefb892ac44f750db1c2b6fdbe). C-reactive protein: 80.52 mg/L (record clinical_event_45f896e03bd6a9ddb67f47c22a4f3ca0). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified. Doxycycline 100 mg administered (record clinical_event_9d30054271e953bd10c171c4fcf052c9). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2024-04-17T01:00:00Z: Clinical review: Norma Welsh, age 77. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. White blood cell count: 13.41 10*3/uL (record clinical_event_95d96cdefb892ac44f750db1c2b6fdbe). White blood cell count: 7.99 10*3/uL (record clinical_event_f352807411aa4b9772397b49673e9505). C-reactive protein: 80.52 mg/L (record clinical_event_45f896e03bd6a9ddb67f47c22a4f3ca0). C-reactive protein: 11.12 mg/L (record clinical_event_e3bb423e1db8ce5cf6aa4839d214e003). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified. Doxycycline 100 mg administered (record clinical_event_2f422463e8893f580cdc15cdd60cf309). Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2024-05-01T20:53:00Z to 2024-05-01T21:40:00Z; acuity 4; HOME; diagnosis J449; episode episode_db1bf18ec1d113cc39394621fa14c589; predecessor encounter_version_c7c697a911c23f229f7fe96685de9a3f.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=1.
  Treatment evidence: Prednisone 200 mg PO COMPLETED.

  OP_NOTE @ 2024-05-01T21:40:00Z: Encounter review: Norma Welsh, age 77. Interval follow-up for increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 95.69 % (record clinical_event_4bdf8c9423600dc62a7b274a8f37be31). Heart rate: 85.50 /min (record clinical_event_29c8bc9c0ac0ddbbc9fd5b50ed998d53). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified. Prednisone 200 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_fa735662eaf954dc87e7215339c46908). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2025-08-31T17:38:00Z to 2025-08-31T19:33:00Z; acuity 3; HOME; diagnosis J449; episode episode_b5131e54295416527754a05b49431a48; predecessor encounter_version_b303b6c4ee9f6adb3b6f8bf8793fb343.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2025-08-31T19:33:00Z: Patient review: Norma Welsh, age 79. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 95.52 % (record clinical_event_3cc96236f8436e1087de4fbe2c970cb2). Heart rate: 93.50 /min (record clinical_event_42acc8616e20122227c8533d7b28cbe2). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2025-10-28T00:32:00Z to 2025-10-28T03:17:00Z; acuity 4; HOME; diagnosis J449; episode episode_da00889fc84247ebe6e063e9660ce81a; predecessor encounter_version_ac1060ab021734b01c28ccd6eda5376a.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-10-28T03:17:00Z: Interval assessment: Norma Welsh, age 79. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 95.97 % (record clinical_event_bc73cad4e1b4f4fbc442d98af8f0493a). Heart rate: 104.25 /min (record clinical_event_63e435e7e18fa3bfac776891950b5e81). White blood cell count: 15.93 10*3/uL (record clinical_event_67b1a6d146413f25bd62b518d85d40d1). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 53: Briana Jones

Stable patient: patient_903bb826608241f4092b41ca5048db7f; birth date 1993-08-05; strata: acuity/3, acuity/5, age/18-34, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/J189, pathway/R079, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- IPD 2023-09-09T06:17:00Z to 2023-09-15T16:17:00Z; acuity 3; TRANSFER; diagnosis J189; episode episode_51bead248bc7560fccb713aa840dbcad; predecessor none.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=13, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Doxycycline 100 mg PO COMPLETED; Doxycycline 100 mg PO COMPLETED.

  PROGRESS_NOTE @ 2023-09-09T10:17:00Z: Assessment update: Briana Jones, age 30. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Body temperature: 38.81 Cel (record clinical_event_96fa8c5fb88be841091dbb80c2d29b7b). Oxygen saturation: 94.86 % (record clinical_event_643c5ec6b5998c61f127a6e31647d768). White blood cell count: 18.27 10*3/uL (record clinical_event_b96354a627517172a18fce6b9344ede3). C-reactive protein: 124.44 mg/L (record clinical_event_cec01a99a3f6902753fe6b6ec21dc461). Prior problem documentation is incomplete; absence of a record does not exclude disease. Doxycycline 100 mg administered (record clinical_event_bcf4dd4b30691dd8308d98ea0ab5eb9c). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-09-15T16:17:00Z: Clinical review: Briana Jones, age 30. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. White blood cell count: 18.27 10*3/uL (record clinical_event_b96354a627517172a18fce6b9344ede3). White blood cell count: 18.50 10*3/uL (record clinical_event_cb7e3f75aa1bcd67f6b68ffd2f5d5caa). C-reactive protein: 124.44 mg/L (record clinical_event_cec01a99a3f6902753fe6b6ec21dc461). C-reactive protein: 124.64 mg/L (record clinical_event_95f2e9cb4775e5bbeea3e87b6b63d5e2). Prior problem documentation is incomplete; absence of a record does not exclude disease. Doxycycline 100 mg administered (record clinical_event_473869fcba501c0a71a6882294c7a4e3). Observed disposition: TRANSFER. Follow-up completion is not established by this document.
- ED 2024-05-14T22:29:00Z to 2024-05-15T01:01:00Z; acuity 5; HOME; diagnosis R079; episode episode_791394814e4312bdb2737fe7a4389989; predecessor encounter_version_c1101039dd1a473032a37da8c9f24070.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2024-05-15T01:01:00Z: Clinical review: Briana Jones, age 30. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 98.16 % (record clinical_event_11b683cdc10159f8c2a427b172024b57). Heart rate: 113.75 /min (record clinical_event_09d53e7bb1b1c0580ed83a58a3c9056e). Troponin I: 3.50 ng/L (record clinical_event_322f6fdafe9cd934a83a41b0cdbc1d1d). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2024-10-03T01:14:00Z to 2024-10-03T03:22:00Z; acuity 5; HOME; diagnosis R1010; episode episode_6411a9f5fab8e51a5fbcb68ad0191249; predecessor encounter_version_33e6726f32ff5e4ae5ebfafe1ce1d1d6.
  Captured evidence: DOCUMENT=1, OBSERVATION=2, ORDER=1, PROCEDURE=1.

  ED_NOTE @ 2024-10-03T03:22:00Z: Interval assessment: Briana Jones, age 31. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 96.60 % (record clinical_event_b8511b68a8969264d9b6be85583c4e48). Heart rate: 96.00 /min (record clinical_event_b90442182566c97c37ac9ad7872f9266). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- OPD 2024-10-21T17:07:00Z to 2024-10-21T18:37:00Z; acuity 3; HOME; diagnosis R1010; episode episode_d65f86e9c41a574a6eca4f6b59efc582; predecessor encounter_version_d2dfd197b2e929a93d432f7b760e09ad.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=1.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  OP_NOTE @ 2024-10-21T18:37:00Z: Interval assessment: Briana Jones, age 31. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.34 % (record clinical_event_6d59a5fb0dbc2b601b17ae0e6b9b678a). Heart rate: 81.00 /min (record clinical_event_8a2a23d92664bdcca1897bb99cf5e38e). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_bf19dde97d03827e6a9b1033fa9ea2fe). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2024-12-25T01:01:00Z to 2024-12-25T03:08:00Z; acuity 5; HOME; diagnosis R1010; episode episode_edd3c5ae3b4c23d032430fa53aab6ec1; predecessor encounter_version_a3a4623695e713cef0d235ec0322885a.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2024-12-25T03:08:00Z: Clinical review: Briana Jones, age 31. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.05 % (record clinical_event_3099bf807030464f84b6fbf1439652a6). Heart rate: 112.75 /min (record clinical_event_0ded82b633e1adb936b88168cf3881ab). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2025-12-12T17:36:00Z to 2025-12-12T19:44:00Z; acuity 5; HOME; diagnosis R079; episode episode_542c11556c1541c5872283f180a85a75; predecessor encounter_version_8b100ac14926fca28ae59402ea097977.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-12-12T19:44:00Z: Assessment update: Briana Jones, age 32. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.77 % (record clinical_event_2eae51ebef8e5b1c1920064f1d01f535). Heart rate: 112.75 /min (record clinical_event_8d0f9920c188bf6e96a68cef9f459285). Troponin I: 7.16 ng/L (record clinical_event_5a947d2b1fb8e625b1f49cd0c18ca15b). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 54: Wanda Baker

Stable patient: patient_fad6f847767ac17dbd44584369c36b15; birth date 1946-02-23; strata: acuity/2, acuity/3, age/65-79, carry/False, long-stay/False, long-stay/True, outcome/HOME, pathway/K8010, pathway/R079, repeat/True, service/IPD, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- OPD 2024-01-12T15:40:00Z to 2024-01-12T17:29:00Z; acuity 3; HOME; diagnosis R079; episode episode_7f6136dc7e2267a8971143f227890490; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2024-01-12T17:29:00Z: Interval assessment: Wanda Baker, age 77. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.99 % (record clinical_event_c1d87ad3a1f869e274f2d6623b3bae0e). Heart rate: 77.10 /min (record clinical_event_1a00bd9779b1edb259027efb697ca57b). Troponin I: 2.30 ng/L (record clinical_event_5c234f4af522cfe669d4fb7638249a89). Previously recorded problems: Chronic kidney disease, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2025-01-07T14:29:00Z to 2025-01-23T09:29:00Z; acuity 2; HOME; diagnosis K8010; episode episode_972a33b91d9027792a72d99095d3bd8b; predecessor encounter_version_954b44562aab6cf39f62eeeb8e786175.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=12, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2025-01-08T00:29:00Z: Clinical review: Wanda Baker, age 78. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 8.00 1 (record clinical_event_65fba454b12bd9497304e18b5821362c). Heart rate: 93.75 /min (record clinical_event_6fc15e9d38ec217947cd39257a50045f). Hemoglobin: 13.88 g/dL (record clinical_event_75e145d0dc17098d82cb007a87380f62). Creatinine: 1.88 mg/dL (record clinical_event_c7acee62a7ca3cd6916e63a17bb69012). Previously recorded problems: Chronic kidney disease, unspecified. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_07b6bb943fb3d10ff5e392fe7c410591). Acetaminophen 650 mg administered (record clinical_event_6173916738386230f7211905fdb992e8). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-01-23T09:29:00Z: Patient review: Wanda Baker, age 78. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 13.88 g/dL (record clinical_event_75e145d0dc17098d82cb007a87380f62). Hemoglobin: 13.18 g/dL (record clinical_event_3bd4d2cf578d0004d6942b99d25392df). Creatinine: 1.88 mg/dL (record clinical_event_c7acee62a7ca3cd6916e63a17bb69012). Creatinine: 1.84 mg/dL (record clinical_event_2ad921355946551e5e7ac4e13024f173). Previously recorded problems: Chronic kidney disease, unspecified. Acetaminophen 650 mg administered (record clinical_event_7dc0332f8ba77d91b83e90ef73c7cba2). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 55: Thomas Glasser

Stable patient: patient_62ce5885df1a91b5080faa769b4c7947; birth date 1942-09-08; strata: acuity/2, acuity/3, age/80+, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/I509, repeat/True, service/ED, service/IPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2023-03-17T23:19:00Z to 2023-03-18T03:19:00Z; acuity 3; TRANSFER; diagnosis I509; episode episode_e191b6fa7798843836c189c657c771aa; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2023-03-18T03:19:00Z: Care assessment: Thomas Glasser, age 80. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 94.26 % (record clinical_event_c15e12b8abe17156ad48aa94ec15979b). Heart rate: 94.75 /min (record clinical_event_663c8831a4c6ac4ee376f66b68874982). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- IPD 2023-03-18T03:19:00Z to 2023-03-23T13:19:00Z; acuity 2; HOME; diagnosis I509; episode episode_e191b6fa7798843836c189c657c771aa; predecessor encounter_version_5a2ec7fcca76532d48095ec57b484877.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=6, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Furosemide 20 mg PO COMPLETED; Furosemide 20 mg PO COMPLETED.

  PROGRESS_NOTE @ 2023-03-18T07:19:00Z: Assessment update: Thomas Glasser, age 80. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Body weight: 100.92 kg (record clinical_event_499be49d9e846a43d29f9ddd19ac296a). Oxygen saturation: 91.23 % (record clinical_event_50c18931036eacce795f6f88d74e7d25). Creatinine: 2.18 mg/dL (record clinical_event_c75768dca3dffa6cbda8d04bf1486bed). Potassium: 4.12 mmol/L (record clinical_event_a8d5e4c87af96b06ae062e4db507cace). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_aa58658b68ffc5cf27a98ffd7d3b0a4b). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-03-23T13:19:00Z: Assessment update: Thomas Glasser, age 80. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Creatinine: 2.18 mg/dL (record clinical_event_c75768dca3dffa6cbda8d04bf1486bed). Creatinine: 2.00 mg/dL (record clinical_event_4afd6b4d951dfa19f377e687bfd50848). Potassium: 4.12 mmol/L (record clinical_event_a8d5e4c87af96b06ae062e4db507cace). Potassium: 3.82 mmol/L (record clinical_event_fd41ff24f90826a036a4e2a5b77fb8db). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_a12a847647b617bea62e2421ce8cdfae). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 56: Stephanie Fields

Stable patient: patient_374421dda704a3c0b33a1d2d910c9af7; birth date 1978-01-15; strata: acuity/2, acuity/3, acuity/4, acuity/5, age/35-49, carry/False, long-stay/False, outcome/HOME, pathway/J189, pathway/K8010, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- OPD 2022-12-27T06:00:00Z to 2022-12-27T08:00:00Z; acuity 4; HOME; diagnosis J189; episode episode_ce9b73921a9bf996991fae17034a0e0f; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  OP_NOTE @ 2022-12-27T08:00:00Z: Assessment update: Stephanie Fields, age 44. Interval follow-up for cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Oxygen saturation: 97.77 % (record clinical_event_86d4034defa0c8914bf45c16dc450101). Heart rate: 84.00 /min (record clinical_event_58e306ddc8804b47581564e0b1c848aa). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2023-05-04T14:04:00Z to 2023-05-08T03:04:00Z; acuity 2; HOME; diagnosis K8010; episode episode_0c7223b11454a1024a3a79dbea662579; predecessor encounter_version_ca78a941056506af99e82b8f953aaec2.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=11, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2023-05-05T00:04:00Z: Patient review: Stephanie Fields, age 45. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 8.00 1 (record clinical_event_4ffc7ede3004062fe4883ce0c141d649). Heart rate: 107.00 /min (record clinical_event_e8cc4ea4ce0fae7225b68a97b9811e63). Hemoglobin: 13.77 g/dL (record clinical_event_4e4442711949f661827e6c26e64ec14f). Creatinine: 1.15 mg/dL (record clinical_event_663650982f1f79935dc25376cedb9e22). Prior problem documentation is incomplete; absence of a record does not exclude disease. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_60e3c35593295c2f6ce990690e0f4cde). Acetaminophen 650 mg administered (record clinical_event_e6524a00ee22310ad17d8c472a8773c5). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-05-08T03:04:00Z: Interval assessment: Stephanie Fields, age 45. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 13.77 g/dL (record clinical_event_4e4442711949f661827e6c26e64ec14f). Hemoglobin: 13.07 g/dL (record clinical_event_a867c0f176ee536fe829f16cee5032b5). Creatinine: 1.15 mg/dL (record clinical_event_663650982f1f79935dc25376cedb9e22). Creatinine: 0.98 mg/dL (record clinical_event_fc3dc140ef5f32c29926b38dd7ba4d19). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 650 mg administered (record clinical_event_51843e7e7b24d364b52567b3452192f8). Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2023-05-16T02:04:00Z to 2023-05-16T04:51:00Z; acuity 3; HOME; diagnosis J189; episode episode_95ee27212c3a81554b9ea2ff80bed873; predecessor encounter_version_bc9dd7a716f974d9ef0778bc3191ea53.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2023-05-16T04:51:00Z: Clinical review: Stephanie Fields, age 45. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Oxygen saturation: 93.33 % (record clinical_event_add7d994c3cfa3f852498bb2fec7d76a). Heart rate: 102.75 /min (record clinical_event_7a125e30d1bd8f3ab5547525c278afd1). White blood cell count: 15.37 10*3/uL (record clinical_event_652dcdc3fb567650f990670ac59e97b7). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2023-05-21T15:38:00Z to 2023-05-21T17:29:00Z; acuity 5; HOME; diagnosis R1010; episode episode_0bb1150ed7ad04b00df35437db4d2b6a; predecessor encounter_version_d8b415ac148862ecfb6704e7e33fcea3.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2023-05-21T17:29:00Z: Interval assessment: Stephanie Fields, age 45. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 98.13 % (record clinical_event_1b131e3fc05b16e652b557230ad7ae5e). Heart rate: 110.50 /min (record clinical_event_cd5b169f77f929204fa16033ea3da15e). Prior problem documentation is incomplete; absence of a record does not exclude disease. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2023-07-05T22:58:00Z to 2023-07-06T01:26:00Z; acuity 5; HOME; diagnosis R1010; episode episode_7aa58a8f3f7ef2bacbccee12e78d0084; predecessor encounter_version_17c305872d9ce70a9345434aa7225160.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2023-07-06T01:26:00Z: Clinical review: Stephanie Fields, age 45. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 96.27 % (record clinical_event_3a9b7afe8418837d4e16ccbe4ff6d741). Heart rate: 108.25 /min (record clinical_event_54edead3db00f07d26f1c6560b015c47). Hemoglobin: 14.00 g/dL (record clinical_event_d4b8385369fb3c76521fde0afca7e287). Prior problem documentation is incomplete; absence of a record does not exclude disease. The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 57: Brandi Walston

Stable patient: patient_97781329fee31575e4d332e841012b30; birth date 1976-05-28; strata: acuity/4, age/35-49, carry/False, long-stay/False, outcome/HOME, pathway/R079, repeat/False, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- OPD 2025-07-14T17:57:00Z to 2025-07-14T19:33:00Z; acuity 4; HOME; diagnosis R079; episode episode_2c262bd10c8554d399947ed542932f28; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2025-07-14T19:33:00Z: Clinical review: Brandi Walston, age 49. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.43 % (record clinical_event_a213fa77f1688d850f58e76b74f78f49). Heart rate: 86.85 /min (record clinical_event_d55c1d9263af6085d9cf830588b4081b). Troponin I: 7.22 ng/L (record clinical_event_c048e2fbde05b94df7bf32103efef762). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 58: Lloyd Fong

Stable patient: patient_408cad9601fafb6577959f45f97d47e3; birth date 1949-09-29; strata: acuity/3, acuity/4, acuity/5, age/65-79, carry/False, long-stay/False, outcome/HOME, pathway/J449, pathway/K8010, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2023-08-31T11:16:00Z to 2023-08-31T13:16:00Z; acuity 5; HOME; diagnosis R1010; episode episode_9372086596cb5b68948dfa045968eddb; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=3, PROCEDURE=1.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  ED_NOTE @ 2023-08-31T13:16:00Z: Interval assessment: Lloyd Fong, age 73. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 98.28 % (record clinical_event_ccc565d780b54b5f13c6b74a361f26a8). Heart rate: 101.25 /min (record clinical_event_7c5fda1bc38947ca4e8245afa353340b). Hemoglobin: 14.40 g/dL (record clinical_event_5232bffc6d11b647b946d04e5b0e7494). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified; Heart failure, unspecified. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_6749fdc4230437ce10978d2ff746d529). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2023-10-13T05:39:00Z to 2023-10-13T08:31:00Z; acuity 4; HOME; diagnosis R1010; episode episode_b912c8808502deed7e1fc4e9befcde77; predecessor encounter_version_64b11a90246c3249ab66ef9a5e752616.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2023-10-13T08:31:00Z: Clinical review: Lloyd Fong, age 74. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 98.34 % (record clinical_event_ab28c2167aa4dc43732b85a4ddbca13f). Heart rate: 113.00 /min (record clinical_event_3148a0bd7dc40173f4698bfd9ec07412). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified; Heart failure, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- IPD 2024-03-11T15:52:00Z to 2024-03-15T16:52:00Z; acuity 3; HOME; diagnosis K8010; episode episode_a4948cfbd48f4bf998c64439c4288e2a; predecessor encounter_version_1830a2e4e96d9315654466c430e6e640.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=10, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2024-03-12T01:52:00Z: Encounter review: Lloyd Fong, age 74. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 8.00 1 (record clinical_event_00f0afa49ac40345bcc299a1479a66ce). Heart rate: 112.00 /min (record clinical_event_dc1729c26fd22f9fd53e9c4e0d58af97). Hemoglobin: 13.95 g/dL (record clinical_event_7c19d32393dc515a8b267f7bb33f356e). Creatinine: 1.99 mg/dL (record clinical_event_1f98d50eaac9bbab10e461918edf9c17). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified; Heart failure, unspecified. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_800e846d22bd556d8fb4d1d74546ba7c). Acetaminophen 650 mg administered (record clinical_event_87dd413da8f44007657bcdde6279a268). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2024-03-15T16:52:00Z: Patient review: Lloyd Fong, age 74. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 13.95 g/dL (record clinical_event_7c19d32393dc515a8b267f7bb33f356e). Hemoglobin: 13.25 g/dL (record clinical_event_e44a6686f78f3952db018d4992092d07). Creatinine: 1.99 mg/dL (record clinical_event_1f98d50eaac9bbab10e461918edf9c17). Creatinine: 1.77 mg/dL (record clinical_event_1236e20c945c46beaf5740d798b628e8). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified; Heart failure, unspecified. Acetaminophen 650 mg administered (record clinical_event_24e42018d2895678c0201aab0f2e8ba8). Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2024-03-25T16:18:00Z to 2024-03-25T17:43:00Z; acuity 3; HOME; diagnosis J449; episode episode_35fcb18c6c364432509d19279b8d1d21; predecessor encounter_version_247c60f7265db6f8a555dd40618b17ad.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2.
  Treatment evidence: Prednisone 200 mg PO COMPLETED.

  OP_NOTE @ 2024-03-25T17:43:00Z: Patient review: Lloyd Fong, age 74. Interval follow-up for increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 95.97 % (record clinical_event_6d38f8d7f3bc563601a215fd5a715dbd). Heart rate: 86.55 /min (record clinical_event_50d41cfef83e4b2bb565011a5f357af7). White blood cell count: 15.78 10*3/uL (record clinical_event_b36dd0e46d5b60148112cfb6b294ecd6). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified; Heart failure, unspecified. Prednisone 200 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_e320399f9b0945cb7a0c24d31d31d5bb). The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2024-10-06T11:56:00Z to 2024-10-06T14:40:00Z; acuity 4; HOME; diagnosis R1010; episode episode_905a82268ec48af699954e6c1763aa7f; predecessor encounter_version_59a4b2568caf5feb9ca0795cc5a5abdf.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2024-10-06T14:40:00Z: Assessment update: Lloyd Fong, age 75. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 98.46 % (record clinical_event_9b171bc91e603ac78c89bb3f75308dfb). Heart rate: 108.75 /min (record clinical_event_82531dfa44a02b76a9862e485c9df723). Hemoglobin: 14.05 g/dL (record clinical_event_e31444c93aa8bb9da24ed23e399646a9). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified; Heart failure, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2025-10-10T02:14:00Z to 2025-10-10T05:11:00Z; acuity 3; HOME; diagnosis R1010; episode episode_f2b6fbeee445b95d3f552c57248fe49f; predecessor encounter_version_1a60ec79d2c62ada561fcc4a13c59edd.
  Captured evidence: DOCUMENT=1, OBSERVATION=2, ORDER=1, PROCEDURE=1.

  ED_NOTE @ 2025-10-10T05:11:00Z: Clinical review: Lloyd Fong, age 76. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 96.30 % (record clinical_event_6dd97c07081a737e0b115fec6320052a). Heart rate: 105.75 /min (record clinical_event_338c5f64cfc07953a3a8039a2bbcc550). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified; Heart failure, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2025-11-01T04:40:00Z to 2025-11-01T06:30:00Z; acuity 5; HOME; diagnosis J449; episode episode_2799596a3933d9f738c0a60cdd93b941; predecessor encounter_version_1c9fbe64cb5eefc52fe4e5772fe7dc04.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2.
  Treatment evidence: Prednisone 200 mg PO COMPLETED.

  ED_NOTE @ 2025-11-01T06:30:00Z: Care assessment: Lloyd Fong, age 76. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 94.56 % (record clinical_event_7a3e5c605201e5e020ef5979e7fc01c7). Heart rate: 96.75 /min (record clinical_event_0866ba94c35e76177a17c004e780b8ce). White blood cell count: 13.71 10*3/uL (record clinical_event_9f7507a2b67a3cfa2483d398a0927fed). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified; Heart failure, unspecified. Prednisone 200 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_1394dc434460d32b7dc3bfc09afff035). Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 59: Denise Velazquez

Stable patient: patient_bd01c7dc0fc26199be7fa7693f3a72f8; birth date 1963-04-28; strata: acuity/3, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/R079, repeat/False, service/ED, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2024-04-26T17:19:00Z to 2024-04-26T19:21:00Z; acuity 3; HOME; diagnosis R079; episode episode_ebb73462507db1170aa3821647e8a62b; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2024-04-26T19:21:00Z: Assessment update: Denise Velazquez, age 60. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.62 % (record clinical_event_553dd2707277d2e3314c90a3a5a07a58). Heart rate: 101.50 /min (record clinical_event_97afc394c649ed19373e59a362e3dfc3). Troponin I: 5.48 ng/L (record clinical_event_be78a8e6592ef0c8beff3a8ecb2cb0ab). Previously recorded problems: Heart failure, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 60: Jennifer Cleveland

Stable patient: patient_c45ce80a9773d0abfa256a1d1cf9e900; birth date 1973-09-17; strata: acuity/2, acuity/3, acuity/4, age/50-64, carry/False, long-stay/False, outcome/HOME, outcome/LEFT_WITHOUT_SEEN, outcome/TRANSFER, pathway/I509, pathway/R079, pathway/R1010, repeat/True, service/ED, service/IPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- ED 2024-09-05T02:37:00Z to 2024-09-05T05:28:00Z; acuity 3; LEFT_WITHOUT_SEEN; diagnosis unassessed; episode episode_6dfa0719e8aee29186e9fc0e7ba387d4; predecessor none.
  Captured evidence: .
- ED 2025-05-30T01:26:00Z to 2025-05-30T05:26:00Z; acuity 2; TRANSFER; diagnosis I509; episode episode_1cffb747192f11e25aec7d0ee31137b5; predecessor encounter_version_baec6e3e7c0b3226a5d5a356c5dc8c4f.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2025-05-30T05:26:00Z: Encounter review: Jennifer Cleveland, age 51. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 91.14 % (record clinical_event_c671dce092309a93ff5f07d8a9a047c1). Heart rate: 108.25 /min (record clinical_event_c68a663f26af1f6f4a2701117536a8f3). Creatinine: 1.23 mg/dL (record clinical_event_a9673ddb9d31681be20b5b55838ddae7). Previously recorded problems: Heart failure, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2025-05-30T05:26:00Z to 2025-06-04T23:26:00Z; acuity 3; HOME; diagnosis I509; episode episode_1cffb747192f11e25aec7d0ee31137b5; predecessor encounter_version_c9ae8c14a25f271e4d230182aedcedd0.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=6, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Furosemide 20 mg PO COMPLETED; Furosemide 20 mg PO COMPLETED.

  PROGRESS_NOTE @ 2025-05-30T09:26:00Z: Assessment update: Jennifer Cleveland, age 51. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Body weight: 67.65 kg (record clinical_event_188546463d00fe830c2a2d3d3dd19d16). Oxygen saturation: 93.96 % (record clinical_event_f5e1715aa61ee3d93cd81d06ebce39f8). Creatinine: 0.91 mg/dL (record clinical_event_ee56601355dcd01ac4ea958db61a11b5). Potassium: 4.37 mmol/L (record clinical_event_f51875e5ebc08ed1169ec976888c5f7d). Previously recorded problems: Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_49a2b03419f6c7fff28e828d4064fe1e). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-06-04T23:26:00Z: Clinical review: Jennifer Cleveland, age 51. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Creatinine: 0.91 mg/dL (record clinical_event_ee56601355dcd01ac4ea958db61a11b5). Creatinine: 0.84 mg/dL (record clinical_event_607ed6d0c11858ec592e9a12739ad85f). Potassium: 4.37 mmol/L (record clinical_event_f51875e5ebc08ed1169ec976888c5f7d). Potassium: 4.07 mmol/L (record clinical_event_759b27426d4ac6ca90c2c905083dbb18). Previously recorded problems: Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_3aa77edf9dde07727dd4d4abd46c3dee). Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2025-10-11T05:09:00Z to 2025-10-11T07:28:00Z; acuity 4; HOME; diagnosis R079; episode episode_985ff57301d2b08d1d38b95fe264b105; predecessor encounter_version_706d945a1a8147e52cd37f2a44aa3cf4.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-10-11T07:28:00Z: Encounter review: Jennifer Cleveland, age 52. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 96.60 % (record clinical_event_336703206fbbe8deeb258ee9189f6626). Heart rate: 95.50 /min (record clinical_event_95d646635d5978891d5fd1eaca308948). Troponin I: 4.82 ng/L (record clinical_event_900f6e6b7f52ed62199c1655284a5363). Previously recorded problems: Heart failure, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2025-12-16T02:38:00Z to 2025-12-16T04:45:00Z; acuity 3; HOME; diagnosis R1010; episode episode_caf403201b17753ee7880a0d9f86f47d; predecessor encounter_version_e075930d8a91bf666299ba210d5c5c40.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-12-16T04:45:00Z: Encounter review: Jennifer Cleveland, age 52. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.23 % (record clinical_event_d882c25510828278c797131542116e93). Heart rate: 102.25 /min (record clinical_event_6535c27a713114ef44c56120ca1151b1). Hemoglobin: 13.57 g/dL (record clinical_event_c1fdc6c76d0a4cdaf3ef5e0c5dc8f708). Previously recorded problems: Heart failure, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 61: Barbara Hickok

Stable patient: patient_b933e87adc4ca4b3c374340a41ff1d03; birth date 1948-03-08; strata: acuity/3, age/65-79, carry/False, long-stay/False, outcome/HOME, pathway/R079, repeat/False, service/ED, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2023-11-17T17:19:00Z to 2023-11-17T19:07:00Z; acuity 3; HOME; diagnosis R079; episode episode_281597156ce865bfd57bbc5e52407df5; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2023-11-17T19:07:00Z: Clinical review: Barbara Hickok, age 75. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 96.09 % (record clinical_event_af8b1a221badd195031bd72344a8114d). Heart rate: 113.75 /min (record clinical_event_e515b2119f5dbfb0954c2c08d11cf193). Troponin I: 6.14 ng/L (record clinical_event_28910bca9e9bb0b90ae67e78032de9ae). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 62: Caleb Pridgen

Stable patient: patient_da2fb46cbd7e6ed85f42e0d256c48240; birth date 1996-07-24; strata: acuity/5, age/18-34, carry/False, long-stay/False, outcome/HOME, pathway/R079, repeat/False, service/ED, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2023-07-11T14:44:00Z to 2023-07-11T16:57:00Z; acuity 5; HOME; diagnosis R079; episode episode_d22090360ad99e833bd7faa479d37104; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2023-07-11T16:57:00Z: Patient review: Caleb Pridgen, age 26. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 96.48 % (record clinical_event_975a9f72b4cc88d787a80001149e1356). Heart rate: 93.25 /min (record clinical_event_968aac7f5f96175da7dfebca67bfb188). Troponin I: 6.56 ng/L (record clinical_event_ed29c5c3a5b44eae64d9c93e0a62bb3f). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 63: Darrell Coffman

Stable patient: patient_8a634c11fe85277943eb9d98b84d1e1c; birth date 1932-12-15; strata: acuity/2, acuity/5, age/80+, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/E119, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- OPD 2024-09-12T15:47:00Z to 2024-09-12T16:49:00Z; acuity 5; HOME; diagnosis R1010; episode episode_e695d56700902171793312f56c44926b; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2024-09-12T16:49:00Z: Clinical review: Darrell Coffman, age 91. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.67 % (record clinical_event_3b327f92f1b03f2c763aba7cc3fd7978). Heart rate: 74.40 /min (record clinical_event_1f79a399198209dcf0163abf6486a579). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Essential (primary) hypertension. Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2025-01-11T09:26:00Z to 2025-01-11T13:26:00Z; acuity 2; TRANSFER; diagnosis E119; episode episode_667697448eb50cfddc1386acfc1bbc1c; predecessor encounter_version_cc4cd4509ce1acf756f02f69f48d7d02.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-01-11T13:26:00Z: Clinical review: Darrell Coffman, age 92. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 97.20 % (record clinical_event_69e92ff148f5b71a3ec5082d95419ee7). Heart rate: 105.00 /min (record clinical_event_02aac95dff47b58f7f837b1f3fd312bd). Serum glucose: 286.00 mg/dL (record clinical_event_46828ba8fabff91c8a0ace5faf82f9db). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Essential (primary) hypertension; Type 2 diabetes mellitus without complications. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2025-01-11T13:26:00Z to 2025-01-16T05:26:00Z; acuity 2; HOME; diagnosis E119; episode episode_667697448eb50cfddc1386acfc1bbc1c; predecessor encounter_version_65f8847a4044387a00f2f5ef8c083c92.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, OBSERVATION=4, ORDER=3, PROCEDURE=1.

  PROGRESS_NOTE @ 2025-01-11T17:26:00Z: Interval assessment: Darrell Coffman, age 92. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Capillary glucose: 260.70 mg/dL (record clinical_event_b4183b2417e167326535e5b0b8eac14c). Heart rate: 99.25 /min (record clinical_event_d0c5caf51e1e082fdf31dad8dd05ceb9). Serum glucose: 260.70 mg/dL (record clinical_event_33e1edee8dfb6a034a3f74ace237a3e4). Creatinine: 0.90 mg/dL (record clinical_event_a82b12d5fa9d3d30805c98f5bded2f84). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Essential (primary) hypertension; Type 2 diabetes mellitus without complications. Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-01-16T05:26:00Z: Care assessment: Darrell Coffman, age 92. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Serum glucose: 260.70 mg/dL (record clinical_event_33e1edee8dfb6a034a3f74ace237a3e4). Serum glucose: 117.00 mg/dL (record clinical_event_c5e5c750c8421061a440268abc84d1b8). Creatinine: 0.90 mg/dL (record clinical_event_a82b12d5fa9d3d30805c98f5bded2f84). Creatinine: 0.80 mg/dL (record clinical_event_eeb83f7537ae79c3e52759cf0acbfcd8). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Essential (primary) hypertension; Type 2 diabetes mellitus without complications. Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 64: William Otoole

Stable patient: patient_82b2dd432d913cc18c231e4e3550a0a5; birth date 1998-12-28; strata: acuity/2, acuity/3, acuity/5, age/18-34, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/J189, pathway/R079, pathway/R1010, repeat/True, service/ED, service/IPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- ED 2025-01-14T23:01:00Z to 2025-01-15T00:59:00Z; acuity 3; HOME; diagnosis R079; episode episode_806557b960e6cd96bbe2b39f136cbd29; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-01-15T00:59:00Z: Care assessment: William Otoole, age 26. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 96.45 % (record clinical_event_5e7897130acbaef6a7f1e8d3f8b3cfbb). Heart rate: 102.25 /min (record clinical_event_4ce884ae5b2873e1ef80855c3f596027). Troponin I: 2.00 ng/L (record clinical_event_fb2196503614c0eb0434f6a05891b12d). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2025-04-15T13:41:00Z to 2025-04-15T15:22:00Z; acuity 5; HOME; diagnosis R1010; episode episode_287bc2cc461f10976f8307baafa870a0; predecessor encounter_version_65e3040df730e358372e216ae764516e.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2025-04-15T15:22:00Z: Encounter review: William Otoole, age 26. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 98.43 % (record clinical_event_5b947c2f0f108308f97a5fc7c22bf6db). Heart rate: 98.50 /min (record clinical_event_093003091e613df26320a7e3adfab81f). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2025-08-23T22:27:00Z to 2025-08-24T02:27:00Z; acuity 2; TRANSFER; diagnosis J189; episode episode_b6042cf9292c09b35c37ce79f56eae28; predecessor encounter_version_3903fd3a54dd811999fdb81dfb93b017.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=1.
  Treatment evidence: Doxycycline 1400 mg PO COMPLETED.

  ED_NOTE @ 2025-08-24T02:27:00Z: Clinical review: William Otoole, age 26. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Oxygen saturation: 91.98 % (record clinical_event_91f7c50e78869ea4f597570b58ff8a3c). Heart rate: 100.75 /min (record clinical_event_da71448776a3941cdf6169b137489d17). Prior problem documentation is incomplete; absence of a record does not exclude disease. Doxycycline 1400 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_ee41dd018c4add1c8b5132cf02148dd1). Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2025-08-24T02:27:00Z to 2025-08-30T12:27:00Z; acuity 2; HOME; diagnosis J189; episode episode_b6042cf9292c09b35c37ce79f56eae28; predecessor encounter_version_80e805504ae78ff74b3be1de23799d07.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=13, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Doxycycline 100 mg PO COMPLETED; Doxycycline 100 mg PO COMPLETED.

  PROGRESS_NOTE @ 2025-08-24T06:27:00Z: Assessment update: William Otoole, age 26. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Body temperature: 38.01 Cel (record clinical_event_e154303b71601848e175af29b5f0e2ed). Oxygen saturation: 90.15 % (record clinical_event_f456d40a6508b4feb2e941698cfd9dac). White blood cell count: 12.85 10*3/uL (record clinical_event_b699b489913e1686246b1bd617bd63d2). C-reactive protein: 66.12 mg/L (record clinical_event_4734014bb6f6319043eeebbdb0fc71cc). Prior problem documentation is incomplete; absence of a record does not exclude disease. Doxycycline 100 mg administered (record clinical_event_99ee06a6d6d9d75235ed44fc7ce0452b). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-08-30T12:27:00Z: Patient review: William Otoole, age 26. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. White blood cell count: 12.85 10*3/uL (record clinical_event_b699b489913e1686246b1bd617bd63d2). White blood cell count: 9.67 10*3/uL (record clinical_event_8fb8f1aa68ccbf27d77a1b19c5cdf395). C-reactive protein: 66.12 mg/L (record clinical_event_4734014bb6f6319043eeebbdb0fc71cc). C-reactive protein: 14.32 mg/L (record clinical_event_e798c04b2afe85d6331034df40a77d20). Prior problem documentation is incomplete; absence of a record does not exclude disease. Doxycycline 100 mg administered (record clinical_event_12fc87db8b0683e2ff206d918e4ec66b). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 65: John Bailey

Stable patient: patient_63a47fecc20a4dc201e0817dbcc7333f; birth date 1966-02-05; strata: acuity/2, acuity/3, acuity/4, acuity/5, age/50-64, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/J449, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- ED 2023-09-05T20:15:00Z to 2023-09-06T00:15:00Z; acuity 2; TRANSFER; diagnosis J449; episode episode_fe506565e2ba5e55f9d46a96676df5d4; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2023-09-06T00:15:00Z: Clinical review: John Bailey, age 57. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 92.94 % (record clinical_event_4bf65e72e0f2340502d3ccbe089a6934). Heart rate: 114.75 /min (record clinical_event_4a3de9aede28239d51351c555e8fbb52). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- IPD 2023-09-06T00:15:00Z to 2023-09-10T13:15:00Z; acuity 3; HOME; diagnosis J449; episode episode_fe506565e2ba5e55f9d46a96676df5d4; predecessor encounter_version_9f73c10f0bf0caa3075c32bba73bf260.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=5, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Prednisone 40 mg PO COMPLETED; Prednisone 40 mg PO COMPLETED.

  PROGRESS_NOTE @ 2023-09-06T04:15:00Z: Encounter review: John Bailey, age 57. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 93.57 % (record clinical_event_35c3572cb0a438bb685b650745981330). Respiratory rate: 27.10 /min (record clinical_event_944d71cf8572744050bea827a87f455e). White blood cell count: 18.60 10*3/uL (record clinical_event_ef7c34faf70629070c44c69052f42b1d). Bicarbonate: 28.47 mmol/L (record clinical_event_e2031c78c2ab24ef7b5b2b1a92d26a5b). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Prednisone 40 mg administered (record clinical_event_fddc1c12c1df9c40d440484e5eeda15d). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-09-10T13:15:00Z: Interval assessment: John Bailey, age 57. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. White blood cell count: 18.60 10*3/uL (record clinical_event_ef7c34faf70629070c44c69052f42b1d). White blood cell count: 9.79 10*3/uL (record clinical_event_8278fce054048ecf727f6e1aa3d2e7a7). Bicarbonate: 28.47 mmol/L (record clinical_event_e2031c78c2ab24ef7b5b2b1a92d26a5b). Bicarbonate: 27.47 mmol/L (record clinical_event_6b614f30d2e554299dae7dbad02dc8d3). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Prednisone 40 mg administered (record clinical_event_783b7f3359355941098b61025d180664). Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2024-05-06T09:07:00Z to 2024-05-06T11:33:00Z; acuity 5; HOME; diagnosis J449; episode episode_70301c5559b42a4fb013b0234725714a; predecessor encounter_version_54eafea2e8ccfd315dda6e061309b818.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2024-05-06T11:33:00Z: Clinical review: John Bailey, age 58. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 94.59 % (record clinical_event_76010a6cc8aaef00cd462b659f66ae8f). Heart rate: 102.50 /min (record clinical_event_a8a31be93df5f15634b4aedb5bf9a8db). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- OPD 2024-10-21T18:25:00Z to 2024-10-21T20:18:00Z; acuity 5; HOME; diagnosis J449; episode episode_e8e7ae59f10b0c34a4c574f42d57aa8b; predecessor encounter_version_0b9624570b105ec99d327fdbcaf96acd.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2024-10-21T20:18:00Z: Patient review: John Bailey, age 58. Interval follow-up for increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 95.99 % (record clinical_event_191b5aa4e9c05a2cef8a7801b6fe9251). Heart rate: 84.45 /min (record clinical_event_0e0587d249102e2bb73734ab2ab38b66). White blood cell count: 15.37 10*3/uL (record clinical_event_6656b323bf175dba9f923ad17049eae6). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- OPD 2025-03-24T15:21:00Z to 2025-03-24T17:02:00Z; acuity 4; HOME; diagnosis R1010; episode episode_3c002d2d25a2a7459a193a07dd7b5db2; predecessor encounter_version_ae1af6ad8aa808e898872723afcb1164.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2025-03-24T17:02:00Z: Assessment update: John Bailey, age 59. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.80 % (record clinical_event_91f88221ef8d4c912989d8a140a5735d). Heart rate: 85.50 /min (record clinical_event_521262943c63aea6487ec97870ad0220). Hemoglobin: 13.82 g/dL (record clinical_event_e75d237b489ccd3336fd9240bcf7e401). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 66: James Gregory

Stable patient: patient_d6b3cbbde975960f3494bc318c574426; birth date 1977-08-15; strata: acuity/2, acuity/4, acuity/5, age/35-49, carry/False, long-stay/False, outcome/HOME, pathway/I509, pathway/R079, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- ED 2025-02-08T05:03:00Z to 2025-02-08T06:57:00Z; acuity 4; HOME; diagnosis R079; episode episode_af0f4659e1151963e470e2e3a7df7926; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-02-08T06:57:00Z: Care assessment: James Gregory, age 47. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.17 % (record clinical_event_77b627d608d32b8f76553a9f500c952a). Heart rate: 112.25 /min (record clinical_event_b96bd46633656fc403ce8af60aa924f6). Troponin I: 2.72 ng/L (record clinical_event_56711187ab5fa1f0bd53f6e3a4fbf1ec). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- OPD 2025-07-02T17:55:00Z to 2025-07-02T19:34:00Z; acuity 5; HOME; diagnosis R079; episode episode_3f2ce33337af07f3a29c51489cbb1b14; predecessor encounter_version_2cceb386eb35fa85129de3d8e5483477.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2025-07-02T19:34:00Z: Clinical review: James Gregory, age 47. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.71 % (record clinical_event_f31721f520d962e2b04148a4d108cd5e). Heart rate: 82.50 /min (record clinical_event_26fd06ccbfb84646af384f605e58e53c). Troponin I: 7.40 ng/L (record clinical_event_d1bf71ce65e62a2d7a1ce715738cd0dc). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2025-08-26T18:49:00Z to 2025-08-30T18:49:00Z; acuity 2; HOME; diagnosis I509; episode episode_4dd3e0d74a12bd0f5da02fbd99474750; predecessor encounter_version_b9534b0756c4788283319a638a21783c.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=4, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Furosemide 20 mg PO COMPLETED; Furosemide 20 mg PO COMPLETED.

  PROGRESS_NOTE @ 2025-08-26T22:49:00Z: Patient review: James Gregory, age 48. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Body weight: 72.21 kg (record clinical_event_f744daab7b5dbbfe4bdb01b212ea8576). Oxygen saturation: 90.27 % (record clinical_event_80560943cddfccdd3b1eab9300bd6437). Creatinine: 1.20 mg/dL (record clinical_event_66183d3e713a63b3ed29b61b03437fe4). Potassium: 4.26 mmol/L (record clinical_event_1d1d8410cd63a729a704339cbf2dfd3f). Previously recorded problems: Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_93bea165931d25661ec95b2ad16f32e4). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-08-30T18:49:00Z: Clinical review: James Gregory, age 48. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Creatinine: 1.20 mg/dL (record clinical_event_66183d3e713a63b3ed29b61b03437fe4). Creatinine: 1.10 mg/dL (record clinical_event_bb3690cf314f7e1c61f414a9339b2420). Potassium: 4.26 mmol/L (record clinical_event_1d1d8410cd63a729a704339cbf2dfd3f). Potassium: 3.96 mmol/L (record clinical_event_2202da4ef19e30e323b41ccad8851a76). Previously recorded problems: Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_732e4a8cdcd9564a957a628127964f1d). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 67: Phyllis Kincade

Stable patient: patient_0e1dcd750c00ba57243e2f6f1b9214b8; birth date 1936-06-06; strata: acuity/2, acuity/3, acuity/4, acuity/5, age/80+, carry/False, long-stay/False, long-stay/True, outcome/HOME, pathway/J449, pathway/R079, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2023-04-07T11:10:00Z to 2023-04-07T13:25:00Z; acuity 4; HOME; diagnosis R079; episode episode_c9d80e48ad767078118a5bdb469a75ac; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2023-04-07T13:25:00Z: Encounter review: Phyllis Kincade, age 86. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 98.79 % (record clinical_event_898f676bfbd8ad0ddc0ec07f4d71db06). Heart rate: 113.25 /min (record clinical_event_cc504206e42b1f09758ecc988901fbbd). Troponin I: 3.08 ng/L (record clinical_event_dd21edc477f11daa70cdb5fe0c0fe5a4). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified; Essential (primary) hypertension. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2023-11-25T06:53:00Z to 2023-12-10T07:53:00Z; acuity 2; HOME; diagnosis J449; episode episode_8d3245a17ed226a0f0add8fb404d21e1; predecessor encounter_version_bccf12ff218e7d882d3ec38bd55ab318.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=5, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Prednisone 40 mg PO COMPLETED; Prednisone 40 mg PO COMPLETED.

  PROGRESS_NOTE @ 2023-11-25T10:53:00Z: Encounter review: Phyllis Kincade, age 87. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 92.37 % (record clinical_event_7a861d7e6bd90af0a24a5412783d834e). Respiratory rate: 28.60 /min (record clinical_event_109101d8ec7c21a5ade42de117eb1d68). White blood cell count: 15.56 10*3/uL (record clinical_event_85ba7cbe6b0304bf4ad252bc393b007b). Bicarbonate: 28.44 mmol/L (record clinical_event_6d334688fa008d3e88bedc4e0d63e750). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified; Essential (primary) hypertension. Prednisone 40 mg administered (record clinical_event_b1dd5299c8f76f504314012e8d1fd50b). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-12-10T07:53:00Z: Care assessment: Phyllis Kincade, age 87. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. White blood cell count: 15.56 10*3/uL (record clinical_event_85ba7cbe6b0304bf4ad252bc393b007b). White blood cell count: 8.38 10*3/uL (record clinical_event_bb5bb87e332ac4bbbad614f709ac66ce). Bicarbonate: 28.44 mmol/L (record clinical_event_6d334688fa008d3e88bedc4e0d63e750). Bicarbonate: 27.44 mmol/L (record clinical_event_acb2892091c6058657b267a10c05be1d). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified; Essential (primary) hypertension. Prednisone 40 mg administered (record clinical_event_e9153c982d9c7033f402da3a1c339fa0). Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2024-06-14T15:41:00Z to 2024-06-14T16:57:00Z; acuity 5; HOME; diagnosis J449; episode episode_6e2297cbcc2c6a6b063183cd107f22f6; predecessor encounter_version_b6affcc05ab7ce3cfc71dc7fdc060212.
  Captured evidence: DOCUMENT=1, OBSERVATION=2, ORDER=1, PROCEDURE=1.

  OP_NOTE @ 2024-06-14T16:57:00Z: Interval assessment: Phyllis Kincade, age 88. Interval follow-up for increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 95.68 % (record clinical_event_b3380a9e7c627f872bba8597a0139e15). Heart rate: 73.95 /min (record clinical_event_ad44192555e7002ed249fabbd599f352). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified; Essential (primary) hypertension. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- OPD 2024-10-11T18:41:00Z to 2024-10-11T20:19:00Z; acuity 5; HOME; diagnosis J449; episode episode_a73387c32d46e0f119c52bd08f9f6a64; predecessor encounter_version_91a10dcba39805d1095c9bd59f673e07.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=3, PROCEDURE=1.
  Treatment evidence: Prednisone 200 mg PO COMPLETED.

  OP_NOTE @ 2024-10-11T20:19:00Z: Clinical review: Phyllis Kincade, age 88. Interval follow-up for increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 95.73 % (record clinical_event_ddd484a910ca53806530d3edb3739931). Heart rate: 79.05 /min (record clinical_event_22366c377bf6fdd28960fb8da816c531). White blood cell count: 16.42 10*3/uL (record clinical_event_940ca3daf178bfe4cffc10570603c375). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified; Essential (primary) hypertension. Prednisone 200 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_7e140bd73eb79aeb7a4e0eb4da78ef47). The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2025-11-08T20:49:00Z to 2025-11-08T22:42:00Z; acuity 3; HOME; diagnosis J449; episode episode_1b375a3ae78a80d26fb68cee3ed2b4b8; predecessor encounter_version_7fb76f686c3803d53863dc763681d995.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-11-08T22:42:00Z: Assessment update: Phyllis Kincade, age 89. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 95.64 % (record clinical_event_a1301589f026168658874e6fa6e0ce97). Heart rate: 112.00 /min (record clinical_event_f5fdb7b4189374d2db16cce6c863478d). White blood cell count: 18.00 10*3/uL (record clinical_event_b930825ae254cf0fa75c7f8f6874ecc4). Previously recorded problems: Chronic kidney disease, unspecified; Chronic obstructive pulmonary disease, unspecified; Essential (primary) hypertension. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 68: Donna Dugan

Stable patient: patient_e67d26752e42b04460f02b4c26cba69b; birth date 1961-09-12; strata: acuity/3, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/R1010, repeat/False, service/ED, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2023-09-07T18:28:00Z to 2023-09-07T21:09:00Z; acuity 3; HOME; diagnosis R1010; episode episode_d17c4574c10f739041140dbb16a2174a; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2023-09-07T21:09:00Z: Clinical review: Donna Dugan, age 61. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 96.42 % (record clinical_event_991349696826669069a84762a88330e6). Heart rate: 113.00 /min (record clinical_event_d026b9762ac5bd21d2fc883f7c9367de). Previously recorded problems: Heart failure, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 69: Peggy Doyle

Stable patient: patient_d4d27ebe7c7a8f18ac5a41bb010d0e16; birth date 1950-08-11; strata: acuity/3, age/65-79, carry/False, long-stay/False, outcome/HOME, pathway/R1010, repeat/False, service/ED, site/facility_7990133218ef060b178c3cf8a0825f76.

- ED 2025-04-01T06:40:00Z to 2025-04-01T08:32:00Z; acuity 3; HOME; diagnosis R1010; episode episode_a4cc125357443eec786b1d2940346420; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2025-04-01T08:32:00Z: Patient review: Peggy Doyle, age 74. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.62 % (record clinical_event_32c9febb401ffb86897ffd2d21ca4d06). Heart rate: 98.25 /min (record clinical_event_46602fb0d8d9001d9d063d8e2c0816b9). Hemoglobin: 14.35 g/dL (record clinical_event_daf7a828d67c21e2c66edbb7f80e4411). Previously recorded problems: Type 2 diabetes mellitus without complications. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 70: Paula Redfield

Stable patient: patient_2aa742ff67a7f1ab766fc60a25278b2d; birth date 1962-04-28; strata: acuity/2, acuity/3, acuity/4, acuity/5, age/50-64, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/J189, pathway/J449, pathway/R079, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- OPD 2023-05-08T14:06:00Z to 2023-05-08T14:52:00Z; acuity 3; HOME; diagnosis R079; episode episode_3dcd29b9fbf7dd4b3f8692365d001260; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2023-05-08T14:52:00Z: Patient review: Paula Redfield, age 61. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.04 % (record clinical_event_aec47bc86e5e8f8192d9ba97bebf2722). Heart rate: 80.70 /min (record clinical_event_4589e9669378f334cdb71246ecc21d0c). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- OPD 2023-09-11T19:43:00Z to 2023-09-11T21:13:00Z; acuity 5; HOME; diagnosis R1010; episode episode_2d836b8c164207fbff8e52ae813997ff; predecessor encounter_version_9aa5aa93a8e237cbbc02b3f27454d2f2.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  OP_NOTE @ 2023-09-11T21:13:00Z: Patient review: Paula Redfield, age 61. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.40 % (record clinical_event_7f596355aa1ba684539caccf6a1fe3fc). Heart rate: 82.50 /min (record clinical_event_f613565122c4d1c8894392514cb09823). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_fa01da9c4eabc18031e03a9fafb0044b). The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2023-11-22T00:38:00Z to 2023-11-22T03:20:00Z; acuity 4; HOME; diagnosis R1010; episode episode_1df4bd6f426d2d7fc3597e65206a298c; predecessor encounter_version_ebf1daa4ae5a21f61cb563331c638a96.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=1.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  ED_NOTE @ 2023-11-22T03:20:00Z: Clinical review: Paula Redfield, age 61. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 96.00 % (record clinical_event_c3cbfe6362c353d403b6ec287dd7dfc0). Heart rate: 93.75 /min (record clinical_event_c86b1d58bce022a70e081a7063a7cf6d). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_bb065f5039b65ac8f29c5a35766dfa82). Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2024-01-11T08:24:00Z to 2024-01-11T10:54:00Z; acuity 5; HOME; diagnosis R1010; episode episode_907b7f10b673e1b6e8f4c273a8e048cd; predecessor encounter_version_3ae83af21976640ef031b1f3aa2073e9.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=1.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  ED_NOTE @ 2024-01-11T10:54:00Z: Care assessment: Paula Redfield, age 61. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.98 % (record clinical_event_5dc9851faba0847fc56e09385eb7014f). Heart rate: 110.50 /min (record clinical_event_dd1b59bdb7ee49a0385f1a3ede8e67f6). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_37ee2c99135f801793806ec80d738337). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- OPD 2025-02-10T21:54:00Z to 2025-02-10T22:37:00Z; acuity 5; HOME; diagnosis J189; episode episode_659ac2276c96925355fa4a210f585aef; predecessor encounter_version_04d3cf2d3b088a4acc9a66654c7483df.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.
  Treatment evidence: Doxycycline 1400 mg PO COMPLETED.

  OP_NOTE @ 2025-02-10T22:37:00Z: Assessment update: Paula Redfield, age 62. Interval follow-up for cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Oxygen saturation: 97.95 % (record clinical_event_61fd589b4a92fa9b7dda19067bf8b116). Heart rate: 73.50 /min (record clinical_event_92cad6d0800979a47f3eea60e038109c). Prior problem documentation is incomplete; absence of a record does not exclude disease. Doxycycline 1400 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_d0b922bdfdc937162b7506a71ca7f4c8). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2025-03-27T15:32:00Z to 2025-03-27T17:48:00Z; acuity 5; HOME; diagnosis R1010; episode episode_5a198436d3b305962e50e00d020859c2; predecessor encounter_version_ae04616ad8704e67cdd1f4d517a67438.
  Captured evidence: DOCUMENT=1, OBSERVATION=2, ORDER=1, PROCEDURE=1.

  ED_NOTE @ 2025-03-27T17:48:00Z: Interval assessment: Paula Redfield, age 62. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 98.43 % (record clinical_event_bcbd36631a02ee4d038f4c906bc8f405). Heart rate: 107.00 /min (record clinical_event_c8bf20d7aae8f3e3f4f5cc1611650661). Prior problem documentation is incomplete; absence of a record does not exclude disease. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2025-10-26T18:37:00Z to 2025-10-26T22:37:00Z; acuity 2; TRANSFER; diagnosis J449; episode episode_cfa988189ff19660a67588e74119ca9d; predecessor encounter_version_1b682b3866707625dfd5d68728b4fa96.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2025-10-26T22:37:00Z: Interval assessment: Paula Redfield, age 63. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 92.94 % (record clinical_event_f8f63ec6b7efdedb919e62adb42dc968). Heart rate: 106.75 /min (record clinical_event_93736e6f8955e6b64b726647b23660da). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- IPD 2025-10-26T22:37:00Z to 2025-10-31T11:37:00Z; acuity 3; HOME; diagnosis J449; episode episode_cfa988189ff19660a67588e74119ca9d; predecessor encounter_version_ee4c55ca2da47b1c1f80915c473c5379.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=5, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Prednisone 40 mg PO COMPLETED; Prednisone 40 mg PO COMPLETED.

  PROGRESS_NOTE @ 2025-10-27T02:37:00Z: Patient review: Paula Redfield, age 63. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 94.77 % (record clinical_event_dad43714934b9e90138f298a91d6f8e2). Respiratory rate: 24.85 /min (record clinical_event_2ebc9dc07f1ece78c7c3a3e162a4f209). White blood cell count: 15.29 10*3/uL (record clinical_event_110f193b2a361234fcfa766fe4b5ad63). Bicarbonate: 27.54 mmol/L (record clinical_event_60bed859b46a9a20a80b48de1064fc3d). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Prednisone 40 mg administered (record clinical_event_fa2a195971e2636ebf85c5cc9dc694cb). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-10-31T11:37:00Z: Patient review: Paula Redfield, age 63. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. White blood cell count: 15.29 10*3/uL (record clinical_event_110f193b2a361234fcfa766fe4b5ad63). White blood cell count: 9.55 10*3/uL (record clinical_event_759a5637c0f5391639cf40f5e2b20a34). Bicarbonate: 27.54 mmol/L (record clinical_event_60bed859b46a9a20a80b48de1064fc3d). Bicarbonate: 26.54 mmol/L (record clinical_event_a8fa110279c15057c27a78644267ceeb). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Prednisone 40 mg administered (record clinical_event_3e33d962a5986bf1e11251dc1af0cf0c). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 71: Jacob Johnston

Stable patient: patient_51b420aa9cea78b1f51d3664350e0fd3; birth date 2000-04-27; strata: acuity/3, age/18-34, carry/False, long-stay/False, outcome/HOME, pathway/R079, repeat/False, service/OPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- OPD 2023-07-25T16:37:00Z to 2023-07-25T18:19:00Z; acuity 3; HOME; diagnosis R079; episode episode_c4bd0d7726f8140a5faf93817e5b9871; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2023-07-25T18:19:00Z: Assessment update: Jacob Johnston, age 23. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.77 % (record clinical_event_ea2f5d6a54a2f85af4ea1866ca950da7). Heart rate: 73.05 /min (record clinical_event_56c998d0fb57d3c312de94eb8c19d977). Troponin I: 7.52 ng/L (record clinical_event_1a926068f0a0230f1bd01162a76d271f). Prior problem documentation is incomplete; absence of a record does not exclude disease. The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 72: Matthew Wilson

Stable patient: patient_e588896188d3422a6594df1a0de69999; birth date 1978-02-28; strata: acuity/3, acuity/4, acuity/5, age/35-49, carry/False, long-stay/False, outcome/HOME, pathway/E119, pathway/K8010, pathway/R079, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- OPD 2022-12-25T06:00:00Z to 2022-12-25T08:00:00Z; acuity 5; HOME; diagnosis E119; episode episode_8c338360b47379a8f50c7dad8dffafbc; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  OP_NOTE @ 2022-12-25T08:00:00Z: Clinical review: Matthew Wilson, age 44. Interval follow-up for symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 97.19 % (record clinical_event_8423814dcab0e2c2f8fe368741a31f8d). Heart rate: 86.10 /min (record clinical_event_40966758820bbe961961a0c5282b75dd). Previously recorded problems: Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2024-02-13T06:01:00Z to 2024-02-13T08:41:00Z; acuity 4; HOME; diagnosis R079; episode episode_ecbfab2a2736a8b798bea0ea378f8fbe; predecessor encounter_version_11ff73d906fbdf39858441c23a53226b.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2024-02-13T08:41:00Z: Interval assessment: Matthew Wilson, age 45. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 96.96 % (record clinical_event_f5541a0e9e9acb0dc7c28c69c6bfa425). Heart rate: 108.75 /min (record clinical_event_82dd9cbc0da56106e8c270d607dc2adf). Troponin I: 4.04 ng/L (record clinical_event_4aba1b5c75551f66239e342f03b39354). Previously recorded problems: Type 2 diabetes mellitus without complications. Continue assessment as results become available. Follow-up completion is not established by this document.
- OPD 2024-11-27T21:56:00Z to 2024-11-27T22:55:00Z; acuity 3; HOME; diagnosis R1010; episode episode_ca45c3d81a3f7154da4fb59eb2c645e6; predecessor encounter_version_1e1cb329eb2cf93e15cebe90c440e47f.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=1.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  OP_NOTE @ 2024-11-27T22:55:00Z: Assessment update: Matthew Wilson, age 46. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.42 % (record clinical_event_772b4a0dcfa4af5a50de787c7eccfdc0). Heart rate: 73.95 /min (record clinical_event_44e47cc1fbf292304f1a4d70ae1b7596). Previously recorded problems: Type 2 diabetes mellitus without complications. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_189af5888d951fe5633369ee01594d52). The current assessment may change with further evidence. Follow-up completion is not established by this document.
- IPD 2025-09-16T15:20:00Z to 2025-09-20T16:20:00Z; acuity 3; HOME; diagnosis K8010; episode episode_270bd3ce97f378b81da86166ce35d0ed; predecessor encounter_version_77427ca5165efc49749f5931269649d1.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=10, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2025-09-17T01:20:00Z: Patient review: Matthew Wilson, age 47. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 7.00 1 (record clinical_event_278200e3a7bbcd8c3d238b0e182e281f). Heart rate: 107.00 /min (record clinical_event_6959f3d86e77e069e316489529257568). Hemoglobin: 13.84 g/dL (record clinical_event_672d06d8df2d85b5f563ee14d22a3c30). Creatinine: 1.11 mg/dL (record clinical_event_2adda8954ed504e25277e35cbf5298de). Previously recorded problems: Type 2 diabetes mellitus without complications. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_03f81b1289036ed64c83f61e54f7e162). Acetaminophen 650 mg administered (record clinical_event_d2967f3e2582d94cea8d1472c07315f0). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-09-20T16:20:00Z: Patient review: Matthew Wilson, age 47. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 13.84 g/dL (record clinical_event_672d06d8df2d85b5f563ee14d22a3c30). Hemoglobin: 13.14 g/dL (record clinical_event_608a50f07076b8878560a3ffa6e10dda). Creatinine: 1.11 mg/dL (record clinical_event_2adda8954ed504e25277e35cbf5298de). Creatinine: 0.94 mg/dL (record clinical_event_7c1348466f3641b40023aab4063152cf). Previously recorded problems: Type 2 diabetes mellitus without complications. Acetaminophen 650 mg administered (record clinical_event_d4032018992bbb83d6b879bfe3d80e72). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 73: Donna May

Stable patient: patient_aeddddd8dbcbc4b8038812a7c4f7855d; birth date 1964-12-18; strata: acuity/2, acuity/5, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/K8010, pathway/R079, repeat/True, service/IPD, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- IPD 2023-04-06T14:43:00Z to 2023-04-11T14:43:00Z; acuity 2; HOME; diagnosis K8010; episode episode_07d9459aa484a69696d8767199003c0b; predecessor none.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=16, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2023-04-07T00:43:00Z: Patient review: Donna May, age 58. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 6.00 1 (record clinical_event_307fe7e6cd5521fd9202074fd0a066d1). Heart rate: 103.50 /min (record clinical_event_c88a9b32c84b1bec69a4ff5eea402149). Hemoglobin: 14.29 g/dL (record clinical_event_5ce1d82db29b89400912d8453ceb876b). Creatinine: 1.20 mg/dL (record clinical_event_37b714b96ad2c2672dedc07f49794fbb). Prior problem documentation is incomplete; absence of a record does not exclude disease. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_066d026a8762da8e87f6e378a40740ff). Acetaminophen 650 mg administered (record clinical_event_392254575843d9f2429ed2646099d3a3). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-04-11T14:43:00Z: Assessment update: Donna May, age 58. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 14.29 g/dL (record clinical_event_5ce1d82db29b89400912d8453ceb876b). Hemoglobin: 13.59 g/dL (record clinical_event_61dde9d1dd0499c77437e5f953b95e0b). Creatinine: 1.20 mg/dL (record clinical_event_37b714b96ad2c2672dedc07f49794fbb). Creatinine: 1.07 mg/dL (record clinical_event_b6d0af16889316c09f20a7735f18d9e8). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 650 mg administered (record clinical_event_629a507f4db77dcbb84c6ea01bc67fa0). Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2025-06-16T15:35:00Z to 2025-06-16T16:23:00Z; acuity 5; HOME; diagnosis R079; episode episode_dadc49fa194be2ca6b2326165201b4b8; predecessor encounter_version_7b4f94acf01cb0eb0b6da32701df6921.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2025-06-16T16:23:00Z: Interval assessment: Donna May, age 60. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.83 % (record clinical_event_34bf592b330066b55f5d7a92946c8f21). Heart rate: 78.15 /min (record clinical_event_379170d12fdad83eeb716e2c7af543cc). Prior problem documentation is incomplete; absence of a record does not exclude disease. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- OPD 2025-09-10T19:34:00Z to 2025-09-10T20:22:00Z; acuity 5; HOME; diagnosis R079; episode episode_f04ff84e7eec72f9f294b96ab393120f; predecessor encounter_version_a07e80a6117feac37202b02f82d33711.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2025-09-10T20:22:00Z: Encounter review: Donna May, age 60. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.27 % (record clinical_event_8eb0d3f417c2f60fda6567655326f0c6). Heart rate: 80.55 /min (record clinical_event_d7d158e0e127047125623dae5b5fb757). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 74: Albert Gunter

Stable patient: patient_bf27c68473f76856129ac84ffafd82dc; birth date 1950-12-29; strata: acuity/3, age/65-79, carry/False, long-stay/False, outcome/HOME, pathway/E119, repeat/False, service/ED, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- ED 2023-09-10T02:36:00Z to 2023-09-10T04:34:00Z; acuity 3; HOME; diagnosis E119; episode episode_c18b3aed7e5da4fb5e7f5ebea7a995e2; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2023-09-10T04:34:00Z: Interval assessment: Albert Gunter, age 72. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 98.61 % (record clinical_event_73c5a1b63b1af03a84c115500fd57e0c). Heart rate: 112.25 /min (record clinical_event_3733d9f2b73b53f2639316eab1814e67). Previously recorded problems: Type 2 diabetes mellitus without complications. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 75: Gary Mitchell

Stable patient: patient_b3c06a8abada6f4a89028668dea1fb38; birth date 1955-12-28; strata: acuity/3, age/65-79, carry/False, long-stay/False, outcome/HOME, pathway/J189, repeat/False, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- OPD 2023-10-23T16:57:00Z to 2023-10-23T17:39:00Z; acuity 3; HOME; diagnosis J189; episode episode_1c31a2579f74065d446f052025d71cfd; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  OP_NOTE @ 2023-10-23T17:39:00Z: Care assessment: Gary Mitchell, age 67. Interval follow-up for cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Oxygen saturation: 97.65 % (record clinical_event_061784e40bfc3eb8089341ab16401ffc). Heart rate: 84.45 /min (record clinical_event_3262d3f41c73430d61bf31b996d6e1c5). Previously recorded problems: Heart failure, unspecified; Hyperlipidemia, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 76: Ann Hurtado

Stable patient: patient_54a7ba3a3db499c295df05146d9d47d0; birth date 1961-05-21; strata: acuity/5, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/R1010, repeat/False, service/ED, site/facility_7990133218ef060b178c3cf8a0825f76.

- ED 2024-01-28T15:48:00Z to 2024-01-28T18:25:00Z; acuity 5; HOME; diagnosis R1010; episode episode_eeee6a22500d2d2ad584fc49d4387645; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2024-01-28T18:25:00Z: Care assessment: Ann Hurtado, age 62. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.26 % (record clinical_event_0df43ca0262e002d6b631a3c55113389). Heart rate: 104.25 /min (record clinical_event_f6dbb76639bc346a13caac104cf23da2). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 77: Zachary Anderson

Stable patient: patient_1ac93348d659de458bfb47917725a3d2; birth date 1972-12-06; strata: acuity/2, acuity/3, acuity/4, acuity/5, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/J189, pathway/R079, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- ED 2023-04-05T02:28:00Z to 2023-04-05T04:50:00Z; acuity 3; HOME; diagnosis R1010; episode episode_3db207ac264a4822c4fc20f37e455048; predecessor none.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=1.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  ED_NOTE @ 2023-04-05T04:50:00Z: Clinical review: Zachary Anderson, age 50. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.38 % (record clinical_event_6c3b7598438dcdbce533f58406e7352e). Heart rate: 103.50 /min (record clinical_event_f17f468e6f7f68b2a9b50a39b8506ab5). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_50589bb347bed0c2647eae3eb96b6103). The current assessment may change with further evidence. Follow-up completion is not established by this document.
- OPD 2023-06-20T16:44:00Z to 2023-06-20T18:10:00Z; acuity 3; HOME; diagnosis R079; episode episode_24bf0774fc26e512bf28e81456a40fd5; predecessor encounter_version_ba4095dfe7c167cfd872ee579c9babcb.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2023-06-20T18:10:00Z: Assessment update: Zachary Anderson, age 50. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.61 % (record clinical_event_8d2625750369aa256c122c04e5454a16). Heart rate: 72.60 /min (record clinical_event_42251316ca2745d067af1ec2d8fca547). Troponin I: 2.30 ng/L (record clinical_event_6727c1c37c6a925127572d63751a2ea3). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2024-04-30T22:17:00Z to 2024-05-01T01:15:00Z; acuity 4; HOME; diagnosis R079; episode episode_1faa54ea34f20f799d9a5881ab416bfd; predecessor encounter_version_510e1ae9b07e02f7bdacc8d6a63ffaab.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2024-05-01T01:15:00Z: Care assessment: Zachary Anderson, age 51. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 96.99 % (record clinical_event_ef8d2309a22fdc11c19e2a4b1c52fa5e). Heart rate: 97.25 /min (record clinical_event_171d90870dfbd3829c8937356ae6753c). Troponin I: 3.68 ng/L (record clinical_event_7f7d2d67d663552de1b6214e4f1f8d51). Prior problem documentation is incomplete; absence of a record does not exclude disease. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2024-05-18T03:33:00Z to 2024-05-18T05:54:00Z; acuity 4; HOME; diagnosis R079; episode episode_114ac8a1982c9ca0ffa0a9a97cc7857c; predecessor encounter_version_cc3ee172ac0a06206ddfef599caf08e8.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2024-05-18T05:54:00Z: Assessment update: Zachary Anderson, age 51. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 98.37 % (record clinical_event_e294edee09064bb2c250c6fef030cc7d). Heart rate: 106.50 /min (record clinical_event_3c3e2b6467bfcb1a392987b4c62198a1). Troponin I: 6.68 ng/L (record clinical_event_b4e1305fc7de33e71cde7b6e2638b162). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- OPD 2025-03-17T21:13:00Z to 2025-03-17T21:48:00Z; acuity 3; HOME; diagnosis R1010; episode episode_71aa5cadb80bc7c35fa8a29958991d6f; predecessor encounter_version_0209cb1a2a3065520f816ef1919923a0.
  Captured evidence: DOCUMENT=1, OBSERVATION=2, ORDER=1, PROCEDURE=1.

  OP_NOTE @ 2025-03-17T21:48:00Z: Clinical review: Zachary Anderson, age 52. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.98 % (record clinical_event_f72c48415af597ce9e86d7bae02086c6). Heart rate: 83.25 /min (record clinical_event_c6fec37548db035da1eebfed3f508607). Prior problem documentation is incomplete; absence of a record does not exclude disease. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- OPD 2025-08-27T17:44:00Z to 2025-08-27T18:44:00Z; acuity 5; HOME; diagnosis R079; episode episode_ebe93f2b4ae105809a0f3b4fe155827d; predecessor encounter_version_a559405195e1afa2a045a8e76ec30af2.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2025-08-27T18:44:00Z: Assessment update: Zachary Anderson, age 52. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.94 % (record clinical_event_aa76a45b40d2ffef7f6bab14b61a8220). Heart rate: 79.65 /min (record clinical_event_281802dd399b87efad893ced2963adbc). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2025-09-13T06:47:00Z to 2025-09-19T18:47:00Z; acuity 2; HOME; diagnosis J189; episode episode_63da964a453815c4bda7d57817d6db15; predecessor encounter_version_ce1da13641f9ece74cbf66d86091266e.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=13, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Doxycycline 100 mg PO COMPLETED; Doxycycline 100 mg PO COMPLETED.

  PROGRESS_NOTE @ 2025-09-13T10:47:00Z: Assessment update: Zachary Anderson, age 52. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Body temperature: 38.13 Cel (record clinical_event_d8732b95fc61fef69e41b51646d773b7). Oxygen saturation: 92.55 % (record clinical_event_5ef76c62d8c2533beae795f0ce6c55cb). White blood cell count: 12.97 10*3/uL (record clinical_event_d741285e0e721f14ec288f764e710f04). C-reactive protein: 77.46 mg/L (record clinical_event_d4e402b90f83edae26700329cacb2e71). Prior problem documentation is incomplete; absence of a record does not exclude disease. Doxycycline 100 mg administered (record clinical_event_9458c2ec72fcb7dbb2a3ab4860a37f86). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-09-19T18:47:00Z: Encounter review: Zachary Anderson, age 52. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. White blood cell count: 12.97 10*3/uL (record clinical_event_d741285e0e721f14ec288f764e710f04). White blood cell count: 8.59 10*3/uL (record clinical_event_db05bd2440501322182b05b85ee8a9de). C-reactive protein: 77.46 mg/L (record clinical_event_d4e402b90f83edae26700329cacb2e71). C-reactive protein: 14.56 mg/L (record clinical_event_ea23385b0c58c1b5b078cb1131afc223). Prior problem documentation is incomplete; absence of a record does not exclude disease. Doxycycline 100 mg administered (record clinical_event_2e30d31c4f2bc9b620f1761bbed3e789). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 78: Henry Williams

Stable patient: patient_dd87c5882cb51307b8cf3cfcddf172d2; birth date 1945-01-09; strata: acuity/2, age/65-79, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/I509, repeat/True, service/ED, service/IPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- ED 2023-07-03T03:44:00Z to 2023-07-03T07:44:00Z; acuity 2; TRANSFER; diagnosis I509; episode episode_2a24740d537f08763b58dc518e3ea53b; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2023-07-03T07:44:00Z: Clinical review: Henry Williams, age 78. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 90.39 % (record clinical_event_42e947f4112d69dd6c254ab0787547ac). Heart rate: 106.50 /min (record clinical_event_41105796de0f625124ab7dc23cd832cd). Creatinine: 1.04 mg/dL (record clinical_event_698897c1464a6a448a2ba032de163c0f). Previously recorded problems: Heart failure, unspecified; Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- IPD 2023-07-03T07:44:00Z to 2023-07-07T21:44:00Z; acuity 2; HOME; diagnosis I509; episode episode_2a24740d537f08763b58dc518e3ea53b; predecessor encounter_version_96b3740064ae016163ae330b66ab5589.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=5, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Furosemide 20 mg PO COMPLETED; Furosemide 20 mg PO COMPLETED.

  PROGRESS_NOTE @ 2023-07-03T11:44:00Z: Patient review: Henry Williams, age 78. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Body weight: 110.37 kg (record clinical_event_0bb7f474f23e6943e8dae5682f7fb4dc). Oxygen saturation: 92.19 % (record clinical_event_d62c736706c301bc5a0ef5cf03404007). Creatinine: 1.19 mg/dL (record clinical_event_31f095155b7cf4715086b379c254c52c). Potassium: 4.25 mmol/L (record clinical_event_3641fca6322a06faa90fc98fbb2632d3). Previously recorded problems: Heart failure, unspecified; Type 2 diabetes mellitus without complications. Furosemide 20 mg administered (record clinical_event_e65e64498e35e0df06e2f725dae9d7d6). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-07-07T21:44:00Z: Clinical review: Henry Williams, age 78. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Creatinine: 1.19 mg/dL (record clinical_event_31f095155b7cf4715086b379c254c52c). Creatinine: 1.00 mg/dL (record clinical_event_dd4ac44b2e7dbad8e43254974c53b044). Potassium: 4.25 mmol/L (record clinical_event_3641fca6322a06faa90fc98fbb2632d3). Potassium: 3.95 mmol/L (record clinical_event_7a99a9f842b2b29de06b6917c6969587). Previously recorded problems: Heart failure, unspecified; Type 2 diabetes mellitus without complications. Furosemide 20 mg administered (record clinical_event_bc7071f0e99b638b3dbb36add6be0506). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 79: Tonya Whitmore

Stable patient: patient_a720fdd91478f5c38bc6dae583c3a2fe; birth date 1978-10-17; strata: acuity/3, acuity/4, age/35-49, carry/False, long-stay/False, outcome/HOME, pathway/K8010, pathway/R1010, repeat/True, service/ED, service/IPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- ED 2023-03-12T05:36:00Z to 2023-03-12T07:51:00Z; acuity 4; HOME; diagnosis R1010; episode episode_b0531365f168511f841682b5019ba03c; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2, ORDER=1, PROCEDURE=1.

  ED_NOTE @ 2023-03-12T07:51:00Z: Interval assessment: Tonya Whitmore, age 44. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 96.54 % (record clinical_event_6d24ff4b2fc4427d98918cbc3d05afeb). Heart rate: 101.25 /min (record clinical_event_7da399cff145f527802178779ae6f0c9). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2023-03-13T13:49:00Z to 2023-03-17T23:49:00Z; acuity 3; HOME; diagnosis K8010; episode episode_a21297c2ee33cc2c0ddc1d5e37c49f8b; predecessor encounter_version_188d506f7776b72ead28bb0c5d3c5da4.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=12, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2023-03-13T23:49:00Z: Clinical review: Tonya Whitmore, age 44. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 8.00 1 (record clinical_event_f5414d88ef3fcc5a8976c55ec98a2911). Heart rate: 90.00 /min (record clinical_event_f15694bbb634e366d572fcfef6002b92). Hemoglobin: 14.48 g/dL (record clinical_event_4ac053c6a2353d62e6c3f3ab2867bc2f). Creatinine: 0.92 mg/dL (record clinical_event_df4426051f73f2c4b53d2ed973384a67). Prior problem documentation is incomplete; absence of a record does not exclude disease. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_597f0d866b42774badab17fbab578f17). Acetaminophen 650 mg administered (record clinical_event_2f18fb9954250e8070325182598b1918). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-03-17T23:49:00Z: Assessment update: Tonya Whitmore, age 44. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 14.48 g/dL (record clinical_event_4ac053c6a2353d62e6c3f3ab2867bc2f). Hemoglobin: 13.78 g/dL (record clinical_event_f8bfa718a9542f4e05ac52a27dcbaf39). Creatinine: 0.92 mg/dL (record clinical_event_df4426051f73f2c4b53d2ed973384a67). Creatinine: 0.92 mg/dL (record clinical_event_d4ebc12efae99dabb810d385c0cef190). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 650 mg administered (record clinical_event_515d4815d100a62f22460f1c86064bff). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 80: Bradley Rush

Stable patient: patient_187103bc7430b7ef61301f88327e740d; birth date 1966-05-11; strata: acuity/4, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/R079, repeat/False, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- OPD 2023-08-15T21:04:00Z to 2023-08-15T21:40:00Z; acuity 4; HOME; diagnosis R079; episode episode_09c14d5606928c28d00382d3e091295a; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2023-08-15T21:40:00Z: Encounter review: Bradley Rush, age 57. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.15 % (record clinical_event_bc2b2db6efb7b9689471e32a024a1903). Heart rate: 73.50 /min (record clinical_event_54d75537c4cfc36f81557118702e6ed8). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 81: Betty Hayes

Stable patient: patient_2d9801eec32f76436d1c792a54badc3f; birth date 1927-02-03; strata: acuity/2, acuity/3, age/80+, carry/False, long-stay/False, outcome/HOME, pathway/E119, pathway/K8010, pathway/R079, repeat/True, service/IPD, service/OPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- OPD 2022-12-19T06:00:00Z to 2022-12-19T08:00:00Z; acuity 3; HOME; diagnosis E119; episode episode_760dd8d1b5c122793c0da9dc7d211ac7; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2022-12-19T08:00:00Z: Clinical review: Betty Hayes, age 95. Interval follow-up for symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 97.73 % (record clinical_event_99b32182e514ae907cc851ac818f6429). Heart rate: 79.80 /min (record clinical_event_1505f8aee62392b6efd1f6728a3bdb61). Serum glucose: 244.20 mg/dL (record clinical_event_828b1ff5929d0034451f633605dd2aed). Previously recorded problems: Essential (primary) hypertension; Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- IPD 2023-11-14T13:50:00Z to 2023-11-19T01:50:00Z; acuity 2; HOME; diagnosis K8010; episode episode_96c74e8f1b76c32f319b6f58ee09efc4; predecessor encounter_version_482a0b6bccd6fa626230ce414bf5af8d.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=12, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2023-11-14T23:50:00Z: Interval assessment: Betty Hayes, age 96. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 6.00 1 (record clinical_event_c14b8f63e56f6a963c63e5fa3fea3ab8). Heart rate: 94.75 /min (record clinical_event_b4f1a7a43d9b84b740cf6f4ca73d8093). Hemoglobin: 13.69 g/dL (record clinical_event_933867b3d50a26363caa277e2c4e42fe). Creatinine: 1.00 mg/dL (record clinical_event_050ec9d567d047b44b2e9dbd80741618). Previously recorded problems: Essential (primary) hypertension; Type 2 diabetes mellitus without complications. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_b68f7dc0c97916a2457ae257dfcd1f48). Acetaminophen 650 mg administered (record clinical_event_9636938e6c7e8eb9e82f093ae4878ae9). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-11-19T01:50:00Z: Patient review: Betty Hayes, age 96. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 13.69 g/dL (record clinical_event_933867b3d50a26363caa277e2c4e42fe). Hemoglobin: 12.99 g/dL (record clinical_event_3bfda775af3261b1d56ae4922d459deb). Creatinine: 1.00 mg/dL (record clinical_event_050ec9d567d047b44b2e9dbd80741618). Creatinine: 0.95 mg/dL (record clinical_event_df77076a332d3c06706789e205146049). Previously recorded problems: Essential (primary) hypertension; Type 2 diabetes mellitus without complications. Acetaminophen 650 mg administered (record clinical_event_bbddec99a61297956c76bd6f2695303f). Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2024-12-16T19:42:00Z to 2024-12-16T20:36:00Z; acuity 3; HOME; diagnosis R079; episode episode_5bdd1764814f9b8e4f22b4febe788de9; predecessor encounter_version_ecc92ed7c47c75c8e5c275cc3b9837b8.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2024-12-16T20:36:00Z: Patient review: Betty Hayes, age 97. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.43 % (record clinical_event_3a51761d21615b5c741d0f46c603d8c6). Heart rate: 84.90 /min (record clinical_event_d1ae65805ca4238cc25ec3819942c626). Previously recorded problems: Essential (primary) hypertension; Type 2 diabetes mellitus without complications. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 82: Jenna Harris

Stable patient: patient_9875380193d8cf5586b65e64a84481ea; birth date 1991-06-14; strata: acuity/2, acuity/4, age/18-34, carry/False, long-stay/False, outcome/HOME, pathway/E119, repeat/True, service/IPD, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- IPD 2023-03-07T12:04:00Z to 2023-03-11T10:04:00Z; acuity 2; HOME; diagnosis E119; episode episode_1f4219ba17d9c5e44e9f76bfdb66588a; predecessor none.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, OBSERVATION=4, ORDER=3, PROCEDURE=1.

  PROGRESS_NOTE @ 2023-03-07T16:04:00Z: Interval assessment: Jenna Harris, age 31. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Capillary glucose: 269.50 mg/dL (record clinical_event_926482a8b5b63eece5781f8a4c76783b). Heart rate: 101.25 /min (record clinical_event_d325711cbdaa8276182f587d57da4a7a). Serum glucose: 269.50 mg/dL (record clinical_event_15036b118a31108262671d08f6109346). Creatinine: 0.95 mg/dL (record clinical_event_1d64396a3f832b773450881aee8dc1ef). Previously recorded problems: Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-03-11T10:04:00Z: Encounter review: Jenna Harris, age 31. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Serum glucose: 269.50 mg/dL (record clinical_event_15036b118a31108262671d08f6109346). Serum glucose: 134.50 mg/dL (record clinical_event_a8cbe985cd05af63d9f05637c8f070a5). Creatinine: 0.95 mg/dL (record clinical_event_1d64396a3f832b773450881aee8dc1ef). Creatinine: 0.84 mg/dL (record clinical_event_dd6db39d82f24b4225e6570282e27c35). Previously recorded problems: Type 2 diabetes mellitus without complications. Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2025-06-20T18:28:00Z to 2025-06-20T19:50:00Z; acuity 4; HOME; diagnosis E119; episode episode_2d0bd003e412eb41e59453917523f5c5; predecessor encounter_version_7a1c1ccf915adbd797f73d438ac1d099.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2025-06-20T19:50:00Z: Assessment update: Jenna Harris, age 34. Interval follow-up for symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 97.62 % (record clinical_event_92c6f2f734443aa379a9618584201642). Heart rate: 78.30 /min (record clinical_event_5298b9efba6462bdba304e86b111e4e3). Serum glucose: 231.00 mg/dL (record clinical_event_ff4abdb0135e7e0cc8949260ef7e58e5). Previously recorded problems: Type 2 diabetes mellitus without complications. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 83: Barbara Marable

Stable patient: patient_121f91a8722787cddc98cd2faf214b28; birth date 1944-03-02; strata: acuity/2, acuity/3, acuity/4, age/65-79, age/80+, carry/False, long-stay/False, outcome/HOME, pathway/K8010, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- IPD 2023-02-20T14:24:00Z to 2023-02-25T13:24:00Z; acuity 2; HOME; diagnosis K8010; episode episode_88a076e32e04c7daa4a4777405ea435e; predecessor none.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=15, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2023-02-21T00:24:00Z: Assessment update: Barbara Marable, age 78. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 8.00 1 (record clinical_event_417009a75bdd36d60f54886621603706). Heart rate: 96.50 /min (record clinical_event_53ce1f72bb44ebc5c8596d3f99fb4020). Hemoglobin: 13.53 g/dL (record clinical_event_c1bbe53dbcb61f8aecb43597e8a0f981). Creatinine: 1.01 mg/dL (record clinical_event_13771c03ad7e2c15da44c5673e33360b). Prior problem documentation is incomplete; absence of a record does not exclude disease. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_c1b06eecb54ee880f58aa7308fc9539d). Acetaminophen 650 mg administered (record clinical_event_e369d64ea58f22556f41a5b53358ba15). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-02-25T13:24:00Z: Patient review: Barbara Marable, age 78. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 13.53 g/dL (record clinical_event_c1bbe53dbcb61f8aecb43597e8a0f981). Hemoglobin: 12.83 g/dL (record clinical_event_5a0be2c54ebb2e7740ec2b5942f47396). Creatinine: 1.01 mg/dL (record clinical_event_13771c03ad7e2c15da44c5673e33360b). Creatinine: 0.95 mg/dL (record clinical_event_e12434b4019803347b9db0f166303c85). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 650 mg administered (record clinical_event_a35a152ec29d8d10fe795f26748034a6). Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2023-03-09T16:36:00Z to 2023-03-09T18:21:00Z; acuity 3; HOME; diagnosis R1010; episode episode_1822b91e3716b4400823ffe65f65f242; predecessor encounter_version_a13d8e8b7f000312e6e0ba38839587fd.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  OP_NOTE @ 2023-03-09T18:21:00Z: Patient review: Barbara Marable, age 79. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.10 % (record clinical_event_a4eb9a6c93a1290dfe1945620a27554f). Heart rate: 81.60 /min (record clinical_event_87e264315dd22ca641ae1818ed750879). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2024-04-10T12:00:00Z to 2024-04-10T14:04:00Z; acuity 4; HOME; diagnosis R1010; episode episode_906f760dd416e8a8ba015653fd54bb1d; predecessor encounter_version_a1ba88ce5e21b3f801ed3faabf8532bc.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2024-04-10T14:04:00Z: Assessment update: Barbara Marable, age 80. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 96.51 % (record clinical_event_18de69f20e6ffd75f9188f5b84a4ea97). Heart rate: 106.75 /min (record clinical_event_ca96ad1309d5b3b8c8fae4ac8de7f9c2). Hemoglobin: 14.07 g/dL (record clinical_event_9ccdfe0393a5ebd660332063a7df0d51). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 84: Elizabeth Cartwright

Stable patient: patient_9de4701209cc76119bf10429605e0b3c; birth date 1980-01-04; strata: acuity/3, acuity/4, acuity/5, age/35-49, carry/False, long-stay/False, outcome/HOME, pathway/E119, pathway/K8010, pathway/R079, repeat/True, service/ED, service/IPD, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- OPD 2022-12-25T06:00:00Z to 2022-12-25T08:00:00Z; acuity 5; HOME; diagnosis E119; episode episode_4c1afaefacc502d98f9ce72ea5672186; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2022-12-25T08:00:00Z: Patient review: Elizabeth Cartwright, age 42. Interval follow-up for symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 97.99 % (record clinical_event_07f2ffbcdd34227ca6ca5fdd5253757e). Heart rate: 73.05 /min (record clinical_event_ac15ff187cc5755f729c554c85edfd8d). Serum glucose: 275.00 mg/dL (record clinical_event_827ca34fe37e65ee567f216474d519cd). Previously recorded problems: Type 2 diabetes mellitus without complications. Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2023-10-22T04:15:00Z to 2023-10-22T06:28:00Z; acuity 4; HOME; diagnosis R079; episode episode_de1ff01c625862bb473f07cdc6263981; predecessor encounter_version_c587e5875d9d67587476512d8e81ca90.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2023-10-22T06:28:00Z: Assessment update: Elizabeth Cartwright, age 43. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 98.91 % (record clinical_event_6081ea0e1e0c8f29b7f6f00754d26242). Heart rate: 106.25 /min (record clinical_event_f891b716a004d5ead231d1ee65e9cc5b). Troponin I: 3.98 ng/L (record clinical_event_a345eb2a078ecfbae1b5a3d704822001). Previously recorded problems: Type 2 diabetes mellitus without complications. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- IPD 2025-02-21T14:59:00Z to 2025-02-26T00:59:00Z; acuity 3; HOME; diagnosis K8010; episode episode_020a14f04999a484229c1527e91993ef; predecessor encounter_version_29c0db126d5408bd43ca5e4877d97595.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=15, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2025-02-22T00:59:00Z: Assessment update: Elizabeth Cartwright, age 45. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 5.00 1 (record clinical_event_e25ff72b940f02f238c9431414e96b1c). Heart rate: 108.25 /min (record clinical_event_0080fd163929a393fd1e23532e1fd63a). Hemoglobin: 13.42 g/dL (record clinical_event_00c68143e04c7b493a87c8e509a94d5b). Creatinine: 1.09 mg/dL (record clinical_event_e4e67f5130bc41ecbebcc29198162d17). Previously recorded problems: Type 2 diabetes mellitus without complications. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_d5fac0900e37efec9b9f9da1246ac1d0). Acetaminophen 650 mg administered (record clinical_event_8d821d853bec00e49340005fb1e41da9). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-02-26T00:59:00Z: Care assessment: Elizabeth Cartwright, age 45. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 13.42 g/dL (record clinical_event_00c68143e04c7b493a87c8e509a94d5b). Hemoglobin: 12.72 g/dL (record clinical_event_e23e8e6203162a38b9b68779e309bbca). Creatinine: 1.09 mg/dL (record clinical_event_e4e67f5130bc41ecbebcc29198162d17). Creatinine: 0.91 mg/dL (record clinical_event_3056a73085f5155d34827ba46d25d4d8). Previously recorded problems: Type 2 diabetes mellitus without complications. Acetaminophen 650 mg administered (record clinical_event_970657329123e719bcfcd840b99e4ac8). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 85: Jason Young

Stable patient: patient_0a89b3a248ee447f49e06163b7fb8195; birth date 1982-03-21; strata: acuity/2, acuity/3, acuity/4, acuity/5, age/35-49, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/E119, pathway/J449, pathway/R079, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2023-06-20T17:34:00Z to 2023-06-20T19:54:00Z; acuity 4; HOME; diagnosis R079; episode episode_d6a27cb568a09f63947cba3adc69fdff; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2023-06-20T19:54:00Z: Assessment update: Jason Young, age 41. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 98.76 % (record clinical_event_c9e6402b4ae589bdb25d00c278a78461). Heart rate: 100.75 /min (record clinical_event_d2c95369ea91cb078d5e95302e950534). Troponin I: 4.04 ng/L (record clinical_event_b68b72cb1470a90f9bc06859a1b90e60). Previously recorded problems: Type 2 diabetes mellitus without complications. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- OPD 2023-12-13T21:01:00Z to 2023-12-13T21:40:00Z; acuity 5; HOME; diagnosis R1010; episode episode_0c04ecf3162aa3e1f46a6d854ceb289a; predecessor encounter_version_171398ceb71b76bc066d35f160946a1d.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  OP_NOTE @ 2023-12-13T21:40:00Z: Clinical review: Jason Young, age 41. Interval follow-up for intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.23 % (record clinical_event_0d17d0ec5d7e41b57ed465d25da2652b). Heart rate: 82.65 /min (record clinical_event_bcc08f3e399358a723d5665e9d261485). Previously recorded problems: Type 2 diabetes mellitus without complications. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2024-09-19T20:12:00Z to 2024-09-19T22:01:00Z; acuity 4; HOME; diagnosis E119; episode episode_581da1a94300aa409488230b72f2d213; predecessor encounter_version_89b04513620641cfc1fd7ef3915c4c51.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2024-09-19T22:01:00Z: Assessment update: Jason Young, age 42. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 98.91 % (record clinical_event_eff2613c0a1ce478b215de95ae6eed5e). Heart rate: 106.25 /min (record clinical_event_f6316d4b2306cf285930441cd8a47bd9). Previously recorded problems: Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2024-10-28T11:56:00Z to 2024-10-28T15:56:00Z; acuity 2; TRANSFER; diagnosis J449; episode episode_95bdc8e1389d75001eea7146744002e2; predecessor encounter_version_f6f55dd776b7e0b813039246d9015566.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2024-10-28T15:56:00Z: Clinical review: Jason Young, age 42. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 92.97 % (record clinical_event_c5eea2617f716904bee1e11a7a8f0982). Heart rate: 100.75 /min (record clinical_event_e52c8ae5b1cd03529f306f35b7204d65). White blood cell count: 14.11 10*3/uL (record clinical_event_de3110a0a9538c259d47f33e900f561d). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Type 2 diabetes mellitus without complications. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- IPD 2024-10-28T15:56:00Z to 2024-11-02T06:56:00Z; acuity 2; HOME; diagnosis J449; episode episode_95bdc8e1389d75001eea7146744002e2; predecessor encounter_version_a47734fed42ee823000840fbc41c4333.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=5, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Prednisone 40 mg PO COMPLETED; Prednisone 40 mg PO COMPLETED.

  PROGRESS_NOTE @ 2024-10-28T19:56:00Z: Clinical review: Jason Young, age 42. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 90.42 % (record clinical_event_af4712db6ff9b243816ba1052eeb9532). Respiratory rate: 26.10 /min (record clinical_event_a57cf08b91dd6a9863d0aef9db0218e2). White blood cell count: 11.52 10*3/uL (record clinical_event_1f06de46e29925a3636c2705142413a5). Bicarbonate: 29.88 mmol/L (record clinical_event_ceab69ae5518bf5aca20564a98e3a223). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Type 2 diabetes mellitus without complications. Prednisone 40 mg administered (record clinical_event_e8e7624726f471f192de013c12d9b879). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2024-11-02T06:56:00Z: Encounter review: Jason Young, age 42. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. White blood cell count: 11.52 10*3/uL (record clinical_event_1f06de46e29925a3636c2705142413a5). White blood cell count: 7.57 10*3/uL (record clinical_event_ca15e680a92c172d397f6f86f8365af2). Bicarbonate: 29.88 mmol/L (record clinical_event_ceab69ae5518bf5aca20564a98e3a223). Bicarbonate: 28.88 mmol/L (record clinical_event_d94c0bd511f3da232aeb85596e734515). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Type 2 diabetes mellitus without complications. Prednisone 40 mg administered (record clinical_event_ee88de0abaafebecd76762f5978a2ebb). Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2024-11-15T02:56:00Z to 2024-11-15T06:56:00Z; acuity 3; TRANSFER; diagnosis J449; episode episode_8de773f94be91dbca46054f7fc883525; predecessor encounter_version_fc8674886edc208e75a0b35cdc905a7b.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2.
  Treatment evidence: Prednisone 200 mg PO COMPLETED.

  ED_NOTE @ 2024-11-15T06:56:00Z: Encounter review: Jason Young, age 42. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 93.78 % (record clinical_event_1182c7db25a6d97eddb1c66c357e7500). Heart rate: 92.75 /min (record clinical_event_9a350407002b41b1f8e80caf07f9c6af). White blood cell count: 12.33 10*3/uL (record clinical_event_dd103fefc98e0b5d29cd630f6d4811ed). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Type 2 diabetes mellitus without complications. Prednisone 200 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_390ea6f6d31414a064d40ae49a195c01). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- IPD 2024-11-15T06:56:00Z to 2024-11-19T19:56:00Z; acuity 2; HOME; diagnosis J449; episode episode_8de773f94be91dbca46054f7fc883525; predecessor encounter_version_65e3887e1c0dd7a461a91d1899a96560.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=5, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Prednisone 40 mg PO COMPLETED; Prednisone 40 mg PO COMPLETED.

  PROGRESS_NOTE @ 2024-11-15T10:56:00Z: Assessment update: Jason Young, age 42. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 91.74 % (record clinical_event_b01632bb5ae77c6c465c78559d7eeb36). Respiratory rate: 27.25 /min (record clinical_event_c30822bfe85cdb85972c42e54d33d8bf). White blood cell count: 13.39 10*3/uL (record clinical_event_659303ba8921e8ac12051b92c48b8a74). Bicarbonate: 28.98 mmol/L (record clinical_event_77d7971093ccd03d844fd423eda2a1bd). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Type 2 diabetes mellitus without complications. Prednisone 40 mg administered (record clinical_event_8c2767b8ffbc3b0a24da7ea1a741440d). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2024-11-19T19:56:00Z: Clinical review: Jason Young, age 42. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. White blood cell count: 13.39 10*3/uL (record clinical_event_659303ba8921e8ac12051b92c48b8a74). White blood cell count: 7.96 10*3/uL (record clinical_event_c2dd9470bd1436717976d16301f89bad). Bicarbonate: 28.98 mmol/L (record clinical_event_77d7971093ccd03d844fd423eda2a1bd). Bicarbonate: 27.98 mmol/L (record clinical_event_30506965e20ce02bba72711f2cc3b880). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Type 2 diabetes mellitus without complications. Prednisone 40 mg administered (record clinical_event_ae58b5015287e7e45dac20e66459bd7a). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 86: Daniel Kennedy

Stable patient: patient_b9135c639d0b38aacbf32e937c70eed9; birth date 1957-09-02; strata: acuity/2, acuity/3, acuity/4, acuity/5, age/65-79, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/E119, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2023-02-24T02:11:00Z to 2023-02-24T04:46:00Z; acuity 5; HOME; diagnosis R1010; episode episode_0cf97497e66b055535e1f2ac51afc1d2; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  ED_NOTE @ 2023-02-24T04:46:00Z: Interval assessment: Daniel Kennedy, age 65. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 98.43 % (record clinical_event_2032cde6d6bf794103901b2c11decd3a). Heart rate: 112.25 /min (record clinical_event_65b409bf224549aaca1da1e516e0e297). Hemoglobin: 14.52 g/dL (record clinical_event_99fe67e0df73144daf5d61d211d16c07). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_febaba5cc5893efcb05d851de95c148d). The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2023-12-16T01:15:00Z to 2023-12-16T05:15:00Z; acuity 2; TRANSFER; diagnosis E119; episode episode_4547e0960cd214d35c9f05d65e739261; predecessor encounter_version_52fcde948661fb55a0ddd9c719070cbc.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2023-12-16T05:15:00Z: Encounter review: Daniel Kennedy, age 66. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 98.19 % (record clinical_event_80f604cdaa5e66f4855d62dc93c694a0). Heart rate: 101.00 /min (record clinical_event_733dfe9287a7798be763538c391431bb). Previously recorded problems: Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- IPD 2023-12-16T05:15:00Z to 2023-12-20T13:15:00Z; acuity 3; HOME; diagnosis E119; episode episode_4547e0960cd214d35c9f05d65e739261; predecessor encounter_version_e313a27f5a90f9bb43db3bc49761caa5.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, OBSERVATION=4, ORDER=3, PROCEDURE=1.

  PROGRESS_NOTE @ 2023-12-16T09:15:00Z: Assessment update: Daniel Kennedy, age 66. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Capillary glucose: 245.30 mg/dL (record clinical_event_d8db06edda2a909ebb4f1ab35bcbae7a). Heart rate: 95.75 /min (record clinical_event_46bf0d3d93fbf5e6d7e936930ed81169). Serum glucose: 245.30 mg/dL (record clinical_event_857c625f24af46fbae2f00fb8287148b). Creatinine: 0.98 mg/dL (record clinical_event_9a46aeea4eb07740c4ee82afddd2f2d8). Previously recorded problems: Type 2 diabetes mellitus without complications. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-12-20T13:15:00Z: Assessment update: Daniel Kennedy, age 66. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Serum glucose: 245.30 mg/dL (record clinical_event_857c625f24af46fbae2f00fb8287148b). Serum glucose: 136.95 mg/dL (record clinical_event_0e98b3d39a40bd0a473e3f581a3c78d8). Creatinine: 0.98 mg/dL (record clinical_event_9a46aeea4eb07740c4ee82afddd2f2d8). Creatinine: 0.92 mg/dL (record clinical_event_c5a3390ecd78487804384351f2980f8c). Previously recorded problems: Type 2 diabetes mellitus without complications. Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2024-01-13T09:15:00Z to 2024-01-13T13:15:00Z; acuity 3; TRANSFER; diagnosis E119; episode episode_c18be4ee564649dcc3ce80f4bfa75cfe; predecessor encounter_version_c76e4d6a978679e9ad8340c226060f45.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2024-01-13T13:15:00Z: Care assessment: Daniel Kennedy, age 66. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 98.43 % (record clinical_event_0d022c672a1bdf1fc1e2e34a8d5ac41c). Heart rate: 102.00 /min (record clinical_event_7696ff86bb55b4b9e0250043d648fca5). Serum glucose: 272.80 mg/dL (record clinical_event_29ee4b12dfe1a46ddc44b9f04d230a99). Previously recorded problems: Type 2 diabetes mellitus without complications. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2024-01-13T13:15:00Z to 2024-01-18T17:15:00Z; acuity 2; HOME; diagnosis E119; episode episode_c18be4ee564649dcc3ce80f4bfa75cfe; predecessor encounter_version_deb454b61a34b293ad12b6e70971b465.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, OBSERVATION=4, ORDER=3, PROCEDURE=1.

  PROGRESS_NOTE @ 2024-01-13T17:15:00Z: Assessment update: Daniel Kennedy, age 66. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Capillary glucose: 304.70 mg/dL (record clinical_event_c7614b3adedf48ca78651b54ced736a8). Heart rate: 109.25 /min (record clinical_event_21269a24b4c070f51de4001bc8dbc27c). Serum glucose: 304.70 mg/dL (record clinical_event_0c52fc47ee7e0445ae01d92bbc95e21c). Creatinine: 1.15 mg/dL (record clinical_event_bfcf57c37682c606b8253a5d91b5bb3b). Previously recorded problems: Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2024-01-18T17:15:00Z: Care assessment: Daniel Kennedy, age 66. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Serum glucose: 304.70 mg/dL (record clinical_event_0c52fc47ee7e0445ae01d92bbc95e21c). Serum glucose: 118.75 mg/dL (record clinical_event_9905702fbc6e316cdc17d67faa060ab1). Creatinine: 1.15 mg/dL (record clinical_event_bfcf57c37682c606b8253a5d91b5bb3b). Creatinine: 0.96 mg/dL (record clinical_event_4fb8218806e4a8c7127755d0575e53a3). Previously recorded problems: Type 2 diabetes mellitus without complications. Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2024-03-21T11:55:00Z to 2024-03-21T14:32:00Z; acuity 5; HOME; diagnosis R1010; episode episode_6543847c34d4178d9a5fb6edab37419e; predecessor encounter_version_f487b2a3edcb942f124a8f6d39e109aa.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2024-03-21T14:32:00Z: Assessment update: Daniel Kennedy, age 66. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 96.51 % (record clinical_event_82892e455015852c2896934dd92271b9). Heart rate: 109.75 /min (record clinical_event_66068d6994869128182d623b147b5605). Previously recorded problems: Type 2 diabetes mellitus without complications. Continue assessment as results become available. Follow-up completion is not established by this document.
- OPD 2024-04-01T19:32:00Z to 2024-04-01T20:48:00Z; acuity 4; HOME; diagnosis E119; episode episode_65d88b095523d9bf17d7417df558efee; predecessor encounter_version_d9da8e34ffe2c27eec29aabc12fd42a7.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2024-04-01T20:48:00Z: Encounter review: Daniel Kennedy, age 66. Interval follow-up for symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 97.17 % (record clinical_event_44bcec8cfc9b1e54efb853f81b41d948). Heart rate: 74.40 /min (record clinical_event_67fa62591b577574c50397e66d568733). Serum glucose: 305.80 mg/dL (record clinical_event_d88595928b347df5a1c8c40ef8d2d33c). Previously recorded problems: Type 2 diabetes mellitus without complications. Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2024-06-15T02:19:00Z to 2024-06-15T04:17:00Z; acuity 4; HOME; diagnosis E119; episode episode_4680dc9e5805e74787e01dbde5a94387; predecessor encounter_version_f4219e524e4fc3aa1693e79034bacfa1.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2024-06-15T04:17:00Z: Care assessment: Daniel Kennedy, age 66. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 97.41 % (record clinical_event_e84f3dc70266ea3edef4e93042500092). Heart rate: 99.75 /min (record clinical_event_55826e9ded49935cb35ceea71b2fc781). Serum glucose: 262.90 mg/dL (record clinical_event_96f66d0eea20cb745bf7e8f1e4bd703a). Previously recorded problems: Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- OPD 2024-09-02T21:54:00Z to 2024-09-02T22:39:00Z; acuity 3; HOME; diagnosis E119; episode episode_84784d40ec0067c6f558d1902e8689ca; predecessor encounter_version_eebc9de75868a617aaaa50227ac87897.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2024-09-02T22:39:00Z: Interval assessment: Daniel Kennedy, age 67. Interval follow-up for symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 97.16 % (record clinical_event_3f9aed350638585fc8298afe4df8a24f). Heart rate: 72.30 /min (record clinical_event_8a9c1d8a8d140fca3e16fab5992b142b). Previously recorded problems: Type 2 diabetes mellitus without complications. Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2024-10-22T01:50:00Z to 2024-10-22T03:30:00Z; acuity 4; HOME; diagnosis E119; episode episode_b94506c28a00930d66e7cd3788dbcd37; predecessor encounter_version_a509deed157f308c86d627944b85a266.
  Captured evidence: DOCUMENT=1, OBSERVATION=2, ORDER=1, PROCEDURE=1.

  ED_NOTE @ 2024-10-22T03:30:00Z: Assessment update: Daniel Kennedy, age 67. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 98.88 % (record clinical_event_e6c0bcd5705aaf4646ccd096e17a2bae). Heart rate: 101.25 /min (record clinical_event_ce18c7f7edf56904ae5998cad56c3e4c). Previously recorded problems: Type 2 diabetes mellitus without complications. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2025-07-16T11:28:00Z to 2025-07-16T13:30:00Z; acuity 4; HOME; diagnosis E119; episode episode_cbff84021e82def0c59c7d5aaa790344; predecessor encounter_version_585eb5bccac32bdb982cdad4b1f351aa.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2025-07-16T13:30:00Z: Assessment update: Daniel Kennedy, age 67. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 97.98 % (record clinical_event_b265db88bb9dd18f34d166730208a460). Heart rate: 90.50 /min (record clinical_event_2e76ab6a915832b1e89bab591db972a5). Previously recorded problems: Type 2 diabetes mellitus without complications. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 87: Jeffery Obrien

Stable patient: patient_0316ce6537c5dbe06b49a9996529b448; birth date 1966-09-25; strata: acuity/3, acuity/5, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/J449, pathway/M1711, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- OPD 2022-12-24T06:00:00Z to 2022-12-24T08:00:00Z; acuity 5; HOME; diagnosis J449; episode episode_cf416b006d2c14cdbc15564b26e09adb; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2, ORDER=1, PROCEDURE=1.

  OP_NOTE @ 2022-12-24T08:00:00Z: Care assessment: Jeffery Obrien, age 56. Interval follow-up for increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 95.01 % (record clinical_event_caa5f088759ffa23f86a9b3aaed8de13). Heart rate: 83.25 /min (record clinical_event_5055f3f7e79a011618bbf204f8fa4c99). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2024-07-01T05:21:00Z to 2024-07-01T07:26:00Z; acuity 3; HOME; diagnosis R1010; episode episode_b0bf2ced05ebc369a92ccac05895aa15; predecessor encounter_version_57a9df83b09a8e69519172f56b2dcb6e.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2024-07-01T07:26:00Z: Assessment update: Jeffery Obrien, age 57. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.65 % (record clinical_event_d36220f00049501a50a68a82cc06d677). Heart rate: 102.75 /min (record clinical_event_1fa3b793ebb8ca19332332aabd6b8e9e). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2025-11-24T15:21:00Z to 2025-11-28T23:21:00Z; acuity 3; HOME; diagnosis M1711; episode episode_46992ed50a7b0ec328f8000b32746e34; predecessor encounter_version_133d312ef1dd371b89fa8f6b59127e0b.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=14, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2025-11-25T01:21:00Z: Care assessment: Jeffery Obrien, age 59. Presenting concern: right knee osteoarthritis limiting mobility. Working assessment: Unilateral primary osteoarthritis, right knee. Pain numeric rating: 5.00 1 (record clinical_event_1a4483b07f99bad28e6b893c015d836a). Mobility assessment: 2.00 1 (record clinical_event_db695847cc6c0fce529b06a6109bd457). Hemoglobin: 13.98 g/dL (record clinical_event_3ad8107bd87cc62627b733c807bd2fd5). Creatinine: 1.04 mg/dL (record clinical_event_ddc3d34dcb29ca98cd1520ad38696d20). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Procedure documented: Replacement of Right Knee Joint with Synthetic Substitute, Cemented, Open Approach (record clinical_event_8f65380321359f0fdde6f194d6defa47). Acetaminophen 650 mg administered (record clinical_event_954efe6cef7bb22275255921e34548ac). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-11-28T23:21:00Z: Care assessment: Jeffery Obrien, age 59. Presenting concern: right knee osteoarthritis limiting mobility. Working assessment: Unilateral primary osteoarthritis, right knee. Hemoglobin: 13.98 g/dL (record clinical_event_3ad8107bd87cc62627b733c807bd2fd5). Hemoglobin: 13.28 g/dL (record clinical_event_8294e910469d9130f2ce72b9bc2adf88). Creatinine: 1.04 mg/dL (record clinical_event_ddc3d34dcb29ca98cd1520ad38696d20). Creatinine: 0.88 mg/dL (record clinical_event_ba90dc9cc76c3c9ff260bf580f3b96ae). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Acetaminophen 650 mg administered (record clinical_event_4a086c81f42309c55146c884695c4457). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 88: Joseph Ramirez

Stable patient: patient_2ee6dbdd587541683669fb3de6ff8f0d; birth date 1955-06-19; strata: acuity/2, acuity/4, acuity/5, age/65-79, carry/False, long-stay/False, outcome/HOME, pathway/J189, pathway/K8010, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- ED 2023-03-29T22:45:00Z to 2023-03-30T01:08:00Z; acuity 5; HOME; diagnosis R1010; episode episode_bea3e85ea836e2a1bfd83037288282eb; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  ED_NOTE @ 2023-03-30T01:08:00Z: Encounter review: Joseph Ramirez, age 67. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 96.96 % (record clinical_event_f881202b751fa6577a094b6fe09c1e0f). Heart rate: 104.50 /min (record clinical_event_8a69592edd611017ccee5e05dace15c0). Hemoglobin: 14.40 g/dL (record clinical_event_408904e8fe1e093c74682a2750881b27). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_0577bee346ffa9b227e69686c6a657ac). Continue assessment as results become available. Follow-up completion is not established by this document.
- IPD 2024-03-11T14:51:00Z to 2024-03-16T03:51:00Z; acuity 2; HOME; diagnosis K8010; episode episode_456ddee7bcaec82dcebae562608069ae; predecessor encounter_version_8b3d9cc300a5decc4b656f209119bd31.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=11, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2024-03-12T00:51:00Z: Encounter review: Joseph Ramirez, age 68. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 7.00 1 (record clinical_event_419616ec4d2b937cb3d4882467e92cde). Heart rate: 105.25 /min (record clinical_event_c1e532baaf37c8e90508a15039a918a6). Hemoglobin: 14.58 g/dL (record clinical_event_3660d5b6db59f8bd38cc693eeca86c48). Creatinine: 1.23 mg/dL (record clinical_event_c6b80872f1f5b6074ad364d0e5f4f6be). Prior problem documentation is incomplete; absence of a record does not exclude disease. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_416fc6f1cddc50d6746215a59fb09bb0). Acetaminophen 650 mg administered (record clinical_event_fc9e4082d8138e9744f74754dc0521a8). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2024-03-16T03:51:00Z: Patient review: Joseph Ramirez, age 68. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 14.58 g/dL (record clinical_event_3660d5b6db59f8bd38cc693eeca86c48). Hemoglobin: 13.88 g/dL (record clinical_event_272f928309a541838290af4e279b7e05). Creatinine: 1.23 mg/dL (record clinical_event_c6b80872f1f5b6074ad364d0e5f4f6be). Creatinine: 1.08 mg/dL (record clinical_event_a7177a190751b5b3331627a3470bc214). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 650 mg administered (record clinical_event_e6c32ae3d5d9df8a92b4c1dbc2521c6b). Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2024-12-31T21:01:00Z to 2024-12-31T21:40:00Z; acuity 4; HOME; diagnosis J189; episode episode_0c03d3796a0df31f57519ee046746f56; predecessor encounter_version_bd3f760bcda9e5c92f64412e3386dd0b.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2024-12-31T21:40:00Z: Clinical review: Joseph Ramirez, age 69. Interval follow-up for cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Oxygen saturation: 97.29 % (record clinical_event_13d5768027dd4caf758951ab09abf29e). Heart rate: 82.65 /min (record clinical_event_d2e937bfab71037d2c38c6c81866d7c3). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 89: Dean Wilson

Stable patient: patient_917f105a79fe78dde4fbf3a76bb79d22; birth date 1952-07-20; strata: acuity/5, age/65-79, carry/False, long-stay/False, outcome/HOME, pathway/J449, repeat/False, service/ED, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- ED 2024-10-18T16:04:00Z to 2024-10-18T17:45:00Z; acuity 5; HOME; diagnosis J449; episode episode_6612d4bbb9a9443bc1364b573ea3c152; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2.
  Treatment evidence: Prednisone 200 mg PO COMPLETED.

  ED_NOTE @ 2024-10-18T17:45:00Z: Care assessment: Dean Wilson, age 72. Presenting concern: increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 93.00 % (record clinical_event_0d084eff3e11e238ed6f3f7fdf6c0798). Heart rate: 102.25 /min (record clinical_event_abe83f836315059be08667e276c3d4f9). White blood cell count: 14.79 10*3/uL (record clinical_event_48a7a475c352f8a19a31a2b7c2815696). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified. Prednisone 200 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_62e55241f6340a638b9600691ae744a0). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 90: Marguerite Schlegel

Stable patient: patient_059b79799788623fccd6923d6a2fb44f; birth date 1945-05-10; strata: acuity/3, age/65-79, carry/False, long-stay/False, outcome/HOME, pathway/R079, repeat/False, service/ED, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2023-12-19T21:05:00Z to 2023-12-19T22:49:00Z; acuity 3; HOME; diagnosis R079; episode episode_a8b37784b08c9c71a7d5f3acfd86b282; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2023-12-19T22:49:00Z: Encounter review: Marguerite Schlegel, age 78. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 98.88 % (record clinical_event_bd10b3d4ecb4d3a7d7f96b7eb38f4cb4). Heart rate: 103.50 /min (record clinical_event_baebb6a9d5aa2545289055e4b41f34a9). Troponin I: 2.96 ng/L (record clinical_event_856786e920c91360c2b2be36b8253a5a). Previously recorded problems: Hyperlipidemia, unspecified. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 91: Theresa McGowan

Stable patient: patient_c152a6ca665b06e25dfcfd2de4ca02f4; birth date 1967-03-01; strata: acuity/4, age/50-64, carry/False, long-stay/False, outcome/HOME, pathway/R079, repeat/False, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- OPD 2024-07-29T17:23:00Z to 2024-07-29T18:34:00Z; acuity 4; HOME; diagnosis R079; episode episode_450f7d27c50f1e29fb4f116d7e33cb2c; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2024-07-29T18:34:00Z: Patient review: Theresa McGowan, age 57. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.96 % (record clinical_event_2a8a2327b67cf6c10298503f734d192b). Heart rate: 75.75 /min (record clinical_event_8c131ae4bf9cd361be066e10d5d044d2). Troponin I: 4.58 ng/L (record clinical_event_230322b3e19db42e14230dd6fb68ce15). Prior problem documentation is incomplete; absence of a record does not exclude disease. The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 92: Mary Williams

Stable patient: patient_24332f776be5fbba167162d172c80e8b; birth date 1957-03-12; strata: acuity/2, acuity/3, acuity/5, age/65-79, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/I509, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- ED 2023-07-01T22:22:00Z to 2023-07-02T02:22:00Z; acuity 3; TRANSFER; diagnosis I509; episode episode_424ac13f9f8c6605590146505e5df753; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2023-07-02T02:22:00Z: Assessment update: Mary Williams, age 66. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 94.53 % (record clinical_event_fdf567c3031ff414d31a9cbf1e68aa47). Heart rate: 93.75 /min (record clinical_event_28eecaa3270af0ae80d954747e96e401). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- IPD 2023-07-02T02:22:00Z to 2023-07-07T06:22:00Z; acuity 2; HOME; diagnosis I509; episode episode_424ac13f9f8c6605590146505e5df753; predecessor encounter_version_ded4e75e9a2cbe7b28fd3524bd526c71.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=6, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Furosemide 20 mg PO COMPLETED; Furosemide 20 mg PO COMPLETED.

  PROGRESS_NOTE @ 2023-07-02T06:22:00Z: Interval assessment: Mary Williams, age 66. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Body weight: 111.79 kg (record clinical_event_141e30a838deb1b2a00b9293a5ed2fb6). Oxygen saturation: 92.73 % (record clinical_event_ee4221a764b42bf0fec6e8bcab866f42). Creatinine: 1.79 mg/dL (record clinical_event_1420acb862f6d54ca2c99fa4a56dcfa6). Potassium: 4.33 mmol/L (record clinical_event_26a4e1e1bdaff4bccdf4739090361a07). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_2e8263a6614f53611718e77bfa640f76). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-07-07T06:22:00Z: Interval assessment: Mary Williams, age 66. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Creatinine: 1.79 mg/dL (record clinical_event_1420acb862f6d54ca2c99fa4a56dcfa6). Creatinine: 1.72 mg/dL (record clinical_event_d1c61cb4c3341fe616568bb9e0166748). Potassium: 4.33 mmol/L (record clinical_event_26a4e1e1bdaff4bccdf4739090361a07). Potassium: 4.03 mmol/L (record clinical_event_165e56e08bdaac162b846a23706fb023). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_3f709c33d2d84e78944866eabb0a74d7). Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2023-07-26T02:22:00Z to 2023-07-26T06:22:00Z; acuity 3; TRANSFER; diagnosis I509; episode episode_34357a8d8498556826a0f193341791b4; predecessor encounter_version_83fc94167d8e5c8c5e58929ba76f009c.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2023-07-26T06:22:00Z: Clinical review: Mary Williams, age 66. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 95.04 % (record clinical_event_d94b2aad21c1a65e3c32181a4920f03d). Heart rate: 98.25 /min (record clinical_event_245609db11dcf77cf824e183d0386f84). Creatinine: 1.90 mg/dL (record clinical_event_ab63a39d7f8e889d4231d56c54634fc0). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- IPD 2023-07-26T06:22:00Z to 2023-07-31T14:22:00Z; acuity 2; HOME; diagnosis I509; episode episode_34357a8d8498556826a0f193341791b4; predecessor encounter_version_df723fc56ac667bbfa13e2d733f2a09e.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=6, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Furosemide 20 mg PO COMPLETED; Furosemide 20 mg PO COMPLETED.

  PROGRESS_NOTE @ 2023-07-26T10:22:00Z: Encounter review: Mary Williams, age 66. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Body weight: 112.10 kg (record clinical_event_6d8f764b9937a06aeeaa0e3a98aa7891). Oxygen saturation: 90.24 % (record clinical_event_98529970697e1fe6ca9f44a90ed62827). Creatinine: 2.14 mg/dL (record clinical_event_427f22a97ec97fbc183abd338bb52880). Potassium: 4.29 mmol/L (record clinical_event_1eb9b37dc6e87af3c099568962550e79). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_39430e27b91e25645523ee726b8ac452). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-07-31T14:22:00Z: Care assessment: Mary Williams, age 66. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Creatinine: 2.14 mg/dL (record clinical_event_427f22a97ec97fbc183abd338bb52880). Creatinine: 1.99 mg/dL (record clinical_event_840213838d49e9e23efa193a43cf1dc0). Potassium: 4.29 mmol/L (record clinical_event_1eb9b37dc6e87af3c099568962550e79). Potassium: 3.99 mmol/L (record clinical_event_eb839fd4b9a928713d48dca134147c17). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Furosemide 20 mg administered (record clinical_event_b54d1731b9949cfbdadbf11ff4519b00). Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2024-01-30T16:33:00Z to 2024-01-30T17:11:00Z; acuity 5; HOME; diagnosis I509; episode episode_27d1a1649666c896a69b800753b80773; predecessor encounter_version_5b8545b5badc260c92eeecff6b982757.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2024-01-30T17:11:00Z: Assessment update: Mary Williams, age 66. Interval follow-up for worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 97.76 % (record clinical_event_b347d3da1fd8f0759ef45261443fbe89). Heart rate: 74.55 /min (record clinical_event_03081d1269db6b849476ee857f928aab). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2024-02-08T01:22:00Z to 2024-02-08T03:45:00Z; acuity 3; HOME; diagnosis I509; episode episode_6ea2265cfac97c257605d6b4919e857a; predecessor encounter_version_7159bb6a9a09a02c14e98317548ba3f2.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.
  Treatment evidence: Furosemide 140 mg PO COMPLETED.

  ED_NOTE @ 2024-02-08T03:45:00Z: Care assessment: Mary Williams, age 66. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 95.73 % (record clinical_event_e16e429735cc183b2079164fb669cfa3). Heart rate: 91.75 /min (record clinical_event_9ee5270af3537c0be376a5628077ce64). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Furosemide 140 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_6acbbb796e38f7c334ea8114e858e98a). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2024-12-11T23:57:00Z to 2024-12-12T01:59:00Z; acuity 3; HOME; diagnosis I509; episode episode_7ace224add9950262983dc895f19a2d8; predecessor encounter_version_d0f0b9cab2a02e549d24283c39b1105d.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2024-12-12T01:59:00Z: Interval assessment: Mary Williams, age 67. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 93.96 % (record clinical_event_e5470571cc40de1b6d4bddb23ce34d5f). Heart rate: 91.25 /min (record clinical_event_f36df52d7f3408ee6bd8dfa96cf21f48). Creatinine: 1.89 mg/dL (record clinical_event_afa155da61e012853de3b8896d4a1c6c). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2025-05-30T01:24:00Z to 2025-05-30T04:23:00Z; acuity 3; HOME; diagnosis I509; episode episode_e93c2bddbc62befcca86c59e3e3c0cbe; predecessor encounter_version_2def4989a46187aa80d7fc630cc03dd2.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2.
  Treatment evidence: Furosemide 140 mg PO COMPLETED.

  ED_NOTE @ 2025-05-30T04:23:00Z: Interval assessment: Mary Williams, age 68. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 93.63 % (record clinical_event_23d11bd1dedbd94114203af4fc051843). Heart rate: 114.00 /min (record clinical_event_567a5d090530383967455629c05894dd). Creatinine: 2.18 mg/dL (record clinical_event_5f004dc2ba1e90c9bdcf0b5265c642f9). Previously recorded problems: Chronic kidney disease, unspecified; Heart failure, unspecified. Furosemide 140 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_ccf0b2d872178629c7afdc36a9363b87). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 93: Larry Twomey

Stable patient: patient_2632896afedc1e480825781fc5ee8521; birth date 1951-03-12; strata: acuity/2, acuity/3, acuity/5, age/65-79, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/J189, pathway/R079, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- OPD 2024-04-15T21:02:00Z to 2024-04-15T22:35:00Z; acuity 5; HOME; diagnosis R079; episode episode_049bc2e07b4744907017b66adfb49f2b; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2024-04-15T22:35:00Z: Clinical review: Larry Twomey, age 73. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.55 % (record clinical_event_7a6b1dedc2e084d8aada40e50c663a7e). Heart rate: 82.20 /min (record clinical_event_92b30e9ffd36ed7f74dea12ca943616e). Troponin I: 5.18 ng/L (record clinical_event_d2476348a05fd3fd5555f80404604465). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2024-10-09T13:00:00Z to 2024-10-09T15:04:00Z; acuity 5; HOME; diagnosis R1010; episode episode_31b4bfc1b362be433f4010726c7a076f; predecessor encounter_version_17e2fe8943d7bba1fab1d5a754530f21.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2024-10-09T15:04:00Z: Encounter review: Larry Twomey, age 73. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.59 % (record clinical_event_a114e94e0b0d82ed5f2294f44f2fafd8). Heart rate: 98.75 /min (record clinical_event_f4556f21ab69b1b4f5dac287f221ffa1). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2025-11-30T16:20:00Z to 2025-11-30T20:20:00Z; acuity 3; TRANSFER; diagnosis J189; episode episode_4f4c997d7844fcbc9736ed642b51779b; predecessor encounter_version_34725bc8df573769f39d0fa872e42346.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2025-11-30T20:20:00Z: Assessment update: Larry Twomey, age 74. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Oxygen saturation: 93.75 % (record clinical_event_a82e3c75acc5099e32412f9ab73a1349). Heart rate: 101.75 /min (record clinical_event_bd5dbd1fcc12227b1e2b72063b4af118). White blood cell count: 15.09 10*3/uL (record clinical_event_37e0070b88abb876aa08255b48daa790). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- IPD 2025-11-30T20:20:00Z to 2025-12-06T19:20:00Z; acuity 2; HOME; diagnosis J189; episode episode_4f4c997d7844fcbc9736ed642b51779b; predecessor encounter_version_f7fe4ec0c33ac7919521b9a68b028d10.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=12, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Doxycycline 100 mg PO COMPLETED; Doxycycline 100 mg PO COMPLETED.

  PROGRESS_NOTE @ 2025-12-01T00:20:00Z: Care assessment: Larry Twomey, age 74. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Body temperature: 38.08 Cel (record clinical_event_871bcc620bc3a55dff74f90a06405f44). Oxygen saturation: 92.28 % (record clinical_event_17c0bfed042026c6b12f894f9019ad76). White blood cell count: 12.34 10*3/uL (record clinical_event_df2c5e7fa42fab9db52430d92b96246e). C-reactive protein: 76.02 mg/L (record clinical_event_0a452ff012427358f76237759ef48598). Prior problem documentation is incomplete; absence of a record does not exclude disease. Doxycycline 100 mg administered (record clinical_event_63d92de352d706a6979055f05d46c95a). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2025-12-06T19:20:00Z: Assessment update: Larry Twomey, age 74. Presenting concern: cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. White blood cell count: 12.34 10*3/uL (record clinical_event_df2c5e7fa42fab9db52430d92b96246e). White blood cell count: 8.17 10*3/uL (record clinical_event_07b594a537f0c8c5b3cf80bc26c5144c). C-reactive protein: 76.02 mg/L (record clinical_event_0a452ff012427358f76237759ef48598). C-reactive protein: 15.92 mg/L (record clinical_event_ac79e8d4120f721eed1a05d19e42ecd0). Prior problem documentation is incomplete; absence of a record does not exclude disease. Doxycycline 100 mg administered (record clinical_event_0c63ace24b4db279db1379a30244f926). Observed disposition: HOME. Follow-up completion is not established by this document.

## Journey 94: Brianne Cook

Stable patient: patient_7ba62c22fca85c7ac2928114f20addb9; birth date 1985-01-08; strata: acuity/2, acuity/3, acuity/4, age/35-49, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/E119, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- ED 2023-04-02T07:08:00Z to 2023-04-02T11:08:00Z; acuity 3; TRANSFER; diagnosis E119; episode episode_52302456bd8cd5c33692fc0ff0440b46; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2023-04-02T11:08:00Z: Patient review: Brianne Cook, age 38. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 96.75 % (record clinical_event_dfdef5aeabd2dbc9e14155dba81026dd). Heart rate: 108.25 /min (record clinical_event_0e924ab18411ebaa3c4d753c8dc20f82). Serum glucose: 300.30 mg/dL (record clinical_event_09062d7366b040f327f4b43e3c72ebbd). Previously recorded problems: Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- IPD 2023-04-02T11:08:00Z to 2023-04-06T01:08:00Z; acuity 2; HOME; diagnosis E119; episode episode_52302456bd8cd5c33692fc0ff0440b46; predecessor encounter_version_148cf0d2da00285d0bad6621b41a779b.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, OBSERVATION=4, ORDER=3, PROCEDURE=1.

  PROGRESS_NOTE @ 2023-04-02T15:08:00Z: Patient review: Brianne Cook, age 38. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Capillary glucose: 322.30 mg/dL (record clinical_event_a7c037186ff0c0693c0cbc1492e5466e). Heart rate: 113.25 /min (record clinical_event_7c99017a9faf475e45802033ca65bf78). Serum glucose: 322.30 mg/dL (record clinical_event_72b01b3d858b7ec8d5c702d164a8e796). Creatinine: 1.14 mg/dL (record clinical_event_7dd44350aeca0a4b6251d7e2f8c4c75d). Previously recorded problems: Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-04-06T01:08:00Z: Clinical review: Brianne Cook, age 38. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Serum glucose: 322.30 mg/dL (record clinical_event_72b01b3d858b7ec8d5c702d164a8e796). Serum glucose: 116.65 mg/dL (record clinical_event_eda40a7de1fee5326493e7ad6c201cf6). Creatinine: 1.14 mg/dL (record clinical_event_7dd44350aeca0a4b6251d7e2f8c4c75d). Creatinine: 0.91 mg/dL (record clinical_event_975137d4a5ba1298be8a302fb95ae8bb). Previously recorded problems: Type 2 diabetes mellitus without complications. Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2023-04-15T15:35:00Z to 2023-04-15T17:46:00Z; acuity 3; HOME; diagnosis R1010; episode episode_20c7f0976140216d2a31c252e15e3b49; predecessor encounter_version_9238ee3f4201e1c3728e7469187b0c49.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2023-04-15T17:46:00Z: Patient review: Brianne Cook, age 38. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 96.09 % (record clinical_event_1f5c9ad257821685b9125c511c313d0e). Heart rate: 111.00 /min (record clinical_event_c01327ef97a87c24cedf97ea4b4c9d13). Hemoglobin: 14.11 g/dL (record clinical_event_70ef7d3f54af79fe9db7fef2d857c4dc). Previously recorded problems: Type 2 diabetes mellitus without complications. Continue assessment as results become available. Follow-up completion is not established by this document.
- OPD 2025-11-10T18:44:00Z to 2025-11-10T19:45:00Z; acuity 4; HOME; diagnosis E119; episode episode_849eecdcaf84067762983b97d672b878; predecessor encounter_version_adf06aeb3b2a34e1c59c2b7f294241d0.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  OP_NOTE @ 2025-11-10T19:45:00Z: Encounter review: Brianne Cook, age 40. Interval follow-up for symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 97.59 % (record clinical_event_76eb23bc9315a6b49430347269aa2601). Heart rate: 83.10 /min (record clinical_event_755da2064a87a2b50454d114d81fc535). Previously recorded problems: Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- ED 2025-12-18T22:25:00Z to 2025-12-19T00:06:00Z; acuity 3; HOME; diagnosis R1010; episode episode_d101717c594fc0240386aad617e94dfa; predecessor encounter_version_a53bbc6f2c90583ba545b406ad4e0304.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2025-12-19T00:06:00Z: Interval assessment: Brianne Cook, age 40. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 97.86 % (record clinical_event_e80875c6b69c763a86603e4e68692727). Heart rate: 95.25 /min (record clinical_event_9c33aa01e5c3567ebccf7ebf1a1709fb). Previously recorded problems: Type 2 diabetes mellitus without complications. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 95: Mary Parra

Stable patient: patient_de603f26412749b0f6d4623cf6047895; birth date 1955-02-03; strata: acuity/5, age/65-79, carry/False, long-stay/False, outcome/HOME, pathway/E119, repeat/False, service/ED, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- ED 2025-07-28T23:10:00Z to 2025-07-29T01:47:00Z; acuity 5; HOME; diagnosis E119; episode episode_96f7a210da4a59bef1a1916e3bab5266; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2025-07-29T01:47:00Z: Patient review: Mary Parra, age 70. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 96.06 % (record clinical_event_0c1a7360fdc7cfb66ec8bdfa8cdae110). Heart rate: 114.75 /min (record clinical_event_022a6e6e3dd7e2137f4139e7ba9d0ff0). Serum glucose: 328.90 mg/dL (record clinical_event_fea824c9090dacd2d54a02a6cc293c02). Previously recorded problems: Heart failure, unspecified; Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 96: Joshua Baumgardner

Stable patient: patient_2925749af9574d71844bedd1121ddd55; birth date 1990-07-12; strata: acuity/3, acuity/5, age/18-34, carry/False, long-stay/False, outcome/HOME, pathway/K8010, pathway/R079, repeat/True, service/ED, service/IPD, site/facility_7990133218ef060b178c3cf8a0825f76.

- IPD 2023-07-28T14:51:00Z to 2023-08-01T16:51:00Z; acuity 3; HOME; diagnosis K8010; episode episode_746d2190daade7de2eb53bd596e791e3; predecessor none.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=10, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2023-07-29T00:51:00Z: Assessment update: Joshua Baumgardner, age 33. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 5.00 1 (record clinical_event_477ea3ef50dd611ddb75376e5f5202e9). Heart rate: 113.25 /min (record clinical_event_e08c6efa3a8370b83b3b057ce6540a6e). Hemoglobin: 13.94 g/dL (record clinical_event_bf9cb505568d9d125c9249d7be5c2aa8). Creatinine: 1.12 mg/dL (record clinical_event_63f125641bfbd7969522f30a160f4e6a). Prior problem documentation is incomplete; absence of a record does not exclude disease. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_3d3ff6455abcf176a6982c4904254fc3). Acetaminophen 650 mg administered (record clinical_event_93a4a5c73c2c3e8039951297e0204432). Continue assessment as results become available. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-08-01T16:51:00Z: Clinical review: Joshua Baumgardner, age 33. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 13.94 g/dL (record clinical_event_bf9cb505568d9d125c9249d7be5c2aa8). Hemoglobin: 13.24 g/dL (record clinical_event_486c1e593c7cffc06774d509a158ab72). Creatinine: 1.12 mg/dL (record clinical_event_63f125641bfbd7969522f30a160f4e6a). Creatinine: 0.89 mg/dL (record clinical_event_3cfbaf3f96fc00b60ac80753c7e56770). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 650 mg administered (record clinical_event_eb791b9d4ba97cf202c8c4a7fe596af2). Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2024-12-31T13:06:00Z to 2024-12-31T15:02:00Z; acuity 5; HOME; diagnosis R079; episode episode_5a4e7a9c0ce4504886360f8ebc6168b4; predecessor encounter_version_58c5aa316ba78cef4fb9a21ff10b1364.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2024-12-31T15:02:00Z: Clinical review: Joshua Baumgardner, age 34. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.83 % (record clinical_event_c85444f950f096878840974a3b4b749d). Heart rate: 114.75 /min (record clinical_event_4d4cf8bf3d7c8d64a234e69f4728e8ee). Troponin I: 3.74 ng/L (record clinical_event_4ea22d9fbb660b01db101438649617af). Prior problem documentation is incomplete; absence of a record does not exclude disease. The current assessment may change with further evidence. Follow-up completion is not established by this document.

## Journey 97: Gloria Rhodes

Stable patient: patient_a13204012b5312bb665a616d0fbdf13f; birth date 1951-04-24; strata: acuity/3, acuity/4, acuity/5, age/65-79, carry/False, long-stay/False, outcome/HOME, outcome/TRANSFER, pathway/E119, pathway/I509, pathway/J189, pathway/J449, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- ED 2023-01-12T03:33:00Z to 2023-01-12T06:26:00Z; acuity 3; HOME; diagnosis E119; episode episode_753cac5b5a5e3bf4591d5832daee38f2; predecessor none.
  Captured evidence: DOCUMENT=1, OBSERVATION=2.

  ED_NOTE @ 2023-01-12T06:26:00Z: Interval assessment: Gloria Rhodes, age 71. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 98.85 % (record clinical_event_e4ab65aac42bc3d06643a625767d27b1). Heart rate: 90.25 /min (record clinical_event_560558a0034262ab6519a34057c8a1d2). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Type 2 diabetes mellitus without complications. Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2023-04-24T08:31:00Z to 2023-04-24T12:31:00Z; acuity 3; TRANSFER; diagnosis I509; episode episode_ccfc7597937434606893374ebe0d4174; predecessor encounter_version_44e3089a5dec1471f0edf623462b8177.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=1.

  ED_NOTE @ 2023-04-24T12:31:00Z: Clinical review: Gloria Rhodes, age 72. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 94.98 % (record clinical_event_2f1ee4f887d2638917391490c5a0d505). Heart rate: 103.75 /min (record clinical_event_ea85e6b9b3e812b363df8c8a4b70d7ec). Creatinine: 1.25 mg/dL (record clinical_event_d1a71907a400e1d25baf047608995581). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Heart failure, unspecified; Type 2 diabetes mellitus without complications. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- IPD 2023-04-24T12:31:00Z to 2023-04-28T22:31:00Z; acuity 3; HOME; diagnosis I509; episode episode_ccfc7597937434606893374ebe0d4174; predecessor encounter_version_3fae87d4d18404ad4d4adfa891f9f768.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=5, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Furosemide 20 mg PO COMPLETED; Furosemide 20 mg PO COMPLETED.

  PROGRESS_NOTE @ 2023-04-24T16:31:00Z: Encounter review: Gloria Rhodes, age 72. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Body weight: 109.17 kg (record clinical_event_dd004c9bc87b195a67be4dc1f537f298). Oxygen saturation: 93.27 % (record clinical_event_561b861fc16e6c96eda19bc3a1332fc1). Creatinine: 1.17 mg/dL (record clinical_event_d30448b2b75c521f9a18155cdfcba6a6). Potassium: 4.39 mmol/L (record clinical_event_7334b335692b552d781fb16fc987b07e). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Heart failure, unspecified; Type 2 diabetes mellitus without complications. Furosemide 20 mg administered (record clinical_event_71029fd12ba6eb62379290a025a36acf). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-04-28T22:31:00Z: Patient review: Gloria Rhodes, age 72. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Creatinine: 1.17 mg/dL (record clinical_event_d30448b2b75c521f9a18155cdfcba6a6). Creatinine: 1.13 mg/dL (record clinical_event_93a197eda35ecb94ec3054328aec625b). Potassium: 4.39 mmol/L (record clinical_event_7334b335692b552d781fb16fc987b07e). Potassium: 4.09 mmol/L (record clinical_event_0991db1452dfedc9e98895caf6d944d7). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Heart failure, unspecified; Type 2 diabetes mellitus without complications. Furosemide 20 mg administered (record clinical_event_05465550387c2adef9bf84b3b844b5b9). Observed disposition: HOME. Follow-up completion is not established by this document.
- ED 2024-04-29T08:27:00Z to 2024-04-29T10:51:00Z; acuity 5; HOME; diagnosis E119; episode episode_aba7a33141fb14b6ea7ee4773bb1fa67; predecessor encounter_version_7ea5ab19c4c5737a265e10ef0f55e4e9.
  Captured evidence: DOCUMENT=1, OBSERVATION=2, ORDER=1, PROCEDURE=1.

  ED_NOTE @ 2024-04-29T10:51:00Z: Clinical review: Gloria Rhodes, age 73. Presenting concern: symptomatic hyperglycemia requiring assessment. Working assessment: Type 2 diabetes mellitus without complications. Oxygen saturation: 97.32 % (record clinical_event_6803df3cd90472109ab5fa75fb8ebbbf). Heart rate: 90.25 /min (record clinical_event_d8d187081f85464ef7ee498da3e27acf). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Heart failure, unspecified; Type 2 diabetes mellitus without complications. The current assessment may change with further evidence. Follow-up completion is not established by this document.
- OPD 2024-05-06T18:56:00Z to 2024-05-06T20:06:00Z; acuity 4; HOME; diagnosis J189; episode episode_fd480136c0141eeac35544dd7c141a50; predecessor encounter_version_de1d7f41ae1b6b0a81be15a0db810b1c.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=2.
  Treatment evidence: Doxycycline 1400 mg PO COMPLETED.

  OP_NOTE @ 2024-05-06T20:06:00Z: Interval assessment: Gloria Rhodes, age 73. Interval follow-up for cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Oxygen saturation: 97.33 % (record clinical_event_f46e382498fafa35fc2c4c8a8b9e3679). Heart rate: 82.65 /min (record clinical_event_5c4c6358a2c8623de5e9cdd84b00ef78). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Heart failure, unspecified; Type 2 diabetes mellitus without complications. Doxycycline 1400 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_432f9e1e76682b0153b938c1e0d159bf). Continue assessment as results become available. Follow-up completion is not established by this document.
- ED 2025-05-10T00:56:00Z to 2025-05-10T02:36:00Z; acuity 3; HOME; diagnosis I509; episode episode_4df9142404e29508d25bc3dbb5e5ab22; predecessor encounter_version_95b21dd4b95aa803f6558e3b7a0c17b8.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=1.
  Treatment evidence: Furosemide 140 mg PO COMPLETED.

  ED_NOTE @ 2025-05-10T02:36:00Z: Encounter review: Gloria Rhodes, age 74. Presenting concern: worsening edema and breathlessness. Working assessment: Heart failure, unspecified. Oxygen saturation: 93.09 % (record clinical_event_4d292bafa724e834f0f4e2cb879b0eaf). Heart rate: 91.25 /min (record clinical_event_6a3e2d519bac18c48936e042a8c5d11e). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Heart failure, unspecified; Type 2 diabetes mellitus without complications. Furosemide 140 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_ec930c7f81be1c3893207a031aebfcda). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- OPD 2025-11-18T17:56:00Z to 2025-11-18T19:34:00Z; acuity 4; HOME; diagnosis J449; episode episode_bf48696a991b3e2a8c6e21b61213cba8; predecessor encounter_version_07b63003f829289b9470f58215f732d7.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=1.
  Treatment evidence: Prednisone 200 mg PO COMPLETED.

  OP_NOTE @ 2025-11-18T19:34:00Z: Patient review: Gloria Rhodes, age 74. Interval follow-up for increased dyspnea with wheezing. Working assessment: Chronic obstructive pulmonary disease, unspecified. Oxygen saturation: 95.29 % (record clinical_event_74b2917b0b9b8d0a45359b34725a83e6). Heart rate: 86.10 /min (record clinical_event_07a24fb0a4d0cfd4c84ede66343da9a1). Previously recorded problems: Chronic obstructive pulmonary disease, unspecified; Heart failure, unspecified; Type 2 diabetes mellitus without complications. Prednisone 200 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_af2fceae249bbee85702e59c36b626b9). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 98: Justin Lam

Stable patient: patient_f25a6ad6d21cf6bd02d508e1aac4491c; birth date 1987-10-16; strata: acuity/3, acuity/5, age/35-49, carry/False, long-stay/False, outcome/HOME, pathway/J189, pathway/K8010, pathway/R079, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- OPD 2022-12-20T06:00:00Z to 2022-12-20T08:00:00Z; acuity 5; HOME; diagnosis J189; episode episode_b475bf926e3630cac44800d66e9c9259; predecessor none.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=1.
  Treatment evidence: Doxycycline 1400 mg PO COMPLETED.

  OP_NOTE @ 2022-12-20T08:00:00Z: Care assessment: Justin Lam, age 35. Interval follow-up for cough, fever and reduced exercise tolerance. Working assessment: Pneumonia, unspecified organism. Oxygen saturation: 97.11 % (record clinical_event_8afbfaf82fac4064c2a04de1148d8cd9). Heart rate: 72.00 /min (record clinical_event_2939b0bf459ffae8c9b38c8f1f1af9c6). Prior problem documentation is incomplete; absence of a record does not exclude disease. Doxycycline 1400 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_af9ff8d60c7f74fd52b91382062becd7). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- IPD 2023-02-06T15:09:00Z to 2023-02-10T18:09:00Z; acuity 3; HOME; diagnosis K8010; episode episode_832325b8cc0f34979d2ffb3f60f433a1; predecessor encounter_version_f83d4b61cca0e4e4e401f0cbd5df295a.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=10, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2023-02-07T01:09:00Z: Encounter review: Justin Lam, age 35. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 6.00 1 (record clinical_event_2d27ca6072d94dcb7ecc7d65afee80c9). Heart rate: 91.00 /min (record clinical_event_91b6dc8d92b39b5f3b9fd04ed09f15a8). Hemoglobin: 14.56 g/dL (record clinical_event_883cad0674784729eb93f340bb83d8ba). Creatinine: 0.91 mg/dL (record clinical_event_f383426de93a3293b62f2782ae7ebbf2). Prior problem documentation is incomplete; absence of a record does not exclude disease. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_372a3b479dbeb9f125db5fe46f90b376). Acetaminophen 650 mg administered (record clinical_event_71c7c68969ad16d0265495289ea09146). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2023-02-10T18:09:00Z: Care assessment: Justin Lam, age 35. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 14.56 g/dL (record clinical_event_883cad0674784729eb93f340bb83d8ba). Hemoglobin: 13.86 g/dL (record clinical_event_d8d3987b36a93cf0f923fe9f463755e3). Creatinine: 0.91 mg/dL (record clinical_event_f383426de93a3293b62f2782ae7ebbf2). Creatinine: 0.90 mg/dL (record clinical_event_6b0e444603247b68913e9ee4f8e47e45). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 650 mg administered (record clinical_event_68e0a7a0c7805584fe13615beb3318eb). Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2025-01-15T19:25:00Z to 2025-01-15T20:40:00Z; acuity 3; HOME; diagnosis R079; episode episode_cae4ca20cda0e67fd490d0a999dac8fa; predecessor encounter_version_e92707bdffb397f557d7b87227caa58c.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2025-01-15T20:40:00Z: Patient review: Justin Lam, age 37. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.36 % (record clinical_event_7a67c0b3276a31ba703a1d3142b5f4a0). Heart rate: 73.95 /min (record clinical_event_e670a83aaef3712b0bca0c268168df8e). Troponin I: 7.34 ng/L (record clinical_event_c47fcda1fa49fde697f1cfceb08209f1). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- ED 2025-06-05T04:16:00Z to 2025-06-05T06:37:00Z; acuity 5; HOME; diagnosis R079; episode episode_01eebf9f55121dcb82cd60c94f3a60e6; predecessor encounter_version_1aaea88f5aa5fa6ce864a99af331764a.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  ED_NOTE @ 2025-06-05T06:37:00Z: Care assessment: Justin Lam, age 37. Presenting concern: episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 98.01 % (record clinical_event_0fa5214b46ea4f2a968593e059aa9622). Heart rate: 108.25 /min (record clinical_event_c67d61499368380008010a820e8e089a). Troponin I: 7.10 ng/L (record clinical_event_aff73301f40c82155f42d2264b6f25fe). Prior problem documentation is incomplete; absence of a record does not exclude disease. Continue assessment as results become available. Follow-up completion is not established by this document.

## Journey 99: Claudia Parks

Stable patient: patient_b63f41d5e083cedf173f4bdaf49adece; birth date 1995-02-07; strata: acuity/2, acuity/3, age/18-34, carry/False, long-stay/False, outcome/HOME, pathway/K8010, pathway/R079, pathway/R1010, repeat/True, service/ED, service/IPD, service/OPD, site/facility_a56f2c2e3a76834b7a766c6ba89f7afe.

- ED 2023-03-08T07:02:00Z to 2023-03-08T09:48:00Z; acuity 3; HOME; diagnosis R1010; episode episode_1645af637f1f5c33e472fac6a07334ff; predecessor none.
  Captured evidence: DOCUMENT=1, MED_DISPENSE=1, OBSERVATION=2, ORDER=1.
  Treatment evidence: Acetaminophen 13000 mg PO COMPLETED.

  ED_NOTE @ 2023-03-08T09:48:00Z: Care assessment: Claudia Parks, age 28. Presenting concern: intermittent upper abdominal discomfort requiring assessment. Working assessment: Upper abdominal pain, unspecified. Oxygen saturation: 98.91 % (record clinical_event_5e6f6cc89d5cf441e2d72087c737f705). Heart rate: 94.00 /min (record clinical_event_469558451fce87905ea4fe7441d3fb40). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 13000 mg dispensed for take-home use; ingestion is unobserved (record clinical_event_75418c8ff6105e0c83a30ba0e3cf072e). Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.
- IPD 2024-02-07T13:19:00Z to 2024-02-12T06:19:00Z; acuity 2; HOME; diagnosis K8010; episode episode_883c73a70578ebe04033e9809cac8bc4; predecessor encounter_version_9fd473fb92cf7d3d79b08f662549a852.
  Captured evidence: DOCUMENT=2, LAB_RESULT=4, MED_ADMIN=12, OBSERVATION=4, ORDER=4, PROCEDURE=1.
  Treatment evidence: Acetaminophen 650 mg PO COMPLETED; Acetaminophen 650 mg PO COMPLETED.

  OPERATIVE_NOTE @ 2024-02-07T23:19:00Z: Interval assessment: Claudia Parks, age 29. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Pain numeric rating: 8.00 1 (record clinical_event_80c51555fa019edf2138a8c4552b9da3). Heart rate: 114.00 /min (record clinical_event_975af3b9723ffb01ffef94ae8a552cc5). Hemoglobin: 14.12 g/dL (record clinical_event_2a73fbf589e37fc8b1b54c8a8a5d9829). Creatinine: 1.35 mg/dL (record clinical_event_94a19fc405fa32fc97aa86b2f3086a13). Prior problem documentation is incomplete; absence of a record does not exclude disease. Procedure documented: Resection of Gallbladder, Percutaneous Endoscopic Approach (record clinical_event_6419b2d826e8ece1a1d1c24acab8ea57). Acetaminophen 650 mg administered (record clinical_event_689914b251d2089e3922030f8406401d). The current assessment may change with further evidence. Follow-up completion is not established by this document.

  DISCHARGE_SUMMARY @ 2024-02-12T06:19:00Z: Care assessment: Claudia Parks, age 29. Presenting concern: recurrent biliary pain with chronic calculous cholecystitis. Working assessment: Calculus of gallbladder with chronic cholecystitis without obstruction. Hemoglobin: 14.12 g/dL (record clinical_event_2a73fbf589e37fc8b1b54c8a8a5d9829). Hemoglobin: 13.42 g/dL (record clinical_event_872bde5e719de39395f8a8ea0feeecba). Creatinine: 1.35 mg/dL (record clinical_event_94a19fc405fa32fc97aa86b2f3086a13). Creatinine: 1.11 mg/dL (record clinical_event_8bdb3975910e3d0434f82aa724565cdf). Prior problem documentation is incomplete; absence of a record does not exclude disease. Acetaminophen 650 mg administered (record clinical_event_805346dd653002c0f813fb9814225d47). Observed disposition: HOME. Follow-up completion is not established by this document.
- OPD 2024-11-19T15:51:00Z to 2024-11-19T17:36:00Z; acuity 3; HOME; diagnosis R079; episode episode_ee067e9adf7b13d22a6283fa6bbe789e; predecessor encounter_version_b1a34cb689e412392932426de14c655f.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2024-11-19T17:36:00Z: Interval assessment: Claudia Parks, age 29. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.23 % (record clinical_event_0ca7a7244a886546259d820149888920). Heart rate: 76.65 /min (record clinical_event_afb0ae397c49029650cb87e4045a688b). Troponin I: 3.68 ng/L (record clinical_event_7832a0f50ca2191fd36b81a9f3569051). Prior problem documentation is incomplete; absence of a record does not exclude disease. Reassessment remains appropriate; later outcomes are unknown here. Follow-up completion is not established by this document.

## Journey 100: Jasmine Shetler

Stable patient: patient_db22b3eb55e1df886930694326d1c164; birth date 2000-08-12; strata: acuity/4, age/18-34, carry/False, long-stay/False, outcome/HOME, pathway/R079, repeat/False, service/OPD, site/facility_a6a95cfdcf7df4bfa7fe88c206195c24.

- OPD 2024-10-04T20:02:00Z to 2024-10-04T20:40:00Z; acuity 4; HOME; diagnosis R079; episode episode_38ba0dd1f40777241074c0cbd5337da5; predecessor none.
  Captured evidence: DOCUMENT=1, LAB_RESULT=1, OBSERVATION=2, ORDER=2, PROCEDURE=1.

  OP_NOTE @ 2024-10-04T20:40:00Z: Patient review: Jasmine Shetler, age 24. Interval follow-up for episodic chest discomfort requiring evaluation. Working assessment: Chest pain, unspecified. Oxygen saturation: 97.50 % (record clinical_event_3d608f5c71a8167d1d5655faec2e1c37). Heart rate: 83.40 /min (record clinical_event_a2716a2afe81709d26276eb937419c1b). Prior problem documentation is incomplete; absence of a record does not exclude disease. The current assessment may change with further evidence. Follow-up completion is not established by this document.

