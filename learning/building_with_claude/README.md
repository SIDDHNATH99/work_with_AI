# Building with Claude

This folder contains hands-on learning scripts and experiments for building applications using the Anthropic Claude API.

## Files Overview

| File                      | Description                                      |
| ------------------------- | ------------------------------------------------ |
| `prompting.py`          | Basic prompting techniques with Claude           |
| `Exercise_prompting.py` | Prompting exercises and practice                 |
| `prompt_caching.py`     | Using prompt caching to reduce latency and cost  |
| `prompts_eval.py`       | Evaluating and comparing prompt outputs          |
| `streamresponse.py`     | Streaming responses from Claude                  |
| `tool_streaming.py`     | Streaming with tool use                          |
| `tool_editors.py`       | Tool use for editing workflows                   |
| `tools.py`              | General tool use with Claude                     |
| `extendedthinking.py`   | Extended thinking / chain-of-thought with Claude |
| `citations.py`          | Extracting citations from Claude responses       |
| `structureddata.py`     | Extracting structured data from Claude outputs   |
| `read_images.py`        | Reading and analyzing images with Claude         |
| `read_pdf.py`           | Reading and analyzing PDFs with Claude           |
| `fileapi.py`            | Using the Files API with Claude                  |
| `embeddings.py`         | Generating and using embeddings                  |
| `vector_db.py`          | Vector database integration                      |
| `bm25.py`               | BM25 keyword search implementation               |
| `hybird.py`             | Hybrid search (BM25 + embeddings)                |
| `chunking_types.py`     | Different chunking strategies for RAG            |
| `websearch.py`          | Web search integration with Claude               |
| `buildbot.py`           | Building a bot with Claude                       |
| `calculator.py`         | Calculator tool example                          |
| `demo.py`               | General demo script                              |
| `test.py`               | Test scripts                                     |

---

## Skills

Skills are reusable, domain-specific capabilities that can be packaged and loaded into Claude's workflow. They contain tested instructions and best practices for a specific domain so Claude can produce high-quality, consistent outputs without repeating context.

**Use cases:**

- Encapsulate specialized knowledge (e.g., API design, testing strategies, performance profiling)
- Loaded on-demand when a matching task is detected
- Can be combined — multiple skills can apply to a single task
- Stored as `SKILL.md` files and read before Claude starts work

**Example:** A `pr-description` skill tells Claude exactly how to write pull request descriptions following team conventions, loaded automatically when you ask Claude to write a PR.

---

## Agents

Agents are autonomous subprocesses that Claude can spawn to handle complex, multi-step tasks independently. Each agent runs a focused job and returns a result back to the main conversation.

**Use cases:**

- Parallel research across multiple files or topics
- Delegating specialized tasks (e.g., a `backend-debugger` agent for tracing errors, an `api-reviewer` for code review)
- Keeping the main conversation clean by offloading long explorations
- Read-only codebase exploration without cluttering context

**Example:** An `Explore` agent searches the entire codebase for a pattern and returns findings, while the main agent continues planning the implementation.

---

## Hooks

Hooks are scripts that run automatically at specific points in Claude's execution lifecycle — before or after a request, tool call, or response. They allow you to intercept, log, validate, or transform data without modifying Claude's core behavior.

**Use cases:**

- **Pre-request hooks** — Validate or enrich input before Claude processes it
- **Post-response hooks** — Log, format, or store Claude's output after it responds
- **Pre-tool hooks** — Inspect or block tool calls before they execute
- **Post-tool hooks** — Process tool results before they are returned to Claude

**Example:** A `query_hook.js` can log every database query Claude makes, and a `read_hook.js` can track which files Claude reads during a session.

---

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Setup

Create a `.env` file in this folder with your Anthropic API key:

```env
ANTHROPIC_API_KEY=your_api_key_here
```
