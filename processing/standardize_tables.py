from __future__ import annotations

import re
from typing import Tuple

LONGTABLE_BEGIN = r"\begin{longtable}"
LONGTABLE_END = r"\end{longtable}"


def _skip_ws(text: str, idx: int) -> int:
    while idx < len(text) and text[idx].isspace():
        idx += 1
    return idx


def _consume_bracket(text: str, idx: int) -> int:
    if text[idx] != "[":
        return idx
    idx += 1
    while idx < len(text) and text[idx] != "]":
        idx += 1
    return idx + 1 if idx < len(text) else idx


def _consume_brace(text: str, idx: int) -> Tuple[str, int]:
    if text[idx] != "{":
        raise ValueError("Expected '{' while parsing LaTeX block.")
    depth = 0
    start = idx
    for i in range(idx, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : i], i + 1
    raise ValueError("Unterminated '{' while parsing LaTeX block.")


def _extract_caption(content: str) -> Tuple[str | None, str]:
    idx = content.find(r"\caption")
    if idx == -1:
        return None, content

    brace_start = content.find("{", idx)
    if brace_start == -1:
        return None, content

    try:
        caption, end_idx = _consume_brace(content, brace_start)
    except ValueError:
        return None, content

    remainder = content[end_idx:]
    remainder = re.sub(r"^\s*\\tabularnewline\s*", "", remainder)

    cleaned = content[:idx] + remainder
    return caption.strip(), cleaned


def _strip_longtable_repeats(content: str) -> str:
    if r"\endfirsthead" in content:
        pre, rest = content.split(r"\endfirsthead", 1)
        if r"\endlastfoot" in rest:
            _, post = rest.split(r"\endlastfoot", 1)
        elif r"\endhead" in rest:
            _, post = rest.split(r"\endhead", 1)
        else:
            post = rest
        content = pre + post

    content = re.sub(r"\\end(firsthead|head|foot|lastfoot)\b", "", content)
    return content.strip()


def _convert_longtable_block(colspec: str, content: str) -> str:
    caption, content = _extract_caption(content)
    content = _strip_longtable_repeats(content)

    lines = [r"\begin{table}[htbp]", r"\centering", r"\small"]
    if caption:
        lines.append(rf"\caption{{{caption}}}")
    lines.append(rf"\begin{{tabularx}}{{\columnwidth}}{{{colspec}}}")
    lines.append(content)
    lines.append(r"\end{tabularx}")
    lines.append(r"\end{table}")
    return "\n".join(lines)


def convert_longtables_to_tabularx(tex_string: str) -> str:
    """convert pandoc longtable blocks to table+tabularx while keeping cell content."""
    out = []
    idx = 0

    while True:
        start = tex_string.find(LONGTABLE_BEGIN, idx)
        if start == -1:
            out.append(tex_string[idx:])
            break

        out.append(tex_string[idx:start])

        j = start + len(LONGTABLE_BEGIN)
        j = _skip_ws(tex_string, j)

        if j < len(tex_string) and tex_string[j] == "[":
            j = _consume_bracket(tex_string, j)
            j = _skip_ws(tex_string, j)

        if j >= len(tex_string) or tex_string[j] != "{":
            end = tex_string.find(LONGTABLE_END, j)
            if end == -1:
                out.append(tex_string[start:])
                break
            out.append(tex_string[start : end + len(LONGTABLE_END)])
            idx = end + len(LONGTABLE_END)
            continue

        try:
            colspec, j = _consume_brace(tex_string, j)
        except ValueError:
            end = tex_string.find(LONGTABLE_END, j)
            if end == -1:
                out.append(tex_string[start:])
                break
            out.append(tex_string[start : end + len(LONGTABLE_END)])
            idx = end + len(LONGTABLE_END)
            continue

        end = tex_string.find(LONGTABLE_END, j)
        if end == -1:
            out.append(tex_string[start:])
            break

        content = tex_string[j:end]
        out.append(_convert_longtable_block(colspec, content))
        idx = end + len(LONGTABLE_END)

    return "".join(out)


def standardize_tables(tex_string: str) -> str:
    return convert_longtables_to_tabularx(tex_string)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    if len(sys.argv) != 2:
        raise SystemExit("Usage: python standardize_tables.py <path-to-tex>")
    path = Path(sys.argv[1])
    path.write_text(standardize_tables(path.read_text()))
