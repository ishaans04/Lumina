# ✍ Write

> **Desktop Writing Application** · CustomTkinter + Python  
> Version 1.0 · May 2026 · Internal Draft

---

## Legend

| Badge | Meaning |
|-------|---------|
| ✅ `DONE` | Already in UI |
| 🔲 `TODO` | Not yet built |
| 🔶 `PARTIAL` | UI exists, needs logic |

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Feature Inventory & Status](#2-feature-inventory--status)
3. [Slash Command Menu — Detailed Spec](#3-slash-command-menu--detailed-spec-f-15)
4. [AI Assistant Panel — Detailed Spec](#4-ai-assistant-panel--detailed-spec)
5. [Local Data Model](#5-local-data-model)
6. [Keyboard Shortcuts Reference](#6-keyboard-shortcuts-reference-f-28)
7. [Build Priority Summary](#7-build-priority-summary)
8. [Sample Acceptance Criteria](#8-sample-acceptance-criteria)

---

## 1. Product Overview

**Write** is a focused desktop writing application built with Python and CustomTkinter. It combines a clean Notion-style block editor with an integrated AI Assistant panel, giving users a distraction-free environment to draft, organise, and improve their writing. The app runs locally on Windows (primary target) and must feel native, fast, and polished.

**Goals:**
- Provide a multi-page document workspace with per-page state
- Support rich block types (text, headings, lists, code, quotes, dividers)
- Offer an in-app AI Assistant for grammar, summarisation, expansion, translation
- Maintain a Focus Score metric that updates based on writing session activity
- Auto-save all content locally with visible save status
- Support Light / Dark mode toggle

---

## 2. Feature Inventory & Status

### Layout & Window

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-01 | App Window & Layout | 3-column layout: Sidebar \| Editor \| AI Panel. Status bar at bottom. Correct sizing and expand-on-launch. | P0 | ✅ DONE |
| F-02 | Title Bar & Breadcrumb | Window title `Write`. Breadcrumb `Personal > Projects > Untitled` updates on page switch. | P1 | 🔶 PARTIAL |
| F-44 | Window Maximise on Launch | App opens maximised (`app.state('zoomed')`) on Windows. | P1 | ✅ DONE |
| F-45 | Dividers Between Panels | 1px visual divider lines between sidebar\|editor and editor\|AI panel. | P2 | ✅ DONE |

### Sidebar

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-03 | Sidebar – Logo & Header | Orange square logo + `Write` label at top of sidebar. | P1 | ✅ DONE |
| F-04 | Sidebar – New Page Button | Clicking `+ New Page` creates a new untitled page entry in the list and opens it in editor. | P0 | 🔶 PARTIAL |
| F-05 | Sidebar – Search | Real-time filter of page list as user types. Clears on empty input. | P1 | 🔲 TODO |
| F-06 | Sidebar – Page List | Shows all pages. Clicking selects page and loads its content. Scrollable when > 6 items. | P0 | 🔶 PARTIAL |
| F-07 | Sidebar – Page Selection Highlight | Selected page row highlighted orange-brown with white text. | P1 | ✅ DONE |
| F-08 | Sidebar – Page Rename | Double-click on page name to rename inline. | P2 | 🔲 TODO |
| F-09 | Sidebar – Page Delete | Right-click context menu with `Delete Page` option. Confirmation dialog. | P2 | 🔲 TODO |
| F-10 | Sidebar – Focus Score | Displays numeric score (0–100) in orange pill badge. Updates every minute based on words written. | P1 | 🔶 PARTIAL |
| F-11 | Sidebar – Light/Dark Toggle | Switches entire app between light and dark theme instantly. | P1 | 🔲 TODO |
| F-12 | Sidebar – Settings | Opens a settings panel or modal (font size, autosave interval, AI model key). | P2 | 🔲 TODO |

### Editor

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-13 | Editor – Title Input | Large editable title field at top. Placeholder `Untitled`. Updates page name in sidebar on change. | P0 | 🔶 PARTIAL |
| F-14 | Editor – Body Text Area | Main writing canvas below title. Supports plain text typing, cursor, selection, copy/paste. | P0 | 🔲 TODO |
| F-15 | Editor – Slash Command Menu | Typing `/` opens a floating block-type picker with 9 options. Arrow-key navigation + Enter to insert. | P0 | 🔲 TODO |

### Blocks

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-16 | Block – Plain Text | Default paragraph block. Press Enter for new block. | P0 | 🔲 TODO |
| F-17 | Block – Heading 1 | Large heading. Shortcut `Ctrl+Alt+1`. Styled larger + bolder than body. | P0 | 🔲 TODO |
| F-18 | Block – Heading 2 | Medium heading. Shortcut `Ctrl+Alt+2`. | P0 | 🔲 TODO |
| F-19 | Block – Bullet List | Unordered list block. `- ` prefix auto-converts to bullet. | P1 | 🔲 TODO |
| F-20 | Block – To-do List | Checkbox list. Clicking checkbox toggles done state. Strikethrough on done items. | P1 | 🔲 TODO |
| F-21 | Block – Quote | Indented block with left accent bar in orange. Italic text styling. | P2 | 🔲 TODO |
| F-22 | Block – Divider | Inserts a horizontal rule line between blocks. | P2 | 🔲 TODO |
| F-23 | Block – AI Prompt | Inline AI generation block. User types prompt, presses Enter, AI output inserted below. | P1 | 🔲 TODO |
| F-24 | Block – Code Block | Monospace font area with syntax-highlighted background. Language selector dropdown. | P2 | 🔲 TODO |
| F-25 | Block – Drag & Drop Reorder | Blocks can be reordered by dragging the handle icon on the left. | P2 | 🔲 TODO |
| F-26 | Block – Delete Block | Backspace on empty block deletes it. Right-click > Delete. | P1 | 🔲 TODO |

### System & Persistence

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-27 | Auto-Save | Content auto-saves to local JSON/SQLite every 30 seconds. Status bar shows `Saved Xm ago`. | P0 | 🔲 TODO |
| F-28 | Keyboard Shortcuts | `Ctrl+S` manual save, `Ctrl+Z` undo, `Ctrl+Y` redo, `Ctrl+B` bold, `Ctrl+I` italic. | P1 | 🔲 TODO |
| F-29 | Word & Page Count | Status bar shows live word count and total page count. Updates on every keystroke. | P1 | 🔶 PARTIAL |
| F-30 | Active Session Indicator | Green dot + `Active` in status bar while app is in focus. | P2 | ✅ DONE |
| F-41 | Multi-Page State Persistence | Each page's content, title, and block structure saved and restored on reopen. | P0 | 🔲 TODO |
| F-43 | Dark Mode Theme | All backgrounds, text, borders switch to dark equivalents. Persists across restarts. | P1 | 🔲 TODO |

### AI Panel

| ID | Feature | Description | Priority | Status |
|----|---------|-------------|----------|--------|
| F-31 | AI Panel – Header | Star icon + `AI Assistant` label. Always visible. | P1 | ✅ DONE |
| F-32 | AI Panel – Context Tags | Pill tags showing which pages are in AI context. `×` removes a tag. Clicking sidebar page adds it. | P1 | 🔶 PARTIAL |
| F-33 | AI Panel – Summarize | Sends current page text to AI. Returns 3–5 sentence summary shown in chat bubble. | P0 | 🔲 TODO |
| F-34 | AI Panel – Fix Grammar | Sends selected text or full page to AI. Returns corrected version with changes highlighted. | P0 | 🔲 TODO |
| F-35 | AI Panel – Expand | Sends selected paragraph. AI expands it to 2× length preserving tone. | P1 | 🔲 TODO |
| F-36 | AI Panel – Translate | Sends text to AI with target language selector. Returns translated version. | P1 | 🔲 TODO |
| F-37 | AI Panel – Ask Question | Free-form chat input at bottom. User types question, AI responds in bubble. Multi-turn conversation. | P0 | 🔲 TODO |
| F-38 | AI Panel – Chat History | Previous messages shown as scrollable bubbles (user right, AI left). Persists per session. | P1 | 🔲 TODO |
| F-39 | AI Panel – Loading State | Spinner or typing indicator while AI request is in-flight. | P1 | 🔲 TODO |
| F-40 | AI Backend Integration | Connects to OpenAI / Anthropic API. API key stored in settings. Graceful error on no key. | P0 | 🔲 TODO |
| F-42 | Focus Score Algorithm | Score = f(words written, time spent, breaks taken). Decays if idle > 5 min. | P2 | 🔲 TODO |

---

## 3. Slash Command Menu — Detailed Spec (F-15)

Triggered when the user types `/` at the start of a new block or on an empty line. The menu floats below the cursor and dismisses on `Escape` or click-outside.

| Icon | Label | Description | Shortcut | Block Tag |
|------|-------|-------------|----------|-----------|
| T | Text | Plain paragraph block | — | `paragraph` |
| H1 | Heading 1 | Large section heading | `Ctrl+Alt+1` | `h1` |
| H2 | Heading 2 | Medium section heading | `Ctrl+Alt+2` | `h2` |
| ≡ | Bullet List | Unordered bulleted list | — | `bullet` |
| ■ | To-do List | Checkbox task list | — | `todo` |
| ❝ | Quote | Indented quote with accent bar | — | `quote` |
| — | Divider | Horizontal rule between blocks | — | `divider` |
| ✦ | AI Prompt | Inline AI generation — type & generate | — | `ai_prompt` |
| `</>` | Code Block | Monospace code area with highlighting | — | `code` |

---

## 4. AI Assistant Panel — Detailed Spec

### Quick Action: Summarize (F-33)
Takes the full text of the currently active page. Sends to AI with prompt: *"Summarise the following in 3–5 sentences."* Displays result as a new chat bubble in the panel.

### Quick Action: Fix Grammar (F-34)
If text is selected in the editor, sends only that selection. Otherwise sends full page. Prompt: *"Fix all grammar and spelling errors. Return only the corrected text."* A **Copy** button appears below the bubble so the user can paste it back.

### Quick Action: Expand (F-35)
Requires a text selection in the editor. Prompt: *"Expand the following paragraph to approximately twice its length while preserving the original tone and meaning."* Returns expanded text in bubble.

### Quick Action: Translate (F-36)
Opens a small language-picker dropdown (10 common languages). Sends selected or full text. Prompt: *"Translate the following to [language]."* Returns translated text.

### Free Chat – Ask Something (F-37)
User types any question in the bottom input. Sends to AI with full page text as context. Conversation is multi-turn — previous messages are included in each subsequent request. User messages appear right-aligned (orange bubble), AI messages left-aligned (white bubble).

### Context Tags (F-32)
Each tag represents a page whose content will be included in the AI context window. Tags are added by right-clicking a page in the sidebar and selecting **Add to AI Context**. The `×` button removes a tag. Maximum **3 context pages** at once.

### API Key Management (F-40)
On first launch, if no API key is stored, show an inline prompt in the AI panel: *"Enter your OpenAI API key to enable AI features."* Key is stored in a local config file. Settings panel allows key update/deletion.

---

## 5. Local Data Model

All data is stored locally in a JSON file (or SQLite for v2).

**File path:** `~/Write/data.json`

```json
{
  "pages": [
    {
      "id": "uuid-string",
      "title": "Untitled",
      "created_at": "ISO-8601",
      "updated_at": "ISO-8601",
      "blocks": [
        {
          "id": "block-uuid",
          "type": "paragraph | h1 | h2 | bullet | todo | quote | divider | ai_prompt | code",
          "content": "string",
          "checked": false,
          "language": "python"
        }
      ]
    }
  ],
  "settings": {
    "theme": "light | dark",
    "font_size": 13,
    "autosave_interval_sec": 30,
    "ai_api_key": "sk-...",
    "ai_provider": "openai | anthropic"
  },
  "session": {
    "last_open_page_id": "uuid-string",
    "focus_score": 85
  }
}
```

> **Note:** `checked` is used for `todo` blocks only. `language` is used for `code` blocks only.

---

## 6. Keyboard Shortcuts Reference (F-28)

| Shortcut | Action |
|----------|--------|
| `Ctrl + S` | Manual save |
| `Ctrl + Z` | Undo last action |
| `Ctrl + Y` | Redo |
| `Ctrl + B` | Bold selected text |
| `Ctrl + I` | Italic selected text |
| `Ctrl + Alt + 1` | Convert block to Heading 1 |
| `Ctrl + Alt + 2` | Convert block to Heading 2 |
| `/` | Open slash command menu on new/empty line |
| `Escape` | Close slash command menu |
| `↑` / `↓` | Navigate slash command menu items |
| `Enter` | Insert selected block type from slash menu |
| `Backspace` | Delete empty block, merge with block above |
| `Ctrl + Enter` | Submit AI prompt block |

---

## 7. Build Priority Summary

### P0 — Must Have *(build first)*

- **F-04** – Sidebar – New Page Button: Clicking `+ New Page` creates a new untitled page and opens it in the editor.
- **F-06** – Sidebar – Page List: Shows all pages. Clicking selects and loads content. Scrollable when > 6 items.
- **F-13** – Editor – Title Input: Large editable title field. Placeholder `Untitled`. Updates sidebar on change.
- **F-14** – Editor – Body Text Area: Main writing canvas. Supports typing, cursor, selection, copy/paste.
- **F-15** – Editor – Slash Command Menu: Typing `/` opens floating block-type picker with 9 options.
- **F-16** – Block – Plain Text: Default paragraph block. Press Enter for new block.
- **F-17** – Block – Heading 1: Large heading. Shortcut `Ctrl+Alt+1`.
- **F-18** – Block – Heading 2: Medium heading. Shortcut `Ctrl+Alt+2`.
- **F-27** – Auto-Save: Saves every 30 seconds. Status bar shows `Saved Xm ago`.
- **F-33** – AI Panel – Summarize: Returns 3–5 sentence summary in chat bubble.
- **F-34** – AI Panel – Fix Grammar: Returns corrected version with changes highlighted.
- **F-37** – AI Panel – Ask Question: Free-form chat with multi-turn conversation.
- **F-40** – AI Backend Integration: OpenAI / Anthropic API. Graceful error on missing key.
- **F-41** – Multi-Page State Persistence: Page content and block structure saved and restored on reopen.

### P1 — Should Have

- **F-02** – Title Bar & Breadcrumb
- **F-05** – Sidebar – Search
- **F-10** – Sidebar – Focus Score
- **F-11** – Sidebar – Light/Dark Toggle
- **F-19** – Block – Bullet List
- **F-20** – Block – To-do List
- **F-23** – Block – AI Prompt
- **F-26** – Block – Delete Block
- **F-28** – Keyboard Shortcuts
- **F-29** – Word & Page Count
- **F-32** – AI Panel – Context Tags
- **F-35** – AI Panel – Expand
- **F-36** – AI Panel – Translate
- **F-38** – AI Panel – Chat History
- **F-39** – AI Panel – Loading State
- **F-43** – Dark Mode Theme

### P2 — Nice to Have

- **F-08** – Sidebar – Page Rename
- **F-09** – Sidebar – Page Delete
- **F-12** – Sidebar – Settings
- **F-21** – Block – Quote
- **F-22** – Block – Divider
- **F-24** – Block – Code Block
- **F-25** – Block – Drag & Drop Reorder
- **F-42** – Focus Score Algorithm

---

## 8. Sample Acceptance Criteria

### F-15 · Slash Command Menu

- [ ] Typing `/` on an empty line displays the menu within 100ms
- [ ] Menu shows all 9 block types with icon, name, and description
- [ ] Arrow keys move selection highlight up/down
- [ ] Pressing `Enter` inserts the selected block type at cursor position
- [ ] Pressing `Escape` or clicking outside dismisses the menu
- [ ] Menu does not appear when `/` is typed mid-word

### F-27 · Auto-Save

- [ ] Content saves automatically every 30 seconds
- [ ] Status bar updates to `Saved just now` immediately after save
- [ ] Status bar shows `Saved Xm ago` and increments correctly
- [ ] On app relaunch, last saved content is restored exactly
- [ ] No data loss if app is force-closed between autosave intervals (graceful write)

### F-37 · AI Chat

- [ ] User message appears in right-aligned orange bubble on `Enter`
- [ ] Loading indicator visible while API call is in-flight
- [ ] AI response appears in left-aligned white bubble
- [ ] Conversation history is maintained for the session
- [ ] If API key is missing, shows inline error: `Please add your API key in Settings`

---

*Write · v1.0 · Internal Draft · May 2026*