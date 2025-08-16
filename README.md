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

## Exemplo - Desenho Químico

<p align="center">
  <img src="assets/image.png" alt="Exemplo de Desenho Químico no HeisenLab" width="80%">
</p>

<p align="center">
  <em>Interface do editor de estruturas moleculares com ferramentas de desenho interativas</em>
</p>

## Instalação

### Opção 1: Instalação Rápida (Recomendada)
```bash
# Baixe o arquivo setup.exe e execute
setup.exe
```
*Instalação automática com todas as dependências incluídas*

### Opção 2: Instalação Manual
```bash
# 1. Clone o repositório
git clone <repository-url>
cd HeisenLab

# 2. Crie ambiente virtual
python -m venv .venv

# 3. Ative o ambiente virtual
# No Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# No Windows (CMD):
.\.venv\Scripts\activate.bat
# No Linux/Mac:
source .venv/bin/activate

# 4. Instale dependências
pip install -r requirements.txt

# 5. Execute a aplicação
python main.py
```

### Requisitos do Sistema
- **Python**: 3.8 ou superior
- **Sistema Operacional**: Windows 10+, Linux, macOS
- **Memória RAM**: 4GB recomendado
- **Espaço em disco**: 500MB livres

## Principais Recursos

### Cálculos Químicos
Ferramentas para diluições, pH/pOH, constantes de equilíbrio e Lei de Beer-Lambert

### Tabela Periódica Interativa
- 118 elementos com interface visual moderna
- Busca por símbolo, nome ou número atômico
- Propriedades detalhadas e modelo atômico de Bohr
- Cores por categoria e layout responsivo

### Desenho Químico
Editor interativo para estruturas moleculares e funções orgânicas com:
- Ferramentas de desenho intuitivas
- Biblioteca de grupos funcionais
- Visualização 2D de moléculas
- Exportação de estruturas

### Análise de Dados
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
