# Rolling API
## Description
`Rolling API` is a repository for the deployment of an analysis of cyclists' menstruation experience, performance, and hormone profile. It serves supplement for a Bachelor degree thesis.

## Application
* Application name: **Rolling**
* Domain: small-cohort cyclists + menstrual + hormone analysis
* Mode: local analyst workstation with optional AI assistant
* Description: _Rolling_ is a locally runnable research tool for analysing small-cohort cycling data, integrating menstrual cycle, performance, and hormone measurements, with optional agentic AI assistance for exploratory analysis and interpretation.

## Status
* What has been completed
    * API routing and configuration
    * Database set-up and stablisation
    * Development-level analyst account and project creation
    * Dataset ingestion and importing
    * Descriptive analysis of hormones, performance, and menstrual symptoms.
    * Initial integration testing
* What is yet to be developed
    * Fully hardened testing
        * For analysis engine
        * For integration
    * AI agent mode
    * Mode selection
    * Results UX
    * Packaging
    * Documentation

### Modules
* Application: [`./app`](./app/)
* Analysis: [`./analysis_engine`](./analysis_engine/)

### Database
* Database: `rolling`
* Owner role: `rolling_owner`
* Migration role: `rolling_migrator`
* API user role: `appuser`
* Schemas:
    * `app_private`
    * `research`
    * `projects`

## Set-up
* Python version: `3.11`
* PostgreSQL version: `14.22`
* To set up the virtual environment, you can download the packages listed in [`requirements.txt`](./requirements.txt):
    * `pip install -r requirements.txt`
* After you have set up the environment in your `.venv`, make sure you activate the virtual environment.

### Environment
* The API has certain environment variables that allow for authorised access.
* When you are first setting up the API:
    * I have initialised a file called [`dotenv`](./dotenv) which contains all the variables you will need for the API. If you are using version control, make sure you include `.env` in your `.gitignore` file or equivalent.
    * Then you can execute this: `mv ./dotenv ./.env`. This is so that the Python script reads the environment variables from this file. Once this is done, you can replace the fields, as I explain below.
* At this stage in development, it is primarily used for PostgreSQL connection.
    * Environment variables `APP_NAME`, `LOG_LEVEL`, `DB_NAME`, and database pool connection already have initial values.
    * For a local set-up you will need to configure:
        * `DB_HOST`: usually localhost, but can be configured otherwise
        * `DB_USER`: this can be `appuser`, an established role for API calls to the database
        * `DB_PASS`: when roles are set up, they have initial passwords; you are to change them on your system, and put the new password here
        * `DB_PORT`: the port to which PostgreSQL works
    * When you have done the above, you can use them to construct `DATABASE_URL`, replacing the `<PLACEHOLDERS>` with the matching literal string.
    * The database pool connection variables are for a later planned stage of development in which the API can handle several connections to the database. At this stage, you may leave it as is.
* How the app connects to PostgreSQL
    * The connection is made using the `psycopg2` library. You simply need to have PostgreSQL installed on your system (development was done in PostgreSQL 14.22)
    * Once you have set up the database, when you run the application, the program will use the environment variables to make a connection.
* Note the default passwords in SQL are dev placeholders

### Database Bootstrap
* Database set up is simplified through a set of sequentially run files
    * In [sql/](./sql/), you will find 13 SQL files. Upon first use, you need to run files `01-init.sql` to `11-populate-lookups.sql` in order.
        * Caveat: depending on how you run the scripts, you may not be able to run the database creation query within a block transaction. You may then execute the queries before in a block, the `CREATE DATABASE` by itself, and then the rest of the queries. The remaining files can then be run in order.
    * When you first run `01-init.sql`, run it as user `postgres` from the `postgres` database. From `02-schemas.sql`, run the scripts as user `rolling_owner` from database `rolling`.
* If you want to completely clear the database, run `00-clear.sql`. You will need to run it as user `rolling_owner` from the `postgres` database. Then as the `postgres` user, you can delete the roles.
* Roles:
    * `rolling_owner`
    * `rolling_migrator`
    * `appuser`

## Usage
### Run the API
* To run the application, you can use either of these commands from the repository root
    * If `uvicorn` is only installed in your virtual environment: `python3 -m uvicorn app.main:app --reload`
    * Otherwise, `uvicorn app.main:app --reload`

### Dev Helpers
* I have three files that can help with development or analyses:
    * `verify`: if you want to do an initial analysis to test your set-up, you can run `./scripts/verify` from the bash terminal from the repository root; you can then review the output or handle errors in your data cleaning.
    * `reset-dev-db`: if you want to clear all the (test) analyses, analyst accounts, and projects you have created, you can run `./scripts/reset-dev-db --apply` which clears imported research data, as well as analyst accounts and projects. Seeded tables are retained.
    * `clear-upload-batches`: this clears all files that were uploaded on to the local disk; you can run `./scripts/clear-upload-batches --apply`.

### Testing
* For file uploads, currently development supports files named exactly for the kind of data they hold. Therefore, for testing, it is necessary to split the test upload files by workflow and scenario:
    * Folder `ingest_import_analyse` thus represents files to be uploaded for the workflow that includes ingesting, importing, and analysing. Within that folder, there is `good_complete_bundle`, which are perfect files that should upload during tests. Files named like `bad_*` are for testing expected failures and errors.

### Current workflow
1. Create an analyst account through the API
2. Create a project under that analyst
3. Upload a dataset bundle to the project
    * The current workflow expects separate files for athletes, performances, hormones, symptoms, and cycle phases.
4. The upload process validates the files, creates dataset records, links datasets to the project, and imports the research rows into the database
5. Run the descriptive hormone analysis for the project through the analysis API endpoint
6. The analysis workflow gathers hormone, menstrual symptom, and performance inputs, computes grouped descriptive statistics, stores the analysis run, result, and report, and returns them through the API
7. Review the generated analysis result and traditional report through the API or by manual database inspection during development
8. During development, use the helper scripts to verify the workflow, reset development data, and clear uploaded batch folders when needed

