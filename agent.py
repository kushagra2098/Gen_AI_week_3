import os
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv
from tools.web import web_search, web_fetch
from tools.papers import paper_search, read_paper
from tools.files import (
    read_file,
    write_file,
    list_files,
    edit_file
)
from session_manager import (
    save_session,
    load_session,
    list_sessions,
    serialize_messages
)
load_dotenv()



client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

MODEL = "openrouter/free"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Fetch a web page",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string"
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "paper_search",
            "description": "Search academic papers",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_paper",
            "description": (
            "Read the full content of a paper. "
            "Use this after paper_search when the user asks "
            "for a summary, detailed explanation, methodology, "
            "results, contributions, or analysis."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "paper_id": {
                        "type": "string"
                    }
                },
                "required": ["paper_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from disk",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string"
                    },
                    "start_line": {
                        "type": "integer"
                    },
                    "read_lines": {
                        "type": "integer"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Write content to a file. "
                "Use when the user asks to save notes, reports, summaries, or documents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string"
                    },
                    "content": {
                        "type": "string"
                    }
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": (
                "Modify an existing file. "
                "Supports append, replace, and delete."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string"
                    },
                    "operation": {
                        "type": "string"
                    },
                    "old_text": {
                        "type": "string"
                    },
                    "new_text": {
                        "type": "string"
                    }
                },
                "required": ["path", "operation"]
            }
        }
    }
]

class Agent:

    def __init__(self):

        self.rules = self.load_rules()
        self.tools = {
            "web_search": web_search,
            "web_fetch": web_fetch,
            "paper_search": paper_search,
            "read_paper": read_paper,
            "read_file": read_file,
            "write_file": write_file,
            "list_files": list_files,
            "edit_file": edit_file
        }

        self.session_id = "default"

        try:

            self.messages = load_session(
                self.session_id
            )

            print("Session loaded")

        except:

            self.messages = [
                {
                    "role": "system",
                    "content": self.rules
                }
            ]

        print("Agent initialized")
        self.session_id = "default"


    def load_rules(self):

        try:

            with open(
                "AGENTS.md",
                "r",
                encoding="utf-8"
            ) as f:

                return f.read()

        except:

            return ""

    def chat(self, user_message):

        self.messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        for _ in range(8):

            response = client.chat.completions.create(
                model=MODEL,
                messages=self.messages,
                tools=TOOLS
            )

            message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason

            print("Finish Reason:", finish_reason)

            if finish_reason == "tool_calls":

                self.messages.append(message)

                for tool_call in message.tool_calls:

                    result = self.dispatch(tool_call)

                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result)
                        }
                    )

                continue

            if finish_reason == "stop":
                if finish_reason == "stop":

                    self.messages.append(message)

                    save_session(
                        self.session_id,
                        serialize_messages(
                        self.messages
                    )
                )

                return message.content

        return "agent stopped."
    
    def dispatch(self, tool_call):

        import json
        name= tool_call.function.name
        print(f"Tool called: {name}")

        name = tool_call.function.name

        arguments = json.loads(
            tool_call.function.arguments
        )

        tool = self.tools.get(name)

        if tool is None:
            return {
                "error": f"Unknown tool: {name}"
            }

        result = tool(**arguments)

        return result

class REPLAgent(Agent):

    def run(self):

        print("""
Research Desk
-------------
Commands:
  /sessions  - List saved sessions
  /save      - Save current session
  quit       - Exit
""")

        while True:

            query = input(">>> ")

            if query.lower() in ["quit", "exit"]:
                print("Goodbye!")
                break

            if query == "/sessions":

                sessions = list_sessions()

                print("\nSaved Sessions:")

                for session in sessions:
                    print("-", session)

                print()
                continue

            if query == "/save":

                save_session(
                    self.session_id,
                    serialize_messages(
                        self.messages
                    )
                )

                print("Session saved.\n")
                continue

            try:

                answer = self.chat(query)

                print("\n" + answer + "\n")

            except Exception as e:

                print(f"Error: {e}")
            

import sys

if __name__ == "__main__":

    if "--tui" in sys.argv:

        from tui import ResearchBotUI

        ResearchBotUI().run()

    else:

        agent = REPLAgent()

        if len(sys.argv) > 1:

            query = " ".join(sys.argv[1:])

            print(agent.chat(query))

        else:

            agent.run()