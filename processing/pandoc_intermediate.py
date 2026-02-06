from pathlib import Path
import subprocess


def create_tex_ir(input_docx):
    project_root = Path.cwd()
    ir_tex_dir = project_root / "data" / "ir_tex"
    paper_num = input_docx.stem

    output_dir = ir_tex_dir / paper_num
    output_dir.mkdir(parents=True, exist_ok=True)

    output_tex = output_dir / f"{paper_num}.tex"

    subprocess.run([
        "pandoc",
        str(input_docx),
        "--from=docx",
        "--to=latex",
        "--output", str(output_tex),
        "--standalone",
        f"--extract-media={output_dir}",
        "--wrap=none"
    ])

    (output_dir / "media").rename(output_dir / "Figures")

    print(f"Files created in:\n{output_dir.resolve()}")
