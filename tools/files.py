from pathlib import Path

def write_file(path, content):

    Path(path).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "success": True,
        "path": path
    }

def read_file(
    path,
    start_line=1,
    read_lines=50
):

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            lines = f.readlines()

        start_idx = start_line - 1
        end_idx = start_idx + read_lines

        selected = lines[start_idx:end_idx]

        content = ""

        for i, line in enumerate(
            selected,
            start=start_line
        ):

            content += (
                f"{i}: {line}"
            )

        return {
            "content": content,
            "has_more": end_idx < len(lines)
        }

    except Exception as e:

        return {
            "error": str(e)
        }

def list_files(path="."):

    try:

        files = []

        for item in Path(path).iterdir():

            files.append(str(item))

        return {
            "files": files
        }

    except Exception as e:

        return {
            "error": str(e)
        }

def edit_file(path, operation, old_text=None, new_text=None):

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:
            content = f.read()

        if operation == "append":

            content += new_text

        elif operation == "replace":

            content = content.replace(
                old_text,
                new_text
            )

        elif operation == "delete":

            content = content.replace(
                old_text,
                ""
            )    

        else:

            return {
                "error": "Unsupported operation"
            }

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(content)

        return {
            "success": True
        }

    except Exception as e:

        return {
            "error": str(e)
        }

if __name__ == "__main__":

    print(
        edit_file(
            "notes/test.md",
            operation="delete",
            old_text="Third line"
        )
    )

    print(
        read_file("notes/test.md")
    )