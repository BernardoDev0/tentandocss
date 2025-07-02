import re
from pathlib import Path

# Lista de arquivos CSS (ordem importa!)
CSS_MODULES = [
    "static/css/variables.css",
    "static/css/base.css",
    "static/css/layout/dashboard.css",
    "static/css/layout/grid.css",
    "static/css/layout/header.css",
    "static/css/components/cards.css",
    "static/css/components/buttons.css",
    "static/css/components/tabs.css",
    "static/css/components/forms.css",
    "static/css/utilities/animations.css",
    "static/css/utilities/helpers.css",
    "static/css/utilities/responsive.css",
]

BUNDLE_PATH = Path("static/css/bundle.min.css")

# Regex simples para remover comentários/espacos
_comment_re = re.compile(r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/", re.S)
_whitespace_re = re.compile(r"\s+")


def minify(css: str) -> str:
    css = _comment_re.sub("", css)  # remove comentários
    css = _whitespace_re.sub(" ", css)  # colapsa espaços
    return css.strip()


def build():
    parts = []
    for rel_path in CSS_MODULES:
        path = Path(rel_path)
        if not path.exists():
            print(f"[WARN] Arquivo não encontrado: {rel_path}")
            continue
        parts.append(path.read_text(encoding="utf-8"))
    bundle = "\n".join(parts)
    BUNDLE_PATH.write_text(minify(bundle), encoding="utf-8")
    print(f"✅ Gerado {BUNDLE_PATH} (tamanho {BUNDLE_PATH.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    build() 