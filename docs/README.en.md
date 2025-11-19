# docling-translate

<p align="center">
  <img src="logo.png" alt="docling-translate logo" width="600"/>
</p>

[한국어로 읽기](../README.md)

**Technical PDFs, now perfectly understood by comparing original and translated sentences side-by-side.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

`docling-translate` is a fast and intuitive open-source translation tool that helps non-native English-speaking students, engineers, and researchers read and understand technical PDF documents with ease.

---

## 🤔 Why use `docling-translate`?

Have you ever faced these challenges when translating technical documents?

*   📄 Copying content from a PDF breaks the formatting, making it difficult to even paste into a translator.
*   😵 Existing translators provide awkward, context-free results that are hard to trust.
*   📑 You waste time switching between the original and translated texts, constantly losing your flow.

`docling-translate` solves all these problems by combining the powerful document analysis capabilities of the **`docling` library** with a **sentence-by-sentence parallel view**.

## ✨ Core Features

| Feature | Description |
| :--- | :--- |
| **📖 Side-by-Side Sentence Comparison** | Compare the original and translated text sentence by sentence to accurately grasp even the subtlest nuances of technical terms. |
| **🏗️ Flawless PDF Structure Analysis** | Accurately parses complex layouts, including multi-column text, tables, and images, preserving the original structure as much as possible using the `docling` library. |
| **📄 Flexible Triple-Format Output** | Generates the original text (`_en.md`), the translated text (`_ko.md`), and a combined version (`_combined.md`) for versatile use. |
| **🏷️ Quick Reference to Original** | Displays the original PDF page number `(p. N)` next to every text block, allowing for quick reference back to the source. |

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Usage

For example, to translate the sample file included in the project (the 'Attention Is All You Need' paper) with default settings (English->Korean), run the following command:

```bash
python main.py "samples/1706.03762v7.pdf"
```

**Specifying Languages (Optional):**

You can specify the source language with the `-f` (`--from`) option and the target language with the `-t` (`--to`) option.

```bash
# Translate an English PDF to German
python main.py "samples/1706.03762v7.pdf" -f en -t de
```

### 🎨 Output Example

The translated output (`_combined.md`) is generated with original and translated sentences side-by-side, making it very convenient to read and compare.

---
**Original (English)** (p. 1)
> This assignment marks the foundation of your project journey, so please complete it thoroughly and thoughtfully.

**Translated (Korean)** (p. 1)
> 이 과제는 프로젝트 여정의 기초를 마련하는 것이므로 철저하고 신중하게 완료하십시오.
***
**Original (English)** (p. 1)
> List at least 3–5 planned features and system requirements.

**Translated (Korean)** (p. 1)
> 최소 3~5개의 계획된 기능과 시스템 요구사항을 나열하십시오.
---

## 🗺️ Development Roadmap

- [x] **PDF → Markdown Conversion**: Accurate structure analysis using `docling`
- [x] **Triple-Format Output**: Generate original/translated/combined Markdown files
- [x] **Page Number Display**: Reference original page numbers in `(p. N)` format
- [x] **Sentence-level Translation & Comparison**: High-readability side-by-side view (Complete!)
- [ ] **Folder-level Translation**: Translate all PDFs in a folder at once
- [ ] **Parallel Processing for Performance**: Improve translation speed for large documents using multiprocessing
- [ ] **Multi-Engine Translation Support**: Add options for different translation engines like GPT API, local LLMs, etc.
- [x] **Multi-language Support**: Expand translation capabilities to languages other than Korean

## 📚 Development Resources

This project heavily relies on the `docling` library. To understand its features and usage, referring to the official documentation is highly recommended.

*   **`docling` Official Docs Site:** [https://docling-project.github.io/docling/](https://docling-project.github.io/docling/)
*   **`docling` Example Code (GitHub):** [https://github.com/docling-project/docling/tree/main/docs/examples](https://github.com/docling-project/docling/tree/main/docs/examples)

## 🤝 Contributing

This project welcomes contributions of all kinds, whether it's bug fixes, new features, or documentation improvements.

For a detailed development workflow and contribution methods, please refer to the [**Contribution Guidelines (CONTRIBUTING.md)**](CONTRIBUTING.md).

Also, please adhere to our [**Code of Conduct (CODE_OF_CONDUCT.md)**](../CODE_OF_CONDUCT.md) to foster a healthy and respectful community.

## 📜 License

This project is licensed under the **Apache License 2.0**. For more details, see the `LICENSE` file.
