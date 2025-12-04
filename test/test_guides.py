import sys
from pathlib import Path
from typing import Any, Dict, Literal
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_community.vectorstores import FAISS
from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, AnyMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
import operator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.assets import AssetsInfo
from src.core import LocalEmbeddings, DEVICE

from prompt import RESEARCHER_PROMPT, EXECUTOR_PROMPT

import logging
from rich.logging import RichHandler
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(message)s",
    datefmt="[%H:%M:%S]",
    handlers=[
        RichHandler(
            rich_tracebacks=True,
            markup=True,
            show_time=False,
            show_path=True,
        )
    ],
)
logger = logging.getLogger("TestGen")
logger.setLevel(logging.DEBUG)

llm = ChatOpenAI(
    model=AssetsInfo.openai_model,
    api_key=AssetsInfo.openai_api_key,
    base_url=AssetsInfo.openai_api_url,
)

TODO_LIST = []
WARNING_MESSAGES = []
NOTES = []

_EMBEDDINGS = None
_VECTORSTORE = None

_TODO_POINTER = -1




class AgentState(TypedDict):
    next: Literal["executor", "searcher", "END"]
    messages: Annotated[list[BaseMessage], operator.add]
    queries: str
    report: str
    input_state: Dict[str, Any]

class ExecutorOutput(BaseModel):
    next: Literal["executor", "searcher", "END"] = Field(..., description="call searcher agent to search the database, or continue, or finish the task.")
    message: str = Field(..., description="queries to the searcher agent, or the final report of the task.")

class SearcherOutput(BaseModel):
    next: Literal["executor", "searcher"] = Field(..., description="call executor agent or continue the work.")
    message: str = Field(..., description="the answer to the queries.")

@tool
def add_to_todo_list(item: str) -> str:
    """
    Add an item to the todo list. Do not add the order number to the item.
    """
    index = len(TODO_LIST) + 1
    content = f"[ - ] {index}. {item}"
    TODO_LIST.append(content)
    logger.debug(f"[yellow]add_to_todo_list[/yellow]: {content}")
    return f"Added \"{content}\" to the todo list."

@tool
def get_current_todo() -> str:
    """
    Get the current task in the todo list.
    """
    global _TODO_POINTER
    if _TODO_POINTER >= len(TODO_LIST):
        return "[FAILED] No more items in the todo list."
    if _TODO_POINTER == -1:
        _TODO_POINTER = 0
    content = TODO_LIST[_TODO_POINTER]
    logger.debug(f"[yellow]get_current_todo[/yellow]: {content}")
    return f"```\n{content}\n```"

@tool
def get_next_todo() -> str:
    """
    Get the next task in the todo list. Always call this tool after you have just made a plan or you finish a task.
    """
    global _TODO_POINTER
    if _TODO_POINTER >= len(TODO_LIST):
        return "[FAILED] No more items in the todo list."
    _TODO_POINTER += 1
    content = TODO_LIST[_TODO_POINTER]
    logger.debug(f"[yellow]get_next_todo[/yellow]: {content}")
    return f"```\n{content}\n```"

@tool
def get_todo_list() -> str:
    """
    Get all items in the todo list with both done and todo items.
    Call this tool only when you need to get the whole list.
    In most cases, you should call `get_next_todo` instead.
    """
    logger.debug(f"[yellow]get_todo_list[/yellow]: {TODO_LIST}")
    return f"```\n{'\n'.join(TODO_LIST)}\n```"



@tool
def add_warning_message(message: str) -> str:
    """
    Add a warning message to the user.
    """
    WARNING_MESSAGES.append(message)
    logger.debug(f"[red]add_warning_message[/red]: {message}")
    return f"Added \"{message}\" as a warning to the user."

@tool
def search_hypothesis_documentation(keywords: str, k = 5) -> str:
    """
    Search the Hypothesis documentation vector store for the given keywords.
    """
    logger.debug(f"[yellow]search_hypothesis_documentation[/yellow]: {keywords}")
    global _VECTORSTORE, _EMBEDDINGS

    if _EMBEDDINGS is None:
        _EMBEDDINGS = LocalEmbeddings(
            model_path=AssetsInfo.local_embeddings_path,
            model_repo=AssetsInfo.local_embeddings_repo,
            device=DEVICE,
        )

    if _VECTORSTORE is None:
        _VECTORSTORE = FAISS.load_local(
            AssetsInfo.vector_path,
            _EMBEDDINGS,
            allow_dangerous_deserialization=True,
        )

    results = _VECTORSTORE.similarity_search(keywords, k=k)
    if not results:
        return "[FAILED] 未找到相关结果。"

    formatted = []
    for idx, doc in enumerate(results, 1):
        title = doc.metadata.get("book_name", "unknown")
        abstract = doc.metadata.get("abstract", "").strip()
        snippet = doc.page_content.strip().replace("\n", " ")

        formatted.append(
            f"{idx}. {title}\n摘要: {abstract}\n内容: {snippet}"
        )

    return "\n\n".join(formatted)

@tool
def get_main_content() -> str:
    """
    Get the main content of the Hypothesis Guidelines documentation. Call the tool only when you need to generate the code immediately.
    """
    logger.debug(f"[yellow]get_main_content[/yellow]")
    dirpath = Path(AssetsInfo.guidelines_json_path).parent
    with open(dirpath / "introduction.md", "r", encoding="utf-8") as f:
        return f.read()

@tool
def take_notes(content: str) -> str:
    """
    write down anything you want to take notes of.
    """
    logger.debug(f"[yellow]take_notes[/yellow]: {content}")
    NOTES.append(content)
    return f"[SUCCESS]"

@tool
def get_notes() -> str:
    """
    Get all the notes you have taken.
    """
    logger.debug(f"[yellow]get_notes[/yellow]: {NOTES}")
    return f"```\n{'\n'.join(NOTES)}\n```"

def executor_agent(state: AgentState) -> dict:
    agent = create_agent(
        model=llm, 
        tools=[add_to_todo_list, get_todo_list, get_next_todo, get_current_todo, add_warning_message, take_notes, get_notes], 
        response_format=ExecutorOutput, 
        checkpointer=MemorySaver()
        )

    human_instruct = EXECUTOR_PROMPT.format(
        function_name=state["input_state"]["function_name"],
        function_doc=state["input_state"]["function_doc"],
        format_information=JsonOutputParser(pydantic_object=ExecutorOutput).get_format_instructions()
    )

    if state["messages"]:
        invoke_messages = state["messages"]
    else:
        logger.info("[blue]create a new conversation[/blue]")
        invoke_messages = [HumanMessage(content=human_instruct)]

    response = agent.invoke({"messages": invoke_messages})
    structured_response = response['structured_response']

    logger.debug(f"[green]executor_agent[/green]: {structured_response.message}")

    assert structured_response.next in ["searcher", "executor", "END"]

    return {
        "next": structured_response.next,
        "messages": response["messages"],
        "queries": structured_response.message,
    }

def searcher_agent(state: AgentState) -> dict:
    agent = create_agent(
        model=llm, 
        tools=[add_warning_message, get_main_content, take_notes, get_notes, search_hypothesis_documentation], 
        response_format=SearcherOutput, 
        checkpointer=MemorySaver()
    )

    human_instruct = RESEARCHER_PROMPT.format(
        query=state["queries"],
        format_information=JsonOutputParser(pydantic_object=SearcherOutput).get_format_instructions()
    )

    response = agent.invoke({"messages": [HumanMessage(content=human_instruct)]})
    structured_response = response['structured_response']

    logger.debug(f"[green]searcher_agent[/green]: {structured_response}")
    
    assert structured_response.next in ["executor", "searcher"]

    return {
        "next": structured_response.next,
        "messages": [AIMessage(content=structured_response.message),],
    }

def router(state: AgentState) -> dict:
    logger.debug(f"[cyan]router[/cyan]: {state["next"]}")
    if state["next"] == "executor":
        return "executor"
    elif state["next"] == "searcher":
        return "searcher"
    elif state["next"] == "END":
        logger.debug(f"[cyan]router[/cyan]: record the report.")
        state["report"] = state["queries"]
        return "END"
    else:
        raise ValueError(f"[red]Invalid next state: {state['next']}[/red]")

if __name__ == "__main__":

    test_func = {
      "name": "filesystem-read_text_file",
      "server_infos":{
        "command": "npx",
        "path": "/home/godqu/workspace/study/test_filesystem/"
      },
      "description": "Read the complete contents of a file from the file system as text. Handles various text encodings and provides detailed error messages if the file cannot be read. Use this tool when you need to examine the contents of a single file. Use the 'head' parameter to read only the first N lines of a file, or the 'tail' parameter to read only the last N lines of a file. Operates on the file as text regardless of extension. Only works within allowed directories.",
      "inputSchema": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
          "path": {
            "type": "string"
          },
          "tail": {
            "description": "If provided, returns only the last N lines of the file",
            "type": "number"
          },
          "head": {
            "description": "If provided, returns only the first N lines of the file",
            "type": "number"
          }
        },
        "required": [
          "path"
        ]
      }
    }

    # workflow
    builder = StateGraph(AgentState)
    builder.add_node("executor", executor_agent)
    builder.add_node("searcher", searcher_agent)

    builder.add_edge(START, "executor")
    builder.add_conditional_edges("executor", router, {"executor": "executor", "searcher": "searcher", "END": END})
    builder.add_conditional_edges("searcher", router, {"executor": "executor", "searcher": "searcher"})

    graph = builder.compile()

    # 尝试直接把 json 丢进去
    logger.info(f"start the llm with: {test_func['name']}")
    response = graph.invoke({"input_state": {"function_name": test_func["name"], "function_doc": str(test_func)}})

    logger.info(f"[green]response[/green]: {response.keys()}")
    