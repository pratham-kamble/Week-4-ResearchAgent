# AI Research Agent (LangGraph)

A command-line research agent built with LangGraph that gathers information from multiple sources — live web search and Wikipedia — and generates a single, synthesized summary in response to a user's question.

## What It Does

- Takes a research question from the user via the CLI
- Searches the web using DuckDuckGo for current, real-time information
- Searches Wikipedia for established, encyclopedic background on the topic
- Combines both sources into a single context block
- Sends that combined context to an LLM (via Groq) to generate one coherent, synthesized summary
- Runs as a LangGraph state graph — not a linear script — so each step (search, summarize) is a discrete node with data flowing through a shared state

## Tech Stack

- **LangGraph** — defines the agent as a graph of nodes and edges, managing state as it flows through each step
- **LangChain** — tool definitions (`@tool` decorator) and core abstractions
- **Groq API** (`llama-3.1-8b-instant`) — LLM used for the final summarization step
- **DuckDuckGo Search** (`ddgs`) — live web search, no API key required
- **Wikipedia API** (`wikipedia-api`) — encyclopedic background search
- **python-dotenv** — environment variable management

## How It Works (Architecture)

```
User Question
     │
     ▼
   START
     │
     ▼
 ┌─────────┐     calls duckduckgo_search tool
 │  search  │ ──► calls wikipedia_search tool
 └─────────┘     combines both results into state
     │
     ▼
 ┌───────────┐   builds prompt from question + combined results
 │ summarize │ ──► calls Groq LLM
 └───────────┘   writes final summary into state
     │
     ▼
    END
     │
     ▼
Final Summary (printed to CLI)
```

**State** flowing through the graph holds three fields:
- `question` — the original user query
- `search_results` — combined, labeled output from both search tools
- `summary` — the final LLM-generated answer

## Tools

**`duckduckgo_search(query: str) -> str`**
Searches the web via DuckDuckGo and returns the top 5 results (title, snippet, source URL), formatted as readable text. Used for current events, recent developments, and information likely to change over time.

**`wikipedia_search(query: str) -> str`**
Searches Wikipedia and returns a summary of the matching page (or a clear "not found" message if no page exists). Used for stable, well-established facts, definitions, and background context. Handles missing pages gracefully without crashing the agent.

## Setup

**1. Clone the repository**
```bash
git clone <your-repo-url>
cd <repo-folder>
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your Groq API key**

Create a `.env` file in the project root:
```
GROQ_API_KEY=your_actual_secret_key_here
```

Get a free API key at [console.groq.com](https://console.groq.com).

**5. Run it**
```bash
python main.py
```

## Example Usage

```
What would you like to research? python

--- SUMMARY ---

**Summary of Python**
Python is a high-level, general-purpose programming language widely used for
various purposes, known for its emphasis on code readability, simplicity, and
ease of writing...

Key Features: code readability, extensive standard library, automatic memory
management, and support for multiple programming paradigms...

Resources for Learning: official documentation at python.org, tutorials on
W3Schools, GeeksforGeeks, and an online compiler via Programiz...
```

## Project Structure

```
.
├── main.py             # Full agent: state, tools, nodes, graph, CLI entry point
├── requirements.txt    # Python dependencies
└── .env                # API key (gitignored, not included in repo)
```

