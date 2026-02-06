from __future__ import annotations

import io
import shutil
import tempfile
import zipfile
from pathlib import Path

from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

from processing.get_msurj_conversion import convert_to_msurj, create_output_directory
from processing.pandoc_intermediate import create_tex_ir


ALLOWED_EXTENSIONS = {".docx"}
PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = PROJECT_ROOT / "output" / "template_dir"

app = Flask(__name__)


def _check_cli(tool: str) -> str | None:
    return shutil.which(tool)


def _allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/convert")
def convert():
    upload = request.files.get("manuscript")
    if not upload or upload.filename == "":
        return render_template("index.html", error="no file uploaded.")

    if not _allowed_file(upload.filename):
        return render_template("index.html", error="please upload a .docx file.")

    pandoc_path = _check_cli("pandoc")
    if not pandoc_path:
        return render_template("index.html", error="pandoc not found on PATH.")

    anystyle_cmd = request.form.get("anystyle_cmd") or "anystyle"
    if not _check_cli(anystyle_cmd):
        return render_template(
            "index.html",
            error="anystyle not found. install anystyle-cli or provide a valid path.",
        )

    if not TEMPLATE_DIR.exists():
        return render_template(
            "index.html",
            error="template_dir not found at /output/template_dir.",
        )

    raw_authors = request.form.getlist("authors")
    raw_affiliations = request.form.getlist("author_affiliations")
    if len(raw_authors) != len(raw_affiliations):
        return render_template(
            "index.html",
            error="author names and affiliations must match.",
        )

    author_pairs = []
    for author, affiliation in zip(raw_authors, raw_affiliations):
        author = author.strip()
        affiliation = affiliation.strip()
        if not author and not affiliation:
            continue
        if not author:
            return render_template("index.html", error="each author needs a name.")
        if not affiliation:
            return render_template(
                "index.html", error="each author needs an affiliation."
            )
        author_pairs.append((author, affiliation))

    if not author_pairs:
        return render_template("index.html", error="please provide at least one author.")

    metadata = {
        "authors": ", ".join(a for a, _ in author_pairs),
        "title": request.form.get("title", "").strip(),
        "submitted_date": request.form.get("submitted_date", "").strip(),
        "article_type": request.form.get("article_type", "").strip(),
        "affiliations": "; ".join(a for _, a in author_pairs),
        "keywords": request.form.get("keywords", "").strip(),
        "email": request.form.get("email", "").strip(),
    }

    filename = secure_filename(upload.filename)

    with tempfile.TemporaryDirectory() as tmp_root:
        tmp_root = Path(tmp_root)
        ir_tex_dir = tmp_root / "ir_tex"
        output_root = tmp_root / "output"
        upload_path = tmp_root / filename

        upload.save(upload_path)

        ir_output_dir = create_tex_ir(upload_path, ir_tex_dir=ir_tex_dir)
        paper_num = ir_output_dir.name
        pandoc_tex_path = ir_output_dir / f"{paper_num}.tex"

        final_tex, bibtex = convert_to_msurj(
            pandoc_tex_path=pandoc_tex_path,
            metadata=metadata,
            enable_citations=True,
            return_bibtex=True,
            anystyle_cmd=anystyle_cmd,
        )

        create_output_directory(
            pandoc_tex_path,
            final_tex,
            bibtex_content=bibtex,
            output_root=output_root,
            template_dir=TEMPLATE_DIR,
        )

        zip_bytes = io.BytesIO()
        with zipfile.ZipFile(zip_bytes, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in (output_root / paper_num).rglob("*"):
                zf.write(path, path.relative_to(output_root))
        zip_bytes.seek(0)

    return send_file(
        zip_bytes,
        as_attachment=True,
        download_name=f"{paper_num}.zip",
        mimetype="application/zip",
    )


if __name__ == "__main__":
    app.run(debug=True)
