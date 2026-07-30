import os
from dotenv import load_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain.tools import tool
from ddgs import DDGS
import wikipediaapi




wiki = wikipediaapi.Wikipedia(
    user_agent="ResearchAgent/1.0 (student-project)",
    language="en"
)


class GraphState(TypedDict):
    question: str
    search_results: str
    summary: str

@tool
def duckduckgo_search(query: str) -> str:
    """Searches the web using DuckDuckGo and returns a summary of the top results.
    Use this tool when you need current information, facts, or research on a topic
    that may not be part of your existing knowledge."""

    results = DDGS().text(query, max_results=5)

    if not results:
        return "No results found for this query."

    formatted_results = []
    for i, result in enumerate(results, start=1):
        title = result.get("title", "No title")
        snippet = result.get("body", "No description")
        url = result.get("href", "No URL")
        formatted_results.append(f"{i}. {title}\n{snippet}\nSource: {url}")

    return "\n\n".join(formatted_results)

@tool
def wikipedia_search(query: str) -> str:
    """Searches Wikipedia for background information, definitions, or established facts about a topic.
    Use this tool for well-known concepts, historical events, or general knowledge questions —
    not for current events or recent news, since Wikipedia content updates slowly."""

    try:
        page = wiki.page(query)

        if not page.exists():
            return "No Wikipedia page found for this query."

        return page.summary[:500]

    except Exception as e:
        return f"An error occurred while searching Wikipedia: {e}"

def search_node(state: GraphState) -> GraphState:
    query = state["question"]
    web_results = duckduckgo_search.invoke({"query": query})
    wiki_results = wikipedia_search.invoke({"query": query})

    combined = f"--- Web Search Results ---\n{web_results}\n\n--- Wikipedia Results ---\n{wiki_results}"
    return {"search_results": combined}

def summarize_node(state: GraphState) -> GraphState:
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.3,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    prompt = f"""You are a research assistant. Based on the search results below,
write a clear, well-organized summary that answers the original question.

Question:
{state["question"]}

Search Results:
{state["search_results"]}

Summary:"""

    response = llm.invoke(prompt)
    return {"summary": response.content}


graph = StateGraph(GraphState)

graph.add_node("search", search_node)
graph.add_node("summarize", summarize_node)

graph.add_edge(START, "search")
graph.add_edge("search", "summarize")
graph.add_edge("summarize", END)

app = graph.compile()


if __name__ == "__main__":
    load_dotenv()
    question = input("What would you like to research? ")
    result = app.invoke({"question": question})
    print("\n--- SUMMARY ---\n")
    print(result["summary"])


    