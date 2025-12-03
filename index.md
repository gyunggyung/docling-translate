---
layout: default
title: Home
---

<div class="hero">
  <div class="hero-bg-glow"></div>
  <div class="container">
    <div class="hero-grid">
      <div class="hero-content">
        <div class="hero-badge">
          <span>✨</span> v1.1.0 Now Available
        </div>
        <h1 class="hero-title">
          Document Translation,<br>
          <span style="color: var(--color-primary);">Reimagined for AI.</span>
        </h1>
        <p class="hero-desc">
          Docling Translate preserves perfect layout structure while translating complex PDFs, DOCX, and PPTX files. Powered by advanced local LLMs.
        </p>
        <div class="hero-actions">
          <a href="https://docling-translate.readthedocs.io/ko/latest/getting_started.html" class="btn btn-primary">
            Get Started
          </a>
          <a href="https://github.com/gyunggyung/docling-translate" class="btn btn-outline">
            View on GitHub
          </a>
        </div>
      </div>
      
      <div class="hero-visual">
        <div class="terminal-window">
          <div class="terminal-header">
            <div class="dot dot-red"></div>
            <div class="dot dot-yellow"></div>
            <div class="dot dot-green"></div>
          </div>
          <div class="terminal-body">
            <div><span class="cmd-prompt">➜</span><span class="cmd-text">pip install docling-translate</span></div>
            <div class="comment"># Installing dependencies...</div>
            <br>
            <div><span class="cmd-prompt">➜</span><span class="cmd-text">docling-translate input.pdf --lang ko</span></div>
            <div class="comment"># 🚀 Processing document...</div>
            <div class="comment"># 📄 Layout analysis complete</div>
            <div class="comment"># 🤖 Translating with Qwen-2.5...</div>
            <div style="color: #10B981;">✔ Translation complete: input_ko.html</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="container">
  <div class="section-title">
    <h2>Why Docling Translate?</h2>
    <p>Built for developers and researchers who need precision and privacy.</p>
  </div>

  <div class="bento-grid">
    <div class="bento-card wide">
      <div class="card-icon">📐</div>
      <h3 class="card-title">Layout-Aware Translation</h3>
      <p class="card-desc">
        Unlike traditional tools that extract plain text, Docling understands the document structure. 
        Tables, multi-column layouts, headers, and formulas are preserved exactly as they appear in the original file.
      </p>
    </div>
    
    <div class="bento-card">
      <div class="card-icon">🔒</div>
      <h3 class="card-title">Privacy First</h3>
      <p class="card-desc">
        Run completely offline with local LLMs like LFM2 and Qwen. 
        Your sensitive documents never leave your machine.
      </p>
    </div>
    
    <div class="bento-card">
      <div class="card-icon">⚡</div>
      <h3 class="card-title">GenAI Ready</h3>
      <p class="card-desc">
        Seamlessly integrates with modern AI pipelines. 
        Export structured data for RAG or fine-tuning.
      </p>
    </div>
    
    <div class="bento-card wide">
      <div class="card-icon">👁️</div>
      <h3 class="card-title">Interactive HTML Viewer</h3>
      <p class="card-desc">
        Review translations with our side-by-side interactive viewer. 
        Hover over translated text to see the original source instantly.
      </p>
    </div>
    
    <div class="bento-card">
      <div class="card-icon">🔌</div>
      <h3 class="card-title">Easy Integration</h3>
      <p class="card-desc">
        Simple Python API and CLI support. 
        Drop it into your existing workflow in minutes.
      </p>
    </div>
  </div>
</div>

<div class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-col">
        <h4>Project</h4>
        <ul class="footer-links">
          <li><a href="https://docling-translate.readthedocs.io/ko/latest/">Documentation</a></li>
          <li><a href="https://github.com/gyunggyung/docling-translate">GitHub Repository</a></li>
          <li><a href="https://pypi.org/project/docling-translate/">PyPI</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Community</h4>
        <ul class="footer-links">
          <li><a href="https://github.com/gyunggyung/docling-translate/discussions">Discussions</a></li>
          <li><a href="https://github.com/gyunggyung/docling-translate/issues">Issue Tracker</a></li>
          <li><a href="https://github.com/gyunggyung/docling-translate/blob/main/CONTRIBUTING.md">Contributing</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Legal</h4>
        <ul class="footer-links">
          <li><a href="https://github.com/gyunggyung/docling-translate/blob/main/LICENSE">License (MIT)</a></li>
        </ul>
      </div>
    </div>
    <div style="margin-top: 3rem; text-align: center; color: var(--color-text-muted); font-size: 0.9rem;">
      © 2025 Docling Translate Project. Open Source Software.
    </div>
  </div>
</div>
