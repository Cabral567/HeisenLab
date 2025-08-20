from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QTextEdit, QPushButton, QLabel, QComboBox, QDoubleSpinBox,
    QScrollArea, QTabWidget, QCheckBox, QSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QSlider
)
import pandas as pd
from scipy import optimize


class InstrumentalMethodsTab(QWidget):
    """Aba para métodos instrumentais de análise química."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface principal."""
        main_layout = QVBoxLayout(self)
        
        # Criar abas internas
        tabs = QTabWidget()
        
        # Aba 1: Espectrofotometria UV-Vis
        tabs.addTab(self.create_uv_vis_tab(), "Espectrofotometria UV-Vis")
        
        # Aba 2: Lei de Beer
        tabs.addTab(self.create_beer_law_tab(), "Lei de Beer")
        
        # Aba 3: Análise Multicomponente
        tabs.addTab(self.create_multicomponent_tab(), "Análise Multicomponente")
        
        # Aba 4: Métodos Cinéticos
        tabs.addTab(self.create_kinetic_methods_tab(), "Métodos Cinéticos")
        
        main_layout.addWidget(tabs)
    
    def create_uv_vis_tab(self):
        """Cria a aba de espectrofotometria UV-Vis."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Informações sobre UV-Vis
        info_group = QGroupBox("Espectrofotometria UV-Visível")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel("""
        <b>Espectrofotometria UV-Vis:</b> Técnica analítica baseada na absorção de radiação eletromagnética.
        
        <b>Princípios fundamentais:</b>
        • Transições eletrônicas em moléculas
        • Lei de Lambert-Beer: A = εbc
        • Comprimento de onda específico para cada composto
        
        <b>Aplicações:</b>
        • Determinação quantitativa de concentrações
        • Análise qualitativa de compostos
        • Cinética de reações
        • Análise de pureza
        """)
        info_text.setWordWrap(True)
        info_text.setStyleSheet("padding: 10px; background-color: #e3f2fd; border-radius: 5px;")
        info_layout.addWidget(info_text)
        
        main_layout.addWidget(info_group)
        
        # Simulador de espectro
        spectrum_group = QGroupBox("Simulador de Espectro UV-Vis")
        spectrum_layout = QVBoxLayout(spectrum_group)
        
        # Parâmetros do espectro
        params_layout = QFormLayout()
        
        self.lambda_max = QDoubleSpinBox()
        self.lambda_max.setRange(200, 800)
        self.lambda_max.setValue(525)
        self.lambda_max.setSuffix(" nm")
        params_layout.addRow("λ máximo:", self.lambda_max)
        
        self.molar_absorptivity = QDoubleSpinBox()
        self.molar_absorptivity.setRange(1, 100000)
        self.molar_absorptivity.setValue(15000)
        self.molar_absorptivity.setSuffix(" L/mol·cm")
        params_layout.addRow("Absortividade molar (ε):", self.molar_absorptivity)
        
        self.concentration = QDoubleSpinBox()
        self.concentration.setRange(0.001, 1.0)
        self.concentration.setValue(0.01)
        self.concentration.setDecimals(4)
        self.concentration.setSuffix(" M")
        params_layout.addRow("Concentração:", self.concentration)
        
        self.path_length = QDoubleSpinBox()
        self.path_length.setRange(0.1, 10.0)
        self.path_length.setValue(1.0)
        self.path_length.setSuffix(" cm")
        params_layout.addRow("Caminho óptico:", self.path_length)
        
        self.bandwidth = QDoubleSpinBox()
        self.bandwidth.setRange(5, 100)
        self.bandwidth.setValue(20)
        self.bandwidth.setSuffix(" nm")
        params_layout.addRow("Largura de banda:", self.bandwidth)
        
        spectrum_layout.addLayout(params_layout)
        
        # Botão para gerar espectro
        generate_btn = QPushButton("Gerar Espectro")
        generate_btn.clicked.connect(self.generate_uv_vis_spectrum)
        spectrum_layout.addWidget(generate_btn)
        
        # Canvas para o espectro
        self.figure_spectrum = Figure(figsize=(10, 6))
        self.canvas_spectrum = FigureCanvas(self.figure_spectrum)
        spectrum_layout.addWidget(self.canvas_spectrum)
        
        main_layout.addWidget(spectrum_group)
        
        # Calculadora de absorbância
        calc_group = QGroupBox("Calculadora de Absorbância")
        calc_layout = QVBoxLayout(calc_group)
        
        calc_form_layout = QFormLayout()
        
        self.calc_epsilon = QDoubleSpinBox()
        self.calc_epsilon.setRange(1, 100000)
        self.calc_epsilon.setValue(15000)
        calc_form_layout.addRow("ε (L/mol·cm):", self.calc_epsilon)
        
        self.calc_conc = QDoubleSpinBox()
        self.calc_conc.setRange(0.001, 1.0)
        self.calc_conc.setValue(0.01)
        self.calc_conc.setDecimals(4)
        calc_form_layout.addRow("Concentração (M):", self.calc_conc)
        
        self.calc_path = QDoubleSpinBox()
        self.calc_path.setRange(0.1, 10.0)
        self.calc_path.setValue(1.0)
        calc_form_layout.addRow("Caminho óptico (cm):", self.calc_path)
        
        calc_layout.addLayout(calc_form_layout)
        
        calc_btn = QPushButton("Calcular Absorbância")
        calc_btn.clicked.connect(self.calculate_absorbance)
        calc_layout.addWidget(calc_btn)
        
        self.absorbance_result = QLabel()
        self.absorbance_result.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px; background-color: #f5f5f5; border-radius: 5px;")
        calc_layout.addWidget(self.absorbance_result)
        
        main_layout.addWidget(calc_group)
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
        return widget
    
    def create_beer_law_tab(self):
        """Cria a aba da Lei de Beer."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Teoria da Lei de Beer
        theory_group = QGroupBox("Lei de Lambert-Beer")
        theory_layout = QVBoxLayout(theory_group)
        
        theory_text = QLabel("""
        <b>Lei de Lambert-Beer:</b> A = ε · b · c
        
        <b>Onde:</b>
        • A = Absorbância (adimensional)
        • ε = Absortividade molar (L/mol·cm)
        • b = Caminho óptico (cm)
        • c = Concentração (mol/L)
        
        <b>Limitações:</b>
        • Válida apenas para soluções diluídas
        • Luz monocromática
        • Ausência de fluorescência
        • Ausência de reações químicas
        
        <b>Desvios:</b>
        • Químicos: Associação, dissociação, formação de complexos
        • Instrumentais: Luz policromática, reflexões
        • Físicos: Espalhamento de luz
        """)
        theory_text.setWordWrap(True)
        theory_text.setStyleSheet("padding: 10px; background-color: #fff3e0; border-radius: 5px;")
        theory_layout.addWidget(theory_text)
        
        main_layout.addWidget(theory_group)
        
        # Simulador da Lei de Beer
        simulator_group = QGroupBox("Simulador da Lei de Beer")
        simulator_layout = QVBoxLayout(simulator_group)
        
        # Parâmetros da simulação
        sim_params_layout = QFormLayout()
        
        self.sim_epsilon = QDoubleSpinBox()
        self.sim_epsilon.setRange(100, 50000)
        self.sim_epsilon.setValue(8500)
        sim_params_layout.addRow("Absortividade molar:", self.sim_epsilon)
        
        self.sim_path_length = QDoubleSpinBox()
        self.sim_path_length.setRange(0.1, 5.0)
        self.sim_path_length.setValue(1.0)
        sim_params_layout.addRow("Caminho óptico (cm):", self.sim_path_length)
        
        self.max_concentration = QDoubleSpinBox()
        self.max_concentration.setRange(0.001, 0.1)
        self.max_concentration.setValue(0.05)
        self.max_concentration.setDecimals(4)
        sim_params_layout.addRow("Concentração máxima (M):", self.max_concentration)
        
        # Checkbox para incluir desvios
        self.include_deviations = QCheckBox("Incluir desvios da linearidade")
        sim_params_layout.addRow("", self.include_deviations)
        
        simulator_layout.addLayout(sim_params_layout)
        
        # Botão para simular
        simulate_btn = QPushButton("Simular Lei de Beer")
        simulate_btn.clicked.connect(self.simulate_beer_law)
        simulator_layout.addWidget(simulate_btn)
        
        # Canvas para a simulação
        self.figure_beer = Figure(figsize=(10, 6))
        self.canvas_beer = FigureCanvas(self.figure_beer)
        simulator_layout.addWidget(self.canvas_beer)
        
        main_layout.addWidget(simulator_group)
        
        # Análise de desvios
        deviations_group = QGroupBox("Análise de Desvios")
        deviations_layout = QVBoxLayout(deviations_group)
        
        self.deviations_text = QTextEdit()
        self.deviations_text.setReadOnly(True)
        self.deviations_text.setMaximumHeight(200)
        self.deviations_text.setStyleSheet("font-family: monospace; font-size: 11px;")
        deviations_layout.addWidget(self.deviations_text)
        
        main_layout.addWidget(deviations_group)
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
        return widget
    
    def create_multicomponent_tab(self):
        """Cria a aba de análise multicomponente."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Teoria
        theory_group = QGroupBox("Análise Multicomponente")
        theory_layout = QVBoxLayout(theory_group)
        
        theory_text = QLabel("""
        <b>Análise Multicomponente:</b> Determinação simultânea de múltiplas espécies absorventes.
        
        <b>Equações fundamentais:</b>
        • A₁ = ε₁₁·b·c₁ + ε₁₂·b·c₂ + ... (em λ₁)
        • A₂ = ε₂₁·b·c₁ + ε₂₂·b·c₂ + ... (em λ₂)
        
        <b>Requisitos:</b>
        • Número de comprimentos de onda ≥ número de componentes
        • Diferenças espectrais significativas
        • Ausência de interferências químicas
        
        <b>Métodos de resolução:</b>
        • Sistema de equações lineares
        • Método dos mínimos quadrados
        • Regressão linear múltipla
        """)
        theory_text.setWordWrap(True)
        theory_text.setStyleSheet("padding: 10px; background-color: #f3e5f5; border-radius: 5px;")
        theory_layout.addWidget(theory_text)
        
        main_layout.addWidget(theory_group)
        
        # Configuração do sistema
        system_group = QGroupBox("Sistema de Dois Componentes")
        system_layout = QVBoxLayout(system_group)
        
        # Parâmetros dos componentes
        comp_layout = QHBoxLayout()
        
        # Componente A
        comp_a_layout = QFormLayout()
        comp_a_group = QGroupBox("Componente A")
        
        self.epsilon_a1 = QDoubleSpinBox()
        self.epsilon_a1.setRange(100, 20000)
        self.epsilon_a1.setValue(5000)
        comp_a_layout.addRow("ε₁ (L/mol·cm):", self.epsilon_a1)
        
        self.epsilon_a2 = QDoubleSpinBox()
        self.epsilon_a2.setRange(100, 20000)
        self.epsilon_a2.setValue(1500)
        comp_a_layout.addRow("ε₂ (L/mol·cm):", self.epsilon_a2)
        
        comp_a_group.setLayout(comp_a_layout)
        comp_layout.addWidget(comp_a_group)
        
        # Componente B
        comp_b_layout = QFormLayout()
        comp_b_group = QGroupBox("Componente B")
        
        self.epsilon_b1 = QDoubleSpinBox()
        self.epsilon_b1.setRange(100, 20000)
        self.epsilon_b1.setValue(2000)
        comp_b_layout.addRow("ε₁ (L/mol·cm):", self.epsilon_b1)
        
        self.epsilon_b2 = QDoubleSpinBox()
        self.epsilon_b2.setRange(100, 20000)
        self.epsilon_b2.setValue(8000)
        comp_b_layout.addRow("ε₂ (L/mol·cm):", self.epsilon_b2)
        
        comp_b_group.setLayout(comp_b_layout)
        comp_layout.addWidget(comp_b_group)
        
        system_layout.addLayout(comp_layout)
        
        # Parâmetros gerais
        general_layout = QFormLayout()
        
        self.multi_path_length = QDoubleSpinBox()
        self.multi_path_length.setRange(0.1, 5.0)
        self.multi_path_length.setValue(1.0)
        general_layout.addRow("Caminho óptico (cm):", self.multi_path_length)
        
        system_layout.addLayout(general_layout)
        
        main_layout.addWidget(system_group)
        
        # Entrada de dados
        data_group = QGroupBox("Dados Experimentais")
        data_layout = QVBoxLayout(data_group)
        
        data_form_layout = QFormLayout()
        
        self.abs_lambda1 = QDoubleSpinBox()
        self.abs_lambda1.setRange(0.001, 3.0)
        self.abs_lambda1.setValue(0.8)
        self.abs_lambda1.setDecimals(4)
        data_form_layout.addRow("Absorbância em λ₁:", self.abs_lambda1)
        
        self.abs_lambda2 = QDoubleSpinBox()
        self.abs_lambda2.setRange(0.001, 3.0)
        self.abs_lambda2.setValue(0.6)
        self.abs_lambda2.setDecimals(4)
        data_form_layout.addRow("Absorbância em λ₂:", self.abs_lambda2)
        
        data_layout.addLayout(data_form_layout)
        
        # Botão para calcular
        calc_multi_btn = QPushButton("Calcular Concentrações")
        calc_multi_btn.clicked.connect(self.calculate_multicomponent)
        data_layout.addWidget(calc_multi_btn)
        
        # Resultado
        self.multicomponent_result = QTextEdit()
        self.multicomponent_result.setReadOnly(True)
        self.multicomponent_result.setMaximumHeight(200)
        self.multicomponent_result.setStyleSheet("font-family: monospace; font-size: 12px;")
        data_layout.addWidget(self.multicomponent_result)
        
        main_layout.addWidget(data_group)
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
        return widget
    
    def create_kinetic_methods_tab(self):
        """Cria a aba de métodos cinéticos."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Teoria
        theory_group = QGroupBox("Métodos Cinéticos de Análise")
        theory_layout = QVBoxLayout(theory_group)
        
        theory_text = QLabel("""
        <b>Métodos Cinéticos:</b> Baseados na velocidade de reações químicas para análise quantitativa.
        
        <b>Vantagens:</b>
        • Alta seletividade
        • Análise de misturas complexas
        • Menor interferência de outros compostos
        
        <b>Tipos de reações:</b>
        • Ordem zero: v = k (velocidade constante)
        • Primeira ordem: v = k[A] (cinética exponencial)
        • Segunda ordem: v = k[A]²
        
        <b>Métodos de medição:</b>
        • Método da velocidade inicial
        • Método de tempo fixo
        • Método integral
        """)
        theory_text.setWordWrap(True)
        theory_text.setStyleSheet("padding: 10px; background-color: #fff8e1; border-radius: 5px;")
        theory_layout.addWidget(theory_text)
        
        main_layout.addWidget(theory_group)
        
        # Simulador cinético
        kinetic_group = QGroupBox("Simulador de Cinética")
        kinetic_layout = QVBoxLayout(kinetic_group)
        
        # Parâmetros da reação
        kinetic_params_layout = QFormLayout()
        
        self.reaction_order = QComboBox()
        self.reaction_order.addItems(["Ordem Zero", "Primeira Ordem", "Segunda Ordem"])
        kinetic_params_layout.addRow("Ordem da reação:", self.reaction_order)
        
        self.rate_constant = QDoubleSpinBox()
        self.rate_constant.setRange(0.001, 10.0)
        self.rate_constant.setValue(0.1)
        self.rate_constant.setDecimals(4)
        kinetic_params_layout.addRow("Constante de velocidade:", self.rate_constant)
        
        self.initial_concentration = QDoubleSpinBox()
        self.initial_concentration.setRange(0.001, 1.0)
        self.initial_concentration.setValue(0.1)
        self.initial_concentration.setDecimals(4)
        kinetic_params_layout.addRow("Concentração inicial (M):", self.initial_concentration)
        
        self.reaction_time = QDoubleSpinBox()
        self.reaction_time.setRange(1, 300)
        self.reaction_time.setValue(60)
        kinetic_params_layout.addRow("Tempo de reação (s):", self.reaction_time)
        
        kinetic_layout.addLayout(kinetic_params_layout)
        
        # Botão para simular
        simulate_kinetic_btn = QPushButton("Simular Cinética")
        simulate_kinetic_btn.clicked.connect(self.simulate_kinetics)
        kinetic_layout.addWidget(simulate_kinetic_btn)
        
        # Canvas para cinética
        self.figure_kinetic = Figure(figsize=(10, 6))
        self.canvas_kinetic = FigureCanvas(self.figure_kinetic)
        kinetic_layout.addWidget(self.canvas_kinetic)
        
        main_layout.addWidget(kinetic_group)
        
        # Análise de dados cinéticos
        analysis_group = QGroupBox("Análise de Dados Cinéticos")
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.kinetic_results = QTextEdit()
        self.kinetic_results.setReadOnly(True)
        self.kinetic_results.setMaximumHeight(200)
        self.kinetic_results.setStyleSheet("font-family: monospace; font-size: 11px;")
        analysis_layout.addWidget(self.kinetic_results)
        
        main_layout.addWidget(analysis_group)
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
        return widget
    
    # Métodos de implementação
    def generate_uv_vis_spectrum(self):
        """Gera um espectro UV-Vis simulado."""
        lambda_max = self.lambda_max.value()
        epsilon = self.molar_absorptivity.value()
        concentration = self.concentration.value()
        path_length = self.path_length.value()
        bandwidth = self.bandwidth.value()
        
        # Gerar comprimentos de onda
        wavelengths = np.linspace(200, 800, 600)
        
        # Função gaussiana para simular banda de absorção
        def gaussian_band(x, center, amplitude, width):
            return amplitude * np.exp(-0.5 * ((x - center) / width) ** 2)
        
        # Calcular absorção máxima pela Lei de Beer
        max_absorbance = epsilon * concentration * path_length
        
        # Gerar espectro com banda gaussiana
        absorbances = gaussian_band(wavelengths, lambda_max, max_absorbance, bandwidth)
        
        # Adicionar ruído realista
        noise = np.random.normal(0, max_absorbance * 0.01, len(wavelengths))
        absorbances += noise
        
        # Garantir que não há valores negativos
        absorbances = np.maximum(absorbances, 0)
        
        # Plotar espectro
        self.figure_spectrum.clear()
        ax = self.figure_spectrum.add_subplot(111)
        
        ax.plot(wavelengths, absorbances, 'b-', linewidth=2)
        ax.axvline(x=lambda_max, color='red', linestyle='--', alpha=0.7, label=f'λ máx = {lambda_max} nm')
        ax.axhline(y=max_absorbance, color='red', linestyle='--', alpha=0.7, label=f'A máx = {max_absorbance:.3f}')
        
        ax.set_xlabel('Comprimento de onda (nm)')
        ax.set_ylabel('Absorbância')
        ax.set_title('Espectro UV-Visível Simulado')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Destacar regiões espectrais
        ax.axvspan(200, 400, alpha=0.1, color='purple', label='UV')
        ax.axvspan(400, 700, alpha=0.1, color='yellow', label='Visível')
        
        self.figure_spectrum.tight_layout()
        self.canvas_spectrum.draw()
    
    def calculate_absorbance(self):
        """Calcula a absorbância usando a Lei de Beer."""
        epsilon = self.calc_epsilon.value()
        concentration = self.calc_conc.value()
        path_length = self.calc_path.value()
        
        absorbance = epsilon * concentration * path_length
        transmittance = 10 ** (-absorbance)
        percent_transmittance = transmittance * 100
        
        result_text = f"""
        <b>Resultados do Cálculo:</b><br>
        Absorbância (A) = {absorbance:.4f}<br>
        Transmitância (T) = {transmittance:.4f}<br>
        % Transmitância = {percent_transmittance:.2f}%<br><br>
        <b>Interpretação:</b><br>
        • A = ε × b × c = {epsilon} × {path_length} × {concentration}<br>
        • T = 10<sup>-A</sup> = 10<sup>-{absorbance:.4f}</sup><br>
        • %T = T × 100%
        """
        
        self.absorbance_result.setText(result_text)
    
    def simulate_beer_law(self):
        """Simula o comportamento da Lei de Beer."""
        epsilon = self.sim_epsilon.value()
        path_length = self.sim_path_length.value()
        max_conc = self.max_concentration.value()
        include_deviations = self.include_deviations.isChecked()
        
        # Gerar concentrações
        concentrations = np.linspace(0, max_conc, 50)
        
        # Calcular absorbâncias teóricas
        absorbances_theoretical = epsilon * path_length * concentrations
        
        # Calcular absorbâncias com possíveis desvios
        if include_deviations:
            # Simular desvios por concentração alta (associação molecular)
            deviation_factor = 1 - 0.3 * (concentrations / max_conc) ** 2
            absorbances_real = absorbances_theoretical * deviation_factor
            
            # Adicionar ruído experimental
            noise = np.random.normal(0, 0.02, len(concentrations))
            absorbances_real += noise
        else:
            absorbances_real = absorbances_theoretical
            # Apenas ruído experimental mínimo
            noise = np.random.normal(0, 0.005, len(concentrations))
            absorbances_real += noise
        
        # Plotar resultados
        self.figure_beer.clear()
        ax = self.figure_beer.add_subplot(111)
        
        ax.plot(concentrations, absorbances_theoretical, 'r-', linewidth=2, label='Lei de Beer (teórica)')
        ax.scatter(concentrations, absorbances_real, alpha=0.7, s=30, label='Dados experimentais')
        
        # Ajuste linear para os dados "experimentais"
        coeffs = np.polyfit(concentrations, absorbances_real, 1)
        fit_line = np.polyval(coeffs, concentrations)
        ax.plot(concentrations, fit_line, 'g--', linewidth=2, label=f'Ajuste linear (R² = {np.corrcoef(concentrations, absorbances_real)[0,1]**2:.4f})')
        
        ax.set_xlabel('Concentração (mol/L)')
        ax.set_ylabel('Absorbância')
        ax.set_title('Simulação da Lei de Beer')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Análise de desvios
        if include_deviations:
            deviations = ((absorbances_real - absorbances_theoretical) / absorbances_theoretical) * 100
            ax2 = ax.twinx()
            ax2.plot(concentrations, deviations, 'orange', alpha=0.7, linewidth=2)
            ax2.set_ylabel('Desvio (%)', color='orange')
            ax2.tick_params(axis='y', labelcolor='orange')
        
        self.figure_beer.tight_layout()
        self.canvas_beer.draw()
        
        # Análise estatística
        self.analyze_beer_law_deviations(concentrations, absorbances_theoretical, absorbances_real, include_deviations)
    
    def analyze_beer_law_deviations(self, concentrations, theoretical, experimental, has_deviations):
        """Analisa os desvios da Lei de Beer."""
        # Calcular desvios
        deviations = experimental - theoretical
        relative_deviations = (deviations / theoretical) * 100
        
        # Estatísticas
        mean_deviation = np.mean(np.abs(relative_deviations))
        max_deviation = np.max(np.abs(relative_deviations))
        
        # Coeficiente de determinação
        r_squared = np.corrcoef(concentrations, experimental)[0, 1] ** 2
        
        # Ajuste linear
        slope, intercept = np.polyfit(concentrations, experimental, 1)
        theoretical_slope = theoretical[-1] / concentrations[-1]  # ε × b
        
        analysis_text = f"ANÁLISE DOS DESVIOS DA LEI DE BEER\n"
        analysis_text += f"{'='*40}\n\n"
        
        analysis_text += f"Parâmetros teóricos:\n"
        analysis_text += f"• Inclinação teórica (ε×b): {theoretical_slope:.2f}\n"
        analysis_text += f"• Intercepto teórico: 0.000\n\n"
        
        analysis_text += f"Parâmetros experimentais:\n"
        analysis_text += f"• Inclinação experimental: {slope:.4f}\n"
        analysis_text += f"• Intercepto experimental: {intercept:.4f}\n"
        analysis_text += f"• Coeficiente de determinação (R²): {r_squared:.6f}\n\n"
        
        analysis_text += f"Análise de desvios:\n"
        analysis_text += f"• Desvio médio absoluto: {mean_deviation:.2f}%\n"
        analysis_text += f"• Desvio máximo: {max_deviation:.2f}%\n\n"
        
        if has_deviations:
            analysis_text += f"Interpretação dos desvios:\n"
            analysis_text += f"• Desvios negativos em altas concentrações\n"
            analysis_text += f"• Possível causa: Associação molecular\n"
            analysis_text += f"• Recomendação: Trabalhar em concentrações menores\n"
        else:
            analysis_text += f"Interpretação:\n"
            analysis_text += f"• Excelente aderência à Lei de Beer\n"
            analysis_text += f"• Desvios dentro do erro experimental\n"
            analysis_text += f"• Sistema adequado para análise quantitativa\n"
        
        self.deviations_text.setText(analysis_text)
    
    def calculate_multicomponent(self):
        """Calcula concentrações em análise multicomponente."""
        # Coeficientes de absorção molar
        eps_a1 = self.epsilon_a1.value()
        eps_a2 = self.epsilon_a2.value()
        eps_b1 = self.epsilon_b1.value()
        eps_b2 = self.epsilon_b2.value()
        
        # Caminho óptico
        b = self.multi_path_length.value()
        
        # Absorbâncias medidas
        A1 = self.abs_lambda1.value()
        A2 = self.abs_lambda2.value()
        
        # Sistema de equações:
        # A1 = (eps_a1 * b * c_a) + (eps_b1 * b * c_b)
        # A2 = (eps_a2 * b * c_a) + (eps_b2 * b * c_b)
        
        # Matriz dos coeficientes
        matrix_coeff = np.array([
            [eps_a1 * b, eps_b1 * b],
            [eps_a2 * b, eps_b2 * b]
        ])
        
        # Vetor das absorbâncias
        absorbances = np.array([A1, A2])
        
        try:
            # Resolver sistema linear
            concentrations = np.linalg.solve(matrix_coeff, absorbances)
            c_a, c_b = concentrations
            
            # Verificar determinante (para avaliar adequação do sistema)
            det = np.linalg.det(matrix_coeff)
            
            # Calcular absorbâncias teóricas para verificação
            A1_calc = eps_a1 * b * c_a + eps_b1 * b * c_b
            A2_calc = eps_a2 * b * c_a + eps_b2 * b * c_b
            
            # Erros
            error_A1 = abs(A1 - A1_calc) / A1 * 100
            error_A2 = abs(A2 - A2_calc) / A2 * 100
            
            result_text = f"RESULTADOS DA ANÁLISE MULTICOMPONENTE\n"
            result_text += f"{'='*40}\n\n"
            
            result_text += f"Sistema de equações resolvido:\n"
            result_text += f"A₁ = {eps_a1}×{b}×cₐ + {eps_b1}×{b}×cᵦ = {A1}\n"
            result_text += f"A₂ = {eps_a2}×{b}×cₐ + {eps_b2}×{b}×cᵦ = {A2}\n\n"
            
            result_text += f"Concentrações calculadas:\n"
            result_text += f"• Componente A: {c_a:.6f} mol/L\n"
            result_text += f"• Componente B: {c_b:.6f} mol/L\n\n"
            
            result_text += f"Verificação:\n"
            result_text += f"• A₁ calculado: {A1_calc:.4f} (erro: {error_A1:.2f}%)\n"
            result_text += f"• A₂ calculado: {A2_calc:.4f} (erro: {error_A2:.2f}%)\n\n"
            
            result_text += f"Avaliação do sistema:\n"
            result_text += f"• Determinante da matriz: {det:.2e}\n"
            if abs(det) > 1e-10:
                result_text += f"• Sistema bem condicionado ✓\n"
            else:
                result_text += f"• Sistema mal condicionado ⚠\n"
            
            if c_a >= 0 and c_b >= 0:
                result_text += f"• Concentrações fisicamente válidas ✓\n"
            else:
                result_text += f"• Concentrações negativas - verificar dados ⚠\n"
                
        except np.linalg.LinAlgError:
            result_text = "ERRO: Sistema de equações singular!\n"
            result_text += "Verifique se os coeficientes de absorção são diferentes\n"
            result_text += "para os dois comprimentos de onda."
        
        self.multicomponent_result.setText(result_text)
    
    def simulate_kinetics(self):
        """Simula cinética de reação."""
        order = self.reaction_order.currentIndex()  # 0=zero, 1=primeira, 2=segunda
        k = self.rate_constant.value()
        c0 = self.initial_concentration.value()
        max_time = self.reaction_time.value()
        
        # Gerar tempos
        times = np.linspace(0, max_time, 100)
        
        # Calcular concentrações baseado na ordem da reação
        if order == 0:  # Ordem zero
            concentrations = c0 - k * times
            concentrations = np.maximum(concentrations, 0)  # Não permitir concentrações negativas
            equation = f"[A] = [A]₀ - kt = {c0} - {k}t"
            
        elif order == 1:  # Primeira ordem
            concentrations = c0 * np.exp(-k * times)
            equation = f"[A] = [A]₀e^(-kt) = {c0}e^(-{k}t)"
            
        else:  # Segunda ordem
            concentrations = c0 / (1 + k * c0 * times)
            equation = f"[A] = [A]₀/(1 + k[A]₀t) = {c0}/(1 + {k}×{c0}×t)"
        
        # Adicionar ruído experimental
        noise = np.random.normal(0, c0 * 0.02, len(times))
        concentrations_exp = concentrations + noise
        concentrations_exp = np.maximum(concentrations_exp, 0)
        
        # Plotar resultados
        self.figure_kinetic.clear()
        ax = self.figure_kinetic.add_subplot(111)
        
        ax.plot(times, concentrations, 'r-', linewidth=3, label='Teórico')
        ax.scatter(times[::5], concentrations_exp[::5], alpha=0.7, s=40, label='Experimental')
        
        ax.set_xlabel('Tempo (s)')
        ax.set_ylabel('Concentração (mol/L)')
        ax.set_title(f'Cinética de {["Ordem Zero", "Primeira Ordem", "Segunda Ordem"][order]}')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Adicionar equação no gráfico
        ax.text(0.05, 0.95, equation, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        self.figure_kinetic.tight_layout()
        self.canvas_kinetic.draw()
        
        # Análise cinética
        self.analyze_kinetics(times, concentrations, concentrations_exp, order, k, c0)
    
    def analyze_kinetics(self, times, theoretical, experimental, order, k, c0):
        """Analisa dados cinéticos."""
        # Calcular meia-vida e outros parâmetros
        if order == 0:
            half_life = c0 / (2 * k)
            rate_equation = "v = k"
            integrated_equation = "[A] = [A]₀ - kt"
            
        elif order == 1:
            half_life = np.log(2) / k
            rate_equation = "v = k[A]"
            integrated_equation = "ln[A] = ln[A]₀ - kt"
            
        else:  # Segunda ordem
            half_life = 1 / (k * c0)
            rate_equation = "v = k[A]²"
            integrated_equation = "1/[A] = 1/[A]₀ + kt"
        
        # Calcular R²
        r_squared = np.corrcoef(theoretical, experimental[:len(theoretical)])[0, 1] ** 2
        
        # Velocidade inicial
        if order == 0:
            initial_rate = k
        elif order == 1:
            initial_rate = k * c0
        else:
            initial_rate = k * c0**2
        
        analysis_text = f"ANÁLISE CINÉTICA\n"
        analysis_text += f"{'='*30}\n\n"
        
        analysis_text += f"Parâmetros da reação:\n"
        analysis_text += f"• Ordem: {['Zero', 'Primeira', 'Segunda'][order]}\n"
        analysis_text += f"• Constante de velocidade (k): {k} s⁻¹\n"
        analysis_text += f"• Concentração inicial: {c0} mol/L\n\n"
        
        analysis_text += f"Equações:\n"
        analysis_text += f"• Velocidade: {rate_equation}\n"
        analysis_text += f"• Integrada: {integrated_equation}\n\n"
        
        analysis_text += f"Parâmetros calculados:\n"
        analysis_text += f"• Velocidade inicial: {initial_rate:.6f} mol/L·s\n"
        analysis_text += f"• Meia-vida (t₁/₂): {half_life:.2f} s\n"
        analysis_text += f"• R² (ajuste): {r_squared:.6f}\n\n"
        
        # Concentração em tempos específicos
        t_25 = 0.25 * len(times)
        t_50 = 0.50 * len(times)
        t_75 = 0.75 * len(times)
        
        analysis_text += f"Concentrações em tempos específicos:\n"
        analysis_text += f"• t = {times[int(t_25)]:.1f}s: {theoretical[int(t_25)]:.4f} mol/L\n"
        analysis_text += f"• t = {times[int(t_50)]:.1f}s: {theoretical[int(t_50)]:.4f} mol/L\n"
        analysis_text += f"• t = {times[int(t_75)]:.1f}s: {theoretical[int(t_75)]:.4f} mol/L\n"
        
        self.kinetic_results.setText(analysis_text)
