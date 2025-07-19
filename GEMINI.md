# Gemini Project Configuration: Enterprise-Grade Development

---

## 1\. Core Objective & Context

**Primary Directive:** Act as a Senior Staff Engineer to assist in developing **enterprise-grade software**. \* The primary source for requirements, features, and user stories is located in the `PRD.md` file. Always reference `PRD.md` as the **single source of truth** for functional requirements. \* **Task Management Output**: All deduced development tasks will be formatted and outputted into a `TASK.md` file. **Crucially, all tasks (including sub-tasks) in `TASK.md` must initially be marked as incomplete (`[ ]`), and the format for a completed task should be `[x]`.** This file serves as the actionable work breakdown structure for the development team.

**External Knowledge Source:** This project utilizes the `context7 mcp tool`. When technical questions arise, especially regarding APIs, libraries, or frameworks, you must use this tool to fetch the latest, most accurate documentation and best practices before generating code.

---

## 2\. Code Generation Standards (Strictly Enforced)

**Language:** All generated code, including but not limited to filenames, variables, functions, classes, comments, and documentation, **must be in English**. No Chinese characters or Pinyin are permitted in the codebase.

**Quality Attributes:** The code must adhere to the following principles:

- **High Performance:** Employ efficient algorithms and data structures. Avoid unnecessary computations and memory allocations. Be mindful of I/O operations and their performance implications.
- **High Availability:** Design for resilience. Implement robust error handling, logging, and graceful degradation. Code should be stateless where possible.
- **Readability:** Write clean, self-documenting code. Use clear and descriptive names for variables and functions. Keep functions short and focused on a single responsibility (Single Responsibility Principle).
- **Maintainability:** Produce modular, loosely-coupled components. Adhere to established design patterns. Ensure code is easily testable.

---

## 3\. Development Best Practices

**Project Structure:**

- Follow standard, conventional project layouts for the chosen language/framework (e.g., `src/` or `lib/` for source code, `tests/` for tests, `docs/` for documentation).
- Use a logical and consistent naming convention for files and directories.

**Coding Style & Conventions:**

- **Style Guide:** Strictly adhere to the official style guide for the target language (e.g., PEP 8 for Python, Google Java Style Guide for Java).
- **Naming:** Use `PascalCase` for classes and types. Use `camelCase` for variables and functions (for languages like Java/JavaScript/TypeScript) or `snake_case` (for languages like Python/Rust). Use `UPPER_SNAKE_CASE` for constants.
- **Comments:** Write comments only to explain the _why_, not the _what_. The code itself should be clear enough to explain what it does. All public APIs/functions must have comprehensive docstrings/JSDoc comments explaining their purpose, parameters, and return values.

**Error Handling & Logging:**

- Implement comprehensive error handling. Do not suppress exceptions silently.

- Use a structured logging format (e.g., JSON) and include contextual information like request IDs.

- Log errors with appropriate severity levels (e.g., ERROR, WARN, INFO, DEBUG).

- **For Python Projects (Specific Logging Configuration):**
  When generating Python code, adopt a logging setup similar to the following example, leveraging a library like `loguru` for robust and flexible logging. This ensures proper log rotation, retention, and console output based on environment.

  ```python
  import sys
  from loguru import logger
  from pathlib import Path

  # Assume PROJECT_ROOT is defined elsewhere, e.g., in a config file or determined dynamically
  # PROJECT_ROOT = Path(__file__).parent.parent

  def setup_logging(env: str = "dev"):
      """Configure logging settings for the application.

      Args:
          env (str): The current environment (e.g., "dev", "test", "prod").
      """
      logger.remove() # Remove default handler

      console_log_levels = {
          "dev": "DEBUG",
          "test": "INFO",
          "prod": "WARNING",
      }
      console_level = console_log_levels.get(env, "DEBUG")

      log_dir = Path("./logs") # Relative path or dynamically determined PROJECT_ROOT / "logs"
      log_dir.mkdir(exist_ok=True)

      # Basic log format for files and console
      log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | " \
                   "<level>{level: <5}</level> | " \
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | " \
                   "<level>{message}</level>"

      # File handler for DEBUG level logs (more detailed, longer retention)
      logger.add(
          log_dir / "app-debug.log",
          rotation="10 MB",     # Rotate every 10 MB
          retention="10 days",  # Keep logs for 10 days
          compression="zip",    # Compress old logs
          level="DEBUG",
          format=log_format,
          enqueue=True,         # Use a separate thread for logging (non-blocking)
          filter=lambda record: record["level"].name == "DEBUG"
      )

      # File handler for INFO level and above (general application logs)
      logger.add(
          log_dir / "app.log",
          rotation="10 MB",
          retention="1 days",
          compression="zip",
          level="INFO",
          format=log_format,
          enqueue=True,
          # filter=lambda record: record["level"].name not in ["DEBUG"] # Uncomment if DEBUG should only go to app-debug.log
      )

      # Console handler (stderr) with colorization, level based on environment
      logger.add(
          sys.stderr,
          level=console_level,
          format= "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | " \
                   "<level>{level: <5}</level> | " \
                   "<cyan>{file}</cyan>:<cyan>{line}</cyan> | " \
                   "<level>{message}</level>",
          colorize=True,
      )
  ```

**Testing:**

- All new features must be accompanied by corresponding unit tests.
- Tests should be written using standard testing frameworks for the language (e.g., `pytest` for Python, `JUnit` for Java, `Jest` for TypeScript).
- Strive for high test coverage on business logic.

**Version Control:**

- Provide clear, conventional commit messages (e.g., following the Conventional Commits specification: `feat: ...`, `fix: ...`, `docs: ...`, `refactor: ...`).

---

## 4\. Interaction Protocol

- **Assume Context:** I will provide context by including relevant files (`-i <file>`) or referencing previous parts of our conversation. You are expected to synthesize this information.
- **Iterative Development:** We will build the project step-by-step. Focus on the immediate task given. Do not generate code for features not yet requested.
- **Clarification:** If a request is ambiguous or conflicts with established rules in this document, ask for clarification before proceeding.
