
# AI Research Agent — Evaluation Report

## 1. Objective

Evaluate the research agent's retrieval workflow, output structure,
source handling, and failure behavior.

## 2. Test Environment

- Language: Python
- Research tools: Wikipedia API and OpenAlex API
- AI synthesis: Not enabled in the current prototype
- Evaluation method: Automated unit tests and manual research-query tests

## 3. Test Cases

The five research questions and their expected behavior are documented
in `evaluation_cases.json`.

## 4. Results

Record the actual outcome after running each test.

| Test | Expected behavior | Actual result | Status |
|---|---|---|---|
| Basic research | Retrieves results and source links | Pending | Not run |
| Comparison | Retrieves findings useful for comparison | Pending | Not run |
| Balanced research | Retrieves relevant findings | Pending | Not run |
| Invalid input | Rejects empty question | Pending | Not run |
| Low-result scenario | Handles no usable results | Pending | Not run |

## 5. What Works

- Research uses two external information sources.
- Results are returned in a structured format.
- Basic tool failures are handled.
- Duplicate findings are filtered.
- Unit tests can run without live AI API calls.

## 6. Current Limitations

- The planner uses predefined rules.
- The system does not yet synthesize findings using an AI model.
- Search snippets may be incomplete or misleading.
- Source links and claims are not fully verified.
- Confidence is currently a qualitative label, not a calibrated score.
- Live search results can vary between runs.

## 7. Future Improvements

- Add AI-based planning and evidence synthesis.
- Improve source-quality checks and citation verification.
- Add retries and structured logging.
- Test prompt-injection resistance.
- Compare the agent against a simple non-agent baseline.
- Evaluate factual accuracy and citation support.

## 8. Conclusion

The current prototype demonstrates basic research orchestration,
retrieval from two tools, structured reporting, and basic failure handling.
Further evaluation is needed before describing it as production-ready.
