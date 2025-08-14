from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Dict, Iterable, Tuple, List, Union

import numpy as np
from numpy.typing import ArrayLike
from scipy import stats


# --- Core analytical calculations ---

def dilution_c1v1_c2v2(c1: float | None, v1: float | None, c2: float | None, v2: float | None) -> dict:
    """
    Resolve C1*V1 = C2*V2. Informe 3 variáveis e deixe 1 como None.
    Retorna um dicionário com todas as quatro chaves preenchidas.
    Unidades consistentes são responsabilidade do usuário.
    """
    known = {k: v for k, v in {"c1": c1, "v1": v1, "c2": c2, "v2": v2}.items() if v is not None}
    if len(known) != 3:
        raise ValueError("Informe exatamente 3 variáveis e deixe 1 como None.")
    if c1 is None:
        c1 = (c2 * v2) / v1  # type: ignore[arg-type]
    elif v1 is None:
        v1 = (c2 * v2) / c1
    elif c2 is None:
        c2 = (c1 * v1) / v2
    elif v2 is None:
        v2 = (c1 * v1) / c2
    return {"c1": float(c1), "v1": float(v1), "c2": float(c2), "v2": float(v2)}  # type: ignore[return-value]


def ph_strong_acid(acid_molar: float) -> float:
    """pH para ácido forte monoprótico (25 °C)."""
    if acid_molar <= 0:
        raise ValueError("Concentração deve ser > 0")
    return -math.log10(acid_molar)


def poh_strong_base(base_molar: float) -> float:
    """pOH para base forte monoprótica (25 °C)."""
    if base_molar <= 0:
        raise ValueError("Concentração deve ser > 0")
    return -math.log10(base_molar)


def ph_from_poh(poh: float) -> float:
    return 14.0 - poh


def calculate_ka_from_ph(ph: float, initial_concentration: float) -> float:
    """
    Calcula Ka de um ácido fraco a partir do pH e concentração inicial.
    Ka = [H+]² / (C₀ - [H+])
    """
    if ph < 0 or ph > 14:
        raise ValueError("pH deve estar entre 0 e 14")
    if initial_concentration <= 0:
        raise ValueError("Concentração inicial deve ser positiva")
    
    h_plus = 10 ** (-ph)
    if h_plus >= initial_concentration:
        raise ValueError("Concentração de H+ não pode ser maior que a concentração inicial")
    
    ka = (h_plus ** 2) / (initial_concentration - h_plus)
    return ka


def calculate_pka_from_ka(ka: float) -> float:
    """Calcula pKa a partir de Ka."""
    if ka <= 0:
        raise ValueError("Ka deve ser positivo")
    return -math.log10(ka)


def calculate_ka_from_pka(pka: float) -> float:
    """Calcula Ka a partir de pKa."""
    return 10 ** (-pka)


def calculate_kb_from_poh(poh: float, initial_concentration: float) -> float:
    """
    Calcula Kb de uma base fraca a partir do pOH e concentração inicial.
    Kb = [OH-]² / (C₀ - [OH-])
    """
    if poh < 0 or poh > 14:
        raise ValueError("pOH deve estar entre 0 e 14")
    if initial_concentration <= 0:
        raise ValueError("Concentração inicial deve ser positiva")
    
    oh_minus = 10 ** (-poh)
    if oh_minus >= initial_concentration:
        raise ValueError("Concentração de OH- não pode ser maior que a concentração inicial")
    
    kb = (oh_minus ** 2) / (initial_concentration - oh_minus)
    return kb


def calculate_pkb_from_kb(kb: float) -> float:
    """Calcula pKb a partir de Kb."""
    if kb <= 0:
        raise ValueError("Kb deve ser positivo")
    return -math.log10(kb)


def calculate_kb_from_pkb(pkb: float) -> float:
    """Calcula Kb a partir de pKb."""
    return 10 ** (-pkb)


def ka_kb_relationship(ka: float = None, kb: float = None) -> dict:
    """
    Relação Ka × Kb = Kw (a 25°C, Kw = 1.0 × 10⁻¹⁴).
    Informe Ka ou Kb para calcular o outro.
    """
    kw = 1.0e-14
    
    if ka is not None and kb is not None:
        raise ValueError("Informe apenas Ka OU Kb, não ambos")
    elif ka is not None:
        if ka <= 0:
            raise ValueError("Ka deve ser positivo")
        kb = kw / ka
        return {"ka": ka, "kb": kb, "pka": calculate_pka_from_ka(ka), "pkb": calculate_pkb_from_kb(kb)}
    elif kb is not None:
        if kb <= 0:
            raise ValueError("Kb deve ser positivo")
        ka = kw / kb
        return {"ka": ka, "kb": kb, "pka": calculate_pka_from_ka(ka), "pkb": calculate_pkb_from_kb(kb)}
    else:
        raise ValueError("Informe Ka ou Kb")


def absorbance_beer_lambert(epsilon: float, path_length_cm: float, concentration_molar: float) -> float:
    """A = ε·b·c"""
    if any(x < 0 for x in (epsilon, path_length_cm, concentration_molar)):
        raise ValueError("Parâmetros devem ser não-negativos")
    return float(epsilon * path_length_cm * concentration_molar)


# --- Linear regression for calibration curves ---

@dataclass
class LinearFit:
    slope: float
    intercept: float
    r_value: float  # Pearson r
    r_squared: float


def linear_fit(x: ArrayLike, y: ArrayLike) -> LinearFit:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size != y.size or x.size < 2:
        raise ValueError("x e y devem ter mesmo tamanho e pelo menos 2 pontos")
    A = np.vstack([x, np.ones_like(x)]).T
    slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]
    # r
    x_mean = x.mean()
    y_mean = y.mean()
    ss_xy = np.sum((x - x_mean) * (y - y_mean))
    ss_xx = np.sum((x - x_mean) ** 2)
    ss_yy = np.sum((y - y_mean) ** 2)
    r = float(ss_xy / math.sqrt(ss_xx * ss_yy)) if ss_xx > 0 and ss_yy > 0 else 0.0
    return LinearFit(float(slope), float(intercept), r, r * r)


# --- Periodic Table and Molecular Mass ---

# Masses are in g/mol (atomic masses)
PERIODIC_TABLE = {
    'H': 1.008, 'He': 4.003, 'Li': 6.941, 'Be': 9.012, 'B': 10.811, 'C': 12.011,
    'N': 14.007, 'O': 15.999, 'F': 18.998, 'Ne': 20.180, 'Na': 22.990, 'Mg': 24.305,
    'Al': 26.982, 'Si': 28.086, 'P': 30.974, 'S': 32.065, 'Cl': 35.453, 'Ar': 39.948,
    'K': 39.098, 'Ca': 40.078, 'Sc': 44.956, 'Ti': 47.867, 'V': 50.942, 'Cr': 51.996,
    'Mn': 54.938, 'Fe': 55.845, 'Co': 58.933, 'Ni': 58.693, 'Cu': 63.546, 'Zn': 65.38,
    'Ga': 69.723, 'Ge': 72.64, 'As': 74.922, 'Se': 78.96, 'Br': 79.904, 'Kr': 83.798,
    'Rb': 85.468, 'Sr': 87.62, 'Y': 88.906, 'Zr': 91.224, 'Nb': 92.906, 'Mo': 95.96,
    'Tc': 98.0, 'Ru': 101.07, 'Rh': 102.906, 'Pd': 106.42, 'Ag': 107.868, 'Cd': 112.411,
    'In': 114.818, 'Sn': 118.71, 'Sb': 121.76, 'Te': 127.6, 'I': 126.904, 'Xe': 131.293,
    'Cs': 132.905, 'Ba': 137.327, 'La': 138.905, 'Ce': 140.116, 'Pr': 140.908, 'Nd': 144.242,
    'Pm': 145.0, 'Sm': 150.36, 'Eu': 151.964, 'Gd': 157.25, 'Tb': 158.925, 'Dy': 162.5,
    'Ho': 164.93, 'Er': 167.259, 'Tm': 168.934, 'Yb': 173.054, 'Lu': 174.967, 'Hf': 178.49,
    'Ta': 180.948, 'W': 183.84, 'Re': 186.207, 'Os': 190.23, 'Ir': 192.217, 'Pt': 195.084,
    'Au': 196.967, 'Hg': 200.59, 'Tl': 204.383, 'Pb': 207.2, 'Bi': 208.98, 'Po': 209.0,
    'At': 210.0, 'Rn': 222.0, 'Fr': 223.0, 'Ra': 226.0, 'Ac': 227.0, 'Th': 232.038,
    'Pa': 231.036, 'U': 238.029, 'Np': 237.0, 'Pu': 244.0, 'Am': 243.0, 'Cm': 247.0,
    'Bk': 247.0, 'Cf': 251.0, 'Es': 252.0, 'Fm': 257.0, 'Md': 258.0, 'No': 259.0,
    'Lr': 262.0, 'Rf': 267.0, 'Db': 268.0, 'Sg': 271.0, 'Bh': 272.0, 'Hs': 270.0,
    'Mt': 276.0, 'Ds': 281.0, 'Rg': 280.0, 'Cn': 285.0, 'Nh': 284.0, 'Fl': 289.0,
    'Mc': 288.0, 'Lv': 293.0, 'Ts': 294.0, 'Og': 294.0
}


def parse_chemical_formula(formula: str) -> Dict[str, int]:
    """
    Parse a chemical formula and return element counts.
    Examples: 'H2SO4' -> {'H': 2, 'S': 1, 'O': 4}
              'Ca(OH)2' -> {'Ca': 1, 'O': 2, 'H': 2}
              'K3[Fe(CN)6]' -> {'K': 3, 'Fe': 1, 'C': 6, 'N': 6}
    """
    formula = formula.replace(' ', '')
    
    # Handle both parentheses and brackets
    while '(' in formula or '[' in formula:
        # Find innermost parentheses or brackets
        start = -1
        bracket_type = None
        
        for i, char in enumerate(formula):
            if char in '([':
                start = i
                bracket_type = char
            elif char in ')]':
                if start == -1:
                    raise ValueError("Parênteses/colchetes desbalanceados")
                
                # Check if closing bracket matches opening
                if (bracket_type == '(' and char != ')') or (bracket_type == '[' and char != ']'):
                    raise ValueError("Tipos de parênteses/colchetes não coincidem")
                
                # Extract content and multiplier
                content = formula[start+1:i]
                after_bracket = formula[i+1:]
                
                # Find the multiplier after closing bracket
                multiplier_match = re.match(r'^(\d+)', after_bracket)
                multiplier = int(multiplier_match.group(1)) if multiplier_match else 1
                
                # Parse content inside brackets
                inner_elements = parse_simple_formula(content)
                
                # Apply multiplier
                expanded = ''
                for element, count in inner_elements.items():
                    expanded += element + str(count * multiplier)
                
                # Replace in formula
                end_pos = i + 1 + (len(multiplier_match.group(1)) if multiplier_match else 0)
                formula = formula[:start] + expanded + formula[end_pos:]
                break
    
    return parse_simple_formula(formula)


def parse_simple_formula(formula: str) -> Dict[str, int]:
    """Parse a simple formula without parentheses."""
    elements = {}
    pattern = r'([A-Z][a-z]?)(\d*)'
    
    for match in re.finditer(pattern, formula):
        element = match.group(1)
        count = int(match.group(2)) if match.group(2) else 1
        
        if element not in PERIODIC_TABLE:
            raise ValueError(f"Elemento desconhecido: {element}")
        
        elements[element] = elements.get(element, 0) + count
    
    return elements


def calculate_molar_mass(formula: str) -> float:
    """Calculate molar mass of a chemical compound in g/mol."""
    try:
        elements = parse_chemical_formula(formula)
        molar_mass = 0.0
        
        for element, count in elements.items():
            molar_mass += PERIODIC_TABLE[element] * count
        
        return molar_mass
    except Exception as e:
        raise ValueError(f"Erro ao calcular massa molar: {str(e)}")


# --- Unit Conversions ---

MASS_CONVERSIONS = {
    'kg': 1000.0,
    'g': 1.0,
    'mg': 0.001,
    'μg': 0.000001,
    'ug': 0.000001  # Alternative for μg
}

VOLUME_CONVERSIONS = {
    'L': 1.0,
    'mL': 0.001,
    'μL': 0.000001,
    'uL': 0.000001  # Alternative for μL
}

CONCENTRATION_CONVERSIONS = {
    'M': 1.0,
    'mM': 0.001,
    'μM': 0.000001,
    'uM': 0.000001  # Alternative for μM
}

PRESSURE_CONVERSIONS = {
    'atm': 1.0,
    'bar': 0.98692,
    'Pa': 9.8692e-6,
    'kPa': 0.0098692,
    'mmHg': 0.00131579,
    'Torr': 0.00131579
}


def convert_mass(value: float, from_unit: str, to_unit: str) -> float:
    """Convert mass between different units."""
    if from_unit not in MASS_CONVERSIONS or to_unit not in MASS_CONVERSIONS:
        raise ValueError(f"Unidades não suportadas. Use: {list(MASS_CONVERSIONS.keys())}")
    
    # Convert to grams first, then to target unit
    grams = value * MASS_CONVERSIONS[from_unit]
    return grams / MASS_CONVERSIONS[to_unit]


def convert_volume(value: float, from_unit: str, to_unit: str) -> float:
    """Convert volume between different units."""
    if from_unit not in VOLUME_CONVERSIONS or to_unit not in VOLUME_CONVERSIONS:
        raise ValueError(f"Unidades não suportadas. Use: {list(VOLUME_CONVERSIONS.keys())}")
    
    # Convert to liters first, then to target unit
    liters = value * VOLUME_CONVERSIONS[from_unit]
    return liters / VOLUME_CONVERSIONS[to_unit]


def convert_concentration(value: float, from_unit: str, to_unit: str) -> float:
    """Convert concentration between different units (molar only)."""
    if from_unit not in CONCENTRATION_CONVERSIONS or to_unit not in CONCENTRATION_CONVERSIONS:
        raise ValueError(f"Unidades não suportadas. Use: {list(CONCENTRATION_CONVERSIONS.keys())}")
    
    # Convert to M first, then to target unit
    molar = value * CONCENTRATION_CONVERSIONS[from_unit]
    return molar / CONCENTRATION_CONVERSIONS[to_unit]


def convert_pressure(value: float, from_unit: str, to_unit: str) -> float:
    """Convert pressure between different units."""
    if from_unit not in PRESSURE_CONVERSIONS or to_unit not in PRESSURE_CONVERSIONS:
        raise ValueError(f"Unidades não suportadas. Use: {list(PRESSURE_CONVERSIONS.keys())}")
    
    # Convert to atm first, then to target unit
    atm = value * PRESSURE_CONVERSIONS[from_unit]
    return atm / PRESSURE_CONVERSIONS[to_unit]


def celsius_to_kelvin(celsius: float) -> float:
    """Convert Celsius to Kelvin."""
    return celsius + 273.15


def kelvin_to_celsius(kelvin: float) -> float:
    """Convert Kelvin to Celsius."""
    return kelvin - 273.15


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9/5) + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5/9


# --- Chemical Properties Calculations ---

def calculate_density(mass: float, volume: float, mass_unit: str = 'g', volume_unit: str = 'mL') -> float:
    """
    Calculate density (ρ = m/V).
    Returns density in g/mL by default.
    """
    if mass <= 0 or volume <= 0:
        raise ValueError("Massa e volume devem ser positivos")
    
    # Convert to standard units (g and mL)
    mass_g = convert_mass(mass, mass_unit, 'g')
    volume_ml = convert_volume(volume, volume_unit, 'mL')
    
    return mass_g / volume_ml


def calculate_molarity(moles: float, volume: float, volume_unit: str = 'L') -> float:
    """
    Calculate molarity (M = n/V).
    Returns molarity in mol/L.
    """
    if moles < 0 or volume <= 0:
        raise ValueError("Número de mols deve ser não-negativo e volume positivo")
    
    # Convert volume to liters
    volume_l = convert_volume(volume, volume_unit, 'L')
    
    return moles / volume_l


def calculate_moles(mass: float, molar_mass: float, mass_unit: str = 'g') -> float:
    """
    Calculate number of moles (n = m/MM).
    Returns moles.
    """
    if mass < 0 or molar_mass <= 0:
        raise ValueError("Massa deve ser não-negativa e massa molar positiva")
    
    # Convert mass to grams
    mass_g = convert_mass(mass, mass_unit, 'g')
    
    return mass_g / molar_mass


def calculate_mass_concentration(mass_solute: float, volume_solution: float, 
                               mass_unit: str = 'g', volume_unit: str = 'L') -> float:
    """
    Calculate mass concentration (C = m_solute/V_solution).
    Returns concentration in g/L by default.
    """
    if mass_solute < 0 or volume_solution <= 0:
        raise ValueError("Massa do soluto deve ser não-negativa e volume da solução positivo")
    
    # Convert to standard units
    mass_g = convert_mass(mass_solute, mass_unit, 'g')
    volume_l = convert_volume(volume_solution, volume_unit, 'L')
    
    return mass_g / volume_l


def calculate_ppm(mass_solute: float, mass_solution: float, 
                  solute_unit: str = 'mg', solution_unit: str = 'kg') -> float:
    """
    Calculate parts per million (ppm).
    ppm = (mass_solute / mass_solution) × 10^6
    """
    if mass_solute < 0 or mass_solution <= 0:
        raise ValueError("Massas devem ser não-negativas e massa da solução positiva")
    
    # Convert both to grams
    solute_g = convert_mass(mass_solute, solute_unit, 'g')
    solution_g = convert_mass(mass_solution, solution_unit, 'g')
    
    return (solute_g / solution_g) * 1e6


def calculate_ppb(mass_solute: float, mass_solution: float, 
                  solute_unit: str = 'μg', solution_unit: str = 'kg') -> float:
    """
    Calculate parts per billion (ppb).
    ppb = (mass_solute / mass_solution) × 10^9
    """
    if mass_solute < 0 or mass_solution <= 0:
        raise ValueError("Massas devem ser não-negativas e massa da solução positiva")
    
    # Convert both to grams
    solute_g = convert_mass(mass_solute, solute_unit, 'g')
    solution_g = convert_mass(mass_solution, solution_unit, 'g')
    
    return (solute_g / solution_g) * 1e9


# --- Statistical Analysis Functions ---


def absolute_deviation(data: List[float], reference: float = None) -> List[float]:
    """
    Calcula o desvio absoluto de cada valor em relação à média ou valor de referência.
    |xi - x̄| ou |xi - ref|
    """
    if not data:
        raise ValueError("Lista de dados não pode estar vazia")
    
    data_array = np.array(data)
    ref_value = reference if reference is not None else np.mean(data_array)
    
    return [abs(x - ref_value) for x in data]


def mean_deviation(data: List[float]) -> float:
    """
    Calcula o desvio médio (desvio absoluto médio).
    Σ|xi - x̄| / n
    """
    if not data:
        raise ValueError("Lista de dados não pode estar vazia")
    
    abs_devs = absolute_deviation(data)
    return sum(abs_devs) / len(abs_devs)


def sample_variance(data: List[float]) -> float:
    """
    Calcula a variância amostral.
    s² = Σ(xi - x̄)² / (n-1)
    """
    if len(data) < 2:
        raise ValueError("Necessário pelo menos 2 valores para variância amostral")
    
    data_array = np.array(data)
    return float(np.var(data_array, ddof=1))


def sample_standard_deviation(data: List[float]) -> float:
    """
    Calcula o desvio padrão amostral.
    s = √[Σ(xi - x̄)² / (n-1)]
    """
    return math.sqrt(sample_variance(data))


def coefficient_of_variation(data: List[float]) -> float:
    """
    Calcula o coeficiente de variação (CV).
    CV = (s / x̄) × 100%
    """
    if not data:
        raise ValueError("Lista de dados não pode estar vazia")
    
    data_array = np.array(data)
    mean_val = np.mean(data_array)
    
    if mean_val == 0:
        raise ValueError("Média não pode ser zero para calcular CV")
    
    std_dev = sample_standard_deviation(data)
    return (std_dev / mean_val) * 100


def correction_factor(n: int) -> float:
    """
    Fator de correção para amostras pequenas.
    f = √[n/(n-1)]
    """
    if n < 2:
        raise ValueError("n deve ser maior que 1")
    
    return math.sqrt(n / (n - 1))


def confidence_interval_mean_small_n(data: List[float], confidence_level: float = 0.95) -> dict:
    """
    Intervalo de confiança da média para n pequeno (usar t de Student).
    IC = x̄ ± t(α/2,n-1) × (s/√n)
    """
    if len(data) < 2:
        raise ValueError("Necessário pelo menos 2 valores")
    
    if not 0 < confidence_level < 1:
        raise ValueError("Nível de confiança deve estar entre 0 e 1")
    
    data_array = np.array(data)
    n = len(data_array)
    mean_val = np.mean(data_array)
    std_dev = sample_standard_deviation(data)
    
    # Graus de liberdade
    df = n - 1
    
    # Valor crítico t
    alpha = 1 - confidence_level
    t_critical = stats.t.ppf(1 - alpha/2, df)
    
    # Margem de erro
    margin_error = t_critical * (std_dev / math.sqrt(n))
    
    return {
        "mean": mean_val,
        "std_dev": std_dev,
        "n": n,
        "df": df,
        "t_critical": t_critical,
        "margin_error": margin_error,
        "lower_limit": mean_val - margin_error,
        "upper_limit": mean_val + margin_error,
        "confidence_level": confidence_level
    }


def confidence_interval_mean_large_n(data: List[float], confidence_level: float = 0.95) -> dict:
    """
    Intervalo de confiança da média para n grande (usar z).
    IC = x̄ ± z(α/2) × (s/√n)
    """
    if len(data) < 30:
        raise ValueError("Para usar distribuição normal, n deve ser ≥ 30")
    
    if not 0 < confidence_level < 1:
        raise ValueError("Nível de confiança deve estar entre 0 e 1")
    
    data_array = np.array(data)
    n = len(data_array)
    mean_val = np.mean(data_array)
    std_dev = sample_standard_deviation(data)
    
    # Valor crítico z
    alpha = 1 - confidence_level
    z_critical = stats.norm.ppf(1 - alpha/2)
    
    # Margem de erro
    margin_error = z_critical * (std_dev / math.sqrt(n))
    
    return {
        "mean": mean_val,
        "std_dev": std_dev,
        "n": n,
        "z_critical": z_critical,
        "margin_error": margin_error,
        "lower_limit": mean_val - margin_error,
        "upper_limit": mean_val + margin_error,
        "confidence_level": confidence_level
    }


def t_test_two_means(data1: List[float], data2: List[float], confidence_level: float = 0.95) -> dict:
    """
    Teste t para comparar duas médias (amostras independentes).
    H₀: μ₁ = μ₂
    H₁: μ₁ ≠ μ₂
    """
    if len(data1) < 2 or len(data2) < 2:
        raise ValueError("Cada amostra deve ter pelo menos 2 valores")
    
    # Usar scipy.stats para teste t
    t_stat, p_value = stats.ttest_ind(data1, data2)
    
    # Estatísticas descritivas
    n1, n2 = len(data1), len(data2)
    mean1, mean2 = np.mean(data1), np.mean(data2)
    std1, std2 = sample_standard_deviation(data1), sample_standard_deviation(data2)
    
    # Graus de liberdade (fórmula de Welch)
    s1_sq, s2_sq = std1**2, std2**2
    df = ((s1_sq/n1 + s2_sq/n2)**2) / ((s1_sq/n1)**2/(n1-1) + (s2_sq/n2)**2/(n2-1))
    
    # Valor crítico
    alpha = 1 - confidence_level
    t_critical = stats.t.ppf(1 - alpha/2, df)
    
    # Decisão
    reject_h0 = abs(t_stat) > t_critical
    
    return {
        "t_statistic": t_stat,
        "p_value": p_value,
        "t_critical": t_critical,
        "df": df,
        "mean1": mean1,
        "mean2": mean2,
        "std1": std1,
        "std2": std2,
        "n1": n1,
        "n2": n2,
        "reject_h0": reject_h0,
        "confidence_level": confidence_level,
        "conclusion": "Médias são significativamente diferentes" if reject_h0 else "Não há diferença significativa entre as médias"
    }


def f_test_two_variances(data1: List[float], data2: List[float], confidence_level: float = 0.95) -> dict:
    """
    Teste F para comparar duas variâncias.
    H₀: σ₁² = σ₂²
    H₁: σ₁² ≠ σ₂²
    F = s₁²/s₂² (onde s₁² é a maior variância)
    """
    if len(data1) < 2 or len(data2) < 2:
        raise ValueError("Cada amostra deve ter pelo menos 2 valores")
    
    # Calcular variâncias
    var1 = sample_variance(data1)
    var2 = sample_variance(data2)
    
    # Garantir que s₁² é a maior variância
    if var1 >= var2:
        f_stat = var1 / var2
        df1, df2 = len(data1) - 1, len(data2) - 1
        larger_var_sample = 1
    else:
        f_stat = var2 / var1
        df1, df2 = len(data2) - 1, len(data1) - 1
        larger_var_sample = 2
    
    # Valor crítico F
    alpha = 1 - confidence_level
    f_critical = stats.f.ppf(1 - alpha/2, df1, df2)
    
    # P-valor (teste bilateral)
    p_value = 2 * (1 - stats.f.cdf(f_stat, df1, df2))
    
    # Decisão
    reject_h0 = f_stat > f_critical
    
    return {
        "f_statistic": f_stat,
        "p_value": p_value,
        "f_critical": f_critical,
        "df1": df1,
        "df2": df2,
        "var1": var1,
        "var2": var2,
        "larger_variance_sample": larger_var_sample,
        "reject_h0": reject_h0,
        "confidence_level": confidence_level,
        "conclusion": "Variâncias são significativamente diferentes" if reject_h0 else "Não há diferença significativa entre as variâncias"
    }
