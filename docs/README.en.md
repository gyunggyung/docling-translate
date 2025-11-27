# docling-translate

<p align="center">
  <img src="logo.png" alt="docling-translate logo"/>
</p>

> **Docling-based Translator for Technical Documents**  
> Supports PDF, DOCX, PPTX, HTML & Images with interactive structure-preserving comparison.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](../requirements.txt)
[![Korean](https://img.shields.io/badge/lang-한국어-blue.svg)](../README.md)

## Overview

`docling-translate` is an open-source tool that leverages IBM's [docling](https://github.com/ds4sd/docling) library to analyze complex document structures (tables, images, multi-column layouts) and provide a **sentence-level 1:1 mapping** between the source and translated text.

Designed to overcome the **imperfections and context loss** often encountered in machine translation. It goes beyond simple text replacement by providing **Side-by-Side** and **Interactive (Click-to-Reveal)** views, allowing users to instantly check the original text and ensure accurate understanding.

## Key Features

- **Multi-Format Support**: Converts and translates `PDF`, `DOCX`, `PPTX`, `HTML`, and `Image` formats into an **Interactive Viewer (HTML)**.
- **Sentence-Level Parallel Translation**: Precisely matches one source sentence to one translated sentence for maximum readability.
- **Layout Preservation**: Maintains tables and images within the document during translation.
- **Flexible Engine Selection**: Supports Google Translate (Free), DeepL (High Quality), Gemini (Context Aware), and **OpenAI GPT-5-nano (Latest AI)**.
- **High Performance**: Fast parallel processing for large volumes of documents using multi-threading (`max_workers`).

## Quick Start

### 1. Installation

Requires Python 3.10 or higher.

```bash
git clone https://github.com/gyunggyung/docling-translate.git
cd docling-translate
pip install -r requirements.txt
```

### 2. CLI Usage

This is the most basic usage. Specify a PDF file to generate an **interactive HTML file**.

```bash
# Basic translation (English -> Korean)
python main.py sample.pdf

# With options (Use DeepL engine, translate to Japanese)
python main.py sample.pdf --engine deepl --to ja

# Use OpenAI GPT-5-nano
python main.py sample.pdf --engine openai --to ko
```

### API Key Setup (Optional)

To use DeepL, Gemini, or OpenAI, configure API keys in the `.env` file.

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env file and add your API keys
OPENAI_API_KEY=sk-proj-your-api-key-here
DEEPL_API_KEY=your-deepl-key-here
GEMINI_API_KEY=your-gemini-key-here
```

**API Key Links**:
- [OpenAI API Keys](https://platform.openai.com/api-keys) - For GPT-5-nano ($0.05/1M input, $0.40/1M output tokens)
- [DeepL API](https://www.deepl.com/pro-api)
- [Google AI Studio](https://aistudio.google.com/app/apikey) - For Gemini

### 3. Web UI Usage

Use the intuitive web interface to upload files and visually verify results.

```bash
streamlit run app.py
```

## Detailed Guide

For more detailed usage and configuration instructions, please refer to the documents below.

- [📖 **Detailed Usage Guide (USAGE.md)**](USAGE.md): Full CLI options, API key setup, format specifics.
- [🛠 **Contributing Guide (CONTRIBUTING.md)**](CONTRIBUTING.md): Project structure, development workflow, testing methods.

## Acknowledgments

This project is built upon the [Docling](https://github.com/docling-project/docling) library.

```bibtex
@techreport{Docling,
  author = {Deep Search Team},
  title = {Docling Technical Report},
  url = {https://arxiv.org/abs/2408.09869},
  year = {2024}
}
```

## License

This project follows the [Apache License 2.0](../LICENSE).