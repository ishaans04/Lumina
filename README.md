# Lumina

**A desktop AI writing and notepad app for drafting, organizing, and improving notes locally.**

Lumina is a Python desktop application that combines a focused note-taking workspace with AI-assisted writing tools. It is built with CustomTkinter/Tkinter, stores notes in a local JSON file, and supports AI providers including OpenAI, Anthropic, and NVIDIA-compatible APIs.

## Overview

Lumina is designed for writers, students, and knowledge workers who want a lightweight desktop notepad with built-in AI support. Users can create and manage pages, write in a distraction-reduced editor, search notes, save work locally, and use AI actions such as summarization, grammar correction, translation, text expansion, and PDF-assisted writing.

The app prioritizes local-first storage and a simple desktop workflow. Notes, settings, page metadata, and session state are persisted in JSON on the user's machine.

## Why Lumina?

Most writers switch between:

- A note-taking app
- An AI chatbot
- A PDF reader

Lumina combines these workflows into a single desktop workspace.

## Key Features

- **Note management**: Create, rename, delete, search, and switch between pages.
- **Local saving**: Stores pages, settings, session state, and metadata in a local JSON file.
- **Autosave**: Saves changes automatically using a configurable autosave interval.
- **AI chat assistant**: Ask questions about the current note and optional context pages.
- **Writing tools**: Summarize, fix grammar, expand selected text, and translate text.
- **PDF support**: Insert a PDF, extract text with PyMuPDF/fitz, and ask the AI to summarize, translate, or work with the extracted content.
- **Context pages**: Add up to three notes as additional context for AI responses.
- **Theme support**: Toggle light/dark mode and persist the selected theme.
- **Editor utilities**: Word count, page count, find-in-page, undo, markdown-style bold rendering, slash command menu, and export current page to `.txt` or `.md`.
- **Settings panel**: Configure theme, AI provider, font, font size, autosave interval, and API key.
- **Focus metrics**: Displays a focus score based on writing activity and page metrics.

## Tech Stack

| Area | Technology |
| --- | --- |
| Language | Python |
| Desktop UI | CustomTkinter, Tkinter |
| Storage | Local JSON file |
| AI APIs | OpenAI, Anthropic, NVIDIA-compatible APIs |
| PDF processing | PyMuPDF / fitz |
| Networking | Python standard library `urllib` |
| Data modeling | Python dataclasses and dictionaries |

## System Architecture

Lumina is organized around a desktop UI layer and a local backend layer.

```text
User Interface (UIMain.py)
  - Sidebar and page navigation
  - Editor and text interactions
  - AI assistant panel
  - Settings, theme, PDF import, and status UI

Backend (WriteMain.py)
  - Local JSON persistence
  - Page and block operations
  - Autosave thread
  - Focus metrics
  - AI provider request handling
  - Chat history and context-page management

External Services
  - OpenAI API
  - Anthropic API
  - NVIDIA-compatible chat completions API

Local Storage
  - ~/Write/data.json by default
  - Can be overridden with WRITE_APP_HOME
```

### Data Flow

1. The user edits a note in the desktop UI.
2. `UIMain.py` captures UI events and sends updates to the backend.
3. `WriteMain.py` updates the in-memory store and writes changes to local JSON.
4. AI actions build prompts from the active page, selected text, PDF text, or context pages.
5. The selected AI provider returns a response, which is displayed in the assistant panel and saved in session chat history.

## Project Structure

```text
AINotepad/
|-- UI.py                  # Application entry point
|-- UIMain.py              # Main CustomTkinter UI and event handling
|-- WriteMain.py           # Backend logic, persistence, AI APIs, and autosave
|-- components/
|   |-- ai_panel.py        # Placeholder for future AI panel modularization
|   |-- editor.py          # Placeholder for future editor modularization
|   `-- sidebar.py         # Placeholder for future sidebar modularization
|-- README.md
|-- LICENSE
`-- .gitignore
```

## Installation Steps

### 1. Clone the repository

```bash
git clone https://github.com/ishaans04/Lumina
cd AINotepad
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install customtkinter PyMuPDF
```

Tkinter is included with most standard Python installations. If it is missing, install the Tkinter package for your operating system.

## How to Run the App

Run the application from the project root:

```bash
python UI.py
```

The app opens as a desktop window titled **Lumina**.

## Configuration/API Key Setup

Lumina supports OpenAI, Anthropic, and NVIDIA-compatible APIs.

### Option 1: Configure inside the app

1. Open Lumina.
2. Click **Settings** in the sidebar.
3. Select the AI provider.
4. Paste the API key.
5. Save settings.

The key is stored locally in the app's JSON data file.

### Option 2: Use environment variables

Lumina can also read provider-specific API keys from environment variables:

```bash
OPENAI_API_KEY=<your_openai_key>
ANTHROPIC_API_KEY=<your_anthropic_key>
NVIDIA_API_KEY=<your_nvidia_key>
```

On Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your_openai_key"
python UI.py
```

If an API key begins with `nvapi-`, Lumina automatically routes the request through the NVIDIA-compatible provider.

### Local data location

By default, Lumina stores app data at:

```text
~/Write/data.json
```

To use a different local data directory, set:

```bash
WRITE_APP_HOME=/path/to/lumina-data
```

## Roadmap / Future Improvements

- Modularize the UI into reusable sidebar, editor, and AI panel components.
- Add RAG-based document workflows for larger note and PDF collections.
- Add embeddings for semantic note retrieval.
- Add semantic search across notes and imported documents.
- Add cloud sync for cross-device access.
- Improve PDF handling for scanned documents and OCR-based extraction.
- Add richer editor formatting and structured block editing.
- Add test coverage for backend persistence, AI request handling, and UI workflows.
- Package the app as an installable desktop executable.

## Skills Demonstrated

- Python desktop application development with CustomTkinter and Tkinter.
- Local-first data persistence using JSON.
- API integration with multiple AI providers.
- Prompt construction for writing assistance, translation, summarization, and grammar correction.
- PDF text extraction using PyMuPDF/fitz.
- Event-driven UI programming and asynchronous background work with threads.
- State management for pages, settings, chat history, context pages, and autosave.
- Practical product design for a writing-focused desktop tool.
