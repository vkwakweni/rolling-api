# Agentic AI Documentation Policy
## Purpose
_Rolling_ allows for an optional AI mode, where an AI agent may interpret aggregated (and non-identifiable) data and analysis reports for clearer and more cohesive reporting. From the aggregated results, it may also make suggestions for further investigation.

In summary, the AI layer is intended to support analysts by:
* summarising structured results
* rewriting reports for readability
* helping interpret descriptive outputs
* suggesting further avenues for investigation

The AI layer is not intended to:
* replace the analysis engine
* make database changes
* provide clinical conclusions
* operate without analyst oversight

## Allowed AI Use
AI may be used for:
* rewriting traditional reports into clearer natural language
* proposing follow-up analytical questions for the analyst
* summarising grouped descriptive outputs effectively

## Disallowed AI Use
AI may not be used for:
* direct SQL execution
* project, dataset, or account administration
* health, diagnosis, treatment, or training plan recommendation
* privileged workflows
* acting without explicit analyst initiation

## Allowed Inputs 
AI may receive:
* structured descriptive analysis outputs
* generated report text
* minimal metadata needed to interpret the report
* analyst-authored instructions related to summarisation or rewriting

As a rule, AI inputs will be limited to the smallest necessary set of inputs needed for a reporting task

## Prohibited Inputs
AI must not receive
* row-level observations
* raw uploaded dataset contents
* `.env` contents
* database credentials
* unnecessary personal identifiers

By default, raw uploaded CSV files should not be passed into AI workflows.

## Output Rules
AI outputs must:
* be grounded in structured application outputs
* avoid diagnostic or treatment language
* be reviewed by an analyst before being treated as final

## Human Review
AI-generated text is draft support material, not final analysis output. A human analyst remains responsible for:
* deciding when AI should be used
* reviewing AI outputs
* deciding whether outputs are accurate and suitable to retain or share

## Current Default
At the current stage of development:
* non-AI reporting remains the baseline
* AI is layered on top of existing descriptive outputs
* AI must not directly access or modify the database
