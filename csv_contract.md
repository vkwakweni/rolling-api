# CSV upload contract
* Every CSV should use
    * UTF-8
    * Header row required
    * Column names are case-sensitive and must match exactly
    * Date format:
        * YYYY-MM-DD
        * YYYY
        * YYYY-MM-DD HH:MM:SS
        * YYYY-MM-DD HH:MM
    * One row = one observation
    * `athlete_code` required in every file
* Uses multiple CSVs
* Required columns must not be blank
* Optional columns can be left blank
* Column names
    * `athletes.csv`
        * Required columns:
            * `athlete_code`
                * Code format: `r"^R[A-Z0-9]{4}$"`
            * `sex`
                * Allowed values: `M`, `F`, `I`
        * Optional columns:
            * `birth_date`
                * Must be a date if provided
            * `birth_year`
                * Must be an integer if provided
            * `age_at_observation`
                * Must be an integer if provided
            * `age_logged_at`
                * Must be a date if provided
            * `notes`
    * `performances.csv`
        * Required columns:
            * `athlete_code`
            * `date`
            * `session_label`
        * Optional columns:
            * `metric_name`
            * `metric_value`
                * Must be numeric
            * `metric_unit`
    * `hormones.csv`
        * Required columns:
            * `athlete_code`
            * `date`
            * `hormone_name`
            * `measurement_value`
                * Must be numeric
        * Optional columns:
            * `measurement_unit`
    * `symptoms.csv`
        * Required columns:
            * `athlete_code`
            * `date`
            * `symptom`
        * Optional columns:
            * `severity`
                * Allowed values: `MILD`, `MODERATE`, `SEVERE`
            * `relative_day_to_cycle`
                * Must be an integer if provided
    * `cycle_phases.csv`
        * Required columns:
            * `athlete_code`
            * `date`
            * `phase`
                * Allowed values: `MENSTRUAL`, `FOLLICULAR`, `OVULATION`, `LUTEAL`
        * Optional columns:
            * `relative_day_to_cycle`
                * Must be an integer if provided