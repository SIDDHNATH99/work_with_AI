# CortexChat — Upgraded Agentic Chatbot

An AI chatbot built on **FastAPI** + **Mistral (via Azure AI Foundry)** with a full agentic tool-calling system, specialist agents, subagent delegation, and MCP server support.

---

## Quick Start

```bash
pip install -r requirements.txt
python main.py
# Open http://localhost:8001
```

Configure your model and settings in `.env`.

---

## Architecture Overview

```
Browser  →  FastAPI (main.py)  →  BaseAgent (agentic loop)
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
              Built-in Tools      Specialist Agents    MCP Servers
              (13 tools)          (research/coder/     (external,
                                   analyst/...)         optional)
```

---

## Tools

Tools are functions the AI can call mid-conversation to take real actions or look up real data. The model decides **when** and **which** tool to use based on your message.

---

### `get_datetime`
Returns the current date and time in UTC.

**When the AI uses it:**
> *"What day is it today?"*
> *"What's today's date and time?"*

**Example conversation:**
```
You:  What time is it right now?
AI:   [calls get_datetime]
      It's Tuesday, March 31 2026 at 07:20 UTC.
```

---

### `calculate`
Safely evaluates a math expression using Python's AST (no `eval()` — secure by design). Supports `sqrt`, `sin`, `cos`, `log`, `pi`, `e`, `factorial`, and all standard arithmetic.

**When the AI uses it:**
> *"What is 15% of 3,840?"*
> *"Calculate the compound interest on $5000 at 7% for 10 years."*
> *"What's sqrt(2) times pi?"*

**Example conversation:**
```
You:  If I invest $10,000 at 8% annual interest for 5 years, what do I get?
AI:   [calls calculate with expression: "10000 * (1 + 0.08)**5"]
      After 5 years at 8% annual interest, your $10,000 grows to $14,693.28.
```

---

### `memory_set`
Stores a key-value pair persistently in `memory_store.json`. Survives server restarts and works across different chat sessions.

**When the AI uses it:**
> *"Remember that my name is Alex."*
> *"Save my preferred language as Python."*
> *"Note that my project deadline is April 15."*

**Example conversation:**
```
You:  Remember that I prefer dark mode and my timezone is GMT+5.
AI:   [calls memory_set key="user-theme" value="dark mode"]
      [calls memory_set key="user-timezone" value="GMT+5"]
      Got it! I'll remember your preferences for future conversations.
```

---

### `memory_get`
Retrieves a previously stored value by key.

**When the AI uses it:**
> *"What timezone did I tell you I'm in?"*
> *"What's my preferred coding language?"*

**Example conversation:**
```
You:  What do you remember about my preferences?
AI:   [calls memory_list]
      [calls memory_get key="user-theme"]
      [calls memory_get key="user-timezone"]
      You prefer dark mode and your timezone is GMT+5.
```

---

### `memory_list`
Lists all keys currently saved in memory.

**When the AI uses it:**
> *"What have you remembered about me?"*
> *"Show me everything you've saved."*

**Example conversation:**
```
You:  What do you have stored in memory?
AI:   [calls memory_list]
      I have 3 things stored: user-theme, user-timezone, project-deadline.
```

---

### `memory_delete`
Removes a specific key from memory.

**When the AI uses it:**
> *"Forget my old deadline."*
> *"Delete the project name you saved."*

**Example conversation:**
```
You:  Forget the deadline you saved earlier.
AI:   [calls memory_delete key="project-deadline"]
      Done — I've removed the deadline from memory.
```

---

### `web_search`
Searches the web using DuckDuckGo. No API key required. Returns titles, URLs, and snippets.

**When the AI uses it:**
> *"What's the latest news on GPT-5?"*
> *"Find me the FastAPI documentation."*
> *"Who won the 2025 World Cup?"*

**Example conversation:**
```
You:  What are the newest features in Python 3.13?
AI:   [calls web_search query="Python 3.13 new features" max_results=5]
      Based on recent results, Python 3.13 introduces:
      - Improved error messages with color support
      - Experimental free-threaded mode (no GIL)
      - A new interactive REPL with multi-line editing
      Sources: python.org, realpython.com, ...
```

---

### `fetch_url`
Fetches and reads the text content of any public web page. SSRF-safe (blocks private IPs and localhost). Used after `web_search` to read articles in full.

**When the AI uses it:**
> *"Can you read this article for me: https://..."*
> *"Summarise the content at this URL."*

**Example conversation:**
```
You:  Summarise this page: https://docs.python.org/3/library/asyncio.html
AI:   [calls fetch_url url="https://docs.python.org/3/library/asyncio.html"]
      Here's a summary of the asyncio documentation:
      asyncio is Python's standard library for writing concurrent code
      using the async/await syntax...
```

---

### `run_python`
Executes Python code in a sandboxed subprocess with a **15-second timeout**. Returns stdout, stderr, and exit code. The AI uses this to test code before presenting it to you.

**When the AI uses it:**
> *"Write a script to sort a list of names."*
> *"Can you test if this regex works?"*
> *"Calculate the Fibonacci sequence up to 100."*

**Example conversation:**
```
You:  Write me a Python function to check if a number is prime.
AI:   [calls run_python with the function + test cases]
      stdout: "True, False, True, True"  ← exit_code: 0
      
      Here's the verified working function:
      
      def is_prime(n):
          if n < 2: return False
          for i in range(2, int(n**0.5) + 1):
              if n % i == 0: return False
          return True
```

---

### `read_workspace_file`
Reads a file from the chatbot's working directory. Path-traversal safe (cannot escape the workspace).

**When the AI uses it:**
> *"Read my config file and tell me what's wrong."*
> *"What's in requirements.txt?"*
> *"Check the contents of my data.csv."*

**Example conversation:**
```
You:  What packages are installed based on requirements.txt?
AI:   [calls read_workspace_file path="requirements.txt"]
      Your project uses: fastapi, uvicorn, openai, pypdf, 
      duckduckgo-search, httpx, mcp, and several others.
```

---

### `write_workspace_file`
Writes content to a file in the workspace. Creates parent directories automatically.

**When the AI uses it:**
> *"Save this script to a file called process_data.py."*
> *"Create a config.json with these settings."*
> *"Write a .gitignore for a Python project."*

**Example conversation:**
```
You:  Create a Python script that reads a CSV and prints the row count, save it as count_rows.py.
AI:   [calls run_python to test the code first]
      [calls write_workspace_file path="count_rows.py" content="..."]
      Done! I've tested and saved count_rows.py to your workspace.
      Run it with: python count_rows.py yourfile.csv
```

---

### `list_workspace_files`
Lists all files and folders in the workspace directory.

**When the AI uses it:**
> *"What files do I have in my project?"*
> *"List everything in the chats_data folder."*

**Example conversation:**
```
You:  What files are in my project right now?
AI:   [calls list_workspace_files]
      Your project contains:
      📁 agents/  📁 skills/  📁 tools/  📁 mcp/
      📄 main.py  📄 .env  📄 requirements.txt  📄 README.md
      📁 chats_data/ (2 conversations stored)
```

---

### `spawn_subagent`
Delegates a complex subtask to a specialist agent (research, coder, or analyst). The subagent runs its own full tool-calling loop and returns its result back to the coordinator. This is how the coordinator handles multi-domain tasks.

**When the AI uses it:**
> *"Research the best Python web frameworks and then write a comparison script that benchmarks them."*
> *"Find the latest pandas documentation, then write code using the new features."*

**Example conversation:**
```
You:  Research the current AI models available on Azure, then write a Python script 
      that lists them using the Azure SDK.

AI (coordinator):
      [calls spawn_subagent agent_type="research" task="Find all AI models on Azure AI Foundry as of 2026"]
        → Research agent: [web_search] → [fetch_url] → returns summary

      [calls spawn_subagent agent_type="coder" task="Write Azure SDK Python script to list AI models" context="<research results>"]
        → Coder agent: [run_python to test] → returns verified code

      Here's what I found and built:
      [research summary + working code]
```

---

## Agents

Agents are the AI's "operating modes". Each one has a different system prompt and a curated set of tools. You pick the mode from the **dropdown in the chat header**.

---

### Coordinator *(default)*
**Tools:** All 13 tools including `spawn_subagent`

The generalist. Handles anything — from casual conversation to multi-step tasks. Can delegate to specialist subagents when a task requires deep focus.

**Best for:**
- Mixed tasks (research + code + writing)
- When you're not sure which agent to pick
- Tasks that require multiple steps across domains

**Example prompts:**
```
"Research the latest LLM benchmarks, then write a Python script to visualise the results as a chart."
"Remember my project name is 'Atlas', search for best practices for it, and save a summary."
"What time is it, what's 15% of my $4,200 invoice, and draft a payment reminder email."
```

---

### Research Agent
**Tools:** Core + `web_search` + `fetch_url`

Specialised in finding, reading, and synthesising information from the web. Always cites sources. Cross-references multiple sources before answering.

**Best for:**
- Current events and news
- Technical documentation lookup
- Competitive analysis
- Fact-checking

**Example prompts:**
```
"What are the differences between GPT-4o and Mistral Large 2?"
"Find me the latest FastAPI release notes."
"Research what MCP (Model Context Protocol) is and how it works."
"What are the current Python best practices for async web APIs in 2026?"
```

---

### Coder Agent
**Tools:** Core + `run_python` + `read_workspace_file` + `write_workspace_file` + `list_workspace_files`

Specialised in writing, testing, and fixing code. Always runs code with `run_python` before presenting it. Iterates until the code works.

**Best for:**
- Writing scripts and utilities
- Debugging code
- Code review and refactoring
- Building small tools

**Example prompts:**
```
"Write a Python script that reads a JSON file and exports it as CSV."
"Debug this function — it's returning None but should return a list."
"Write a regex to extract all email addresses from a block of text and test it."
"Create a Flask app skeleton with 3 routes and save it to app.py."
```

---

### Analyst Agent
**Tools:** Core + `web_search` + `fetch_url` + `run_python` + `read_workspace_file`

Specialised in data analysis, statistics, and computation. Combines web research for context with Python execution for number-crunching. Shows methodology and caveats.

**Best for:**
- Statistical analysis
- Processing uploaded CSV/Excel data
- Financial calculations
- Generating data summaries

**Example prompts:**
```
"Analyse this sales data and tell me which region is underperforming."  (upload a CSV)
"Calculate the ROI if I invest $50k at 12% annual return over 8 years, with monthly compounding."
"Find current exchange rates and convert my £8,500 salary to USD, EUR, and AED."
"Look up Python pandas performance benchmarks and run a comparison script."
```

---

### Assistant
**Tools:** Core only (datetime, calculate, memory)

A lightweight mode for simple conversations with basic utilities. No web access, no code execution. Fastest response time.

**Best for:**
- Quick questions and chat
- Math calculations
- Saving/retrieving preferences
- When you want a fast, focused answer

**Example prompts:**
```
"What's the square root of 8,192?"
"Remember that I prefer tabs over spaces."
"What's 18% tip on a $67.50 dinner bill?"
"Explain the difference between async and sync Python."
```

---

### Fast (no tools)
**Tools:** None — raw LLM call only

The original chatbot experience. No agentic loop, no tool calls. Lowest latency.

**Best for:**
- Creative writing
- Brainstorming
- Simple Q&A from training knowledge
- When speed matters more than accuracy

**Example prompts:**
```
"Write a short story about a robot who learns to paint."
"Give me 10 startup ideas in the health tech space."
"Explain quantum entanglement simply."
"Proofread this paragraph for me."
```

---

## MCP Servers

MCP (Model Context Protocol) lets you connect **any external tool server** to CortexChat without writing Python code. Once connected, its tools appear automatically in all agents.

**Current status:** No MCP servers connected (`MCP_SERVERS_JSON=[]` in `.env`)

---

### How to add an MCP server

Edit `.env`:

```env
MCP_SERVERS_JSON=[
  {"name": "filesystem", "command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]}
]
```

Restart the server. That's it — tools are auto-discovered and registered.

---

### Example: Filesystem MCP Server

Connects the official MCP filesystem server, giving the AI direct read/write access to your local files through the MCP protocol.

**Install:** `npm install -g @modelcontextprotocol/server-filesystem`

**Config:**
```env
MCP_SERVERS_JSON=[{"name":"filesystem","command":"npx","args":["-y","@modelcontextprotocol/server-filesystem","."]}]
```

**Registered tools (auto-discovered):**
- `mcp__filesystem__read_file`
- `mcp__filesystem__write_file`
- `mcp__filesystem__list_directory`
- `mcp__filesystem__create_directory`

**Example prompts once connected:**
```
"Read my Documents/notes.txt and summarise it."
"Create a folder called 'output' and save a report there."
"List all files in my Downloads folder."
```

---

### Example: Database MCP Server

Connects a database — the AI can query it directly in natural language.

**Config:**
```env
MCP_SERVERS_JSON=[{"name":"postgres","command":"npx","args":["-y","@modelcontextprotocol/server-postgres","postgresql://user:pass@localhost/mydb"]}]
```

**Example prompts once connected:**
```
"How many users signed up this month?"
"Show me the top 10 products by revenue."
"Which orders have been pending for more than 7 days?"
```

---

### Example: Custom Python MCP Server

You can write your own MCP server in Python to expose any internal system (your API, proprietary data, etc.).

**`my_mcp_server.py`** (minimal example):
```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

server = Server("my-company-tools")

@server.list_tools()
async def list_tools():
    return [types.Tool(name="get_stock_price", description="Get real-time stock price",
                       inputSchema={"type":"object","properties":{"ticker":{"type":"string"}},"required":["ticker"]})]

@server.call_tool()
async def call_tool(name, arguments):
    if name == "get_stock_price":
        # your real logic here
        return [types.TextContent(type="text", text=f"AAPL: $189.50")]

if __name__ == "__main__":
    import asyncio
    asyncio.run(stdio_server(server))
```

**Config:**
```env
MCP_SERVERS_JSON=[{"name":"company","command":"python","args":["my_mcp_server.py"]}]
```

**Example prompts once connected:**
```
"What's Apple's current stock price?"
```

---

## Configuration Reference (`.env`)

```env
# Model
AZURE_OPENAI_ENDPOINT=https://your-endpoint.services.ai.azure.com/models
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_MODEL_NAME=mistral-small-2503

# Agent behaviour
ENABLE_TOOLS=true                # false = disable all tools globally
AGENT_MODE=coordinator           # default mode when page loads
MAX_TOOL_ITERATIONS=10           # max tool calls per response (prevent loops)

# Inference tuning
AI_TEMPERATURE=0.3               # 0.0 = deterministic, 1.0 = creative
AI_TOP_P=0.9
AI_FREQUENCY_PENALTY=0.1
AI_MAX_TOKENS=4096

# MCP Servers
MCP_SERVERS_JSON=[]              # add server configs here
```

---

## Tool → Agent Matrix

| Tool | Coordinator | Research | Coder | Analyst | Assistant |
|------|:-----------:|:--------:|:-----:|:-------:|:---------:|
| `get_datetime` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `calculate` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `memory_set/get/list/delete` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `web_search` | ✅ | ✅ | ❌ | ✅ | ❌ |
| `fetch_url` | ✅ | ✅ | ❌ | ✅ | ❌ |
| `run_python` | ✅ | ❌ | ✅ | ✅ | ❌ |
| `read_workspace_file` | ✅ | ❌ | ✅ | ✅ | ❌ |
| `write_workspace_file` | ✅ | ❌ | ✅ | ❌ | ❌ |
| `list_workspace_files` | ✅ | ❌ | ✅ | ❌ | ❌ |
| `spawn_subagent` | ✅ | ❌ | ❌ | ❌ | ❌ |
| MCP tools | ✅ | ✅ | ✅ | ✅ | ✅ |
