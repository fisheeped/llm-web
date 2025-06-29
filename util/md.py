import re
def remove_markdown_links(text: str) -> str:
    """Modifies a markdown text to remove all markdown links.
    Example: [DISPLAY](LINK) to DISPLAY
    First find all markdown links with regex.
    Then replace them with: $1
    Args:
        text (str): Markdown text containing markdown links
    Returns:
        str: Markdown text without markdown links.
    """

    # find all markdown links
    markdown_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)

    # remove link keep display text
    for display, link in markdown_links:
        text = text.replace(f"[{display}]({link})", display)

    return text

def latex(text:str) -> str:
    return text.replace('\\(', "$").replace('\\)', "$").replace('\\[', "$$").replace('\\]', "$$")


