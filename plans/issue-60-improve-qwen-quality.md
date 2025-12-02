# Implementation Plan - Improve Qwen Translation Quality

## Goal Description
Improve the translation quality and reliability of the Qwen engine by:
1.  Using full language names (e.g., "English", "Korean") instead of codes (e.g., "en", "ko") in the prompt to provide better context.
2.  Wrapping input text in `<text>` tags to clearly delimit the content to be translated, reducing the chance of the model mistaking text for instructions or failing to translate.
3.  Refining the system prompt to explicitly instruct the model to translate the content within the tags.

## Proposed Changes

### `src/translation/engines/qwen.py`

#### [MODIFY] `src/translation/engines/qwen.py`
-   **Import**: Import `LANGUAGE_NAMES` from `..utils`.
-   **Method `translate`**:
    -   Resolve `src` and `dest` to full language names using `LANGUAGE_NAMES.get()`.
    -   Update `system_prompt` to:
        -   Use full language names.
        -   Instruct to translate text within `<text>` tags.
        -   Retain `/no_think` and "Do not output thinking process" instructions.
    -   Update `user_prompt` to wrap `text` in `<text>...</text>`.
    -   Update post-processing to remove `<text>` tags if they appear in the output (in addition to `<think>` tags).

## Verification Plan

### Automated Tests
-   Run `python tests/test_qwen.py` to verify basic translation functionality.
-   Create a new test script `tests/test_qwen_quality.py` (temporary) to test with a tricky sentence that previously might have failed or been ambiguous, to confirm the new prompt structure works.

### Manual Verification
-   User can test with the Streamlit app to see if the "untranslated" issues are resolved.
