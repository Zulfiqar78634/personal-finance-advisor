# Personal Finance Advisor

Python assessment prototype with LangGraph orchestration, a LangChain spending agent, deterministic financial tools, session memory and a CLI. This is not production banking software.

## Files
- app.py: model-driven planner, tool-calling spending specialist, graph and CLI.
- finance.py: mock data, categorization, calculations, recommendations, alerts and rendering.
- test_finance.py: 18 deterministic unit tests.

## Architecture
Customer -> Planner -> Spending Analysis -> optional Recommendation -> optional Alerting -> Response.
The planner selects action, month, focus, category and ranking metric using structured output. Full reviews visit both supporting nodes. Clarification bypasses financial analysis. Transient results are cleared each turn.

The spending specialist calls monthly_totals and monthly_trends. It can optionally select merchant_breakdown(category), so its choice changes the evidence shown to the user. The month is bound by the application; tools cannot select arbitrary customers. Recommendation and Alerting are simplified rule-based specialists, not independent LLMs. Generated specialist prose is not used as numerical evidence; responses are rendered from tool results.

## Setup
Use Python 3.10 or later. Create and activate a virtual environment, then run:

```bash
pip install -r requirements.txt
```

PowerShell:
```powershell
$env:OPENAI_API_KEY="your-key"
$env:OPENAI_MODEL="your-tool-capable-model"
python app.py
```

Linux/macOS:
```bash
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="your-tool-capable-model"
python app.py
```
Use an actual model supporting tools and structured output. No credentials are included. Model calls can incur charges. Dependency ranges are not a validated lockfile.

## Tests and offline demonstration
These commands need only the Python standard library:
```bash
python -m unittest -v
python app.py --demo
```
The demo exercises financial functions and rendering, not LangGraph or live agents. In the preparation environment, all 18 tests and the offline demo passed; Python sources also parsed successfully. This revised modular version has 18 tests, not the 27 tests in an earlier draft. Dependency installation, live model calls, LangGraph execution, memory integration and provider compatibility have NOT been verified there.

## Live demonstration to run locally
Ask: How can I improve my monthly savings?
Then ask: How much did I spend on food? Which category increased the most by percentage? Which increased the most in rupees?
Use trace to inspect component/tool execution. Use reset to discard the graph and switch to a new thread. Use exit to stop. Verify routing and follow-ups before claiming a working end-to-end demonstration.

## Expected mock results
October income INR 60,000; expenses INR 44,800; net cash flow INR 15,200. Food increased 25% (INR 2,400); Shopping approximately 33.33% (INR 2,000); Entertainment 90% (INR 1,800). Entertainment has the largest percentage increase; Food the largest rupee increase. Food and Shopping each exceed their configured budget by INR 2,000. Returning both to budget yields an illustrative INR 4,000 reduction and INR 19,200 cash flow, assuming unchanged income and other spending.

## Financial controls
Money uses integer INR paise and Decimal percentage rounding. Zero baselines produce undefined percentages. Missing months are unavailable, not zero. Unknown merchants map to Other. Positive-only rankings distinguish rupees from percentages. Housing and Bills are protected from reduction suggestions. Alerts trigger at 90% budget use, overspending, and increases of at least 25%; zero budgets with positive spending are handled.

## Memory, failures and limitations
InMemorySaver retains state for one CLI customer/session; planner context uses the last four exchanges. Reset creates a new graph and thread. Earlier checkpoints are not a durable storage or retention solution. Tool loops are bounded. Specialist failures or missing mandatory tools use deterministic completion, disclosed in the answer and trace. Planner/API failures surface as sanitized CLI errors rather than claimed success. Prompt instructions are not a security guarantee.

The complete mock monthly data is INR-only. No transfers, refunds, reversals, real banking connection, profile editing, account actions or investment execution are supported. Alerts run on demand, not through background notifications. There is no authentication or multi-user API. Production deployment, regulatory compliance and security certification are not claimed. Reviewers should test live routing, same-thread follow-ups, reset and adversarial inputs separately; domain tests do not establish these properties.
