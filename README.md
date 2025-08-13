# HeisenLab

Aplicativo de Química Analítica com interface gráfica (PySide6), gráficos (matplotlib) e cálculos úteis para química.

## Funcionalidades

### Aba "Cálculos"
- **Calculadora de diluição** (C₁V₁ = C₂V₂)
- **Cálculos de pH/pOH**:
  - pH para ácidos fortes
  - pOH e pH para bases fortes
- **Constantes de equilíbrio**:
  - Cálculo de Ka a partir do pH
  - Conversões pKa ↔ Ka
  - Cálculo de Kb a partir do pOH
  - Conversões pKb ↔ Kb
  - Relação Ka×Kb = Kw
- **Espectrofotometria**:
  - Lei de Beer-Lambert (A = ε·b·c)

### Aba "Calibração"
- Calibração linear com gráfico (dispersão + reta) e R²
- Entrada de dados em tabela
- Ajuste automático de curva
- Cálculo de coeficiente de correlação

### Aba "Propriedades & Conversões"
- **Cálculo de Massa Molar**: Parse de fórmulas químicas complexas
  - Suporte a parênteses: `Ca(OH)2`
  - Suporte a colchetes: `K3[Fe(CN)6]`
  - Composição detalhada com massas atômicas
  - Composição percentual

- **Conversão de Unidades**:
  - Massa: g, kg, mg, μg
  - Volume: L, mL, μL
  - Temperatura: °C, K, °F
  - Pressão: atm, bar, Pa, mmHg, Torr

- **Cálculos de Propriedades**:
  - Densidade (ρ = m/V)
  - Molaridade (M = n/V)
  - Número de mols (n = m/MM)
  - Concentração em massa
  - Partes por milhão (ppm)
  - Partes por bilhão (ppb)

### Aba "Estatística"
- **Estatística descritiva**:
  - Desvio absoluto e desvio médio
  - Variância e desvio padrão amostral
  - Coeficiente de variação (CV)
  - Fator de correção para amostras pequenas
- **Intervalos de confiança**:
  - Para amostras pequenas (distribuição t)
  - Para amostras grandes (distribuição normal)
- **Testes estatísticos**:
  - Teste t para duas médias
  - Teste F para duas variâncias

## Instalação

### Pré-requisitos
- Python 3.8 ou superior

### Passos para instalação

1) Crie um ambiente virtual e ative:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Instale as dependências:
```powershell
pip install -r requirements.txt
```

3) Execute o aplicativo:
```powershell
python main.py
```

### Dependências incluídas
- PySide6 (interface gráfica)
- matplotlib (gráficos)
- numpy (cálculos científicos)
- pandas (manipulação de dados)

## Estrutura do Projeto

```
HeisenLab/
├── main.py                    # Arquivo principal (ponto de entrada)
├── requirements.txt           # Dependências do projeto
├── heisenlab/                 # Pacote principal
│   ├── __init__.py           
│   ├── calculations.py        # Funções de cálculo e conversões
│   ├── plotting.py           # Funções de plotagem com matplotlib
│   └── ui/                   # Interface gráfica
│       ├── __init__.py       
│       ├── main_window.py    # Janela principal
│       ├── calculations_tab.py # Aba de cálculos químicos
│       ├── calibration_tab.py  # Aba de calibração linear
│       ├── properties_tab.py   # Aba de propriedades e conversões
│       └── statistics_tab.py   # Aba de estatística descritiva
```

## Status do Projeto

✅ **Funcionalidades Implementadas**:
- Calculadora de diluição
- Cálculos de pH/pOH para ácidos e bases fortes
- Constantes de equilíbrio (Ka, Kb, pKa, pKb)
- Lei de Beer-Lambert
- Calibração linear com R²
- Parser de fórmulas químicas
- Conversões de unidades
- Cálculos de propriedades químicas
- Estatística descritiva completa

✅ **Interface Gráfica**:
- Interface moderna com PySide6
- Organização em abas
- Gráficos interativos com matplotlib
- Validação de entrada de dados
- Resultados formatados

## Recursos Técnicos

- **Parser Químico**: Análise de fórmulas complexas com parênteses e colchetes
- **Validação de Dados**: Verificação automática de entradas
- **Gráficos Dinâmicos**: Plots atualizados em tempo real
- **Estatística Robusta**: Testes t e F para análise de dados
- **Interface Responsiva**: Layout adaptável e intuitivo
- **Cálculos químicos** (densidade, molaridade, número de mols, ppm, ppb)

## Estrutura do projeto

```
HeisenLab/
	heisenlab/
		__init__.py
		calculations.py          # Cálculos químicos e conversões
		plotting.py
		ui/
			__init__.py
			main_window.py
			calculations_tab.py
			calibration_tab.py
			properties_tab.py    # ⭐ Nova aba
	main.py
	requirements.txt
	test_simple.py              # ⭐ Testes das funcionalidades
	LICENSE
	README.md
```

Sinta-se à vontade para sugerir novos módulos de cálculo e rotinas específicas do laboratório da UFF.
