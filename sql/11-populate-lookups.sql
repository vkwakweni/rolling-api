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
       ('OVULATORY'),
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
       ('TSH', 'PITUITARY', 'PEPTIDE'),
       ('PROLACTIN', 'PITUITARY', 'PEPTIDE');

-- research.hormone_relations
INSERT INTO research.hormone_relations(source_hormone, target_hormone, relation, notes)
VALUES ('FSH', 'OESTROGEN', 'STIMULATES', 'Follicular development increases oestrogen production'),
       ('LH', 'PROGESTERONE', 'STIMULATES', 'Ovulation/luteal function supports progesterone production'),
       ('OESTROGEN', 'LH', 'POSITIVE_FEEDBACK_ON', 'High estradiol can contribute to LH surge'),
       ('OESTROGEN', 'FSH', 'NEGATIVE_FEEDBACK_ON', 'Typical follicular negative feedback'),
       ('PROGESTERONE', 'LH', 'NEGATIVE_FEEDBACK_ON', 'Luteal-phase feedback'),
       ('PROGESTERONE', 'FSH', 'NEGATIVE_FEEDBACK_ON', 'Luteal-phase feedback'),
       ('PROLACTIN', 'FSH', 'INHIBITS', 'Hyperprolactinemia can suppress gonadotropin axis'),
       ('PROLACTIN', 'LH', 'INHIBITS', 'Hyperprolactinemia can suppress gonadotropin axis'),
       ('CORTISOL', 'LH', 'INHIBITS', 'Stress-axis effects can suppress reproductive axis'),
       ('CORTISOL', 'FSH', 'INHIBITS', 'Stress-axis effects can suppress reproductive axis'),
       ('TSH', 'FT4', 'STIMULATES', 'TSH stimulates thyroid hormone production'),
       ('TSH', 'FT3', 'STIMULATES', 'TSH stimulates thyroid hormone production');

-- INSERT INTO research.sexes (sex)
-- VALUES ('F'), ('M'), ('I');

-- INSERT INTO research.symptom_severity (symptom_severity)
-- VALUES ('MILD'), ('MODERATE'), ('SEVERE');
