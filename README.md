# HeisenLab

<p align="center">
  <img src="assets/banner.png" alt="HeisenLab Banner" width="100%">
</p>

<p align="center">
  <strong>Química Analítica • Interface Moderna • Cálculos Precisos</strong>
</p>

Aplicativo de Química Analítica com interface gráfica para cálculos químicos, voltamogramas e análise estatística. Desenvolvido com PySide6, matplotlib e numpy para máxima precisão e usabilidade.

## Funcionalidades

- **Cálculos Químicos**: Diluição, pH/pOH, constantes de equilíbrio, Lei de Beer-Lambert
- **Tabela Periódica Interativa**: 118 elementos com busca, propriedades detalhadas e modelo atômico visual
- **Desenho Químico**: Editor de estruturas moleculares e funções orgânicas interativo
- **Voltamograma**: Importação e visualização de dados experimentais
- **Propriedades & Conversões**: Massa molar, densidade, molaridade e conversões de unidades
- **Análise Estatística**: Estatística descritiva, intervalos de confiança, testes t e F

## Instalação

**Opção 1:** Baixe e execute `setup.exe` (recomendado)

**Opção 2:** Build manual:
```bash
git clone <repository-url>
cd HeisenLab
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Principais Recursos

### 🧪 Cálculos Químicos
Ferramentas para diluições, pH/pOH, constantes de equilíbrio e Lei de Beer-Lambert

### 🔬 Tabela Periódica Interativa
- 118 elementos com interface visual moderna
- Busca por símbolo, nome ou número atômico
- Propriedades detalhadas e modelo atômico de Bohr
- Cores por categoria e layout responsivo

### ⚗️ Desenho Químico
Editor interativo para estruturas moleculares e funções orgânicas com:
- Ferramentas de desenho intuitivas
- Biblioteca de grupos funcionais
- Visualização 2D de moléculas
- Exportação de estruturas

### 📊 Análise de Dados
- Importação de voltamogramas (Excel)
- Análise estatística completa
- Gráficos interativos e personalizáveis

## Dependências

PySide6 • matplotlib • numpy • pandas • openpyxl

## Estrutura Principal

```
HeisenLab/
├── main.py                           # Aplicação principal
├── requirements.txt                  # Dependências
└── heisenlab/
    ├── calculations.py              # Cálculos químicos
    ├── plotting.py                  # Visualizações
    └── ui/                          # Interface gráfica
        ├── main_window.py           # Janela principal
        ├── calculations_tab.py      # Cálculos
        ├── periodic_table_tab_final.py  # Tabela periódica
        ├── chemical_draw_tab.py     # Desenho químico
        ├── calibration_tab.py       # Voltamogramas
        ├── properties_tab.py        # Propriedades
        └── statistics_tab.py        # Estatística
```

## Autores

**Lucas Cabral** • **Artur Cesar**

Laboratório de Química Analítica - Universidade Federal Fluminense (UFF)
