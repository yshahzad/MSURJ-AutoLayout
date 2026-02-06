from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Dict, Iterable, List, Tuple


REFERENCE_SECTION_RE = re.compile(
    r"\\section\{References\}.*?(?:\n|$)", re.IGNORECASE
)

ITEM_MARKER = "@@ITEM@@"


@dataclass
class CitationResult:
    body_text: str
    bibtex: str
    key_map: Dict[int, str]


def extract_references_section(tex: str) -> Tuple[str, str]:
    match = REFERENCE_SECTION_RE.search(tex)
    if not match:
        raise ValueError("No References section found (expected \\section{References}).")

    before = tex[:match.start()].rstrip()
    after = tex[match.end():].strip()

    if not after:
        raise ValueError("References section found but it is empty.")

    return before, after


def _strip_enumerate_controls(text: str) -> str:
    text = re.sub(r"\\def\\labelenumi\{[^}]*\}", "", text)
    text = re.sub(r"\\setcounter\{enumi\}\{[^}]*\}", "", text)
    text = text.replace("\\begin{enumerate}", "")
    text = text.replace("\\end{enumerate}", "")
    text = text.replace("\\item", f"\n{ITEM_MARKER}")
    return text


def split_reference_items(ref_section: str) -> List[str]:
    text = _strip_enumerate_controls(ref_section)
    text = text.replace("\\begin{quote}", "\n")
    text = text.replace("\\end{quote}", "\n")

    chunks = [c.strip() for c in text.split(ITEM_MARKER)]

    items = [c for c in chunks[1:] if c]

    if items:
        return items

    fallback = [c.strip() for c in re.split(r"\n\s*\n", ref_section) if c.strip()]
    return fallback


def _unwrap_command(text: str, command: str) -> str:
    pattern = re.compile(rf"\\{command}\{{([^{{}}]*)\}}")
    return pattern.sub(r"\1", text)


def latex_to_text(text: str) -> str:
    text = re.sub(r"\\url\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\href\{([^}]*)\}\{[^}]*\}", r"\1", text)

    for cmd in ["emph", "textbf", "textit", "ul", "underline"]:
        text = _unwrap_command(text, cmd)

    text = text.replace(r"\&", "&")
    text = text.replace(r"\%", "%")
    text = text.replace(r"\_", "_")
    text = text.replace(r"\textasciitilde", "~")

    text = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?\{([^{}]*)\}", r"\2", text)

    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_bibtex_with_anystyle(
    references: Iterable[str],
    *,
    anystyle_cmd: str = "anystyle",
    output_format: str = "bib",
) -> str:
    refs_text = "\n".join(references).strip() + "\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=True) as tmp:
        tmp.write(refs_text)
        tmp.flush()

        try:
            result = subprocess.run(
                [anystyle_cmd, "--stdout", "-f", output_format, "parse", tmp.name],
                check=True,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                "AnyStyle CLI not found. Install it or provide anystyle_cmd."
            ) from exc
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f"AnyStyle failed with exit code {exc.returncode}: {exc.stderr.strip()}"
            ) from exc

    bibtex = result.stdout.strip()
    if not bibtex:
        raise RuntimeError("AnyStyle produced no BibTeX output.")

    return bibtex


def rewrite_bibtex_keys(bibtex: str, key_map: Dict[int, str]) -> str:
    entry_header = re.compile(r"@([a-zA-Z]+)\s*\{\s*([^,]+),")
    idx = 1

    def repl(match: re.Match) -> str:
        nonlocal idx
        if idx not in key_map:
            return match.group(0)
        new_key = key_map[idx]
        idx += 1
        return f"@{match.group(1)}{{{new_key},"

    updated = entry_header.sub(repl, bibtex)

    if idx - 1 != len(key_map):
        raise RuntimeError(
            "BibTeX entry count does not match reference count. "
            "Check the references section or AnyStyle output."
        )

    return updated


def parse_citation_numbers(text: str) -> List[int]:
    normalized = text.replace("–", "-").replace("—", "-")
    tokens = re.findall(r"\d+(?:\s*-\s*\d+)?", normalized)

    nums: List[int] = []
    for token in tokens:
        if "-" in token:
            start_s, end_s = [t.strip() for t in token.split("-", 1)]
            if not start_s.isdigit() or not end_s.isdigit():
                continue
            start, end = int(start_s), int(end_s)
            if end < start:
                start, end = end, start
            nums.extend(range(start, end + 1))
        else:
            nums.append(int(token))

    seen = set()
    ordered = []
    for n in nums:
        if n in seen:
            continue
        seen.add(n)
        ordered.append(n)

    return ordered


def replace_superscript_citations(
    text: str,
    key_map: Dict[int, str],
    *,
    wrap_in_superscript: bool = True,
    strict: bool = True,
) -> str:
    pattern = re.compile(r"\\textsuperscript\{([^}]*)\}")

    def repl(match: re.Match) -> str:
        numbers = parse_citation_numbers(match.group(1))
        if not numbers:
            return match.group(0)

        keys: List[str] = []
        missing: List[int] = []
        for n in numbers:
            key = key_map.get(n)
            if not key:
                missing.append(n)
            else:
                keys.append(key)

        if missing and strict:
            raise ValueError(
                f"Missing BibTeX keys for citations: {', '.join(map(str, missing))}"
            )

        cite = "\\cite{" + ",".join(keys) + "}"
        return f"\\textsuperscript{{{cite}}}" if wrap_in_superscript else cite

    return pattern.sub(repl, text)


def apply_citation_pipeline(
    body_text: str,
    *,
    anystyle_cmd: str = "anystyle",
    bib_key_prefix: str = "ref",
    wrap_in_superscript: bool = True,
) -> CitationResult:
    cleaned_body, ref_section = extract_references_section(body_text)
    raw_items = split_reference_items(ref_section)

    if not raw_items:
        raise ValueError("No reference items found in References section.")

    refs_plain = [latex_to_text(item) for item in raw_items]

    bibtex_raw = build_bibtex_with_anystyle(refs_plain, anystyle_cmd=anystyle_cmd)

    key_map = {i + 1: f"{bib_key_prefix}{i + 1}" for i in range(len(raw_items))}
    bibtex = rewrite_bibtex_keys(bibtex_raw, key_map)

    body_with_cites = replace_superscript_citations(
        cleaned_body,
        key_map,
        wrap_in_superscript=wrap_in_superscript,
    )

    return CitationResult(body_text=body_with_cites, bibtex=bibtex, key_map=key_map)
