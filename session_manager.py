import json
from pathlib import Path


def save_session(session_id, messages):

    Path(".agent/sessions").mkdir(
        parents=True,
        exist_ok=True
    )

    path = (
        f".agent/sessions/{session_id}.json"
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            messages,
            f,
            indent=2
        )

    return path

def load_session(session_id):

    path = (
        f".agent/sessions/{session_id}.json"
    )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)
    
def list_sessions():

    session_dir = Path(
        ".agent/sessions"
    )

    if not session_dir.exists():
        return []

    sessions = []

    for file in session_dir.glob("*.json"):

        sessions.append(
            file.stem
        )

    return sessions

def serialize_messages(messages):

    serialized = []

    for msg in messages:

        if isinstance(msg, dict):
            serialized.append(msg)

        else:

            if msg.content is None:
                continue

            serialized.append(
                {
                    "role": msg.role,
                    "content": msg.content
                }
            )

    return serialized

if __name__ == "__main__":

    print(
        list_sessions()
    )