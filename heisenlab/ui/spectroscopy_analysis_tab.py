from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QTextEdit, QPushButton, QLabel, QComboBox, QDoubleSpinBox,
    QScrollArea, QTabWidget, QCheckBox, QSpinBox, QFileDialog,
    QTableWidget, QTableWidgetItem
)
from scipy import signal, integrate, optimize, stats
import pandas as pd


class SpectroscopyAnalysisTab(QWidget):
    """Aba para análise de dados espectroscópicos."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.spectrum_data = None
        self.wavelengths = None
        self.intensities = None
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface principal."""
        main_layout = QVBoxLayout(self)
        
        # Criar abas internas
        tabs = QTabWidget()
        
        # Aba 1: Análise de Espectros
        tabs.addTab(self.create_spectrum_analysis_tab(), "Análise de Espectros")
        
        # Aba 2: Identificação de Picos
        tabs.addTab(self.create_peak_analysis_tab(), "Identificação de Picos")
        
        # Aba 3: Tratamento de Dados
        tabs.addTab(self.create_data_treatment_tab(), "Tratamento de Dados")
        
        # Aba 4: Análise Quantitativa
        tabs.addTab(self.create_quantitative_analysis_tab(), "Análise Quantitativa")
        
        # Aba 5: Biblioteca de Espectros
        tabs.addTab(self.create_spectrum_library_tab(), "Biblioteca de Espectros")
        
        main_layout.addWidget(tabs)
    
    def create_spectrum_analysis_tab(self):
        """Cria a aba de análise de espectros."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Importação de dados
        import_group = QGroupBox("Importação de Dados Espectroscópicos")
        import_layout = QVBoxLayout(import_group)
        
        # Botões de importação
        import_buttons_layout = QHBoxLayout()
        
        import_file_btn = QPushButton("Importar Arquivo de Espectro")
        import_file_btn.clicked.connect(self.import_spectrum_file)
        import_buttons_layout.addWidget(import_file_btn)
        
        generate_demo_btn = QPushButton("Gerar Espectro Demonstrativo")
        generate_demo_btn.clicked.connect(self.generate_demo_spectrum)
        import_buttons_layout.addWidget(generate_demo_btn)
        
        import_layout.addLayout(import_buttons_layout)
        
        # Informações do arquivo
        self.file_info = QLabel("Nenhum arquivo carregado")
        self.file_info.setStyleSheet("padding: 10px; background-color: #f5f5f5; border-radius: 5px;")
        import_layout.addWidget(self.file_info)
        
        main_layout.addWidget(import_group)
        
        # Visualização do espectro
        visualization_group = QGroupBox("Visualização do Espectro")
        visualization_layout = QVBoxLayout(visualization_group)
        
        # Canvas para o espectro
        self.figure_spectrum = Figure(figsize=(12, 8))
        self.canvas_spectrum = FigureCanvas(self.figure_spectrum)
        visualization_layout.addWidget(self.canvas_spectrum)
        
        # Controles de visualização
        controls_layout = QHBoxLayout()
        
        self.show_grid = QCheckBox("Mostrar grade")
        self.show_grid.setChecked(True)
        self.show_grid.stateChanged.connect(self.update_spectrum_plot)
        controls_layout.addWidget(self.show_grid)
        
        self.normalize_spectrum = QCheckBox("Normalizar espectro")
        self.normalize_spectrum.stateChanged.connect(self.update_spectrum_plot)
        controls_layout.addWidget(self.normalize_spectrum)
        
        self.invert_yaxis = QCheckBox("Inverter eixo Y")
        self.invert_yaxis.stateChanged.connect(self.update_spectrum_plot)
        controls_layout.addWidget(self.invert_yaxis)
        
        controls_layout.addStretch()
        
        update_plot_btn = QPushButton("Atualizar Gráfico")
        update_plot_btn.clicked.connect(self.update_spectrum_plot)
        controls_layout.addWidget(update_plot_btn)
        
        visualization_layout.addLayout(controls_layout)
        
        main_layout.addWidget(visualization_group)
        
        # Análise básica
        basic_analysis_group = QGroupBox("Análise Básica do Espectro")
        basic_analysis_layout = QVBoxLayout(basic_analysis_group)
        
        analyze_btn = QPushButton("Executar Análise Básica")
        analyze_btn.clicked.connect(self.perform_basic_analysis)
        basic_analysis_layout.addWidget(analyze_btn)
        
        self.basic_analysis_results = QTextEdit()
        self.basic_analysis_results.setReadOnly(True)
        self.basic_analysis_results.setMaximumHeight(200)
        self.basic_analysis_results.setStyleSheet("font-family: monospace; font-size: 11px;")
        basic_analysis_layout.addWidget(self.basic_analysis_results)
        
        main_layout.addWidget(basic_analysis_group)
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
        return widget
    
    def create_peak_analysis_tab(self):
        """Cria a aba de identificação de picos."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Parâmetros de detecção de picos
        peak_params_group = QGroupBox("Parâmetros de Detecção de Picos")
        peak_params_layout = QFormLayout(peak_params_group)
        
        self.peak_height_threshold = QDoubleSpinBox()
        self.peak_height_threshold.setRange(0.01, 1.0)
        self.peak_height_threshold.setValue(0.1)
        self.peak_height_threshold.setDecimals(3)
        peak_params_layout.addRow("Altura mínima (% do máximo):", self.peak_height_threshold)
        
        self.peak_width_min = QDoubleSpinBox()
        self.peak_width_min.setRange(1, 100)
        self.peak_width_min.setValue(5)
        peak_params_layout.addRow("Largura mínima (pontos):", self.peak_width_min)
        
        self.peak_distance = QDoubleSpinBox()
        self.peak_distance.setRange(1, 100)
        self.peak_distance.setValue(10)
        peak_params_layout.addRow("Distância mínima entre picos:", self.peak_distance)
        
        main_layout.addWidget(peak_params_group)
        
        # Botão de detecção
        detect_peaks_btn = QPushButton("Detectar Picos")
        detect_peaks_btn.clicked.connect(self.detect_peaks)
        main_layout.addWidget(detect_peaks_btn)
        
        # Gráfico com picos identificados
        peaks_group = QGroupBox("Picos Identificados")
        peaks_layout = QVBoxLayout(peaks_group)
        
        self.figure_peaks = Figure(figsize=(12, 6))
        self.canvas_peaks = FigureCanvas(self.figure_peaks)
        peaks_layout.addWidget(self.canvas_peaks)
        
        main_layout.addWidget(peaks_group)
        
        # Tabela de picos
        peaks_table_group = QGroupBox("Dados dos Picos")
        peaks_table_layout = QVBoxLayout(peaks_table_group)
        
        self.peaks_table = QTableWidget()
        self.peaks_table.setColumnCount(6)
        self.peaks_table.setHorizontalHeaderLabels([
            "Pico", "Posição (nm)", "Intensidade", "Largura", "Área", "FWHM"
        ])
        self.peaks_table.horizontalHeader().setStretchLastSection(True)
        peaks_table_layout.addWidget(self.peaks_table)
        
        main_layout.addWidget(peaks_table_group)
        
        # Análise dos picos
        peak_analysis_group = QGroupBox("Análise dos Picos")
        peak_analysis_layout = QVBoxLayout(peak_analysis_group)
        
        self.peak_analysis_results = QTextEdit()
        self.peak_analysis_results.setReadOnly(True)
        self.peak_analysis_results.setMaximumHeight(150)
        self.peak_analysis_results.setStyleSheet("font-family: monospace; font-size: 11px;")
        peak_analysis_layout.addWidget(self.peak_analysis_results)
        
        main_layout.addWidget(peak_analysis_group)
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
        return widget
    
    def create_data_treatment_tab(self):
        """Cria a aba de tratamento de dados."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Filtragem e suavização
        filtering_group = QGroupBox("Filtragem e Suavização")
        filtering_layout = QVBoxLayout(filtering_group)
        
        # Parâmetros de filtro
        filter_params_layout = QFormLayout()
        
        self.filter_type = QComboBox()
        self.filter_type.addItems([
            "Média móvel",
            "Savitzky-Golay",
            "Filtro Gaussiano",
            "Filtro Butterworth"
        ])
        filter_params_layout.addRow("Tipo de filtro:", self.filter_type)
        
        self.filter_window = QSpinBox()
        self.filter_window.setRange(3, 51)
        self.filter_window.setValue(11)
        filter_params_layout.addRow("Janela do filtro:", self.filter_window)
        
        self.polynomial_order = QSpinBox()
        self.polynomial_order.setRange(1, 5)
        self.polynomial_order.setValue(3)
        filter_params_layout.addRow("Ordem polinomial (S-G):", self.polynomial_order)
        
        filtering_layout.addLayout(filter_params_layout)
        
        # Botões de filtro
        filter_buttons_layout = QHBoxLayout()
        
        apply_filter_btn = QPushButton("Aplicar Filtro")
        apply_filter_btn.clicked.connect(self.apply_filter)
        filter_buttons_layout.addWidget(apply_filter_btn)
        
        reset_data_btn = QPushButton("Resetar Dados")
        reset_data_btn.clicked.connect(self.reset_spectrum_data)
        filter_buttons_layout.addWidget(reset_data_btn)
        
        filtering_layout.addLayout(filter_buttons_layout)
        
        main_layout.addWidget(filtering_group)
        
        # Correção de linha de base
        baseline_group = QGroupBox("Correção de Linha de Base")
        baseline_layout = QVBoxLayout(baseline_group)
        
        baseline_params_layout = QFormLayout()
        
        self.baseline_method = QComboBox()
        self.baseline_method.addItems([
            "Linear",
            "Polinomial",
            "Asymmetric Least Squares"
        ])
        baseline_params_layout.addRow("Método:", self.baseline_method)
        
        self.polynomial_degree = QSpinBox()
        self.polynomial_degree.setRange(1, 5)
        self.polynomial_degree.setValue(2)
        baseline_params_layout.addRow("Grau do polinômio:", self.polynomial_degree)
        
        baseline_layout.addLayout(baseline_params_layout)
        
        correct_baseline_btn = QPushButton("Corrigir Linha de Base")
        correct_baseline_btn.clicked.connect(self.correct_baseline)
        baseline_layout.addWidget(correct_baseline_btn)
        
        main_layout.addWidget(baseline_group)
        
        # Gráfico de comparação
        comparison_group = QGroupBox("Comparação: Original vs Processado")
        comparison_layout = QVBoxLayout(comparison_group)
        
        self.figure_comparison = Figure(figsize=(12, 6))
        self.canvas_comparison = FigureCanvas(self.figure_comparison)
        comparison_layout.addWidget(self.canvas_comparison)
        
        main_layout.addWidget(comparison_group)
        
        # Estatísticas do processamento
        stats_group = QGroupBox("Estatísticas do Processamento")
        stats_layout = QVBoxLayout(stats_group)
        
        self.processing_stats = QTextEdit()
        self.processing_stats.setReadOnly(True)
        self.processing_stats.setMaximumHeight(150)
        self.processing_stats.setStyleSheet("font-family: monospace; font-size: 11px;")
        stats_layout.addWidget(self.processing_stats)
        
        main_layout.addWidget(stats_group)
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
        return widget
    
    def create_quantitative_analysis_tab(self):
        """Cria a aba de análise quantitativa."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Informações sobre análise quantitativa
        info_group = QGroupBox("Análise Quantitativa Espectroscópica")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel("""
        <b>Análise Quantitativa:</b> Determinação da concentração de substâncias baseada em propriedades espectrais.
        
        <b>Métodos disponíveis:</b>
        • Lei de Beer-Lambert (absorbância vs concentração)
        • Análise de área de pico
        • Análise de altura de pico
        • Método de padrão interno
        • Método de adição padrão
        """)
        info_text.setWordWrap(True)
        info_text.setStyleSheet("padding: 10px; background-color: #e8f5e8; border-radius: 5px;")
        info_layout.addWidget(info_text)
        
        main_layout.addWidget(info_group)
        
        # Seleção de método
        method_group = QGroupBox("Método de Análise")
        method_layout = QFormLayout(method_group)
        
        self.quantitative_method = QComboBox()
        self.quantitative_method.addItems([
            "Lei de Beer (Absorbância)",
            "Área de Pico",
            "Altura de Pico",
            "Adição Padrão"
        ])
        method_layout.addRow("Método:", self.quantitative_method)
        
        main_layout.addWidget(method_group)
        
        # Entrada de dados de calibração
        calibration_group = QGroupBox("Dados de Calibração")
        calibration_layout = QVBoxLayout(calibration_group)
        
        # Botões para dados de calibração
        calib_buttons_layout = QHBoxLayout()
        
        add_standard_btn = QPushButton("Adicionar Padrão")
        add_standard_btn.clicked.connect(self.add_calibration_standard)
        calib_buttons_layout.addWidget(add_standard_btn)
        
        clear_standards_btn = QPushButton("Limpar Padrões")
        clear_standards_btn.clicked.connect(self.clear_calibration_standards)
        calib_buttons_layout.addWidget(clear_standards_btn)
        
        calibration_layout.addLayout(calib_buttons_layout)
        
        # Tabela de padrões
        self.standards_table = QTableWidget()
        self.standards_table.setColumnCount(3)
        self.standards_table.setHorizontalHeaderLabels([
            "Concentração", "Sinal Analítico", "Observações"
        ])
        self.standards_table.setMaximumHeight(200)
        calibration_layout.addWidget(self.standards_table)
        
        main_layout.addWidget(calibration_group)
        
        # Análise da curva de calibração
        curve_analysis_group = QGroupBox("Curva de Calibração")
        curve_analysis_layout = QVBoxLayout(curve_analysis_group)
        
        build_curve_btn = QPushButton("Construir Curva de Calibração")
        build_curve_btn.clicked.connect(self.build_calibration_curve)
        curve_analysis_layout.addWidget(build_curve_btn)
        
        # Gráfico da curva
        self.figure_calibration = Figure(figsize=(10, 6))
        self.canvas_calibration = FigureCanvas(self.figure_calibration)
        curve_analysis_layout.addWidget(self.canvas_calibration)
        
        # Resultados da calibração
        self.calibration_results = QTextEdit()
        self.calibration_results.setReadOnly(True)
        self.calibration_results.setMaximumHeight(150)
        self.calibration_results.setStyleSheet("font-family: monospace; font-size: 11px;")
        curve_analysis_layout.addWidget(self.calibration_results)
        
        main_layout.addWidget(curve_analysis_group)
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
        return widget
    
    def create_spectrum_library_tab(self):
        """Cria a aba de biblioteca de espectros."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Informações sobre biblioteca
        info_group = QGroupBox("Biblioteca de Espectros de Referência")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel("""
        <b>Biblioteca de Espectros:</b> Coleção de espectros de referência para identificação de compostos.
        
        <b>Funcionalidades:</b>
        • Comparação com espectros conhecidos
        • Identificação de compostos
        • Análise de similaridade
        • Base de dados de compostos orgânicos e inorgânicos
        """)
        info_text.setWordWrap(True)
        info_text.setStyleSheet("padding: 10px; background-color: #fff3e0; border-radius: 5px;")
        info_layout.addWidget(info_text)
        
        main_layout.addWidget(info_group)
        
        # Seleção de composto de referência
        reference_group = QGroupBox("Espectros de Referência")
        reference_layout = QVBoxLayout(reference_group)
        
        ref_selector_layout = QFormLayout()
        
        self.reference_compound = QComboBox()
        self.reference_compound.addItems([
            "Benzeno",
            "Tolueno", 
            "Acetona",
            "Etanol",
            "Ácido Acético",
            "Fenol",
            "Anilina",
            "Naftaleno"
        ])
        ref_selector_layout.addRow("Composto:", self.reference_compound)
        
        self.reference_technique = QComboBox()
        self.reference_technique.addItems([
            "UV-Vis",
            "IR",
            "Fluorescência",
            "Raman"
        ])
        ref_selector_layout.addRow("Técnica:", self.reference_technique)
        
        reference_layout.addLayout(ref_selector_layout)
        
        # Botões
        ref_buttons_layout = QHBoxLayout()
        
        load_reference_btn = QPushButton("Carregar Espectro de Referência")
        load_reference_btn.clicked.connect(self.load_reference_spectrum)
        ref_buttons_layout.addWidget(load_reference_btn)
        
        compare_spectra_btn = QPushButton("Comparar com Amostra")
        compare_spectra_btn.clicked.connect(self.compare_spectra)
        ref_buttons_layout.addWidget(compare_spectra_btn)
        
        reference_layout.addLayout(ref_buttons_layout)
        
        main_layout.addWidget(reference_group)
        
        # Gráfico de comparação
        comparison_spec_group = QGroupBox("Comparação de Espectros")
        comparison_spec_layout = QVBoxLayout(comparison_spec_group)
        
        self.figure_comparison_spec = Figure(figsize=(12, 8))
        self.canvas_comparison_spec = FigureCanvas(self.figure_comparison_spec)
        comparison_spec_layout.addWidget(self.canvas_comparison_spec)
        
        main_layout.addWidget(comparison_spec_group)
        
        # Resultados da comparação
        comparison_results_group = QGroupBox("Resultados da Comparação")
        comparison_results_layout = QVBoxLayout(comparison_results_group)
        
        self.comparison_results = QTextEdit()
        self.comparison_results.setReadOnly(True)
        self.comparison_results.setMaximumHeight(200)
        self.comparison_results.setStyleSheet("font-family: monospace; font-size: 11px;")
        comparison_results_layout.addWidget(self.comparison_results)
        
        main_layout.addWidget(comparison_results_group)
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
        return widget
    
    # Métodos de implementação
    def import_spectrum_file(self):
        """Importa arquivo de espectro."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importar Espectro", "", 
            "Arquivos de dados (*.txt *.csv *.dat);;Todos os arquivos (*)"
        )
        
        if file_path:
            try:
                # Tentar diferentes formatos de arquivo
                if file_path.endswith('.csv'):
                    data = pd.read_csv(file_path)
                else:
                    data = pd.read_csv(file_path, delimiter='\t', header=None)
                
                # Assumir primeira coluna = comprimento de onda, segunda = intensidade
                self.wavelengths = data.iloc[:, 0].values
                self.intensities = data.iloc[:, 1].values
                
                # Informações do arquivo
                info_text = f"Arquivo carregado: {file_path.split('/')[-1]}\n"
                info_text += f"Pontos de dados: {len(self.wavelengths)}\n"
                info_text += f"Faixa: {self.wavelengths.min():.1f} - {self.wavelengths.max():.1f} nm"
                
                self.file_info.setText(info_text)
                self.update_spectrum_plot()
                
            except Exception as e:
                self.file_info.setText(f"Erro ao carregar arquivo: {str(e)}")
    
    def generate_demo_spectrum(self):
        """Gera um espectro demonstrativo."""
        # Gerar espectro UV-Vis sintético com múltiplos picos
        self.wavelengths = np.linspace(200, 800, 600)
        
        # Função para gerar picos gaussianos
        def gaussian_peak(x, center, amplitude, width):
            return amplitude * np.exp(-0.5 * ((x - center) / width) ** 2)
        
        # Criar espectro com múltiplos picos
        self.intensities = np.zeros_like(self.wavelengths)
        
        # Pico 1: UV (280 nm) - Proteínas
        self.intensities += gaussian_peak(self.wavelengths, 280, 0.8, 15)
        
        # Pico 2: Visível (525 nm) - Composto orgânico
        self.intensities += gaussian_peak(self.wavelengths, 525, 1.0, 25)
        
        # Pico 3: Visível (650 nm) - Segundo máximo
        self.intensities += gaussian_peak(self.wavelengths, 650, 0.6, 20)
        
        # Adicionar linha de base e ruído
        baseline = 0.05 + 0.0002 * self.wavelengths
        noise = np.random.normal(0, 0.02, len(self.wavelengths))
        self.intensities += baseline + noise
        
        # Garantir valores positivos
        self.intensities = np.maximum(self.intensities, 0)
        
        # Atualizar informações
        self.file_info.setText("Espectro demonstrativo gerado\nPontos: 600\nFaixa: 200-800 nm")
        self.update_spectrum_plot()
    
    def update_spectrum_plot(self):
        """Atualiza o gráfico do espectro."""
        if self.wavelengths is None or self.intensities is None:
            return
        
        self.figure_spectrum.clear()
        ax = self.figure_spectrum.add_subplot(111)
        
        # Normalizar se solicitado
        intensities_plot = self.intensities.copy()
        if self.normalize_spectrum.isChecked():
            intensities_plot = intensities_plot / np.max(intensities_plot)
        
        # Plotar espectro
        ax.plot(self.wavelengths, intensities_plot, 'b-', linewidth=1.5)
        
        ax.set_xlabel('Comprimento de onda (nm)')
        ax.set_ylabel('Absorbância' if not self.normalize_spectrum.isChecked() else 'Absorbância Normalizada')
        ax.set_title('Espectro UV-Visível')
        
        if self.show_grid.isChecked():
            ax.grid(True, alpha=0.3)
        
        if self.invert_yaxis.isChecked():
            ax.invert_yaxis()
        
        self.figure_spectrum.tight_layout()
        self.canvas_spectrum.draw()
    
    def perform_basic_analysis(self):
        """Executa análise básica do espectro."""
        if self.wavelengths is None or self.intensities is None:
            self.basic_analysis_results.setText("Nenhum espectro carregado")
            return
        
        # Estatísticas básicas
        max_intensity = np.max(self.intensities)
        min_intensity = np.min(self.intensities)
        mean_intensity = np.mean(self.intensities)
        std_intensity = np.std(self.intensities)
        
        # Posição do máximo
        max_position = self.wavelengths[np.argmax(self.intensities)]
        
        # Largura espectral (onde intensidade > 10% do máximo)
        threshold = 0.1 * max_intensity
        above_threshold = self.intensities > threshold
        if np.any(above_threshold):
            spectral_width = self.wavelengths[above_threshold][-1] - self.wavelengths[above_threshold][0]
        else:
            spectral_width = 0
        
        # Área sob a curva
        total_area = integrate.trapz(self.intensities, self.wavelengths)
        
        # Formatação dos resultados
        analysis_text = f"ANÁLISE BÁSICA DO ESPECTRO\n"
        analysis_text += f"{'='*35}\n\n"
        analysis_text += f"Estatísticas gerais:\n"
        analysis_text += f"• Número de pontos: {len(self.wavelengths)}\n"
        analysis_text += f"• Faixa espectral: {self.wavelengths.min():.1f} - {self.wavelengths.max():.1f} nm\n"
        analysis_text += f"• Resolução média: {np.mean(np.diff(self.wavelengths)):.2f} nm\n\n"
        
        analysis_text += f"Propriedades espectrais:\n"
        analysis_text += f"• Intensidade máxima: {max_intensity:.4f}\n"
        analysis_text += f"• Posição do máximo: {max_position:.1f} nm\n"
        analysis_text += f"• Intensidade mínima: {min_intensity:.4f}\n"
        analysis_text += f"• Intensidade média: {mean_intensity:.4f}\n"
        analysis_text += f"• Desvio padrão: {std_intensity:.4f}\n"
        analysis_text += f"• Largura espectral (10%): {spectral_width:.1f} nm\n"
        analysis_text += f"• Área total: {total_area:.2f}\n\n"
        
        # Razão sinal/ruído estimada
        signal = max_intensity - min_intensity
        noise = std_intensity
        snr = signal / noise if noise > 0 else float('inf')
        analysis_text += f"Qualidade do espectro:\n"
        analysis_text += f"• Razão sinal/ruído: {snr:.1f}\n"
        
        if snr > 100:
            analysis_text += f"• Qualidade: Excelente\n"
        elif snr > 50:
            analysis_text += f"• Qualidade: Boa\n"
        elif snr > 20:
            analysis_text += f"• Qualidade: Moderada\n"
        else:
            analysis_text += f"• Qualidade: Baixa - considere suavização\n"
        
        self.basic_analysis_results.setText(analysis_text)
    
    def detect_peaks(self):
        """Detecta picos no espectro."""
        if self.wavelengths is None or self.intensities is None:
            return
        
        # Parâmetros de detecção
        height_threshold = self.peak_height_threshold.value() * np.max(self.intensities)
        min_width = int(self.peak_width_min.value())
        min_distance = int(self.peak_distance.value())
        
        # Detectar picos
        peaks, properties = signal.find_peaks(
            self.intensities,
            height=height_threshold,
            width=min_width,
            distance=min_distance
        )
        
        # Plotar espectro com picos
        self.figure_peaks.clear()
        ax = self.figure_peaks.add_subplot(111)
        
        ax.plot(self.wavelengths, self.intensities, 'b-', linewidth=1.5, label='Espectro')
        ax.plot(self.wavelengths[peaks], self.intensities[peaks], 'ro', markersize=8, label='Picos detectados')
        
        # Marcar picos com números
        for i, peak in enumerate(peaks):
            ax.annotate(f'{i+1}', (self.wavelengths[peak], self.intensities[peak]),
                       xytext=(5, 5), textcoords='offset points', fontsize=10, color='red')
        
        ax.set_xlabel('Comprimento de onda (nm)')
        ax.set_ylabel('Absorbância')
        ax.set_title(f'Picos Detectados ({len(peaks)} picos)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.figure_peaks.tight_layout()
        self.canvas_peaks.draw()
        
        # Preencher tabela de picos
        self.populate_peaks_table(peaks, properties)
        
        # Análise dos picos
        self.analyze_detected_peaks(peaks, properties)
    
    def populate_peaks_table(self, peaks, properties):
        """Preenche a tabela com dados dos picos."""
        self.peaks_table.setRowCount(len(peaks))
        
        for i, peak in enumerate(peaks):
            # Número do pico
            self.peaks_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            
            # Posição
            position = self.wavelengths[peak]
            self.peaks_table.setItem(i, 1, QTableWidgetItem(f"{position:.2f}"))
            
            # Intensidade
            intensity = self.intensities[peak]
            self.peaks_table.setItem(i, 2, QTableWidgetItem(f"{intensity:.4f}"))
            
            # Largura (se disponível)
            if 'widths' in properties:
                width = properties['widths'][i] * np.mean(np.diff(self.wavelengths))
                self.peaks_table.setItem(i, 3, QTableWidgetItem(f"{width:.2f}"))
                
                # FWHM aproximado
                fwhm = width * 2.355  # Conversão Gaussiana
                self.peaks_table.setItem(i, 5, QTableWidgetItem(f"{fwhm:.2f}"))
            else:
                self.peaks_table.setItem(i, 3, QTableWidgetItem("N/A"))
                self.peaks_table.setItem(i, 5, QTableWidgetItem("N/A"))
            
            # Área aproximada (integral numérica local)
            try:
                start_idx = max(0, peak - 20)
                end_idx = min(len(self.intensities), peak + 20)
                area = integrate.trapz(
                    self.intensities[start_idx:end_idx],
                    self.wavelengths[start_idx:end_idx]
                )
                self.peaks_table.setItem(i, 4, QTableWidgetItem(f"{area:.2f}"))
            except:
                self.peaks_table.setItem(i, 4, QTableWidgetItem("N/A"))
    
    def analyze_detected_peaks(self, peaks, properties):
        """Analisa os picos detectados."""
        if len(peaks) == 0:
            self.peak_analysis_results.setText("Nenhum pico detectado")
            return
        
        # Análise estatística dos picos
        peak_positions = self.wavelengths[peaks]
        peak_intensities = self.intensities[peaks]
        
        analysis_text = f"ANÁLISE DOS PICOS DETECTADOS\n"
        analysis_text += f"{'='*35}\n\n"
        analysis_text += f"Número total de picos: {len(peaks)}\n"
        analysis_text += f"Pico mais intenso: {peak_positions[np.argmax(peak_intensities)]:.1f} nm\n"
        analysis_text += f"Intensidade máxima: {np.max(peak_intensities):.4f}\n"
        analysis_text += f"Faixa de posições: {peak_positions.min():.1f} - {peak_positions.max():.1f} nm\n\n"
        
        # Classificação por região espectral
        uv_peaks = np.sum(peak_positions < 400)
        visible_peaks = np.sum((peak_positions >= 400) & (peak_positions < 700))
        nir_peaks = np.sum(peak_positions >= 700)
        
        analysis_text += f"Distribuição espectral:\n"
        analysis_text += f"• Região UV (< 400 nm): {uv_peaks} picos\n"
        analysis_text += f"• Região Visível (400-700 nm): {visible_peaks} picos\n"
        analysis_text += f"• Região NIR (> 700 nm): {nir_peaks} picos\n\n"
        
        # Intensidades relativas
        max_intensity = np.max(peak_intensities)
        strong_peaks = np.sum(peak_intensities > 0.7 * max_intensity)
        medium_peaks = np.sum((peak_intensities > 0.3 * max_intensity) & (peak_intensities <= 0.7 * max_intensity))
        weak_peaks = np.sum(peak_intensities <= 0.3 * max_intensity)
        
        analysis_text += f"Intensidade relativa:\n"
        analysis_text += f"• Picos fortes (> 70%): {strong_peaks}\n"
        analysis_text += f"• Picos médios (30-70%): {medium_peaks}\n"
        analysis_text += f"• Picos fracos (< 30%): {weak_peaks}\n"
        
        self.peak_analysis_results.setText(analysis_text)
    
    def apply_filter(self):
        """Aplica filtro aos dados espectrais."""
        if self.wavelengths is None or self.intensities is None:
            return
        
        filter_type = self.filter_type.currentText()
        window = self.filter_window.value()
        
        # Garantir janela ímpar
        if window % 2 == 0:
            window += 1
        
        original_intensities = self.intensities.copy()
        
        try:
            if filter_type == "Média móvel":
                # Filtro de média móvel
                kernel = np.ones(window) / window
                self.intensities = np.convolve(self.intensities, kernel, mode='same')
                
            elif filter_type == "Savitzky-Golay":
                # Filtro Savitzky-Golay
                poly_order = self.polynomial_order.value()
                if window > len(self.intensities):
                    window = len(self.intensities) // 2 * 2 - 1
                if poly_order >= window:
                    poly_order = window - 1
                self.intensities = signal.savgol_filter(self.intensities, window, poly_order)
                
            elif filter_type == "Filtro Gaussiano":
                # Filtro Gaussiano
                sigma = window / 6  # Aproximação
                self.intensities = signal.gaussian_filter1d(self.intensities, sigma)
                
            elif filter_type == "Filtro Butterworth":
                # Filtro Butterworth passa-baixa
                from scipy.signal import butter, filtfilt
                nyquist = 0.5 * len(self.intensities)
                cutoff = window / nyquist
                cutoff = min(cutoff, 0.95)  # Evitar frequência muito alta
                b, a = butter(3, cutoff, btype='low')
                self.intensities = filtfilt(b, a, self.intensities)
            
            # Atualizar gráficos
            self.update_spectrum_plot()
            self.plot_processing_comparison(original_intensities, self.intensities, f"Filtro: {filter_type}")
            
        except Exception as e:
            self.processing_stats.setText(f"Erro na filtragem: {str(e)}")
    
    def correct_baseline(self):
        """Corrige a linha de base do espectro."""
        if self.wavelengths is None or self.intensities is None:
            return
        
        method = self.baseline_method.currentText()
        original_intensities = self.intensities.copy()
        
        try:
            if method == "Linear":
                # Correção linear baseada nos extremos
                baseline = np.linspace(self.intensities[0], self.intensities[-1], len(self.intensities))
                self.intensities = self.intensities - baseline
                
            elif method == "Polinomial":
                # Ajuste polinomial
                degree = self.polynomial_degree.value()
                coeffs = np.polyfit(self.wavelengths, self.intensities, degree)
                baseline = np.polyval(coeffs, self.wavelengths)
                self.intensities = self.intensities - baseline
                
            elif method == "Asymmetric Least Squares":
                # ALS (implementação simplificada)
                # Usar pontos mínimos locais para estimar baseline
                from scipy.signal import argrelmin
                min_indices = argrelmin(self.intensities, order=10)[0]
                if len(min_indices) > 2:
                    baseline = np.interp(self.wavelengths, 
                                       self.wavelengths[min_indices], 
                                       self.intensities[min_indices])
                    self.intensities = self.intensities - baseline
            
            # Atualizar gráficos
            self.update_spectrum_plot()
            self.plot_processing_comparison(original_intensities, self.intensities, f"Correção de baseline: {method}")
            
        except Exception as e:
            self.processing_stats.setText(f"Erro na correção de baseline: {str(e)}")
    
    def plot_processing_comparison(self, original, processed, title):
        """Plota comparação entre dados originais e processados."""
        self.figure_comparison.clear()
        ax = self.figure_comparison.add_subplot(111)
        
        ax.plot(self.wavelengths, original, 'b-', linewidth=1.5, alpha=0.7, label='Original')
        ax.plot(self.wavelengths, processed, 'r-', linewidth=1.5, label='Processado')
        
        ax.set_xlabel('Comprimento de onda (nm)')
        ax.set_ylabel('Absorbância')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.figure_comparison.tight_layout()
        self.canvas_comparison.draw()
        
        # Calcular estatísticas do processamento
        self.calculate_processing_stats(original, processed)
    
    def calculate_processing_stats(self, original, processed):
        """Calcula estatísticas do processamento."""
        # Diferença
        difference = processed - original
        
        # Estatísticas
        max_change = np.max(np.abs(difference))
        mean_change = np.mean(np.abs(difference))
        rms_change = np.sqrt(np.mean(difference**2))
        
        # Razão sinal/ruído antes e depois
        snr_original = np.max(original) / np.std(original)
        snr_processed = np.max(processed) / np.std(processed)
        
        stats_text = f"ESTATÍSTICAS DO PROCESSAMENTO\n"
        stats_text += f"{'='*35}\n\n"
        stats_text += f"Mudanças nos dados:\n"
        stats_text += f"• Mudança máxima: {max_change:.6f}\n"
        stats_text += f"• Mudança média: {mean_change:.6f}\n"
        stats_text += f"• RMS da mudança: {rms_change:.6f}\n\n"
        stats_text += f"Qualidade do sinal:\n"
        stats_text += f"• S/N original: {snr_original:.2f}\n"
        stats_text += f"• S/N processado: {snr_processed:.2f}\n"
        stats_text += f"• Melhoria: {snr_processed/snr_original:.2f}x\n"
        
        self.processing_stats.setText(stats_text)
    
    def reset_spectrum_data(self):
        """Reseta os dados do espectro para o estado original."""
        # Recarregar dados originais (seria necessário armazenar cópia)
        self.generate_demo_spectrum()  # Por simplicidade, gerar novamente
    
    def add_calibration_standard(self):
        """Adiciona padrão de calibração."""
        # Diálogo simples para entrada de dados
        from PySide6.QtWidgets import QInputDialog
        
        concentration, ok1 = QInputDialog.getDouble(self, "Concentração", "Concentração do padrão:", 0, 0, 1000, 6)
        if not ok1:
            return
            
        signal_value, ok2 = QInputDialog.getDouble(self, "Sinal", "Sinal analítico:", 0, 0, 10, 6)
        if not ok2:
            return
        
        # Adicionar à tabela
        row = self.standards_table.rowCount()
        self.standards_table.insertRow(row)
        self.standards_table.setItem(row, 0, QTableWidgetItem(f"{concentration:.6f}"))
        self.standards_table.setItem(row, 1, QTableWidgetItem(f"{signal_value:.6f}"))
        self.standards_table.setItem(row, 2, QTableWidgetItem("Padrão"))
    
    def clear_calibration_standards(self):
        """Limpa todos os padrões de calibração."""
        self.standards_table.setRowCount(0)
    
    def build_calibration_curve(self):
        """Constrói curva de calibração."""
        # Extrair dados da tabela
        concentrations = []
        signals = []
        
        for row in range(self.standards_table.rowCount()):
            try:
                conc = float(self.standards_table.item(row, 0).text())
                signal = float(self.standards_table.item(row, 1).text())
                concentrations.append(conc)
                signals.append(signal)
            except:
                continue
        
        if len(concentrations) < 2:
            self.calibration_results.setText("São necessários pelo menos 2 padrões")
            return
        
        concentrations = np.array(concentrations)
        signals = np.array(signals)
        
        # Regressão linear
        slope, intercept, r_value, p_value, std_err = stats.linregress(concentrations, signals)
        
        # Plotar curva
        self.figure_calibration.clear()
        ax = self.figure_calibration.add_subplot(111)
        
        ax.scatter(concentrations, signals, color='blue', s=50, label='Padrões')
        
        # Linha de ajuste
        conc_line = np.linspace(concentrations.min(), concentrations.max(), 100)
        signal_line = slope * conc_line + intercept
        ax.plot(conc_line, signal_line, 'r-', linewidth=2, label=f'y = {slope:.4f}x + {intercept:.4f}')
        
        ax.set_xlabel('Concentração')
        ax.set_ylabel('Sinal Analítico')
        ax.set_title('Curva de Calibração')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.figure_calibration.tight_layout()
        self.canvas_calibration.draw()
        
        # Resultados
        r_squared = r_value**2
        
        results_text = f"CURVA DE CALIBRAÇÃO\n"
        results_text += f"{'='*25}\n\n"
        results_text += f"Equação: y = {slope:.6f}x + {intercept:.6f}\n"
        results_text += f"R² = {r_squared:.6f}\n"
        results_text += f"Coeficiente de correlação: {r_value:.6f}\n"
        results_text += f"Valor p: {p_value:.2e}\n"
        results_text += f"Erro padrão: {std_err:.6f}\n\n"
        results_text += f"Sensibilidade: {slope:.6f}\n"
        results_text += f"Limite de detecção estimado: {3*std_err/slope:.6f}\n"
        results_text += f"Limite de quantificação estimado: {10*std_err/slope:.6f}\n"
        
        self.calibration_results.setText(results_text)
    
    def load_reference_spectrum(self):
        """Carrega espectro de referência."""
        compound = self.reference_compound.currentText()
        technique = self.reference_technique.currentText()
        
        # Gerar espectro de referência sintético baseado no composto
        ref_wavelengths = np.linspace(200, 800, 600)
        
        # Espectros característicos simplificados
        if compound == "Benzeno":
            # Benzeno: bandas em 254, 260, 266 nm
            ref_intensities = (
                0.8 * np.exp(-0.5 * ((ref_wavelengths - 254) / 8) ** 2) +
                1.0 * np.exp(-0.5 * ((ref_wavelengths - 260) / 6) ** 2) +
                0.6 * np.exp(-0.5 * ((ref_wavelengths - 266) / 8) ** 2)
            )
        elif compound == "Tolueno":
            # Tolueno: similar ao benzeno mas deslocado
            ref_intensities = (
                0.7 * np.exp(-0.5 * ((ref_wavelengths - 261) / 10) ** 2) +
                0.9 * np.exp(-0.5 * ((ref_wavelengths - 267) / 8) ** 2)
            )
        elif compound == "Acetona":
            # Acetona: banda larga em 280 nm
            ref_intensities = 0.5 * np.exp(-0.5 * ((ref_wavelengths - 280) / 25) ** 2)
        else:
            # Espectro genérico
            ref_intensities = 0.7 * np.exp(-0.5 * ((ref_wavelengths - 350) / 30) ** 2)
        
        # Adicionar linha de base e ruído
        baseline = 0.02 + 0.0001 * ref_wavelengths
        noise = np.random.normal(0, 0.01, len(ref_wavelengths))
        ref_intensities += baseline + noise
        ref_intensities = np.maximum(ref_intensities, 0)
        
        # Armazenar dados de referência
        self.ref_wavelengths = ref_wavelengths
        self.ref_intensities = ref_intensities
        self.ref_compound = compound
        
        # Plotar espectro de referência
        self.figure_comparison_spec.clear()
        ax = self.figure_comparison_spec.add_subplot(111)
        
        ax.plot(ref_wavelengths, ref_intensities, 'g-', linewidth=2, label=f'{compound} (Referência)')
        
        ax.set_xlabel('Comprimento de onda (nm)')
        ax.set_ylabel('Absorbância')
        ax.set_title(f'Espectro de Referência: {compound}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.figure_comparison_spec.tight_layout()
        self.canvas_comparison_spec.draw()
    
    def compare_spectra(self):
        """Compara espectro da amostra com referência."""
        if not hasattr(self, 'ref_wavelengths') or self.wavelengths is None:
            self.comparison_results.setText("Carregue primeiro um espectro de referência e uma amostra")
            return
        
        # Interpolar espectros para mesma base de comprimento de onda
        common_wavelengths = np.linspace(
            max(self.wavelengths.min(), self.ref_wavelengths.min()),
            min(self.wavelengths.max(), self.ref_wavelengths.max()),
            500
        )
        
        sample_interp = np.interp(common_wavelengths, self.wavelengths, self.intensities)
        ref_interp = np.interp(common_wavelengths, self.ref_wavelengths, self.ref_intensities)
        
        # Normalizar espectros
        sample_norm = sample_interp / np.max(sample_interp)
        ref_norm = ref_interp / np.max(ref_interp)
        
        # Calcular similaridade (correlação)
        correlation = np.corrcoef(sample_norm, ref_norm)[0, 1]
        
        # Diferença RMS
        rms_diff = np.sqrt(np.mean((sample_norm - ref_norm)**2))
        
        # Índice de similaridade espectral
        similarity_index = (1 - rms_diff) * correlation * 100
        
        # Plotar comparação
        self.figure_comparison_spec.clear()
        ax = self.figure_comparison_spec.add_subplot(111)
        
        ax.plot(common_wavelengths, sample_norm, 'b-', linewidth=2, label='Amostra (normalizada)')
        ax.plot(common_wavelengths, ref_norm, 'g-', linewidth=2, label=f'{self.ref_compound} (referência)')
        ax.plot(common_wavelengths, np.abs(sample_norm - ref_norm), 'r--', alpha=0.7, label='Diferença absoluta')
        
        ax.set_xlabel('Comprimento de onda (nm)')
        ax.set_ylabel('Absorbância Normalizada')
        ax.set_title('Comparação de Espectros')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.figure_comparison_spec.tight_layout()
        self.canvas_comparison_spec.draw()
        
        # Resultados da comparação
        results_text = f"COMPARAÇÃO DE ESPECTROS\n"
        results_text += f"{'='*30}\n\n"
        results_text += f"Amostra vs {self.ref_compound}\n\n"
        results_text += f"Correlação: {correlation:.4f}\n"
        results_text += f"Diferença RMS: {rms_diff:.4f}\n"
        results_text += f"Índice de similaridade: {similarity_index:.1f}%\n\n"
        
        # Interpretação
        if similarity_index > 90:
            interpretation = "Excelente correspondência - Composto provavelmente identificado"
        elif similarity_index > 70:
            interpretation = "Boa correspondência - Composto possivelmente identificado"
        elif similarity_index > 50:
            interpretation = "Correspondência moderada - Composto relacionado"
        else:
            interpretation = "Baixa correspondência - Composto diferente"
        
        results_text += f"Interpretação: {interpretation}\n"
        
        # Análise de picos principais
        if hasattr(self, 'ref_wavelengths'):
            sample_max_pos = common_wavelengths[np.argmax(sample_norm)]
            ref_max_pos = common_wavelengths[np.argmax(ref_norm)]
            max_shift = abs(sample_max_pos - ref_max_pos)
            
            results_text += f"\nAnálise de picos:\n"
            results_text += f"• Máximo da amostra: {sample_max_pos:.1f} nm\n"
            results_text += f"• Máximo da referência: {ref_max_pos:.1f} nm\n"
            results_text += f"• Deslocamento: {max_shift:.1f} nm\n"
        
        self.comparison_results.setText(results_text)
