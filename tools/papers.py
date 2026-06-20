import requests


def paper_search(query):
    url = "https://huggingface.co/api/papers/search"

    response = requests.get(
        url,
        params={"q": query}
    )

    if response.status_code != 200:
        return {
            "error": f"Request failed: {response.status_code}"
        }

    papers = response.json()

    results = []

    for paper in papers[:5]:

        results.append(
            {
                "id": paper["paper"]["id"],
                "title": paper["paper"]["title"],
                "summary": paper["paper"]["summary"][:300]
            }
        )

    return results


def read_paper(paper_id):

    metadata_url = (
        f"https://huggingface.co/api/papers/{paper_id}"
    )

    markdown_url = (
        f"https://huggingface.co/api/papers/{paper_id}.md"
    )

    metadata = requests.get(metadata_url)

    markdown = requests.get(markdown_url)

    if metadata.status_code != 200:
        return {
            "error": "Could not fetch paper metadata"
        }

    return {
        "metadata": metadata.json(),
        "content": markdown.text[:5000]
    }

if __name__ == "__main__":

    result = read_paper("2602.03442")

    print(result.keys())
    