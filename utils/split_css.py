"""split_css.py
Script utilitário para dividir o arquivo monolítico static/semutilizacao.css
em arquivos menores no diretório static/css/ preservando a estrutura modular.

Regras de divisão (heurísticas):
1. Variáveis (:root { ... })  -> variables.css
2. Reset e body/base          -> base.css
3. Layout (container, header, tabs, grids, progress, charts) -> layout/dashboard.css
4. Componentes (cards, buttons, tabs específicos) -> components/*.css
5. Utilitários e animações    -> utilities/animations.css & utilities/helpers.css

O script lê semutilizacao.css, identifica blocos por comentários "=====" e
escreve nos destinos adequados. Caso não encontre um bloco, ele mantém o conteúdo
no arquivo layout/dashboard.css para evitar perda de estilo.

Executar:
    python utils/split_css.py
Requerimentos:
    - Python 3
    - Caminhos de saída já existirem (static/css/...)
"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # raiz do workspace
CSS_SRC = PROJECT_ROOT / 'static' / 'semutilizacao.css'
CSS_DEST = PROJECT_ROOT / 'static' / 'css'

# Mapeamento de seções para arquivos de destino (subcaminho em CSS_DEST)
SECTION_MAP = {
    'VARIABLES': 'variables.css',
    'RESET': 'base.css',
    'CONTAINER': 'layout/dashboard.css',
    'HEADER': 'layout/dashboard.css',
    'TABS CORPORATIVOS': 'components/tabs.css',
    'OVERVIEW GRID': 'components/cards.css',
    'PROGRESS SECTION': 'layout/dashboard.css',
    'WEEK SELECTOR': 'layout/dashboard.css',
    'EMPLOYEE GRID': 'layout/dashboard.css',
    'CHARTS': 'layout/dashboard.css',
    'BTN': 'components/buttons.css',
    'UTILITARIOS': 'utilities/helpers.css',
    'ANIMAÇÕES': 'utilities/animations.css',
}

def ensure_paths():
    # cria subpastas necessárias
    for sub in ['layout', 'components', 'utilities']:
        (CSS_DEST / sub).mkdir(parents=True, exist_ok=True)

def write_chunk(dest_rel, chunk):
    dest_path = CSS_DEST / dest_rel
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    mode = 'a' if dest_path.exists() else 'w'
    with dest_path.open(mode, encoding='utf-8') as f:
        f.write(chunk + '\n')


def split():
    ensure_paths()
    current_file = 'layout/dashboard.css'  # default catch-all
    buffer = []

    pattern = re.compile(r'/\*+\s*=====\s*(.*?)\s*=====')
    with CSS_SRC.open(encoding='utf-8') as f:
        for line in f:
            m = pattern.search(line)
            if m:
                # Encontrou cabeçalho de seção, descarrega buffer
                if buffer:
                    write_chunk(current_file, ''.join(buffer))
                    buffer.clear()
                section = m.group(1).strip().upper()
                # Determina destino
                for key, dest in SECTION_MAP.items():
                    if key in section:
                        current_file = dest
                        break
                else:
                    current_file = 'layout/dashboard.css'
            buffer.append(line)
        # flush final
        if buffer:
            write_chunk(current_file, ''.join(buffer))

if __name__ == '__main__':
    split()
    print('CSS dividido com sucesso!') 