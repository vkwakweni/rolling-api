# Agentic AI Technical Policy
## Purpose
The following document defines the technical controls that the limit the scope and reach of AI services in the _Rolling_ API. Generally, the AI layer for the API must reamin bounded, non-privileged, analyst-initiated, and restrict to approved reporting tasks.

## Architectural Principle
The following section provides a general overview of the AI workflow with _Rolling_. Here, we discuss the design decisions and provide a schematic of the AI workflow with the application layer.

* The intended flow for AI mode is:
    1. Core backend executes analysis normally
    2. The application builds a reduced AI-safe payload from approved outputs
    3. The AI service receives only that reduced payload
    4. The AI returns a more cohesive narrative report
    5. The analyst reviews the output.

* To support the distinction between traditional and AI reporting, there is a strict distinction between analysis outputs, namely:
    * structured analysis result payloads
    * traditional reports
    * AI-generated report drafts.

The AI service is completely decoupled from the analysis engine. The components of the AI reporting service work with each other through models, with details like prompt building and output validation broken into different components.

The AI services has five modules: one for building input, another for building the prompt, a client module for generating the report, a validator for the output, and finally an orchestrator module that structures the components.

The first stage is converting the analysis results and report into an AI prompt with definitive instructions. This is broken into two modules.
* `AIInputBuilder` class:
    * The main method of this `analysis_reults: list[AnalysisResultResponse]` and `analysis_report: AnalysisReportResponse`
        * Given that `analysis_results` contains the observation values for a set of statistics, it is here that these observations are removed.
        * Aside from summary data (like means and effect sizes), meta data is collected. The metadata contains the IDs from which the results and report were derived, a field for the kind of analysis result (in version 1, a descriptive analysis), and the table names (a snake-cased set of cartesian products of the parameters for analysis).
    * The main method of this class produces an `AIAnalysisReportInput`.
* `AIPReportPromtBuilder` class:
    * Takes `ai_input: AIAnalysiisReportInput`.
    * There is a class variable `SYSTEM_PROMPT` that describes the role of the AI service. In version one, this is providing a more cohesive narrative of the report.
    * The main method of this class takes the report summaries and tables from `AIAnalysisReportInput` and formats it in a `user_prompt`, where it formats it to an understable prompt and requests a specific output type.
    * The main method of this class produces an `AIPrompt`.

The next stage is setting up the AI service. This is broken into two modules.
* `AIProvider` class:
    * This is an abstract class. For working with a particular AI service, a new class must be created, inheriting this abstract class. It is implements its own way generating an AI prompt which the parameters necessary (e.g. OpenAI's model would need the prompts (user and system) to be given to parameter `input`, where an Ollama model needs to message `messages`). This abstrasct method is `geenrate` and it outputs a dictionary, that was parsed from the JSON output of the model.
* `AIModelClient` class:
    * To be instantiated, this class needs a model name and a provider.
        * The details of calling the AI external client are encapsulated within its provider attribute.
    * The main method of this class produces an `AIModelOutput`, using the `generate` function from its provder.

The output needs to be verified that the model name is non-empty and the generated text is not empty.
* `AIReportValidator` class:
    * The main method of class takes `generated_output: AIModelOutput`.
    * Should validation be successful, it return the same `AIModelOutput`.
    * Should validation be unsuccessful, `ValueError`s are through with an appropriate message.

Finally, these four modules are organised into a workflwo in an orchestrator class. This is the outward facing interface that would be called during routing.
* `AIReportOrchestrator` class:
    * The main method of this class takes an `analyst_id: UUID` and an `analysis_run_id: UUID`.
    * It confirms that the given analayst has access to the given analysis run, which also prove existence.
    * It then constructs and passes on an `AIAnalysisReportInput`, `AIPrompt`, `AIModelOutput` (and verifies it).
    * Following verifcation, it persists the metadata and the report to the database.
    * the main method of this class outputs a `GenerateAIAnalysisReportResponse`, producing the persisted records.

## Approved AI Boundary
The following section starts with providing an overview of tasks that the AI may and may not perform.

* AI may:
    * interpret structured descriptive analysis outputs
    * rewrite generated reports for clarity
    * summarise group findings by analyst request
    * propose follow-up analytical questions

These allowed input are detailed in [`prompt_builder.py`](../app/services/ai/prompt_builder.py).

* AI may not:
    * execute database queries directly
    * read arbitrary local files
    * invoke destructive scripts
    * choose or change permissions
    * operate without explicit analyst or route initiation.

These prohibitions are implemented in [`input_builder.py`](../app/services/ai/input_builder.py) and [`orchestrator.py`](../app/services/ai/orchestrator.py). In `input_builder`, inputs are build from passed variables. In `orchestrator.py`, while database queries are made, this is not part of prompt instructions. The only input received by the AI is the what the codebase passes explicitly. Finally, specific routes need to be posted and specific payload need to be given for the AI service to be used.

### Enforced Boundary Module
The following section provides a detailed description of how the AI boundary is enforced. AI functionality is centralised in a dedicated directory: ['app/services/ai`](../app/services/ai/).

There is no repository or analysis engine module that calls the model directory. AI-facing code does not import or call repository functions directly.

There are two ways in which a person may generate an AI analysis report: by toggling AI-assisted mode when executing an analysis (default is off) or by explicitly requesting an AI analysis report for an already existing analysis run (given an analysis result exists, too).

## Approved Input Construction
AI inputs are contstructed through an explicit whitelist build. In these whitelisting functions, fields are labelled explicitly and transformed into models. When unapproved fields are received, they will be rejected. In the following section, the whitelisting functions will be described, as well as their expected payloads.

AI inputs are constructed in `input_builder.py` and `prompt_builder.py`. The most senstive part is the removal of `measured_values` from the `analysis_results`. This is only operational is the codebase (including repository functions) are aligned with the database. These redact `analysis_results` are then passed onto `AIReportPromptBuilder.build_prompt`.

Input and prompt payloads are constructed explicitly, with these models used in the associated circumstances. The input model is `AIAanlysisReportInput` which needs a `summary` (which is an unpacked row from the databse), `tables` (cartesian products of parameters and their statistics), `report_text` (traditionally generated), `summary_text`, and `metadata`. `AIReportPromptBuilder` takes this input and formats it into a prompt for a predictable result from the AI service.

## Prohibited AI Input Sources
The AI service works on a principle of least-privileged. Only through the `AIInputBuilder` can things be allowed to be given to the AI.

## Tool Restrictions
At this stage in development, there are no tools with in the application's codebase the AI service as access to. Given that it's only task is re-write the generated analysis report (and eventually point out notable relationships between certain statistics), its natural language processing capabilities are sufficient. Thus, the given tool set is empty for version 1.

## Storage rules
For everything successfully generated AI report (i.e. non-empty and in the correct format), a record of the generation is kept in the table agent_traces and the actual report content is kept in the ai_analysis_reports table. The orchestrator module is responsible for using repository functions, decoupled the AI input and output components.

## Testing Requirements
The nature of the AI assistance is to create a more readable report that is meant to be reviewed and augmented by an analyst for real analysis workflows. Thus, the quality of the output is not tested, since this is up to the model a user selects. Instead, testing is done so that with a working provider, the workflow happens as expected. Conversely, an adverse conditions have been checked so that understandable errors and HTTP responses are returned.
