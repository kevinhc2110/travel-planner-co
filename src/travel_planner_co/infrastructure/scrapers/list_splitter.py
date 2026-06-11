import re


def is_list_article(title: str, content: str) -> bool:
    keywords = [
        "top", "mejores", "imperdibles", "más hermosos", "más bonitos",
        "pueblos mágicos", "lugares para visitar", "qué hacer en",
        "guía de viaje", "itinerario", "días en", "cosas que hacer",
        "playas", "cascadas", "parques", "museos", "restaurantes",
        "alojamiento", "hoteles",
    ]
    title_lower = title.lower()
    for kw in keywords:
        if kw in title_lower:
            return True

    # Check for numbered items in content
    numbered = re.findall(r"(?:^|\n)\s*\d+[\.\)]\s+", content)
    if len(numbered) >= 3:
        return True

    return False


def split_list_article(
    title: str, content: str
) -> list[dict]:
    if not is_list_article(title, content):
        return [{"title": title, "content": content}]

    # Try to split by numbered patterns like "1. " or "1) "
    sections = _split_by_numbers(content)

    # If no numbered split worked, try splitting by common section patterns
    if len(sections) < 2:
        sections = _split_by_headings(content)

    if len(sections) < 2:
        return [{"title": title, "content": content}]

    results = []
    for section_name, section_text in sections:
        section_name = section_name.strip().rstrip(".:")
        if not section_name or len(section_text.strip()) < 20:
            continue
        combined_title = f"{section_name}"
        results.append({"title": combined_title, "content": section_text.strip()})

    return results if results else [{"title": title, "content": content}]


def _split_by_numbers(content: str) -> list[tuple[str, str]]:
    pattern = r"(?:^|\n)\s*(\d+[\.\)])\s+([^\n]+)"
    matches = list(re.finditer(pattern, content))
    if len(matches) < 2:
        return []

    sections = []
    for i, match in enumerate(matches):
        item_name = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        item_text = content[start:end].strip()
        sections.append((item_name, item_text))
    return sections


def _split_by_headings(content: str) -> list[tuple[str, str]]:
    lines = content.split("\n")
    sections = []
    current_heading = None
    current_lines = []

    for line in lines:
        stripped = line.strip()
        # Detect potential headings (short lines without ending punctuation)
        if (
            stripped
            and not stripped.endswith(("."))
            and len(stripped) < 80
            and current_heading is not None
        ):
            sections.append((current_heading, "\n".join(current_lines).strip()))
            current_heading = stripped
            current_lines = []
        elif current_heading is None:
            if stripped and not stripped.endswith((".")):
                current_heading = stripped
            else:
                current_lines.append(line)
        else:
            current_lines.append(line)

    if current_heading:
        sections.append((current_heading, "\n".join(current_lines).strip()))

    return sections
