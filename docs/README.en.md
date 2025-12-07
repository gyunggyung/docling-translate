# docling-translate

<!-- <p align="center">
  <img src="assets/images/logo.png" alt="docling-translate logo"/>
</p> -->

> **Docling-based Translator for Technical Documents**  
> Supports PDF, DOCX, PPTX, HTML & Images with interactive structure-preserving comparison.

[![Stars](https://img.shields.io/github/stars/gyunggyung/docling-translate?style=social)](https://github.com/gyunggyung/docling-translate/stargazers)
[![Documentation Status](https://readthedocs.org/projects/docling-translate/badge/?version=latest)](https://docling-translate.readthedocs.io/ko/latest/?badge=latest)
[![License](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)](../requirements.txt)
[![Korean](https://img.shields.io/badge/lang-한국어-blue.svg)](../README.md)
[![Discussions](https://img.shields.io/github/discussions/gyunggyung/docling-translate?color=6524fa)](https://github.com/gyunggyung/docling-translate/discussions)

## Overview

`docling-translate` is an open-source tool that leverages IBM's [docling](https://github.com/ds4sd/docling) library to analyze complex document structures (tables, images, multi-column layouts) and provide a **sentence-level 1:1 mapping** between the source and translated text.

<p align="center">
  <img src="assets/images/docling.png" alt="Supported Formats" width="80%">
</p>

Designed to overcome the **imperfections and context loss** often encountered in machine translation. It goes beyond simple text replacement by providing **Side-by-Side** and **Interactive (Click-to-Reveal)** views, allowing users to instantly check the original text and ensure accurate understanding.

## Demo

<p align="center">
  <video src="assets/videos/demo.mp4" controls="controls" style="max-width: 100%;">
  </video>
</p>

## Key Features

- **Multi-Format Support**: Converts and translates `PDF`, `DOCX`, `PPTX`, `HTML`, and `Image` formats into an **Interactive Viewer (HTML)**.
- **Sentence-Level Parallel Translation**: Precisely matches one source sentence to one translated sentence for maximum readability.
- **Layout Preservation**: Maintains tables and images within the document during translation.
- **Flexible Engine Selection**: Supports Google Translate, DeepL, Gemini, OpenAI GPT-5-nano, Qwen(Local), LFM2(Local), Yanolja(Local).
- **High Performance**: Fast parallel processing for large volumes of documents using multi-threading (`max_workers`).

## Quick Start

### 1. Installation

Requires Python 3.10 or higher.

```bash
git clone https://github.com/gyunggyung/docling-translate.git
cd docling-translate
pip install -r requirements.txt
```

**(Optional) For Local Translation Model (Qwen, LFM2, Yanolja)**
To use local LLMs like Qwen, LFM2 or Yanolja, you need to install `llama-cpp-python` and `huggingface_hub`.
- **Windows Users**: Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (Check "Desktop development with C++") then:
  ```bash
  pip install llama-cpp-python huggingface_hub
  ```
- **Mac/Linux Users**:
  ```bash
  pip install llama-cpp-python huggingface_hub
  ```

### 2. CLI Usage

This is the most basic usage. Specify a PDF file to generate an **interactive HTML file**.

```bash
# Basic translation (English -> Korean)
python main.py sample.pdf

# With options (Use DeepL engine, translate to Japanese)
python main.py sample.pdf --engine deepl --target ja

# Use OpenAI GPT-5-nano
python main.py sample.pdf --engine openai --target ko

# Use LFM2 local model
python main.py sample.pdf --engine lfm2 --target ko
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

### Web UI Key Features

- **Focus Mode**: Hides the sidebar and controls to let you focus solely on the translation results.
- **View Mode Control**: Switch between "Inspection Mode" (Side-by-Side) and "Reading Mode" (Translation Only).
- **Real-time Progress**: View detailed status and real-time progress for each step, including document conversion, text extraction, translation, and image saving.
- **History Management**: Automatically saves and loads previous translation results.

## Architecture

<p align="center">
  <img src="assets/images/architecture.png" alt="Architecture Diagram" width="100%">
</p>

## Detailed Guide

For more detailed usage and configuration instructions, please refer to the documents below.

- [📖 **Detailed Usage Guide (USAGE.md)**](USAGE.md): Full CLI options, API key setup, format specifics.
- [🛠 **Contributing Guide (CONTRIBUTING.md)**](CONTRIBUTING.md): Project structure, development workflow, testing methods.
- [🤝 **Support Guide (SUPPORT.md)**](SUPPORT.md): How to join the community and ask questions.

## Project Website

<p align="center">
  <img src="assets/images/qr.png" alt="Scan to Visit Website">
</p>

<!-- <p align="center">
  <a href="https://gyunggyung.github.io/docling-translate/">https://gyunggyung.github.io/docling-translate/</a>
</p> -->

## Acknowledgments

This project is built upon the [Docling](https://github.com/docling-project/docling) library. It also utilizes open-source models from [Qwen](https://huggingface.co/Qwen/Qwen3-0.6B-GGUF), [LFM2](https://huggingface.co/LiquidAI/LFM2-1.2B-GGUF), and [Yanolja](https://huggingface.co/yanolja/YanoljaNEXT-Rosetta-4B-2511-GGUF) for local translation capabilities.

```bibtex
@techreport{Docling,
  author = {Deep Search Team},
  title = {Docling Technical Report},
  url = {https://arxiv.org/abs/2408.09869},
  year = {2024}
}

@misc{qwen3,
  title  = {Qwen3},
  url    = {https://qwenlm.github.io/blog/qwen3/},
  author = {Qwen Team},
  month  = {April},
  year   = {2025}
}

@misc{yanolja2025yanoljanextrosetta,
  author = {Yanolja NEXT Co., Ltd.},
  title = {YanoljaNEXT-Rosetta-4B-2511},
  year = {2025},
  publisher = {Hugging Face},
  journal = {Hugging Face repository},
  howpublished = {\\url{https://huggingface.co/yanolja/YanoljaNEXT-Rosetta-4B-2511}}
}

@article{liquidai2025lfm2technicalreport,
  title={LFM2 Technical Report}, 
  author={Liquid AI},
  year={2025},
  eprint={2511.23404},
  archivePrefix={arXiv},
  primaryClass={cs.LG},
  url={https://arxiv.org/abs/2511.23404}, 
}

```

## License

This project follows the [Apache License 2.0](../LICENSE).