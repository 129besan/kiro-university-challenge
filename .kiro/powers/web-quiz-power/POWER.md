# Web Article Quiz Generator Power ⚡

A complete, reusable Kiro Power that bundles external web fetching, automated code standards, and custom agent auditing into a single installable package.

## Package Components

- **MCP Tool**: `@modelcontextprotocol/server-fetch` to securely download public blog articles and technical documentation.
- **Custom Agent**: `@quiz-reviewer` (`.kiro/agents/quiz-reviewer.json`) to audit quiz clarity, test options, and verify technical correctness.
- **Steering**: Enforces strict typing, dataclasses, and zero-side-effect business logic in `src/quiz_engine.py`.
- **Hooks**: Automatically validates all unit tests and Hypothesis properties via pytest on `.py` file save.

## Usage in Kiro Sessions

1. Enable the Power in Kiro IDE via the **Powers** panel or import from this repository.
2. The agent automatically activates the `fetch` tool when a URL is supplied.
3. Call `@quiz-reviewer` to audit questions generated from online documentation.
