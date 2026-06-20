from textual.app import App
from textual.widgets import Header, Footer, Input, RichLog
from textual import work

from agent import Agent

agent = Agent()


class ResearchBotUI(App):

    BINDINGS = [
        ("ctrl+l", "clear_chat", "Clear"),
        ("ctrl+k", "clear_chat", "Clear"),
        ("ctrl+q", "quit", "Quit")
    ]

    def compose(self):

        yield Header()

        yield RichLog(
            id="chat"
        )

        yield Input(
            placeholder="Ask a research question..."
        )

        yield Footer()

    def on_input_submitted(self, event):

        chat = self.query_one("#chat")

        user_message = event.value

        event.input.value = ""

        chat.write(
            f"[USER] {user_message}"
        )

        chat.write(
            "[BOT] Thinking..."
        )

        self.ask_agent(user_message)

    @work(thread=True)
    def ask_agent(self, question):

        chat = self.query_one("#chat")

        try:

            answer = agent.chat(question)

            self.call_from_thread(
                chat.write,
                f"[BOT] {answer}"
            )

        except Exception as e:

            self.call_from_thread(
                chat.write,
                f"[ERROR] {str(e)}"
            )

    def action_clear_chat(self):

        chat = self.query_one("#chat")

        chat.clear()


if __name__ == "__main__":

    ResearchBotUI().run()