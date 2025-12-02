# Implementation Plan - Update Documentation for Qwen Engine

## Goal Description
Update project documentation (`GEMINI.md` and `docs/USAGE.md`) to accurately reflect the recent addition of the Qwen translation engine, the new file structure, and specific installation requirements for local LLM support.

## Proposed Changes

### 1. `GEMINI.md`
-   **Section: Core Principles (Modularity)**
    -   Update the example `translator.py` to `src/translation/` to reflect the new package structure.

### 2. `docs/USAGE.md`
-   **Section: 1. CLI (Major Options)**
    -   Add `qwen` and `qwen-0.6b` to the `--engine` option description.
-   **Section: 3. Environment Setup (API Key)**
    -   Add a note that the `qwen` engine runs locally and does not require an API key, but requires optional dependencies (`llama-cpp-python`).
-   **Section: 5. Troubleshooting (FAQ)**
    -   Add an entry for `llama-cpp-python` installation errors on Windows, guiding users to install Visual Studio Build Tools.

## Verification Plan

### Manual Verification
-   Review the rendered Markdown files to ensure clarity and correctness.
-   No code execution is required for documentation updates.
