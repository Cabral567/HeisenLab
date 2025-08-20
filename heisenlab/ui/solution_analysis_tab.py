from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QTextEdit, QPushButton, QLabel, QComboBox, QDoubleSpinBox,
    QScrollArea, QTabWidget, QCheckBox, QSpinBox, QLineEdit
)
import math


class SolutionAnalysisTab(QWidget):
    """Aba para análise de soluções, pH, tampões e equilíbrios químicos."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface principal."""
        main_layout = QVBoxLayout(self)
        
        # Criar abas internas
        tabs = QTabWidget()
        
        # Aba 1: Cálculo de pH
        tabs.addTab(self.create_ph_calculator_tab(), "Calculadora de pH")
        
        # Aba 2: Sistemas Tampão
        tabs.addTab(self.create_buffer_systems_tab(), "Sistemas Tampão")
        
        # Aba 3: Titulações
        tabs.addTab(self.create_titration_curves_tab(), "Curvas de Titulação")
        
        # Aba 4: Preparo de Soluções
        tabs.addTab(self.create_solution_preparation_tab(), "Preparo de Soluções")
        
        # Aba 5: Indicadores
        tabs.addTab(self.create_indicators_tab(), "Indicadores de pH")
        
        main_layout.addWidget(tabs)
    
    def create_ph_calculator_tab(self):
        """Cria a aba de cálculo de pH."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Informações sobre pH
        info_group = QGroupBox("Calculadora de pH e pOH")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel("""
        <b>pH:</b> Potencial hidrogeniônico - medida da acidez/basicidade de uma solução
        
        <b>Fórmulas fundamentais:</b>
        • pH = -log[H⁺]
        • pOH = -log[OH⁻]
        • pH + pOH = 14 (a 25°C)
        • Kw = [H⁺][OH⁻] = 1,0 × 10⁻¹⁴
        
        <b>Escala de pH:</b>
        • 0-7: Ácido • 7: Neutro • 7-14: Básico
        """)
        info_text.setWordWrap(True)
        info_text.setStyleSheet("padding: 10px; background-color: #e8f5e8; border-radius: 5px;")
        info_layout.addWidget(info_text)
        
        main_layout.addWidget(info_group)
        
        # Seletor de tipo de solução
        type_group = QGroupBox("Tipo de Solução")
        type_layout = QVBoxLayout(type_group)
        
        self.solution_type = QComboBox()
        self.solution_type.addItems([
            "Ácido Forte",
            "Base Forte", 
            "Ácido Fraco",
            "Base Fraca",
            "Concentração de H⁺",
            "Concentração de OH⁻"
        ])
        self.solution_type.currentTextChanged.connect(self.on_solution_type_changed)
        type_layout.addWidget(self.solution_type)
        
        main_layout.addWidget(type_group)
        
        # Parâmetros da solução
        params_group = QGroupBox("Parâmetros da Solução")
        params_layout = QFormLayout(params_group)
        
        self.concentration = QDoubleSpinBox()
        self.concentration.setRange(1e-15, 10.0)
        self.concentration.setDecimals(10)
        self.concentration.setValue(0.1)
        self.concentration.setSuffix(" M")
        params_layout.addRow("Concentração:", self.concentration)
        
        self.ka_value = QDoubleSpinBox()
        self.ka_value.setRange(1e-15, 1.0)
        self.ka_value.setDecimals(15)
        self.ka_value.setValue(1.8e-5)
        self.ka_value.setVisible(False)
        params_layout.addRow("Ka:", self.ka_value)
        
        self.kb_value = QDoubleSpinBox()
        self.kb_value.setRange(1e-15, 1.0)
        self.kb_value.setDecimals(15)
        self.kb_value.setValue(1.8e-5)
        self.kb_value.setVisible(False)
        params_layout.addRow("Kb:", self.kb_value)
        
        main_layout.addWidget(params_group)
        
        # Botão de cálculo
        calc_btn = QPushButton("Calcular pH")
        calc_btn.clicked.connect(self.calculate_ph)
        main_layout.addWidget(calc_btn)
        
        # Resultados
        results_group = QGroupBox("Resultados")
        results_layout = QVBoxLayout(results_group)
        
        self.ph_results = QTextEdit()
        self.ph_results.setReadOnly(True)
        self.ph_results.setMaximumHeight(200)
        self.ph_results.setStyleSheet("font-family: monospace; font-size: 12px;")
        results_layout.addWidget(self.ph_results)
        
        main_layout.addWidget(results_group)
        
        # Gráfico da escala de pH
        scale_group = QGroupBox("Escala de pH Visual")
        scale_layout = QVBoxLayout(scale_group)
        
        self.figure_ph_scale = Figure(figsize=(10, 3))
        self.canvas_ph_scale = FigureCanvas(self.figure_ph_scale)
        scale_layout.addWidget(self.canvas_ph_scale)
        
        main_layout.addWidget(scale_group)
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
        return widget
    
    def create_buffer_systems_tab(self):
        """Cria a aba de sistemas tampão."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Teoria de tampões
        theory_group = QGroupBox("Sistemas Tampão")
        theory_layout = QVBoxLayout(theory_group)
        
        theory_text = QLabel("""
        <b>Sistemas Tampão:</b> Soluções que resistem a mudanças de pH quando pequenas quantidades de ácido ou base são adicionadas.
        
        <b>Equação de Henderson-Hasselbalch:</b>
        • pH = pKa + log([A⁻]/[HA])
        • Válida para tampões ácido fraco/base conjugada
        
        <b>Características:</b>
        • Máxima capacidade tamponante quando pH = pKa
        • Faixa efetiva: pKa ± 1
        • Importante em sistemas biológicos
        """)
        theory_text.setWordWrap(True)
        theory_text.setStyleSheet("padding: 10px; background-color: #fff3e0; border-radius: 5px;")
        theory_layout.addWidget(theory_text)
        
        main_layout.addWidget(theory_group)
        
        # Calculadora de tampão
        buffer_group = QGroupBox("Calculadora de Tampão")
        buffer_layout = QFormLayout(buffer_group)
        
        self.buffer_pka = QDoubleSpinBox()
        self.buffer_pka.setRange(0.0, 14.0)
        self.buffer_pka.setValue(4.75)  # Ácido acético
        self.buffer_pka.setDecimals(2)
        buffer_layout.addRow("pKa do ácido:", self.buffer_pka)
        
        self.acid_conc = QDoubleSpinBox()
        self.acid_conc.setRange(0.001, 10.0)
        self.acid_conc.setValue(0.1)
        self.acid_conc.setDecimals(4)
        self.acid_conc.setSuffix(" M")
        buffer_layout.addRow("Concentração do ácido:", self.acid_conc)
        
        self.salt_conc = QDoubleSpinBox()
        self.salt_conc.setRange(0.001, 10.0)
        self.salt_conc.setValue(0.1)
        self.salt_conc.setDecimals(4)
        self.salt_conc.setSuffix(" M")
        buffer_layout.addRow("Concentração da base conjugada:", self.salt_conc)
        
        main_layout.addWidget(buffer_group)
        
        # Botão de cálculo
        calc_buffer_btn = QPushButton("Calcular pH do Tampão")
        calc_buffer_btn.clicked.connect(self.calculate_buffer_ph)
        main_layout.addWidget(calc_buffer_btn)
        
        # Resultados do tampão
        buffer_results_group = QGroupBox("Resultados do Tampão")
        buffer_results_layout = QVBoxLayout(buffer_results_group)
        
        self.buffer_results = QTextEdit()
        self.buffer_results.setReadOnly(True)
        self.buffer_results.setMaximumHeight(200)
        self.buffer_results.setStyleSheet("font-family: monospace; font-size: 11px;")
        buffer_results_layout.addWidget(self.buffer_results)
        
        main_layout.addWidget(buffer_results_group)
        
        # Gráfico de capacidade tamponante
        capacity_group = QGroupBox("Capacidade Tamponante")
        capacity_layout = QVBoxLayout(capacity_group)
        
        self.figure_buffer = Figure(figsize=(10, 6))
        self.canvas_buffer = FigureCanvas(self.figure_buffer)
        capacity_layout.addWidget(self.canvas_buffer)
        
        plot_capacity_btn = QPushButton("Plotar Capacidade Tamponante")
        plot_capacity_btn.clicked.connect(self.plot_buffer_capacity)
        capacity_layout.addWidget(plot_capacity_btn)
        
        main_layout.addWidget(capacity_group)
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
        return widget
    
    def create_titration_curves_tab(self):
        """Cria a aba de curvas de titulação."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Informações sobre titulação
        info_group = QGroupBox("Curvas de Titulação")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel("""
        <b>Titulação:</b> Técnica analítica para determinar concentração de uma solução através da reação com solução de concentração conhecida.
        
        <b>Tipos de titulação:</b>
        • Ácido forte vs Base forte
        • Ácido fraco vs Base forte
        • Base fraca vs Ácido forte
        • Ácido poliprótico
        
        <b>Ponto de equivalência:</b> Ponto onde moles de titulante = moles de analito
        """)
        info_text.setWordWrap(True)
        info_text.setStyleSheet("padding: 10px; background-color: #e3f2fd; border-radius: 5px;")
        info_layout.addWidget(info_text)
        
        main_layout.addWidget(info_group)
        
        # Parâmetros da titulação
        titration_group = QGroupBox("Parâmetros da Titulação")
        titration_layout = QFormLayout(titration_group)
        
        self.titration_type = QComboBox()
        self.titration_type.addItems([
            "Ácido forte vs Base forte",
            "Ácido fraco vs Base forte",
            "Base fraca vs Ácido forte"
        ])
        titration_layout.addRow("Tipo de titulação:", self.titration_type)
        
        self.analyte_conc = QDoubleSpinBox()
        self.analyte_conc.setRange(0.001, 2.0)
        self.analyte_conc.setValue(0.1)
        self.analyte_conc.setDecimals(4)
        self.analyte_conc.setSuffix(" M")
        titration_layout.addRow("Concentração do analito:", self.analyte_conc)
        
        self.titrant_conc = QDoubleSpinBox()
        self.titrant_conc.setRange(0.001, 2.0)
        self.titrant_conc.setValue(0.1)
        self.titrant_conc.setDecimals(4)
        self.titrant_conc.setSuffix(" M")
        titration_layout.addRow("Concentração do titulante:", self.titrant_conc)
        
        self.analyte_volume = QDoubleSpinBox()
        self.analyte_volume.setRange(1.0, 1000.0)
        self.analyte_volume.setValue(25.0)
        self.analyte_volume.setSuffix(" mL")
        titration_layout.addRow("Volume do analito:", self.analyte_volume)
        
        self.analyte_ka = QDoubleSpinBox()
        self.analyte_ka.setRange(1e-15, 1.0)
        self.analyte_ka.setDecimals(15)
        self.analyte_ka.setValue(1.8e-5)
        titration_layout.addRow("Ka do ácido fraco:", self.analyte_ka)
        
        main_layout.addWidget(titration_group)
        
        # Botão para gerar curva
        generate_curve_btn = QPushButton("Gerar Curva de Titulação")
        generate_curve_btn.clicked.connect(self.generate_titration_curve)
        main_layout.addWidget(generate_curve_btn)
        
        # Gráfico da titulação
        curve_group = QGroupBox("Curva de Titulação")
        curve_layout = QVBoxLayout(curve_group)
        
        self.figure_titration = Figure(figsize=(10, 6))
        self.canvas_titration = FigureCanvas(self.figure_titration)
        curve_layout.addWidget(self.canvas_titration)
        
        main_layout.addWidget(curve_group)
        
        # Análise da titulação
        analysis_group = QGroupBox("Análise da Titulação")
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.titration_analysis = QTextEdit()
        self.titration_analysis.setReadOnly(True)
        self.titration_analysis.setMaximumHeight(150)
        self.titration_analysis.setStyleSheet("font-family: monospace; font-size: 11px;")
        analysis_layout.addWidget(self.titration_analysis)
        
        main_layout.addWidget(analysis_group)
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
        return widget
    
    def create_solution_preparation_tab(self):
        """Cria a aba de preparo de soluções."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Diluições
        dilution_group = QGroupBox("Cálculo de Diluições")
        dilution_layout = QFormLayout(dilution_group)
        
        # Fórmula: C1V1 = C2V2
        formula_label = QLabel("<b>Fórmula:</b> C₁V₁ = C₂V₂")
        formula_label.setStyleSheet("padding: 5px; background-color: #f5f5f5;")
        dilution_layout.addRow("", formula_label)
        
        self.initial_conc = QDoubleSpinBox()
        self.initial_conc.setRange(0.001, 20.0)
        self.initial_conc.setValue(1.0)
        self.initial_conc.setDecimals(4)
        self.initial_conc.setSuffix(" M")
        dilution_layout.addRow("Concentração inicial (C₁):", self.initial_conc)
        
        self.initial_volume = QDoubleSpinBox()
        self.initial_volume.setRange(0.1, 10000.0)
        self.initial_volume.setValue(10.0)
        self.initial_volume.setSuffix(" mL")
        dilution_layout.addRow("Volume inicial (V₁):", self.initial_volume)
        
        self.final_conc = QDoubleSpinBox()
        self.final_conc.setRange(0.001, 20.0)
        self.final_conc.setValue(0.1)
        self.final_conc.setDecimals(4)
        self.final_conc.setSuffix(" M")
        dilution_layout.addRow("Concentração final (C₂):", self.final_conc)
        
        calc_dilution_btn = QPushButton("Calcular Volume Final")
        dilution_layout.addRow("", calc_dilution_btn)
        calc_dilution_btn.clicked.connect(self.calculate_dilution)
        
        self.dilution_result = QLabel()
        self.dilution_result.setStyleSheet("font-weight: bold; padding: 10px; background-color: #e8f5e8; border-radius: 5px;")
        dilution_layout.addRow("Resultado:", self.dilution_result)
        
        main_layout.addWidget(dilution_group)
        
        # Preparo de soluções molares
        molar_group = QGroupBox("Preparo de Soluções Molares")
        molar_layout = QFormLayout(molar_group)
        
        self.compound_name = QLineEdit()
        self.compound_name.setPlaceholderText("Ex: NaCl, H₂SO₄, KOH")
        molar_layout.addRow("Composto:", self.compound_name)
        
        self.molar_mass = QDoubleSpinBox()
        self.molar_mass.setRange(1.0, 1000.0)
        self.molar_mass.setValue(58.44)  # NaCl
        self.molar_mass.setSuffix(" g/mol")
        molar_layout.addRow("Massa molar:", self.molar_mass)
        
        self.desired_molarity = QDoubleSpinBox()
        self.desired_molarity.setRange(0.001, 20.0)
        self.desired_molarity.setValue(1.0)
        self.desired_molarity.setDecimals(4)
        self.desired_molarity.setSuffix(" M")
        molar_layout.addRow("Molaridade desejada:", self.desired_molarity)
        
        self.solution_volume = QDoubleSpinBox()
        self.solution_volume.setRange(1.0, 10000.0)
        self.solution_volume.setValue(1000.0)
        self.solution_volume.setSuffix(" mL")
        molar_layout.addRow("Volume da solução:", self.solution_volume)
        
        calc_mass_btn = QPushButton("Calcular Massa Necessária")
        molar_layout.addRow("", calc_mass_btn)
        calc_mass_btn.clicked.connect(self.calculate_mass_needed)
        
        self.mass_result = QLabel()
        self.mass_result.setStyleSheet("font-weight: bold; padding: 10px; background-color: #fff3e0; border-radius: 5px;")
        molar_layout.addRow("Massa necessária:", self.mass_result)
        
        main_layout.addWidget(molar_group)
        
        # Conversões de concentração
        conversion_group = QGroupBox("Conversões de Concentração")
        conversion_layout = QFormLayout(conversion_group)
        
        self.conv_molarity = QDoubleSpinBox()
        self.conv_molarity.setRange(0.001, 20.0)
        self.conv_molarity.setValue(1.0)
        self.conv_molarity.setDecimals(4)
        self.conv_molarity.setSuffix(" M")
        conversion_layout.addRow("Molaridade:", self.conv_molarity)
        
        self.conv_molar_mass = QDoubleSpinBox()
        self.conv_molar_mass.setRange(1.0, 1000.0)
        self.conv_molar_mass.setValue(58.44)
        self.conv_molar_mass.setSuffix(" g/mol")
        conversion_layout.addRow("Massa molar:", self.conv_molar_mass)
        
        self.solution_density = QDoubleSpinBox()
        self.solution_density.setRange(0.1, 5.0)
        self.solution_density.setValue(1.0)
        self.solution_density.setDecimals(3)
        self.solution_density.setSuffix(" g/mL")
        conversion_layout.addRow("Densidade da solução:", self.solution_density)
        
        convert_btn = QPushButton("Converter Concentrações")
        conversion_layout.addRow("", convert_btn)
        convert_btn.clicked.connect(self.convert_concentrations)
        
        self.conversion_results = QTextEdit()
        self.conversion_results.setReadOnly(True)
        self.conversion_results.setMaximumHeight(150)
        self.conversion_results.setStyleSheet("font-family: monospace; font-size: 11px;")
        conversion_layout.addRow("Resultados:", self.conversion_results)
        
        main_layout.addWidget(conversion_group)
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
        return widget
    
    def create_indicators_tab(self):
        """Cria a aba de indicadores de pH."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Informações sobre indicadores
        info_group = QGroupBox("Indicadores de pH")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel("""
        <b>Indicadores de pH:</b> Substâncias que mudam de cor dependendo do pH da solução.
        
        <b>Características:</b>
        • Ácidos ou bases fracas
        • Diferentes cores em formas protonada e desprotonada
        • Faixa de viragem característica
        • Utilizados para determinar pontos finais em titulações
        """)
        info_text.setWordWrap(True)
        info_text.setStyleSheet("padding: 10px; background-color: #f3e5f5; border-radius: 5px;")
        info_layout.addWidget(info_text)
        
        main_layout.addWidget(info_group)
        
        # Tabela de indicadores comuns
        indicators_group = QGroupBox("Indicadores Comuns")
        indicators_layout = QVBoxLayout(indicators_group)
        
        # Dados dos indicadores
        indicators_text = QTextEdit()
        indicators_text.setReadOnly(True)
        indicators_text.setMaximumHeight(300)
        
        indicators_data = """INDICADORES DE pH MAIS UTILIZADOS

Indicador                | Faixa de pH | Cor Ácida    | Cor Básica
========================|=============|==============|==============
Azul de timol           | 1,2 - 2,8   | Vermelho     | Amarelo
Alaranjado de metila    | 3,1 - 4,4   | Vermelho     | Amarelo
Verde de bromocresol    | 3,8 - 5,4   | Amarelo      | Azul
Vermelho de metila      | 4,2 - 6,3   | Vermelho     | Amarelo
Azul de bromotimol      | 6,0 - 7,6   | Amarelo      | Azul
Fenolftaleína          | 8,0 - 10,0  | Incolor      | Rosa/Magenta
Timolftaleína          | 9,3 - 10,5  | Incolor      | Azul

APLICAÇÕES:
• Alaranjado de metila: Titulações de ácidos fortes
• Fenolftaleína: Titulações de bases fortes
• Azul de bromotimol: Próximo ao pH neutro
• Verde de bromocresol: Faixa ácida moderada
"""
        
        indicators_text.setText(indicators_data)
        indicators_text.setStyleSheet("font-family: monospace; font-size: 10px;")
        indicators_layout.addWidget(indicators_text)
        
        main_layout.addWidget(indicators_group)
        
        # Simulador de cores
        color_group = QGroupBox("Simulador de Cores dos Indicadores")
        color_layout = QVBoxLayout(color_group)
        
        # Seletor de indicador
        indicator_selector_layout = QFormLayout()
        
        self.indicator_choice = QComboBox()
        self.indicator_choice.addItems([
            "Azul de timol (1,2-2,8)",
            "Alaranjado de metila (3,1-4,4)",
            "Verde de bromocresol (3,8-5,4)",
            "Vermelho de metila (4,2-6,3)",
            "Azul de bromotimol (6,0-7,6)",
            "Fenolftaleína (8,0-10,0)",
            "Timolftaleína (9,3-10,5)"
        ])
        indicator_selector_layout.addRow("Indicador:", self.indicator_choice)
        
        self.test_ph = QDoubleSpinBox()
        self.test_ph.setRange(0.0, 14.0)
        self.test_ph.setValue(7.0)
        self.test_ph.setDecimals(1)
        indicator_selector_layout.addRow("pH da solução:", self.test_ph)
        
        color_layout.addLayout(indicator_selector_layout)
        
        # Botão para simular
        simulate_color_btn = QPushButton("Simular Cor do Indicador")
        simulate_color_btn.clicked.connect(self.simulate_indicator_color)
        color_layout.addWidget(simulate_color_btn)
        
        # Resultado da simulação
        self.color_result = QLabel()
        self.color_result.setStyleSheet("font-size: 14px; font-weight: bold; padding: 20px; border-radius: 10px; text-align: center;")
        self.color_result.setAlignment(Qt.AlignCenter)
        color_layout.addWidget(self.color_result)
        
        main_layout.addWidget(color_group)
        
        # Gráfico de faixas de viragem
        ranges_group = QGroupBox("Faixas de Viragem dos Indicadores")
        ranges_layout = QVBoxLayout(ranges_group)
        
        self.figure_indicators = Figure(figsize=(12, 6))
        self.canvas_indicators = FigureCanvas(self.figure_indicators)
        ranges_layout.addWidget(self.canvas_indicators)
        
        plot_ranges_btn = QPushButton("Plotar Faixas de Viragem")
        plot_ranges_btn.clicked.connect(self.plot_indicator_ranges)
        ranges_layout.addWidget(plot_ranges_btn)
        
        main_layout.addWidget(ranges_group)
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
        return widget
    
    # Métodos de implementação
    def on_solution_type_changed(self, solution_type):
        """Atualiza a interface baseado no tipo de solução."""
        self.ka_value.setVisible("Ácido Fraco" in solution_type)
        self.kb_value.setVisible("Base Fraca" in solution_type)
    
    def calculate_ph(self):
        """Calcula o pH baseado no tipo de solução."""
        solution_type = self.solution_type.currentText()
        concentration = self.concentration.value()
        
        if solution_type == "Ácido Forte":
            if concentration > 0:
                h_conc = concentration
                ph = -math.log10(h_conc)
                oh_conc = 1e-14 / h_conc
                poh = -math.log10(oh_conc)
            else:
                ph = 7.0
                poh = 7.0
                h_conc = 1e-7
                oh_conc = 1e-7
                
        elif solution_type == "Base Forte":
            if concentration > 0:
                oh_conc = concentration
                poh = -math.log10(oh_conc)
                h_conc = 1e-14 / oh_conc
                ph = -math.log10(h_conc)
            else:
                ph = 7.0
                poh = 7.0
                h_conc = 1e-7
                oh_conc = 1e-7
                
        elif solution_type == "Ácido Fraco":
            ka = self.ka_value.value()
            # Aproximação para ácidos fracos: [H+] = sqrt(Ka * C)
            h_conc = math.sqrt(ka * concentration)
            ph = -math.log10(h_conc)
            oh_conc = 1e-14 / h_conc
            poh = -math.log10(oh_conc)
            
        elif solution_type == "Base Fraca":
            kb = self.kb_value.value()
            # Aproximação para bases fracas: [OH-] = sqrt(Kb * C)
            oh_conc = math.sqrt(kb * concentration)
            poh = -math.log10(oh_conc)
            h_conc = 1e-14 / oh_conc
            ph = -math.log10(h_conc)
            
        elif solution_type == "Concentração de H⁺":
            h_conc = concentration
            ph = -math.log10(h_conc)
            oh_conc = 1e-14 / h_conc
            poh = -math.log10(oh_conc)
            
        elif solution_type == "Concentração de OH⁻":
            oh_conc = concentration
            poh = -math.log10(oh_conc)
            h_conc = 1e-14 / oh_conc
            ph = -math.log10(h_conc)
        
        # Formatação dos resultados
        result_text = f"RESULTADOS DO CÁLCULO DE pH\n"
        result_text += f"{'='*35}\n\n"
        result_text += f"Tipo de solução: {solution_type}\n"
        result_text += f"Concentração: {concentration:.6f} M\n\n"
        result_text += f"pH = {ph:.3f}\n"
        result_text += f"pOH = {poh:.3f}\n"
        result_text += f"[H⁺] = {h_conc:.2e} M\n"
        result_text += f"[OH⁻] = {oh_conc:.2e} M\n\n"
        
        # Classificação
        if ph < 7:
            classification = "ÁCIDA"
            color = "red"
        elif ph > 7:
            classification = "BÁSICA"
            color = "blue"
        else:
            classification = "NEUTRA"
            color = "green"
        
        result_text += f"Classificação: {classification}\n"
        
        # Verificação
        result_text += f"\nVerificação: pH + pOH = {ph + poh:.3f}\n"
        result_text += f"Kw = [H⁺][OH⁻] = {h_conc * oh_conc:.2e}"
        
        self.ph_results.setText(result_text)
        
        # Atualizar escala visual
        self.plot_ph_scale(ph)
    
    def plot_ph_scale(self, ph_value):
        """Plota a escala visual de pH."""
        self.figure_ph_scale.clear()
        ax = self.figure_ph_scale.add_subplot(111)
        
        # Criar escala de pH
        ph_range = np.linspace(0, 14, 15)
        colors = ['red', 'red', 'orange', 'orange', 'yellow', 'yellow', 'yellow', 
                 'green', 'lightblue', 'lightblue', 'blue', 'blue', 'purple', 'purple', 'purple']
        
        # Plotar barras coloridas
        for i, (ph, color) in enumerate(zip(ph_range, colors)):
            ax.barh(0, 1, left=ph, height=0.5, color=color, alpha=0.7, edgecolor='black')
            ax.text(ph + 0.5, 0, str(int(ph)), ha='center', va='center', fontweight='bold')
        
        # Marcar o pH calculado
        ax.axvline(x=ph_value, color='red', linewidth=4, label=f'pH = {ph_value:.2f}')
        ax.scatter([ph_value], [0], color='red', s=200, marker='v', zorder=5)
        
        ax.set_xlim(0, 14)
        ax.set_ylim(-0.5, 0.5)
        ax.set_xlabel('pH')
        ax.set_title('Escala de pH')
        ax.set_yticks([])
        ax.legend()
        
        # Adicionar labels
        ax.text(2, -0.3, 'ÁCIDO', ha='center', fontweight='bold', color='red')
        ax.text(7, -0.3, 'NEUTRO', ha='center', fontweight='bold', color='green')
        ax.text(12, -0.3, 'BÁSICO', ha='center', fontweight='bold', color='blue')
        
        self.figure_ph_scale.tight_layout()
        self.canvas_ph_scale.draw()
    
    def calculate_buffer_ph(self):
        """Calcula o pH de um sistema tampão."""
        pka = self.buffer_pka.value()
        acid_conc = self.acid_conc.value()
        salt_conc = self.salt_conc.value()
        
        # Equação de Henderson-Hasselbalch
        ph = pka + math.log10(salt_conc / acid_conc)
        
        # Cálculos adicionais
        ka = 10**(-pka)
        total_conc = acid_conc + salt_conc
        ionic_strength = 0.5 * total_conc  # Aproximação
        
        result_text = f"CÁLCULO DO SISTEMA TAMPÃO\n"
        result_text += f"{'='*35}\n\n"
        result_text += f"Equação de Henderson-Hasselbalch:\n"
        result_text += f"pH = pKa + log([A⁻]/[HA])\n"
        result_text += f"pH = {pka} + log({salt_conc}/{acid_conc})\n"
        result_text += f"pH = {pka} + {math.log10(salt_conc / acid_conc):.3f}\n\n"
        result_text += f"RESULTADOS:\n"
        result_text += f"pH do tampão: {ph:.3f}\n"
        result_text += f"pKa do ácido: {pka}\n"
        result_text += f"Ka = {ka:.2e}\n"
        result_text += f"Razão [A⁻]/[HA]: {salt_conc/acid_conc:.3f}\n"
        result_text += f"Concentração total: {total_conc:.3f} M\n\n"
        
        # Eficiência do tampão
        efficiency = 1 / (1 + abs(ph - pka))
        result_text += f"AVALIAÇÃO DO TAMPÃO:\n"
        result_text += f"Eficiência relativa: {efficiency:.3f}\n"
        if abs(ph - pka) <= 1:
            result_text += f"✓ Tampão eficiente (|pH - pKa| ≤ 1)\n"
        else:
            result_text += f"⚠ Tampão pouco eficiente (|pH - pKa| > 1)\n"
        
        result_text += f"Faixa efetiva: {pka-1:.1f} - {pka+1:.1f}\n"
        
        self.buffer_results.setText(result_text)
    
    def plot_buffer_capacity(self):
        """Plota a capacidade tamponante vs pH."""
        pka = self.buffer_pka.value()
        
        self.figure_buffer.clear()
        ax = self.figure_buffer.add_subplot(111)
        
        # Gerar faixa de pH
        ph_range = np.linspace(pka - 3, pka + 3, 100)
        
        # Calcular capacidade tamponante (β)
        # β = 2.303 * C * Ka * [H+] / (Ka + [H+])²
        ka = 10**(-pka)
        h_conc = 10**(-ph_range)
        
        # Assumindo concentração total de 0.1 M
        c_total = 0.1
        beta = 2.303 * c_total * ka * h_conc / (ka + h_conc)**2
        
        # Plotar
        ax.plot(ph_range, beta, 'b-', linewidth=3, label='Capacidade Tamponante')
        ax.axvline(x=pka, color='red', linestyle='--', linewidth=2, label=f'pKa = {pka}')
        ax.axhline(y=max(beta)/2, color='orange', linestyle=':', alpha=0.7)
        
        ax.set_xlabel('pH')
        ax.set_ylabel('Capacidade Tamponante (β)')
        ax.set_title('Capacidade Tamponante vs pH')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Marcar pontos importantes
        max_beta_idx = np.argmax(beta)
        ax.scatter([ph_range[max_beta_idx]], [beta[max_beta_idx]], 
                  color='red', s=100, zorder=5, label='Máxima capacidade')
        
        self.figure_buffer.tight_layout()
        self.canvas_buffer.draw()
    
    def generate_titration_curve(self):
        """Gera curva de titulação."""
        titration_type = self.titration_type.currentText()
        analyte_conc = self.analyte_conc.value()
        titrant_conc = self.titrant_conc.value()
        analyte_vol = self.analyte_volume.value() / 1000  # Converter para L
        ka = self.analyte_ka.value()
        
        # Volume de equivalência
        equiv_volume = (analyte_conc * analyte_vol) / titrant_conc * 1000  # mL
        
        # Gerar volumes de titulante
        volumes = np.linspace(0, equiv_volume * 2, 200)
        ph_values = []
        
        for vol in volumes:
            vol_L = vol / 1000  # Converter para L
            total_vol = analyte_vol + vol_L
            
            # Moles de analito e titulante
            moles_analyte = analyte_conc * analyte_vol
            moles_titrant = titrant_conc * vol_L
            
            if titration_type == "Ácido forte vs Base forte":
                if moles_titrant < moles_analyte:
                    # Antes do ponto de equivalência
                    excess_acid = (moles_analyte - moles_titrant) / total_vol
                    ph = -math.log10(excess_acid)
                elif moles_titrant > moles_analyte:
                    # Após o ponto de equivalência
                    excess_base = (moles_titrant - moles_analyte) / total_vol
                    poh = -math.log10(excess_base)
                    ph = 14 - poh
                else:
                    # Ponto de equivalência
                    ph = 7.0
                    
            elif titration_type == "Ácido fraco vs Base forte":
                if moles_titrant < moles_analyte:
                    # Sistema tampão
                    conc_acid = (moles_analyte - moles_titrant) / total_vol
                    conc_salt = moles_titrant / total_vol
                    if conc_acid > 0:
                        ph = -math.log10(ka) + math.log10(conc_salt / conc_acid)
                    else:
                        ph = 7.0
                elif moles_titrant > moles_analyte:
                    # Excesso de base
                    excess_base = (moles_titrant - moles_analyte) / total_vol
                    poh = -math.log10(excess_base)
                    ph = 14 - poh
                else:
                    # Ponto de equivalência - hidrólise da base conjugada
                    conc_salt = moles_analyte / total_vol
                    kb = 1e-14 / ka
                    oh_conc = math.sqrt(kb * conc_salt)
                    poh = -math.log10(oh_conc)
                    ph = 14 - poh
            
            # Limitação física do pH
            ph = max(0, min(14, ph))
            ph_values.append(ph)
        
        # Plotar curva
        self.figure_titration.clear()
        ax = self.figure_titration.add_subplot(111)
        
        ax.plot(volumes, ph_values, 'b-', linewidth=3, label='Curva de titulação')
        ax.axvline(x=equiv_volume, color='red', linestyle='--', linewidth=2, 
                  label=f'Ponto de equivalência ({equiv_volume:.1f} mL)')
        
        ax.set_xlabel('Volume de titulante (mL)')
        ax.set_ylabel('pH')
        ax.set_title(f'Titulação: {titration_type}')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Marcar ponto de equivalência
        equiv_idx = np.argmin(np.abs(volumes - equiv_volume))
        ax.scatter([equiv_volume], [ph_values[equiv_idx]], 
                  color='red', s=100, zorder=5)
        
        self.figure_titration.tight_layout()
        self.canvas_titration.draw()
        
        # Análise da titulação
        self.analyze_titration(equiv_volume, ph_values[equiv_idx], titration_type)
    
    def analyze_titration(self, equiv_volume, equiv_ph, titration_type):
        """Analisa os resultados da titulação."""
        analysis_text = f"ANÁLISE DA TITULAÇÃO\n"
        analysis_text += f"{'='*30}\n\n"
        analysis_text += f"Tipo: {titration_type}\n"
        analysis_text += f"Volume de equivalência: {equiv_volume:.2f} mL\n"
        analysis_text += f"pH no ponto de equivalência: {equiv_ph:.2f}\n\n"
        
        # Sugestão de indicador
        if equiv_ph < 6:
            indicator = "Alaranjado de metila (3,1-4,4)"
        elif 6 <= equiv_ph <= 8:
            indicator = "Azul de bromotimol (6,0-7,6)"
        else:
            indicator = "Fenolftaleína (8,0-10,0)"
        
        analysis_text += f"Indicador sugerido: {indicator}\n"
        
        self.titration_analysis.setText(analysis_text)
    
    def calculate_dilution(self):
        """Calcula volume final em diluição."""
        c1 = self.initial_conc.value()
        v1 = self.initial_volume.value()
        c2 = self.final_conc.value()
        
        # C1V1 = C2V2 → V2 = C1V1/C2
        v2 = (c1 * v1) / c2
        water_volume = v2 - v1
        
        result_text = f"Volume final (V₂): {v2:.2f} mL\n"
        result_text += f"Água a adicionar: {water_volume:.2f} mL\n"
        result_text += f"Fator de diluição: {v2/v1:.1f}x"
        
        self.dilution_result.setText(result_text)
    
    def calculate_mass_needed(self):
        """Calcula massa necessária para preparo de solução."""
        molar_mass = self.molar_mass.value()
        molarity = self.desired_molarity.value()
        volume = self.solution_volume.value() / 1000  # Converter para L
        
        # n = M × V → m = n × MM
        moles = molarity * volume
        mass = moles * molar_mass
        
        result_text = f"{mass:.4f} g de {self.compound_name.text()}\n"
        result_text += f"Dissolver em água destilada e completar\n"
        result_text += f"o volume para {self.solution_volume.value()} mL"
        
        self.mass_result.setText(result_text)
    
    def convert_concentrations(self):
        """Converte entre diferentes unidades de concentração."""
        molarity = self.conv_molarity.value()
        molar_mass = self.conv_molar_mass.value()
        density = self.solution_density.value()
        
        # Conversões
        molality = molarity / density  # Aproximação
        normality = molarity  # Assumindo 1 equivalente por mol
        mass_percent = (molarity * molar_mass) / (density * 1000) * 100
        g_per_L = molarity * molar_mass
        
        result_text = f"CONVERSÕES DE CONCENTRAÇÃO\n"
        result_text += f"{'='*30}\n\n"
        result_text += f"Molaridade (M): {molarity:.4f} mol/L\n"
        result_text += f"Molalidade (m): {molality:.4f} mol/kg\n"
        result_text += f"Normalidade (N): {normality:.4f} eq/L\n"
        result_text += f"Porcentagem em massa: {mass_percent:.4f}%\n"
        result_text += f"Concentração em g/L: {g_per_L:.4f} g/L\n"
        result_text += f"ppm: {g_per_L * 1000:.0f} ppm"
        
        self.conversion_results.setText(result_text)
    
    def simulate_indicator_color(self):
        """Simula a cor do indicador no pH especificado."""
        indicator = self.indicator_choice.currentText()
        ph = self.test_ph.value()
        
        # Dados dos indicadores (nome, pH_min, pH_max, cor_ácida, cor_básica)
        indicators_data = {
            "Azul de timol (1,2-2,8)": (1.2, 2.8, "Vermelho", "Amarelo", "#FF0000", "#FFFF00"),
            "Alaranjado de metila (3,1-4,4)": (3.1, 4.4, "Vermelho", "Amarelo", "#FF4500", "#FFFF00"),
            "Verde de bromocresol (3,8-5,4)": (3.8, 5.4, "Amarelo", "Azul", "#FFFF00", "#0000FF"),
            "Vermelho de metila (4,2-6,3)": (4.2, 6.3, "Vermelho", "Amarelo", "#FF0000", "#FFFF00"),
            "Azul de bromotimol (6,0-7,6)": (6.0, 7.6, "Amarelo", "Azul", "#FFFF00", "#0000FF"),
            "Fenolftaleína (8,0-10,0)": (8.0, 10.0, "Incolor", "Rosa", "#FFFFFF", "#FF69B4"),
            "Timolftaleína (9,3-10,5)": (9.3, 10.5, "Incolor", "Azul", "#FFFFFF", "#0000FF")
        }
        
        if indicator in indicators_data:
            ph_min, ph_max, color_acid, color_basic, hex_acid, hex_basic = indicators_data[indicator]
            
            if ph < ph_min:
                color_name = color_acid
                color_hex = hex_acid
                state = "Forma ácida"
            elif ph > ph_max:
                color_name = color_basic
                color_hex = hex_basic
                state = "Forma básica"
            else:
                color_name = f"Transição ({color_acid} → {color_basic})"
                # Interpolação de cor na faixa de transição
                ratio = (ph - ph_min) / (ph_max - ph_min)
                color_hex = "#FF8000"  # Cor de transição
                state = "Zona de transição"
            
            result_text = f"pH: {ph:.1f} | Estado: {state}\nCor: {color_name}"
            self.color_result.setText(result_text)
            self.color_result.setStyleSheet(f"background-color: {color_hex}; color: {'white' if color_hex in ['#FF0000', '#0000FF'] else 'black'}; font-size: 14px; font-weight: bold; padding: 20px; border-radius: 10px; text-align: center;")
    
    def plot_indicator_ranges(self):
        """Plota as faixas de viragem dos indicadores."""
        self.figure_indicators.clear()
        ax = self.figure_indicators.add_subplot(111)
        
        # Dados dos indicadores
        indicators = [
            ("Azul de timol", 1.2, 2.8, "#FF0000", "#FFFF00"),
            ("Alaranjado de metila", 3.1, 4.4, "#FF4500", "#FFFF00"),
            ("Verde de bromocresol", 3.8, 5.4, "#FFFF00", "#0000FF"),
            ("Vermelho de metila", 4.2, 6.3, "#FF0000", "#FFFF00"),
            ("Azul de bromotimol", 6.0, 7.6, "#FFFF00", "#0000FF"),
            ("Fenolftaleína", 8.0, 10.0, "#FFFFFF", "#FF69B4"),
            ("Timolftaleína", 9.3, 10.5, "#FFFFFF", "#0000FF")
        ]
        
        for i, (name, ph_min, ph_max, color1, color2) in enumerate(indicators):
            # Plotar faixa
            ax.barh(i, ph_max - ph_min, left=ph_min, height=0.6, 
                   color=color2, alpha=0.7, edgecolor='black')
            
            # Adicionar nome
            ax.text(-0.5, i, name, ha='right', va='center', fontsize=10)
            
            # Adicionar valores de pH
            ax.text(ph_min, i, f'{ph_min}', ha='center', va='bottom', fontsize=8)
            ax.text(ph_max, i, f'{ph_max}', ha='center', va='bottom', fontsize=8)
        
        ax.set_xlim(0, 14)
        ax.set_ylim(-0.5, len(indicators) - 0.5)
        ax.set_xlabel('pH')
        ax.set_title('Faixas de Viragem dos Indicadores de pH')
        ax.set_yticks([])
        ax.grid(True, axis='x', alpha=0.3)
        
        # Adicionar escala de pH no topo
        ax2 = ax.twiny()
        ax2.set_xlim(0, 14)
        ax2.set_xticks(range(0, 15))
        ax2.set_xlabel('Escala de pH')
        
        self.figure_indicators.tight_layout()
        self.canvas_indicators.draw()
