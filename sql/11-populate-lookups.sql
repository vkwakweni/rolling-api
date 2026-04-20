-- TODO: set some kind of role that can do these inserts

-- research.performance_metric_types
INSERT INTO research.performance_metric_types(name, unit)
VALUES ('TSS', ''), -- TODO: double check TSS, Avg Power and IF
       ('DISTANCE', 'KM'),
       ('AVG HR', 'BPM'),
       ('AVG POWER', 'W'),
       ('IF', '');

-- research.performance_types
INSERT INTO research.performance_types(name)
VALUES ('TRAINING-RECOVERY'), ('TRAINING-TAPERING'), ('TRAINING-PREPARATION'),
       ('RACE'), ('OFF SEASON'); -- TODO: clarify what each stage actually is

-- research.cycle_phase_types
INSERT INTO research.cycle_phase_types(name)
VALUES ('FOLLICULAR'),
       ('MENSTRUAL'),
       ('OVULATION'),
       ('LUTEAL');

-- research.menstrual_symptoms
INSERT INTO research.menstrual_symptoms(name)
VALUES ('DYSMENORRHEA'),
       ('BREAST TENDERNESS'),
       ('ACHES'),
       ('HEADACHES'),
       ('BLOATING'),
       ('SLEEP CHANGES'),
       ('MOOD CHANGES');

-- research.relations
INSERT INTO research.relations(name)
VALUES ('STIMULATES'),
       ('INHIBITS'),
       ('NEGATIVE_FEEDBACK_ON'),
       ('POSITIVE_FEEDBACK_ON'),
       ('MODULATES'),
       ('PERMITS'),
       ('UPREGULATES_RECEPTOR_FOR'),
       ('DOWNREGULATES_RECEPTOR_FOR');

-- research.glands
INSERT INTO research.glands(name)
VALUES ('PINEAL'),
       ('PITUITARY'),
       ('HYPOTHALAMUS'),
       ('THYROID'),
       ('THYMUS'),
       ('STOMACH'),
       ('LIVER'),
       ('PANCREAS'),
       ('OVARY'),
       ('UTERUS'),
	   ('ADRENAL'),
       ('TESTES');

-- research.chemical_classes
INSERT INTO research.chemical_classes(name)
VALUES ('LIPID'),
       ('AMINO ACID-DERIVED'),
       ('PEPTIDE');

-- research.hormones
INSERT INTO research.hormones(name, gland, chemical_class)
VALUES ('CORTISOL', 'ADRENAL', 'LIPID'),
       ('OESTROGEN', 'OVARY', 'LIPID'),
       ('TESTOSTERONE', 'TESTES', 'LIPID'),
       ('PROGESTERONE', 'OVARY', 'LIPID'),
       ('LH', 'PITUITARY', 'PEPTIDE'),
       ('FSH', 'PITUITARY', 'PEPTIDE'),
       ('FT3', 'THYROID', 'AMINO ACID-DERIVED'),
       ('FT4', 'THYROID', 'AMINO ACID-DERIVED'),
       ('RT3', 'THYROID', 'AMINO ACID-DERIVED'),
       ('HTSH', 'PITUITARY', 'PEPTIDE'),
       ('PROLACTIN', 'PITUITARY', 'PEPTIDE');

-- research.hormone_relations
INSERT INTO research.hormone_relations(source_hormone, target_hormone, relation, notes)
VALUES (6, 2, 'STIMULATES', 'Follicular development increases oestrogen production'),
       (5, 4, 'STIMULATES', 'Ovulation/luteal function supports progesterone production'),
       (2, 5, 'POSITIVE_FEEDBACK_ON', 'High estradiol can contribute to LH surge'),
       (2, 6, 'NEGATIVE_FEEDBACK_ON', 'Typical follicular negative feedback'),
       (4, 5, 'NEGATIVE_FEEDBACK_ON', 'Luteal-phase feedback'),
       (4, 6, 'NEGATIVE_FEEDBACK_ON', 'Luteal-phase feedback'),
       (11, 6, 'INHIBITS', 'Hyperprolactinemia can suppress gonadotropin axis'),
       (11, 5, 'INHIBITS', 'Hyperprolactinemia can suppress gonadotropin axis'),
       (1, 5, 'INHIBITS', 'Stress-axis effects can suppress reproductive axis'),
       (1, 6, 'INHIBITS', 'Stress-axis effects can suppress reproductive axis'),
       (10, 8, 'STIMULATES', 'TSH stimulates thyroid hormone production'),
       (10, 7, 'STIMULATES', 'TSH stimulates thyroid hormone production');

INSERT INTO research.sexes (sex)
VALUES ('F'), ('M'), ('I');

INSERT INTO research.symptom_severity (symptom_severity)
VALUES ('MILD'), ('MODERATE'), ('SEVERE');
