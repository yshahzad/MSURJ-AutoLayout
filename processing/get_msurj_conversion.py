from pathlib import Path
import shutil
import re

from processing.citations import apply_citation_pipeline, replace_superscript_citations, CitationResult
from processing.standardize_tables import standardize_tables


def standardize_figs(tex_string):
    new_tex_string = re.sub(
        r"\\includegraphics\[[^\]]*\]",
        r"\\includegraphics[width=\\columnwidth]",
        tex_string
    )

    return new_tex_string


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

    shutil.copytree(
        project_root / "data" / "ir_tex" / paper_num / "Figures",
        output_dir / "Figures",
        dirs_exist_ok=True
    )

    if bibtex_content:
        bib_path = output_dir / "bib.bib"
        Path(bib_path).write_text(bibtex_content)

   
