# BDD QA Agent

An MVP QA agent focused on analyzing user stories and generating structured BDD artifacts.

## Goal

This project delivers a structured, non-autonomous LLM workflow to analyze a user story and return:

- BDD scenarios in Gherkin
- Acceptance criteria validation
- Negative test cases
- Edge cases
- Ambiguities and missing requirements
- Functional risks
- Automation suggestions
- Questions for refinement

## Why this architecture

The first version needs to be fast to implement, predictable, and easy to evolve into a multi-agent system later. That's why the foundation uses:

- FastAPI to expose the HTTP endpoint
- LangChain as the orchestration layer
- Pydantic for input and output contracts
- Versioned prompts outside business code
- A simple service layer between route and chain to facilitate future multi-agent orchestration

## Recommended structure

```text
app/
  api/
    routes/
  chains/
  core/
  prompts/
  schemas/
  services/
```

## Initial dependencies

- fastapi
- uvicorn[standard]
- pydantic
- pydantic-settings
- langchain
- langchain-core
- langchain-openai

Dev:

- pytest
- httpx
- ruff

## How the workflow operates

1. The API receives a story, optionally with acceptance criteria.
2. The service normalizes the input and calls the chain.
3. The chain uses a system prompt and few-shot examples to guide the model.
4. The model responds with structured JSON via a Pydantic schema.
5. The route returns the payload without additional transformation.

## Expected contract

Input:

```json
{
  "story": "As a user, I want to reset my password so I can recover access to my account.",
  "acceptance_criteria": [
    "The user must receive a reset email",
    "The reset link expires in 30 minutes",
    "The new password must contain at least one number"
  ]
}
```

Output:

```json
{
  "summary": "",
  "bdd_scenarios": [],
  "negative_cases": [],
  "edge_cases": [],
  "ambiguities": [],
  "risks": [],
  "automation_suggestions": [],
  "questions_for_refinement": []
}
```

## Quick setup

1. Create a virtual environment.
2. Install dependencies from `pyproject.toml`.
3. Copy `.env.example` to `.env` and configure credentials.
4. Run the API with `uvicorn app.main:app --reload`.

## Future multi-agent integration

The foundation already separates concerns to allow expansion without rewriting the core:

- `chains/` for domain-specific LLM workflows
- `services/` for orchestration between chains
- `schemas/` for stable contracts
- `prompts/` for independent prompt evolution
- `api/routes/` for HTTP exposure without business logic

## Best practices for evolution

- Make each new capability a standalone chain or service.
- Prefer typed and validated outputs.
- Use versioned prompts with minimal examples.
- Keep each agent specialized in one decision type.
- Centralize routing to avoid scattering logic across routes.
- Log structured messages with sufficient context for audit and debugging.

## Testing

This project includes comprehensive unit and integration tests that mock external dependencies, allowing you to validate the application without requiring OpenAI API credentials.

### Test Structure

- **tests/conftest.py**: Shared pytest fixtures and mock LLM responses.
- **tests/test_schemas.py**: Pydantic contract validation tests.
- **tests/test_chains.py**: LangChain workflow tests with mocked LLM.
- **tests/test_api.py**: FastAPI route tests with mocked service layer.

### Running Tests

Install test dependencies:

```bash
pip install -e ".[dev]"
```

Run all tests:

```bash
pytest
```

Run specific test file:

```bash
pytest tests/test_schemas.py
```

Run with coverage:

```bash
pip install pytest-cov
pytest --cov=app tests/
```

### Test Mocking Strategy

Tests use `unittest.mock.patch` to replace the real `ChatOpenAI` client with a mock that returns structured JSON responses without calling OpenAI's API. This keeps tests fast and dependency-free.

The `conftest.py` provides reusable fixtures:

- `test_client`: FastAPI TestClient for route testing.
- `mock_qa_response`: Realistic QA analysis response for validation.
- `mock_llm_response`: Mock LLM response as AIMessage.

### Coverage

Tests validate:

1. **Schema contracts** — Request validation (story required, criteria optional), response completeness, field types.
2. **Chain workflows** — Initialization, prompt loading, acceptance criteria formatting, mock LLM invocation.
3. **API routes** — Health check endpoint, QA analysis with valid/invalid payloads, response structure.

### Continuous Integration

Tests are designed to run in any environment without external dependencies. All tests must pass and coverage should stay above 80%:

```bash
pytest --cov=app tests/
```
