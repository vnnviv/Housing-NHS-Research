import sys, pathlib, fitz

for p in sys.argv[1:]:
    src = pathlib.Path(p)
    doc = fitz.open(src)
    text = "\n\n".join(page.get_text() for page in doc)
    out = pathlib.Path("sources") / (src.stem + ".md")
    out.parent.mkdir(exist_ok=True)
    out.write_text(f"# {src.stem}\n\n{text}", encoding="utf-8")
    print(out, len(text), "chars")
