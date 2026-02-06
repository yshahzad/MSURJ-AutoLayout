from pathlib import Path
import shutil
import re

from processing.citations import apply_citation_pipeline, replace_superscript_citations, CitationResult
from processing.standardize_tables import standardize_tables


def _dim_to_inches(value: str, unit: str) -> float | None:
    try:
        num = float(value)
    except ValueError:
        return None

    unit = unit.lower()
    if unit == "in":
        return num
    if unit == "cm":
        return num / 2.54
    if unit == "mm":
        return num / 25.4
    if unit == "pt":
        return num / 72.27
    if unit == "bp":
        return num / 72.0
    return None


def _is_wide_figure(block: str, *, width_threshold_in: float, height_threshold_in: float) -> bool:
    include_re = re.compile(r"\\includegraphics(?:\[(?P<opts>[^\]]*)\])?\{[^}]+\}")
    width_re = re.compile(r"width\s*=\s*([0-9.]+)\s*(in|cm|mm|pt|bp)")
    height_re = re.compile(r"height\s*=\s*([0-9.]+)\s*(in|cm|mm|pt|bp)")

    for match in include_re.finditer(block):
        opts = match.group("opts") or ""
        width_match = width_re.search(opts)
        if width_match:
            w = _dim_to_inches(width_match.group(1), width_match.group(2))
            if w is not None and w >= width_threshold_in:
                return True

        height_match = height_re.search(opts)
        if height_match:
            h = _dim_to_inches(height_match.group(1), height_match.group(2))
            if h is not None and h >= height_threshold_in:
                return True

    return False


def _set_includegraphics_width(text: str, width: str) -> str:
    def repl_opts(_: re.Match) -> str:
        return f"\\includegraphics[width={width}]"

    def repl_no_opts(_: re.Match) -> str:
        return f"\\includegraphics[width={width}]{{"

    text = re.sub(
        r"\\includegraphics\[[^\]]*\]",
        repl_opts,
        text,
    )
    text = re.sub(
        r"\\includegraphics(?!\[)\{",
        repl_no_opts,
        text,
    )
    return text


def standardize_figs(tex_string):
    figure_re = re.compile(
        r"(\\begin{figure\*?}(?:\[[^\]]*\])?)(.*?)(\\end{figure\*?})",
        re.DOTALL,
    )

    out = []
    last = 0
    for match in figure_re.finditer(tex_string):
        out.append(_set_includegraphics_width(tex_string[last:match.start()], r"\\columnwidth"))

        begin, body, end = match.groups()
        is_star = begin.startswith(r"\begin{figure*}")
        wide = is_star or _is_wide_figure(body, width_threshold_in=4.5, height_threshold_in=4.5)

        if wide and not is_star:
            begin = begin.replace(r"\begin{figure}", r"\begin{figure*}", 1)
            end = end.replace(r"\end{figure}", r"\end{figure*}", 1)

        target_width = r"\textwidth" if wide else r"\columnwidth"
        if r"\captionsetup" not in body:
            body = f"\\captionsetup{{width={target_width}}}\n" + body
        body = _set_includegraphics_width(body, target_width)
        out.append(f"{begin}{body}{end}")
        last = match.end()

    out.append(_set_includegraphics_width(tex_string[last:], r"\\columnwidth"))
    return "".join(out)


def convert_to_msurj(
    pandoc_tex_path,
    metadata,
    *,
    enable_citations=True,
    return_bibtex=False,
    anystyle_cmd="anystyle",
):
    """
    convert a pandoc latex file into msurj-formatted latex.
    metadata: dict with authors, title, submitted_date, article_type, affiliations, keywords, email
    """
    text = Path(pandoc_tex_path).read_text()

    abstract_start = text.find(r'\section{Abstract}')
    if abstract_start == -1:
        raise ValueError("No Abstract section found in file.")
    text_after_abstract = text[abstract_start + len(r'\section{Abstract}') :]

    section_match = re.search(r'\\section\{', text_after_abstract)
    if section_match:
        abstract_text = text_after_abstract[:section_match.start()].strip()
        body_text = text_after_abstract[section_match.start():].strip()
    else:
        abstract_text = text_after_abstract.strip()
        body_text = ""

    body_text = re.sub(r'\\tightlist', '', body_text)
    body_text = re.sub(r'\\setlength\{\\parskip\}\{[^}]+\}', '', body_text)
    body_text = re.sub(r'\\setlength\{\\parindent\}\{[^}]+\}', '', body_text)

    body_text = re.sub(
        r'\\includegraphics(\[.*?\])?\{.*?([^/]+?\.(png|jpg|jpeg|pdf))\}',
        r'\\includegraphics\1{Figures/\2}', body_text
    )

    body_text = standardize_tables(body_text)

    bibtex_content = None
    if enable_citations:
        try:
            citation_result: CitationResult = apply_citation_pipeline(
                body_text, anystyle_cmd=anystyle_cmd
            )
            body_text = citation_result.body_text
            abstract_text = replace_superscript_citations(
                abstract_text,
                citation_result.key_map,
                wrap_in_superscript=True,
            )
            bibtex_content = citation_result.bibtex
        except Exception:
            raise

    header = f"""
        \\documentclass{{msurj}}
        \\usepackage{{multirow}}
        \\begin{{document}}
        \\twocolumn[
        \\begin{{@twocolumnfalse}}
        \\maketitle
        {{{metadata['authors']}}}
        {{{metadata['title']}\\strut\\\\}}
        {{{metadata['submitted_date']}}}
        {{{metadata['article_type']}}}
        {{{metadata['affiliations']}}}
        {{{metadata['keywords']}}}
        {{{metadata['email']}}}
        {{{abstract_text}}}
        \\end{{@twocolumnfalse}}]
        """

    final_tex = f"{header}\n\n{body_text}\n\n\\printbibliography\n\\end{{document}}"
    final_tex = standardize_figs(final_tex)

    if return_bibtex:
        return final_tex, bibtex_content
    return final_tex

def create_output_directory(
    pandoc_tex_path,
    final_tex,
    bibtex_content=None,
    *,
    output_root=None,
    template_dir=None,
    figures_dir=None,
):
    project_root = Path.cwd()
    paper_num = Path(pandoc_tex_path).stem

    if output_root is None:
        output_root = project_root / "output"
    else:
        output_root = Path(output_root)

    output_dir = output_root / paper_num
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{paper_num}.tex"
    Path(output_path).write_text(final_tex)

    if template_dir is None:
        template_dir = project_root / "output" / "template_dir"
    else:
        template_dir = Path(template_dir)
    shutil.copytree(
        template_dir,
        output_dir,
        dirs_exist_ok=True
    )

    if figures_dir is None:
        figures_dir = project_root / "data" / "ir_tex" / paper_num / "Figures"
    else:
        figures_dir = Path(figures_dir)

    if figures_dir.exists():
        shutil.copytree(
            figures_dir,
            output_dir / "Figures",
            dirs_exist_ok=True
        )
    else:
        (output_dir / "Figures").mkdir(parents=True, exist_ok=True)

    if bibtex_content:
        bib_path = output_dir / "bib.bib"
        Path(bib_path).write_text(bibtex_content)

   
