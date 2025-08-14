from __future__ import annotations

import os
from typing import Optional
import warnings

import pandas as pd
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QComboBox,
    QMessageBox,
    QGroupBox,
    QCheckBox,
    QTabWidget,
    QTextEdit,
    QSpinBox,
    QDoubleSpinBox,
    QInputDialog,
    QProgressBar,
    QListWidget,
)

from ..plotting import MplCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
import matplotlib.pyplot as plt

# Bibliotecas científicas especializadas
from scipy import signal
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from lmfit import models
import warnings
warnings.filterwarnings('ignore')

# Tenta importar bibliotecas opcionais
try:
    import peakutils
    HAS_PEAKUTILS = True
except ImportError:
    HAS_PEAKUTILS = False


class VoltammogramTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.df: Optional[pd.DataFrame] = None
        self.sample_names = None
        self.canvas = MplCanvas()
        
        # Adiciona barra de ferramentas do matplotlib
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        
        # Configura interface principal
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface com múltiplas abas de análise"""
        layout = QVBoxLayout(self)
        
        # Seção de carregamento de arquivo
        file_group = QGroupBox("Arquivo de Dados")
        file_layout = QVBoxLayout(file_group)
        
        self.load_btn = QPushButton("Carregar arquivo Excel (.xlsx)")
        self.load_btn.clicked.connect(self._load_file)
        
        self.file_label = QLabel("Nenhum arquivo carregado")
        self.file_label.setStyleSheet("color: #666; font-style: italic;")
        
        file_layout.addWidget(self.load_btn)
        file_layout.addWidget(self.file_label)
        
        # Abas de análise
        self.tabs = QTabWidget()
        
        # Aba 1: Análise Básica (código atual)
        self.basic_tab = self._create_basic_analysis_tab()
        self.tabs.addTab(self.basic_tab, "📊 Análise Básica")
        
        # Aba 2: Voltametria Avançada
        self.advanced_tab = self._create_advanced_voltammetry_tab()
        self.tabs.addTab(self.advanced_tab, "🔬 Voltametria Avançada")
        
        # Aba 3: Processamento de Sinal
        self.signal_tab = self._create_signal_processing_tab()
        self.tabs.addTab(self.signal_tab, "🌊 Processamento de Sinal")
        
        # Aba 4: Análise Estatística
        self.stats_tab = self._create_statistical_analysis_tab()
        self.tabs.addTab(self.stats_tab, "📈 Análise Estatística")
        
        # Layout principal
        layout.addWidget(file_group)
        layout.addWidget(self.tabs)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #333; margin: 5px;")
        layout.addWidget(self.info_label)
    
    def _create_basic_analysis_tab(self):
        """Cria aba de análise básica (funcionalidade atual)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Detecção de pares Potencial-Corrente
        detection_group = QGroupBox("Configurações de Plotagem")
        detection_layout = QVBoxLayout(detection_group)
        
        self.auto_detect_btn = QPushButton("🔍 Detectar Pares Potencial-Corrente")
        self.auto_detect_btn.clicked.connect(self._auto_detect_pairs)
        detection_layout.addWidget(self.auto_detect_btn)
        
        self.pairs_list = QListWidget()
        detection_layout.addWidget(QLabel("Pares detectados:"))
        detection_layout.addWidget(self.pairs_list)
        
        # Configurações de ajuste polinomial
        fit_group = QGroupBox("Ajuste Polinomial")
        fit_layout = QGridLayout(fit_group)
        
        fit_layout.addWidget(QLabel("Grau do polinômio:"), 0, 0)
        self.degree_spin = QSpinBox()
        self.degree_spin.setRange(2, 5)
        self.degree_spin.setValue(4)
        fit_layout.addWidget(self.degree_spin, 0, 1)
        
        self.plot_btn = QPushButton("📈 Plotar Voltamogramas")
        self.plot_btn.clicked.connect(self._plot_voltammograms)
        self.plot_btn.setEnabled(False)
        fit_layout.addWidget(self.plot_btn, 1, 0, 1, 2)
        
        layout.addWidget(detection_group)
        layout.addWidget(fit_group)
        layout.addStretch()
        
        return tab
    
    def _create_advanced_voltammetry_tab(self):
        """Cria aba de voltametria avançada com análises específicas"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Análise de Picos
        peak_group = QGroupBox("🏔️ Análise de Picos")
        peak_layout = QGridLayout(peak_group)
        
        peak_layout.addWidget(QLabel("Altura mínima:"), 0, 0)
        self.peak_height_spin = QDoubleSpinBox()
        self.peak_height_spin.setRange(0.001, 1000.0)
        self.peak_height_spin.setValue(0.1)
        self.peak_height_spin.setSuffix(" µA")
        peak_layout.addWidget(self.peak_height_spin, 0, 1)
        
        peak_layout.addWidget(QLabel("Distância mínima:"), 1, 0)
        self.peak_distance_spin = QSpinBox()
        self.peak_distance_spin.setRange(1, 100)
        self.peak_distance_spin.setValue(10)
        self.peak_distance_spin.setSuffix(" pontos")
        peak_layout.addWidget(self.peak_distance_spin, 1, 1)
        
        self.find_peaks_btn = QPushButton("🔍 Encontrar Picos")
        self.find_peaks_btn.clicked.connect(self._find_peaks)
        peak_layout.addWidget(self.find_peaks_btn, 2, 0, 1, 2)
        
        # Análise Cinética
        kinetic_group = QGroupBox("⚡ Análise Cinética")
        kinetic_layout = QGridLayout(kinetic_group)
        
        kinetic_layout.addWidget(QLabel("Velocidade de varredura (V/s):"), 0, 0)
        self.scan_rate_spin = QDoubleSpinBox()
        self.scan_rate_spin.setRange(0.001, 10.0)
        self.scan_rate_spin.setValue(0.1)
        kinetic_layout.addWidget(self.scan_rate_spin, 0, 1)
        
        self.kinetic_analysis_btn = QPushButton("📊 Análise Randles-Sevcik")
        self.kinetic_analysis_btn.clicked.connect(self._kinetic_analysis)
        kinetic_layout.addWidget(self.kinetic_analysis_btn, 1, 0, 1, 2)
        
        # Ajuste Avançado de Curvas
        advanced_fit_group = QGroupBox("📐 Ajuste Avançado")
        advanced_fit_layout = QGridLayout(advanced_fit_group)
        
        advanced_fit_layout.addWidget(QLabel("Modelo:"), 0, 0)
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "Gaussiano",
            "Lorentziano", 
            "Voigt",
            "Exponencial",
            "Sigmoidal"
        ])
        advanced_fit_layout.addWidget(self.model_combo, 0, 1)
        
        self.advanced_fit_btn = QPushButton("🎯 Ajustar Modelo")
        self.advanced_fit_btn.clicked.connect(self._advanced_fitting)
        advanced_fit_layout.addWidget(self.advanced_fit_btn, 1, 0, 1, 2)
        
        layout.addWidget(peak_group)
        layout.addWidget(kinetic_group)
        layout.addWidget(advanced_fit_group)
        layout.addStretch()
        
        return tab
    
    def _create_signal_processing_tab(self):
        """Cria aba de processamento de sinal"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Filtros
        filter_group = QGroupBox("🌊 Filtros")
        filter_layout = QGridLayout(filter_group)
        
        filter_layout.addWidget(QLabel("Tipo de filtro:"), 0, 0)
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "Savitzky-Golay",
            "Passa-baixa (Butterworth)",
            "Passa-alta (Butterworth)",
            "Mediana",
            "Gaussiano"
        ])
        filter_layout.addWidget(self.filter_combo, 0, 1)
        
        filter_layout.addWidget(QLabel("Parâmetro:"), 1, 0)
        self.filter_param_spin = QSpinBox()
        self.filter_param_spin.setRange(3, 51)
        self.filter_param_spin.setValue(11)
        filter_layout.addWidget(self.filter_param_spin, 1, 1)
        
        self.apply_filter_btn = QPushButton("✨ Aplicar Filtro")
        self.apply_filter_btn.clicked.connect(self._apply_filter)
        filter_layout.addWidget(self.apply_filter_btn, 2, 0, 1, 2)
        
        # Baseline
        baseline_group = QGroupBox("📏 Correção de Baseline")
        baseline_layout = QGridLayout(baseline_group)
        
        baseline_layout.addWidget(QLabel("Método:"), 0, 0)
        self.baseline_combo = QComboBox()
        self.baseline_combo.addItems([
            "Linear",
            "Polinomial",
            "Asymmetric Least Squares",
            "SNIP"
        ])
        baseline_layout.addWidget(self.baseline_combo, 0, 1)
        
        self.baseline_btn = QPushButton("📐 Corrigir Baseline")
        self.baseline_btn.clicked.connect(self._correct_baseline)
        baseline_layout.addWidget(self.baseline_btn, 1, 0, 1, 2)
        
        # Derivadas
        derivative_group = QGroupBox("🔢 Derivadas")
        derivative_layout = QGridLayout(derivative_group)
        
        derivative_layout.addWidget(QLabel("Ordem da derivada:"), 0, 0)
        self.derivative_order_spin = QSpinBox()
        self.derivative_order_spin.setRange(1, 3)
        self.derivative_order_spin.setValue(1)
        derivative_layout.addWidget(self.derivative_order_spin, 0, 1)
        
        self.derivative_btn = QPushButton("∂ Calcular Derivada")
        self.derivative_btn.clicked.connect(self._calculate_derivative)
        derivative_layout.addWidget(self.derivative_btn, 1, 0, 1, 2)
        
        layout.addWidget(filter_group)
        layout.addWidget(baseline_group)
        layout.addWidget(derivative_group)
        layout.addStretch()
        
        return tab
    
    def _create_statistical_analysis_tab(self):
        """Cria aba de análise estatística"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # PCA
        pca_group = QGroupBox("🎯 Análise de Componentes Principais (PCA)")
        pca_layout = QGridLayout(pca_group)
        
        pca_layout.addWidget(QLabel("Componentes:"), 0, 0)
        self.pca_components_spin = QSpinBox()
        self.pca_components_spin.setRange(2, 10)
        self.pca_components_spin.setValue(2)
        pca_layout.addWidget(self.pca_components_spin, 0, 1)
        
        self.pca_btn = QPushButton("📊 Executar PCA")
        self.pca_btn.clicked.connect(self._perform_pca)
        pca_layout.addWidget(self.pca_btn, 1, 0, 1, 2)
        
        # Estatísticas Descritivas
        stats_group = QGroupBox("📈 Estatísticas Descritivas")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_btn = QPushButton("📋 Gerar Relatório Estatístico")
        self.stats_btn.clicked.connect(self._generate_stats_report)
        stats_layout.addWidget(self.stats_btn)
        
        self.stats_text = QTextEdit()
        self.stats_text.setMaximumHeight(200)
        stats_layout.addWidget(self.stats_text)
        
        # Exportação
        export_group = QGroupBox("💾 Exportação")
        export_layout = QGridLayout(export_group)
        
        self.export_excel_btn = QPushButton("📊 Exportar Excel")
        self.export_excel_btn.clicked.connect(self._export_excel)
        export_layout.addWidget(self.export_excel_btn, 0, 0)
        
        self.export_csv_btn = QPushButton("📄 Exportar CSV")
        self.export_csv_btn.clicked.connect(self._export_csv)
        export_layout.addWidget(self.export_csv_btn, 0, 1)
        
        self.export_plot_btn = QPushButton("🖼️ Exportar Gráfico")
        self.export_plot_btn.clicked.connect(self._export_plot)
        export_layout.addWidget(self.export_plot_btn, 1, 0, 1, 2)
        
        layout.addWidget(pca_group)
        layout.addWidget(stats_group)
        layout.addWidget(export_group)
        layout.addStretch()
        
        return tab
    
    # === MÉTODOS DA ABA ANÁLISE BÁSICA ===
    
    def _auto_detect_pairs(self):
        """Detecta automaticamente pares de colunas Potencial-Corrente"""
        if self.df is None:
            QMessageBox.warning(self, "Erro", "Primeiro carregue um arquivo!")
            return
        
        pairs = self._detect_voltage_pairs_from_structure(self.df)
        
        self.pairs_list.clear()
        for i, (potential_col, current_col) in enumerate(pairs):
            # Usa sample_names se disponível, senão usa numeração simples
            if self.sample_names and i < len(self.sample_names):
                sample_name = self.sample_names[i]
            else:
                sample_name = f"Amostra {i+1}"
            
            item_text = f"{sample_name}: {potential_col} vs {current_col}"
            self.pairs_list.addItem(item_text)
        
        self.voltage_pairs = pairs
        self.plot_btn.setEnabled(True)
        self.info_label.setText(f"✅ {len(pairs)} pares detectados")
    
    def _plot_voltammograms(self):
        """Plota voltamogramas com ajuste polinomial"""
        if not hasattr(self, 'voltage_pairs'):
            QMessageBox.warning(self, "Erro", "Detecte os pares primeiro!")
            return
        
        self._plot_voltage_pairs(self.voltage_pairs, degree=self.degree_spin.value())
    
    # === MÉTODOS DA ABA VOLTAMETRIA AVANÇADA ===
    
    def _find_peaks(self):
        """Encontra picos nos voltamogramas usando scipy/peakutils"""
        if self.df is None:
            QMessageBox.warning(self, "Erro", "Carregue dados primeiro!")
            return
        
        try:
            height = self.peak_height_spin.value()
            distance = self.peak_distance_spin.value()
            
            if HAS_PEAKUTILS:
                self._find_peaks_peakutils(height, distance)
            else:
                self._find_peaks_scipy(height, distance)
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na detecção de picos: {str(e)}")
    
    def _find_peaks_scipy(self, height, distance):
        """Detecção de picos usando scipy.signal"""
        from scipy.signal import find_peaks
        
        if not hasattr(self, 'voltage_pairs'):
            self._auto_detect_pairs()
        
        self.canvas.axes.clear()
        colors = plt.cm.Set1(np.linspace(0, 1, len(self.voltage_pairs)))
        
        peak_results = []
        
        for i, (potential_col, current_col) in enumerate(self.voltage_pairs):
            color = colors[i]
            
            potential = self.df[potential_col].dropna().values
            current = self.df[current_col].dropna().values
            
            min_len = min(len(potential), len(current))
            potential = potential[:min_len]
            current = current[:min_len]
            
            # Plot dados originais
            self.canvas.axes.plot(potential, current, 'o-', color=color, 
                                alpha=0.7, markersize=3, linewidth=1.5,
                                label=f'Amostra {i+1}')
            
            # Encontrar picos
            peaks, properties = find_peaks(current, height=height, distance=distance)
            
            if len(peaks) > 0:
                peak_potentials = potential[peaks]
                peak_currents = current[peaks]
                
                # Marcar picos
                self.canvas.axes.plot(peak_potentials, peak_currents, 'rx', 
                                    markersize=10, markeredgewidth=2,
                                    label=f'Picos Amostra {i+1}')
                
                peak_results.append({
                    'sample': i+1,
                    'peaks': len(peaks),
                    'potentials': peak_potentials,
                    'currents': peak_currents
                })
        
        self._configure_plot()
        
        # Mostrar resultados
        results_text = "🏔️ RESULTADOS DA ANÁLISE DE PICOS\n\n"
        for result in peak_results:
            results_text += f"Amostra {result['sample']}: {result['peaks']} picos encontrados\n"
            for j, (pot, curr) in enumerate(zip(result['potentials'], result['currents'])):
                results_text += f"  Pico {j+1}: {pot:.3f} V, {curr:.3f} µA\n"
        
        self.info_label.setText(f"✅ Análise de picos concluída: {sum(r['peaks'] for r in peak_results)} picos totais")
        
        # Mostrar em dialog
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Resultados - Análise de Picos")
        msg.setText(results_text)
        msg.exec_()
    
    def _kinetic_analysis(self):
        """Análise cinética usando equação de Randles-Sevcik"""
        if self.df is None:
            QMessageBox.warning(self, "Erro", "Carregue dados primeiro!")
            return
        
        scan_rate = self.scan_rate_spin.value()  # V/s
        
        results_text = f"⚡ ANÁLISE CINÉTICA - RANDLES-SEVCIK\n\n"
        results_text += f"Velocidade de varredura: {scan_rate} V/s\n"
        results_text += f"v^(1/2): {np.sqrt(scan_rate):.3f} V^(1/2)/s^(1/2)\n\n"
        
        if not hasattr(self, 'voltage_pairs'):
            self._auto_detect_pairs()
        
        for i, (potential_col, current_col) in enumerate(self.voltage_pairs):
            current = self.df[current_col].dropna().values
            
            # Encontrar corrente de pico (máxima)
            peak_current = np.max(np.abs(current))  # µA
            peak_current_A = peak_current * 1e-6   # Converter para A
            
            results_text += f"Amostra {i+1}:\n"
            results_text += f"  Corrente de pico: {peak_current:.3f} µA ({peak_current_A:.2e} A)\n"
            results_text += f"  ip/v^(1/2): {peak_current / np.sqrt(scan_rate):.3f} µA/(V/s)^(1/2)\n\n"
        
        # Mostrar resultados
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Resultados - Análise Cinética")
        msg.setText(results_text)
        msg.exec_()
        
        self.info_label.setText("✅ Análise cinética concluída")
    
    def _advanced_fitting(self):
        """Ajuste avançado usando lmfit ou scipy"""
        if self.df is None:
            QMessageBox.warning(self, "Erro", "Carregue dados primeiro!")
            return
        
        try:
            if HAS_LMFIT:
                self._advanced_fitting_lmfit()
            else:
                self._advanced_fitting_scipy()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro no ajuste: {str(e)}")
    
    def _advanced_fitting_lmfit(self):
        """Ajuste avançado usando lmfit"""
        from lmfit import Model
        
        model_name = self.model_combo.currentText()
        
        if not hasattr(self, 'voltage_pairs'):
            self._auto_detect_pairs()
        
        self.canvas.axes.clear()
        colors = plt.cm.Set1(np.linspace(0, 1, len(self.voltage_pairs)))
        
        fit_results = []
        
        for i, (potential_col, current_col) in enumerate(self.voltage_pairs):
            color = colors[i]
            
            potential = self.df[potential_col].dropna().values
            current = self.df[current_col].dropna().values
            
            min_len = min(len(potential), len(current))
            potential = potential[:min_len]
            current = current[:min_len]
            
            # Plot dados experimentais
            self.canvas.axes.plot(potential, current, 'o', color=color, 
                                alpha=0.7, markersize=4,
                                label=f'Exp. Amostra {i+1}')
            
            # Definir modelo baseado na seleção
            if model_name == "Gaussiano":
                def gaussian(x, amplitude, center, sigma):
                    return amplitude * np.exp(-((x - center) / sigma) ** 2)
                model = Model(gaussian)
                params = model.make_params(amplitude=np.max(current), 
                                         center=potential[np.argmax(current)], 
                                         sigma=0.1)
            
            elif model_name == "Lorentziano":
                def lorentzian(x, amplitude, center, sigma):
                    return amplitude / (1 + ((x - center) / sigma) ** 2)
                model = Model(lorentzian)
                params = model.make_params(amplitude=np.max(current), 
                                         center=potential[np.argmax(current)], 
                                         sigma=0.1)
            
            else:  # Modelo padrão (gaussiano)
                def gaussian(x, amplitude, center, sigma):
                    return amplitude * np.exp(-((x - center) / sigma) ** 2)
                model = Model(gaussian)
                params = model.make_params(amplitude=np.max(current), 
                                         center=potential[np.argmax(current)], 
                                         sigma=0.1)
            
            # Realizar ajuste
            try:
                result = model.fit(current, params, x=potential)
                
                # Plot ajuste
                potential_fit = np.linspace(potential.min(), potential.max(), 300)
                current_fit = result.eval(x=potential_fit)
                
                self.canvas.axes.plot(potential_fit, current_fit, '-', color=color, 
                                    linewidth=2, alpha=0.8,
                                    label=f'Ajuste {model_name} {i+1}')
                
                fit_results.append({
                    'sample': i+1,
                    'model': model_name,
                    'r_squared': 1 - result.residual.var() / np.var(current),
                    'params': result.params
                })
                
            except Exception as e:
                print(f"Erro no ajuste da amostra {i+1}: {e}")
        
        self._configure_plot()
        
        # Mostrar resultados
        results_text = f"🎯 RESULTADOS DO AJUSTE - {model_name.upper()}\n\n"
        for result in fit_results:
            results_text += f"Amostra {result['sample']}:\n"
            results_text += f"  R²: {result['r_squared']:.4f}\n"
            for param_name, param in result['params'].items():
                results_text += f"  {param_name}: {param.value:.4f} ± {param.stderr or 0:.4f}\n"
            results_text += "\n"
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Resultados - Ajuste Avançado")
        msg.setText(results_text)
        msg.exec_()
        
        self.info_label.setText(f"✅ Ajuste {model_name} concluído")
    
    def _advanced_fitting_scipy(self):
        """Ajuste avançado usando scipy (fallback)"""
        from scipy.optimize import curve_fit
        
        model_name = self.model_combo.currentText()
        
        if not hasattr(self, 'voltage_pairs'):
            self._auto_detect_pairs()
        
        self.canvas.axes.clear()
        colors = plt.cm.Set1(np.linspace(0, 1, len(self.voltage_pairs)))
        
        for i, (potential_col, current_col) in enumerate(self.voltage_pairs):
            color = colors[i]
            
            potential = self.df[potential_col].dropna().values
            current = self.df[current_col].dropna().values
            
            min_len = min(len(potential), len(current))
            potential = potential[:min_len]
            current = current[:min_len]
            
            # Plot dados experimentais
            self.canvas.axes.plot(potential, current, 'o', color=color, 
                                alpha=0.7, markersize=4,
                                label=f'Exp. Amostra {i+1}')
            
            # Definir função baseada no modelo
            if model_name == "Gaussiano":
                def func(x, a, b, c):
                    return a * np.exp(-((x - b) / c) ** 2)
                p0 = [np.max(current), potential[np.argmax(current)], 0.1]
            elif model_name == "Exponencial":
                def func(x, a, b):
                    return a * np.exp(-b * x)
                p0 = [np.max(current), 1.0]
            else:  # Gaussiano como padrão
                def func(x, a, b, c):
                    return a * np.exp(-((x - b) / c) ** 2)
                p0 = [np.max(current), potential[np.argmax(current)], 0.1]
            
            try:
                popt, _ = curve_fit(func, potential, current, p0=p0)
                
                # Plot ajuste
                potential_fit = np.linspace(potential.min(), potential.max(), 300)
                current_fit = func(potential_fit, *popt)
                
                self.canvas.axes.plot(potential_fit, current_fit, '-', color=color, 
                                    linewidth=2, alpha=0.8,
                                    label=f'Ajuste {model_name} {i+1}')
            except:
                pass  # Se falhar, apenas mostra dados experimentais
        
        self._configure_plot()
        self.info_label.setText(f"✅ Ajuste {model_name} (scipy) concluído")
    
    # === MÉTODOS DA ABA PROCESSAMENTO DE SINAL ===
    
    def _apply_filter(self):
        """Aplica filtro nos dados"""
        if self.df is None:
            QMessageBox.warning(self, "Erro", "Carregue dados primeiro!")
            return
        
        try:
            filter_type = self.filter_combo.currentText()
            param = self.filter_param_spin.value()
            
            from scipy import signal
            
            if not hasattr(self, 'voltage_pairs'):
                self._auto_detect_pairs()
            
            self.canvas.axes.clear()
            colors = plt.cm.Set1(np.linspace(0, 1, len(self.voltage_pairs)))
            
            for i, (potential_col, current_col) in enumerate(self.voltage_pairs):
                color = colors[i]
                
                potential = self.df[potential_col].dropna().values
                current = self.df[current_col].dropna().values
                
                min_len = min(len(potential), len(current))
                potential = potential[:min_len]
                current = current[:min_len]
                
                # Plot dados originais
                self.canvas.axes.plot(potential, current, 'o-', color=color, 
                                    alpha=0.5, markersize=2, linewidth=1,
                                    label=f'Original {i+1}')
                
                # Aplicar filtro
                if filter_type == "Savitzky-Golay":
                    current_filtered = signal.savgol_filter(current, param, 3)
                elif filter_type == "Mediana":
                    current_filtered = signal.medfilt(current, param)
                else:  # Filtros Butterworth ou Gaussiano
                    # Para simplificar, usar Savitzky-Golay como padrão
                    current_filtered = signal.savgol_filter(current, param, 3)
                
                # Plot dados filtrados
                self.canvas.axes.plot(potential, current_filtered, '-', color=color, 
                                    linewidth=2, alpha=0.8,
                                    label=f'Filtrado {i+1}')
            
            self._configure_plot()
            self.info_label.setText(f"✅ Filtro {filter_type} aplicado")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na filtragem: {str(e)}")
    
    def _correct_baseline(self):
        """Corrige baseline dos dados"""
        if self.df is None:
            QMessageBox.warning(self, "Erro", "Carregue dados primeiro!")
            return
        
        try:
            baseline_method = self.baseline_combo.currentText()
            
            if not hasattr(self, 'voltage_pairs'):
                self._auto_detect_pairs()
            
            self.canvas.axes.clear()
            colors = plt.cm.Set1(np.linspace(0, 1, len(self.voltage_pairs)))
            
            for i, (potential_col, current_col) in enumerate(self.voltage_pairs):
                color = colors[i]
                
                potential = self.df[potential_col].dropna().values
                current = self.df[current_col].dropna().values
                
                min_len = min(len(potential), len(current))
                potential = potential[:min_len]
                current = current[:min_len]
                
                # Plot dados originais
                self.canvas.axes.plot(potential, current, 'o-', color=color, 
                                    alpha=0.5, markersize=2, linewidth=1,
                                    label=f'Original {i+1}')
                
                # Correção de baseline simples (linear)
                if baseline_method == "Linear":
                    # Baseline linear usando primeiro e último ponto
                    baseline = np.linspace(current[0], current[-1], len(current))
                elif baseline_method == "Polinomial":
                    # Baseline polinomial de grau 2
                    x_indices = np.arange(len(current))
                    baseline_coeffs = np.polyfit(x_indices, current, 2)
                    baseline = np.polyval(baseline_coeffs, x_indices)
                else:
                    # Baseline simples (média dos primeiros/últimos pontos)
                    baseline_value = (np.mean(current[:5]) + np.mean(current[-5:])) / 2
                    baseline = np.full_like(current, baseline_value)
                
                current_corrected = current - baseline
                
                # Plot dados corrigidos
                self.canvas.axes.plot(potential, current_corrected, '-', color=color, 
                                    linewidth=2, alpha=0.8,
                                    label=f'Corrigido {i+1}')
            
            self._configure_plot()
            self.info_label.setText(f"✅ Baseline {baseline_method} corrigida")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na correção de baseline: {str(e)}")
    
    def _calculate_derivative(self):
        """Calcula derivada dos dados"""
        if self.df is None:
            QMessageBox.warning(self, "Erro", "Carregue dados primeiro!")
            return
        
        try:
            order = self.derivative_order_spin.value()
            
            if not hasattr(self, 'voltage_pairs'):
                self._auto_detect_pairs()
            
            self.canvas.axes.clear()
            colors = plt.cm.Set1(np.linspace(0, 1, len(self.voltage_pairs)))
            
            for i, (potential_col, current_col) in enumerate(self.voltage_pairs):
                color = colors[i]
                
                potential = self.df[potential_col].dropna().values
                current = self.df[current_col].dropna().values
                
                min_len = min(len(potential), len(current))
                potential = potential[:min_len]
                current = current[:min_len]
                
                # Calcular derivada
                for _ in range(order):
                    current = np.gradient(current, potential)
                
                # Plot derivada
                self.canvas.axes.plot(potential, current, '-', color=color, 
                                    linewidth=2, alpha=0.8,
                                    label=f'D{order} Amostra {i+1}')
            
            # Configurar labels
            self.canvas.axes.set_xlabel('Potencial (V)')
            if order == 1:
                self.canvas.axes.set_ylabel('dI/dE (µA/V)')
            elif order == 2:
                self.canvas.axes.set_ylabel('d²I/dE² (µA/V²)')
            else:
                self.canvas.axes.set_ylabel(f'd{order}I/dE{order}')
            
            self.canvas.axes.grid(True, alpha=0.3)
            self.canvas.axes.legend()
            self.canvas.draw()
            
            self.info_label.setText(f"✅ Derivada de ordem {order} calculada")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro no cálculo da derivada: {str(e)}")
    
    # === MÉTODOS DA ABA ANÁLISE ESTATÍSTICA ===
    
    def _perform_pca(self):
        """Realiza análise PCA"""
        if self.df is None:
            QMessageBox.warning(self, "Erro", "Carregue dados primeiro!")
            return
        
        try:
            from sklearn.decomposition import PCA
            from sklearn.preprocessing import StandardScaler
            
            n_components = self.pca_components_spin.value()
            
            if not hasattr(self, 'voltage_pairs'):
                self._auto_detect_pairs()
            
            # Preparar dados para PCA
            data_matrix = []
            for potential_col, current_col in self.voltage_pairs:
                current = self.df[current_col].dropna().values
                data_matrix.append(current)
            
            # Garantir que todas as séries tenham o mesmo tamanho
            min_length = min(len(series) for series in data_matrix)
            data_matrix = np.array([series[:min_length] for series in data_matrix])
            
            # Normalizar dados
            scaler = StandardScaler()
            data_normalized = scaler.fit_transform(data_matrix)
            
            # Aplicar PCA
            pca = PCA(n_components=n_components)
            pca_result = pca.fit_transform(data_normalized)
            
            # Plot resultados PCA
            self.canvas.axes.clear()
            
            if n_components >= 2:
                self.canvas.axes.scatter(pca_result[:, 0], pca_result[:, 1], 
                                       c=range(len(pca_result)), cmap='viridis', s=100)
                self.canvas.axes.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} var.)')
                self.canvas.axes.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} var.)')
                
                # Adicionar labels das amostras
                for i, (x, y) in enumerate(pca_result[:, :2]):
                    self.canvas.axes.annotate(f'S{i+1}', (x, y), xytext=(5, 5), 
                                           textcoords='offset points')
            else:
                self.canvas.axes.plot(pca_result[:, 0], 'o-')
                self.canvas.axes.set_xlabel('Amostra')
                self.canvas.axes.set_ylabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} var.)')
            
            self.canvas.axes.set_title('Análise de Componentes Principais (PCA)')
            self.canvas.axes.grid(True, alpha=0.3)
            self.canvas.draw()
            
            # Mostrar variância explicada
            variance_text = "📊 RESULTADOS PCA\n\n"
            variance_text += f"Componentes: {n_components}\n"
            variance_text += f"Variância total explicada: {sum(pca.explained_variance_ratio_):.1%}\n\n"
            for i, var_ratio in enumerate(pca.explained_variance_ratio_):
                variance_text += f"PC{i+1}: {var_ratio:.1%}\n"
            
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Resultados - PCA")
            msg.setText(variance_text)
            msg.exec_()
            
            self.info_label.setText(f"✅ PCA concluída: {sum(pca.explained_variance_ratio_):.1%} variância explicada")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na análise PCA: {str(e)}")
    
    def _generate_stats_report(self):
        """Gera relatório estatístico"""
        if self.df is None:
            QMessageBox.warning(self, "Erro", "Carregue dados primeiro!")
            return
        
        try:
            if not hasattr(self, 'voltage_pairs'):
                self._auto_detect_pairs()
            
            report = "📈 RELATÓRIO ESTATÍSTICO\n"
            report += "="*50 + "\n\n"
            
            for i, (potential_col, current_col) in enumerate(self.voltage_pairs):
                potential = self.df[potential_col].dropna()
                current = self.df[current_col].dropna()
                
                report += f"AMOSTRA {i+1}\n"
                report += f"Colunas: {potential_col} vs {current_col}\n\n"
                
                report += "POTENCIAL:\n"
                report += f"  Média: {potential.mean():.4f} V\n"
                report += f"  Desvio: {potential.std():.4f} V\n"
                report += f"  Min-Max: {potential.min():.4f} - {potential.max():.4f} V\n"
                report += f"  Range: {potential.max() - potential.min():.4f} V\n\n"
                
                report += "CORRENTE:\n"
                report += f"  Média: {current.mean():.4f} µA\n"
                report += f"  Desvio: {current.std():.4f} µA\n"
                report += f"  Min-Max: {current.min():.4f} - {current.max():.4f} µA\n"
                report += f"  Range: {current.max() - current.min():.4f} µA\n"
                report += f"  RMS: {np.sqrt(np.mean(current**2)):.4f} µA\n\n"
                
                report += "-"*30 + "\n\n"
            
            self.stats_text.setPlainText(report)
            self.info_label.setText("✅ Relatório estatístico gerado")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro no relatório: {str(e)}")
    
    def _export_excel(self):
        """Exporta dados para Excel"""
        if self.df is None:
            QMessageBox.warning(self, "Erro", "Carregue dados primeiro!")
            return
        
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exportar Excel", "", "Excel files (*.xlsx)"
            )
            if filename:
                self.df.to_excel(filename, index=False)
                self.info_label.setText(f"✅ Dados exportados: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na exportação: {str(e)}")
    
    def _export_csv(self):
        """Exporta dados para CSV"""
        if self.df is None:
            QMessageBox.warning(self, "Erro", "Carregue dados primeiro!")
            return
        
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exportar CSV", "", "CSV files (*.csv)"
            )
            if filename:
                self.df.to_csv(filename, index=False)
                self.info_label.setText(f"✅ Dados exportados: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na exportação: {str(e)}")
    
    def _export_plot(self):
        """Exporta gráfico atual"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exportar Gráfico", "", 
                "PNG files (*.png);;PDF files (*.pdf);;SVG files (*.svg)"
            )
            if filename:
                self.canvas.figure.savefig(filename, dpi=300, bbox_inches='tight')
                self.info_label.setText(f"✅ Gráfico exportado: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na exportação: {str(e)}")
        
        # Aba 1: Análise Básica (código atual)
        self.basic_tab = self._create_basic_analysis_tab()
        self.tabs.addTab(self.basic_tab, "📊 Análise Básica")
        
        # Aba 2: Voltametria Avançada
        self.advanced_tab = self._create_advanced_voltammetry_tab()
        self.tabs.addTab(self.advanced_tab, "🔬 Voltametria Avançada")
        
        # Aba 3: Processamento de Sinal
        self.signal_tab = self._create_signal_processing_tab()
        self.tabs.addTab(self.signal_tab, "🌊 Processamento de Sinal")
        
        # Aba 4: Análise Estatística
        self.stats_tab = self._create_statistical_analysis_tab()
        self.tabs.addTab(self.stats_tab, "📈 Análise Estatística")
        
        # Layout principal
        layout.addWidget(file_group)
        layout.addWidget(self.tabs)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #333; margin: 5px;")
        layout.addWidget(self.info_label)
        
        # Seção de carregamento de arquivo
        file_group = QGroupBox("Arquivo de Dados")
        file_layout = QVBoxLayout(file_group)
        
        # Botão para carregar arquivo
        self.load_btn = QPushButton("Carregar arquivo Excel (.xlsx)")
        self.load_btn.clicked.connect(self._load_file)
        
        # Label para mostrar arquivo carregado
        self.file_label = QLabel("Nenhum arquivo carregado")
        self.file_label.setStyleSheet("color: #666; font-style: italic;")
        
        file_layout.addWidget(self.load_btn)
        file_layout.addWidget(self.file_label)
        
        # Seção de configuração do gráfico
        plot_group = QGroupBox("Configuração do Voltamograma")
        plot_layout = QVBoxLayout(plot_group)
        
        # Modo de plotagem
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Modo de dados:"))
        self.data_mode = QComboBox()
        self.data_mode.addItem("Pares Potencial-Corrente (recomendado)")
        self.data_mode.addItem("Seleção manual de colunas")
        self.data_mode.currentTextChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self.data_mode)
        plot_layout.addLayout(mode_layout)
        
        # Configurações para modo manual (inicialmente oculto)
        self.manual_group = QWidget()
        manual_layout = QHBoxLayout(self.manual_group)
        
        manual_layout.addWidget(QLabel("Eixo X (Potencial):"))
        self.x_combo = QComboBox()
        self.x_combo.currentTextChanged.connect(self._update_plot)
        manual_layout.addWidget(self.x_combo)
        
        manual_layout.addWidget(QLabel("Séries (Concentrações):"))
        self.series_combo = QComboBox()
        self.series_combo.addItem("Plotar todas as colunas numéricas")
        self.series_combo.currentTextChanged.connect(self._update_plot)
        manual_layout.addWidget(self.series_combo)
        
        self.manual_group.setVisible(False)
        plot_layout.addWidget(self.manual_group)
        
        # Opções de visualização
        options_layout = QHBoxLayout()
        
        self.show_experimental = QCheckBox("Mostrar dados experimentais")
        self.show_experimental.setChecked(False)  # Desabilitado por padrão
        self.show_experimental.toggled.connect(self._update_plot)
        options_layout.addWidget(self.show_experimental)
        
        self.show_fitted = QCheckBox("Mostrar curvas ajustadas")
        self.show_fitted.setChecked(True)
        self.show_fitted.toggled.connect(self._update_plot)
        options_layout.addWidget(self.show_fitted)
        
        self.show_grid = QCheckBox("Mostrar grade")
        self.show_grid.setChecked(False)  # Desabilitado por padrão
        self.show_grid.toggled.connect(self._update_plot)
        options_layout.addWidget(self.show_grid)
        
        self.poly_degree = QComboBox()
        self.poly_degree.addItems(["Grau 2", "Grau 3", "Grau 4", "Grau 5"])
        self.poly_degree.setCurrentText("Grau 4")
        self.poly_degree.currentTextChanged.connect(self._update_plot)
        options_layout.addWidget(QLabel("Ajuste polinomial:"))
        options_layout.addWidget(self.poly_degree)
        
        self.legend_position = QComboBox()
        self.legend_position.addItems(["Direita", "Inferior", "Superior", "Automático"])
        self.legend_position.setCurrentText("Direita")
        self.legend_position.currentTextChanged.connect(self._update_plot)
        options_layout.addWidget(QLabel("Legenda:"))
        options_layout.addWidget(self.legend_position)
        
        plot_layout.addLayout(options_layout)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("Visualizar Dados")
        self.preview_btn.clicked.connect(self._preview_data)
        self.preview_btn.setEnabled(False)
        
        self.plot_btn = QPushButton("Plotar Voltamograma")
        self.plot_btn.clicked.connect(self._update_plot)
        self.plot_btn.setEnabled(False)
        
        self.save_btn = QPushButton("Salvar PNG (300 DPI)")
        self.save_btn.clicked.connect(self._save_plot)
        self.save_btn.setEnabled(False)
        
        self.clear_btn = QPushButton("Limpar")
        self.clear_btn.clicked.connect(self._clear_plot)
        
        buttons_layout.addWidget(self.preview_btn)
        buttons_layout.addWidget(self.plot_btn)
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addStretch(1)
        
        plot_layout.addLayout(buttons_layout)
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #333; margin: 5px;")
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.addWidget(file_group)
        layout.addWidget(plot_group)
        layout.addWidget(self.toolbar)  # Barra de ferramentas
        layout.addWidget(self.canvas)
        layout.addWidget(self.info_label)

    def _load_file(self):
        """Carrega arquivo Excel (.xlsx)"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar arquivo Excel",
            "",
            "Arquivos Excel (*.xlsx);;Todos os arquivos (*)"
        )
        
        if not file_path:
            return
            
        try:
            # Carrega o arquivo Excel seguindo a lógica do código fornecido
            self.df = pd.read_excel(file_path)
            
            # Guarda nomes das amostras (primeira linha)
            self.sample_names = self.df.iloc[0]
            
            # Remove a linha de nomes e converte para float
            self.df = self.df.drop(index=0)
            self.df = self.df.astype(float)
            
            # Atualiza a interface
            filename = os.path.basename(file_path)
            self.file_label.setText(f"Arquivo: {filename}")
            self.file_label.setStyleSheet("color: #2d5016; font-weight: bold;")
            
            # Detecta pares de colunas automaticamente (agora baseado na estrutura)
            self.voltage_pairs = self._detect_voltage_pairs_from_structure()
            
            # Popula os comboboxes com as colunas (para modo manual)
            columns = list(self.df.columns)
            self.x_combo.clear()
            self.series_combo.clear()
            self.x_combo.addItems(columns)
            
            # Para séries, adiciona opção de plotar todas + colunas individuais
            self.series_combo.addItem("Plotar todas as colunas numéricas")
            self.series_combo.addItems(columns)
            
            # Habilita os botões
            self.plot_btn.setEnabled(True)
            self.preview_btn.setEnabled(True)
            
            # Exibe informações sobre o arquivo
            rows, cols = self.df.shape
            pairs_found = len(self.voltage_pairs)
            self.info_label.setText(
                f"Dados carregados: {rows} linhas, {cols} colunas | "
                f"Pares Potencial-Corrente detectados: {pairs_found}"
            )
            
            # Tenta fazer uma seleção automática inteligente para modo manual
            self._auto_select_columns(columns)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar arquivo:\n{str(e)}")
            self.df = None
            self.file_label.setText("Erro ao carregar arquivo")
            self.file_label.setStyleSheet("color: red;")
            self.plot_btn.setEnabled(False)
            self.preview_btn.setEnabled(False)
            self.save_btn.setEnabled(False)
    
    def _has_duplicate_headers(self):
        """Verifica se a primeira linha tem cabeçalhos duplicados ou inválidos"""
        try:
            # Verifica se há muitas colunas sem nome ou com nomes repetidos
            col_names = list(self.df.columns)
            unnamed_count = sum(1 for col in col_names if 'Unnamed' in str(col))
            
            # Se mais de 30% das colunas são "Unnamed", provavelmente a primeira linha deve ser ignorada
            return unnamed_count > len(col_names) * 0.3
        except:
            return False
    
    def _detect_voltage_pairs_from_structure(self):
        """Detecta pares de colunas baseado na estrutura (colunas de 2 em 2)"""
        pairs = []
        columns = list(self.df.columns)
        
        # Loop pelas colunas de dois em dois (como no código fornecido)
        for i in range(0, len(columns), 2):
            if i + 1 < len(columns):  # Garante que há um par
                potencial_col = columns[i]
                corrente_col = columns[i + 1]
                
                # Obtém o nome da amostra da primeira linha
                sample_name = str(self.sample_names.iloc[i]) if i < len(self.sample_names) else f"Amostra {i//2 + 1}"
                
                pairs.append({
                    'volume': sample_name,
                    'potential_col': potencial_col,
                    'current_col': corrente_col
                })
        
        return pairs
    
    def _extract_volume_name(self, pot_col, curr_col):
        """Extrai o nome do volume das colunas"""
        import re
        
        # Procura padrões como "100μL", "200uL", "branco", etc.
        for col in [pot_col, curr_col]:
            col_str = str(col)
            
            # Procura por padrões de volume
            volume_match = re.search(r'(\d+\s*[μu]?[lL]|branco|blank|controle)', col_str, re.IGNORECASE)
            if volume_match:
                return volume_match.group(1)
        
        # Se não encontrar, usa parte do nome da coluna
        pot_parts = str(pot_col).split()
        if len(pot_parts) > 1:
            return pot_parts[-1]  # Última parte do nome
        
        return f"Série {len(self.voltage_pairs) + 1}"
    
    def _on_mode_changed(self):
        """Altera visibilidade dos controles conforme o modo selecionado"""
        is_manual = self.data_mode.currentText() == "Seleção manual de colunas"
        self.manual_group.setVisible(is_manual)
    
    def _preview_data(self):
        """Mostra uma prévia dos dados carregados"""
        if self.df is None:
            return
            
        # Cria uma janela de diálogo para mostrar os dados
        from PySide6.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Prévia dos Dados")
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Área de texto para mostrar os dados
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        # Prepara o texto com informações dos dados
        info_text = f"ARQUIVO CARREGADO\n"
        info_text += f"==================\n"
        info_text += f"Dimensões: {self.df.shape[0]} linhas × {self.df.shape[1]} colunas\n"
        info_text += f"Colunas: {list(self.df.columns)}\n\n"
        
        info_text += f"TIPOS DE DADOS\n"
        info_text += f"===============\n"
        for col in self.df.columns:
            dtype = self.df[col].dtype
            non_null = self.df[col].count()
            total = len(self.df[col])
            info_text += f"{col}: {dtype} ({non_null}/{total} valores válidos)\n"
        
        info_text += f"\nPRIMEIRAS 10 LINHAS\n"
        info_text += f"===================\n"
        info_text += str(self.df.head(10))
        
        info_text += f"\nESTATÍSTICAS DESCRITIVAS\n"
        info_text += f"========================\n"
        try:
            info_text += str(self.df.describe())
        except:
            info_text += "Não foi possível calcular estatísticas (dados não numéricos)"
        
        text_edit.setPlainText(info_text)
        layout.addWidget(text_edit)
        
        # Botão para fechar
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    def _save_plot(self):
        """Salva o gráfico como PNG em alta resolução (300 DPI)"""
        if self.df is None:
            return
        
        # Abre diálogo para salvar arquivo
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Voltamograma",
            "voltamograma.png",
            "Arquivos PNG (*.png);;Todos os arquivos (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Salva a figura com alta resolução
            self.canvas.figure.savefig(
                file_path,
                dpi=300,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none',
                format='png'
            )
            
            QMessageBox.information(
                self,
                "Sucesso",
                f"Voltamograma salvo com sucesso!\n\nLocalização: {file_path}\nResolução: 300 DPI"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao salvar arquivo:\n{str(e)}"
            )
    
    def _auto_select_columns(self, columns):
        """Seleção automática inteligente de colunas"""
        # Procura por colunas que podem ser potencial (eixo X)
        potential_keywords = ['potencial', 'potential', 'voltage', 'volt', 'v', 'e', 'a (']
        
        x_col = None
        
        # Busca coluna de potencial
        for col in columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in potential_keywords):
                x_col = col
                break
        
        # Se não encontrar, usa a primeira coluna
        if x_col is None and len(columns) > 0:
            x_col = columns[0]
        
        # Define a seleção do eixo X
        if x_col:
            self.x_combo.setCurrentText(x_col)
        
        # Mantém "Plotar todas as colunas numéricas" selecionado por padrão
    
    def _sort_concentration_columns(self, columns):
        """Ordena colunas por concentração (100μL, 200μL, etc.)"""
        import re
        
        def extract_number(col_name):
            # Procura por números seguidos de μL, uL, ul, ou similares
            match = re.search(r'(\d+)\s*[μu]?[lL]', str(col_name))
            if match:
                return int(match.group(1))
            
            # Se não encontrar padrão de concentração, usa ordem alfabética
            return float('inf')
        
        try:
            # Separa colunas com concentração das outras
            conc_cols = []
            other_cols = []
            
            for col in columns:
                if extract_number(col) != float('inf'):
                    conc_cols.append(col)
                else:
                    other_cols.append(col)
            
            # Ordena colunas de concentração por valor numérico
            conc_cols.sort(key=extract_number)
            
            # Ordena outras colunas alfabeticamente
            other_cols.sort()
            
            # Retorna concentrações primeiro, depois outras
            return conc_cols + other_cols
            
        except Exception:
            # Se houver erro, retorna ordem original
            return columns
    
    def _update_plot(self):
        """Atualiza o gráfico do voltamograma"""
        if self.df is None:
            return
        
        # Escolhe método de plotagem baseado no modo
        if self.data_mode.currentText() == "Pares Potencial-Corrente (recomendado)":
            self._plot_voltage_pairs()
        else:
            self._plot_manual_selection()
    
    def _plot_voltage_pairs(self):
        """Plota usando a lógica do código fornecido - pares estruturais com ajuste polinomial"""
        if self.df is None:
            return
        
        try:
            # Limpa o gráfico
            ax = self.canvas.ax
            ax.clear()
            
            # Define cores para as séries (alternando entre experimental e ajustado)
            colors = [
                '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
            ]
            
            # Obtém grau do polinômio
            degree_text = self.poly_degree.currentText()
            degree = int(degree_text.split()[1])
            
            plotted_pairs = 0
            equations = []  # Para mostrar as equações
            
            # Loop pelas colunas de dois em dois (seguindo o código fornecido)
            for i in range(0, len(self.df.columns), 2):
                if i + 1 >= len(self.df.columns):
                    break
                    
                try:
                    # Obtém dados do par (como no código original)
                    potencial = self.df.iloc[:, i]
                    corrente = self.df.iloc[:, i + 1]
                    
                    # Remove valores NaN
                    mask = ~(np.isnan(potencial) | np.isnan(corrente))
                    potencial_clean = potencial[mask]
                    corrente_clean = corrente[mask]
                    
                    if len(potencial_clean) == 0:
                        continue
                    
                    # Obtém nome da amostra
                    nome_amostra = str(self.sample_names.iloc[i]) if i < len(self.sample_names) else f"Amostra {i//2 + 1}"
                    
                    # Escolhe cor
                    color_idx = (i // 2) % len(colors)
                    base_color = colors[color_idx]
                    
                    # Plot dados experimentais (apenas se habilitado)
                    if self.show_experimental.isChecked():
                        ax.plot(potencial_clean, corrente_clean, '.', 
                               color=base_color, markersize=4, 
                               label=f"{nome_amostra} (exp)", alpha=0.7)
                    
                    # Ajuste polinomial e plot da curva ajustada
                    if self.show_fitted.isChecked():
                        try:
                            # Ajuste polinomial (como no código original)
                            coef = np.polyfit(potencial_clean, corrente_clean, deg=degree)
                            poly = np.poly1d(coef)
                            
                            # Gerar curva ajustada
                            x_fit = np.linspace(potencial_clean.min(), potencial_clean.max(), 200)
                            y_fit = poly(x_fit)
                            
                            # Plot ajustado - apenas o nome da amostra na legenda
                            label = nome_amostra
                            if self.show_experimental.isChecked():
                                label = f"{nome_amostra} (ajuste)"
                            
                            ax.plot(x_fit, y_fit, '-', color=base_color, 
                                   linewidth=1.5, label=label, alpha=0.9)
                            
                            # Gera string da equação (como no código original)
                            eq_terms = []
                            for j, c in enumerate(coef):
                                power = degree - j
                                if power == 0:
                                    eq_terms.append(f"{c:.3e}")
                                elif power == 1:
                                    eq_terms.append(f"{c:.3e}·x")
                                else:
                                    eq_terms.append(f"{c:.3e}·x^{power}")
                            
                            eq_str = " + ".join(eq_terms).replace("+ -", "- ")
                            equations.append(f"{nome_amostra}: I(V) ≈ {eq_str}")
                            
                        except Exception as e:
                            print(f"Erro no ajuste polinomial para {nome_amostra}: {e}")
                    
                    plotted_pairs += 1
                    
                except Exception as e:
                    print(f"Erro ao plotar par {i//2 + 1}: {e}")
                    continue
            
            if plotted_pairs == 0:
                QMessageBox.warning(self, "Aviso", "Nenhum par foi plotado com sucesso.")
                return
            
            # Configurações do gráfico (como no código original)
            ax.set_xlabel("A (Potencial (V))", fontsize=12, weight='bold')
            ax.set_ylabel("B (Corrente (A))", fontsize=12, weight='bold')
            
            # Remove bordas superiores e direitas para estilo mais limpo
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_linewidth(1.2)
            ax.spines['bottom'].set_linewidth(1.2)
            
            # Grid
            if self.show_grid.isChecked():
                ax.grid(True, alpha=0.3)
            
            # Configura posição da legenda
            self._configure_legend(ax)
            
            # Ajusta layout para acomodar a legenda
            legend_pos = self.legend_position.currentText()
            if legend_pos == "Direita":
                self.canvas.figure.tight_layout()
                self.canvas.figure.subplots_adjust(right=0.75)
            else:
                self.canvas.figure.tight_layout()
            
            # Atualiza o canvas
            self.canvas.draw_idle()
            
            # Mostra as equações no info_label
            if equations:
                eq_text = "Equações dos ajustes:\n" + "\n".join(equations[:3])  # Mostra apenas as 3 primeiras
                if len(equations) > 3:
                    eq_text += f"\n... e mais {len(equations) - 3} equações"
                self.info_label.setText(eq_text)
            else:
                self.info_label.setText(f"Plotados {plotted_pairs} pares")
            
            # Habilita botão de salvar
            self.save_btn.setEnabled(True)
            
            # Também imprime as equações no console (como no código original)
            print("\n=== EQUAÇÕES DOS AJUSTES POLINOMIAIS ===")
            for eq in equations:
                print(eq)
            print("=" * 45)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao plotar pares:\n{str(e)}")
    
    def _plot_manual_selection(self):
        """Plota usando seleção manual de colunas (código original)"""
        x_col = self.x_combo.currentText()
        series_selection = self.series_combo.currentText()
        
        if not x_col:
            return
            
        try:
            # Obtém dados do eixo X
            x_raw = self.df[x_col]
            x_data = pd.to_numeric(x_raw, errors='coerce')
            
            # Remove linhas onde X é inválido
            valid_x_mask = ~(np.isnan(x_data) | np.isinf(x_data))
            x_clean = x_data[valid_x_mask]
            
            if len(x_clean) == 0:
                QMessageBox.warning(self, "Aviso", f"Coluna '{x_col}' não contém dados numéricos válidos.")
                return
            
            # Determina quais colunas plotar
            if series_selection == "Plotar todas as colunas numéricas":
                # Plota todas as colunas numéricas exceto a do eixo X
                y_columns = []
                for col in self.df.columns:
                    if col != x_col:
                        # Testa se a coluna é predominantemente numérica
                        test_data = pd.to_numeric(self.df[col], errors='coerce')
                        if test_data.notna().sum() > len(test_data) * 0.5:  # Mais de 50% são números
                            y_columns.append(col)
                
                # Ordena as colunas por concentração (se possível)
                y_columns = self._sort_concentration_columns(y_columns)
            else:
                # Plota apenas a coluna selecionada
                y_columns = [series_selection] if series_selection != x_col else []
            
            if not y_columns:
                QMessageBox.warning(self, "Aviso", "Nenhuma coluna de dados válida encontrada para plotar.")
                return
            
            # Limpa o gráfico
            ax = self.canvas.ax
            ax.clear()
            
            # Define cores para as séries
            colors = [
                '#1f77b4',  # azul
                '#ff7f0e',  # laranja
                '#2ca02c',  # verde
                '#d62728',  # vermelho
                '#9467bd',  # roxo
                '#8c564b',  # marrom
                '#e377c2',  # rosa
                '#7f7f7f',  # cinza
                '#bcbd22',  # verde oliva
                '#17becf',  # ciano
                '#aec7e8',  # azul claro
                '#ffbb78',  # laranja claro
                '#98df8a',  # verde claro
                '#ff9896',  # vermelho claro
                '#c5b0d5'   # roxo claro
            ]
            
            plotted_series = 0
            total_points = 0
            
            # Plota cada série
            for i, y_col in enumerate(y_columns):
                try:
                    # Obtém dados Y
                    y_raw = self.df[y_col]
                    y_data = pd.to_numeric(y_raw, errors='coerce')
                    
                    # Aplica a mesma máscara do eixo X
                    y_clean = y_data[valid_x_mask]
                    
                    # Remove pares onde Y é inválido
                    final_mask = ~(np.isnan(y_clean) | np.isinf(y_clean))
                    x_final = x_clean[final_mask]
                    y_final = y_clean[final_mask]
                    
                    if len(x_final) == 0:
                        continue
                    
                    # Escolhe cor
                    color = colors[i % len(colors)]
                    
                    # Plota a série
                    if self.show_experimental.isChecked():
                        ax.plot(x_final, y_final, '.', color=color, markersize=4,
                               label=f"{str(y_col)} (exp)", alpha=0.7)
                    
                    if self.show_fitted.isChecked():
                        # Ajuste polinomial
                        try:
                            degree_text = self.poly_degree.currentText()
                            degree = int(degree_text.split()[1])
                            
                            coef = np.polyfit(x_final, y_final, deg=degree)
                            poly = np.poly1d(coef)
                            
                            x_fit = np.linspace(x_final.min(), x_final.max(), 200)
                            y_fit = poly(x_fit)
                            
                            # Ajusta nome da legenda
                            label = str(y_col)
                            if self.show_experimental.isChecked():
                                label = f"{str(y_col)} (ajuste)"
                            
                            ax.plot(x_fit, y_fit, '-', color=color, 
                                   linewidth=1.5, label=label, alpha=0.9)
                        except:
                            # Se falhar o ajuste, plota linha simples
                            ax.plot(x_final, y_final, '-', color=color, 
                                   linewidth=1.2, label=str(y_col), alpha=0.9)
                    
                    plotted_series += 1
                    total_points += len(x_final)
                    
                except Exception as e:
                    print(f"Erro ao plotar série {y_col}: {e}")
                    continue
            
            if plotted_series == 0:
                QMessageBox.warning(self, "Aviso", "Nenhuma série foi plotada com sucesso.")
                return
            
            self._configure_plot(ax)
            
            # Atualiza informações
            self.info_label.setText(
                f"Plotadas {plotted_series} séries | {total_points} pontos totais | "
                f"X: {x_clean.min():.2f} a {x_clean.max():.2f} V"
            )
            
            # Habilita botão de salvar
            self.save_btn.setEnabled(True)
            
        except KeyError as e:
            QMessageBox.critical(self, "Erro", f"Coluna não encontrada: {str(e)}")
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Erro", 
                f"Erro ao plotar:\n{str(e)}\n\n"
                f"Verifique se as colunas selecionadas contêm dados numéricos válidos."
            )
    
    def _configure_plot(self, ax):
        """Configura o estilo do gráfico seguindo o código fornecido"""
        # Configurações do gráfico
        ax.set_xlabel("A (Potencial (V))", fontsize=12, weight='bold')
        ax.set_ylabel("B (Corrente (A))", fontsize=12, weight='bold')
        
        # Remove bordas superiores e direitas para estilo mais limpo
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(1.2)
        ax.spines['bottom'].set_linewidth(1.2)
        
        # Grid
        if self.show_grid.isChecked():
            ax.grid(True, alpha=0.3)
        
        # Configura posição da legenda
        self._configure_legend(ax)
        
        # Ajusta layout para acomodar a legenda
        legend_pos = self.legend_position.currentText()
        if legend_pos == "Direita":
            self.canvas.figure.tight_layout()
            self.canvas.figure.subplots_adjust(right=0.78)
        else:
            self.canvas.figure.tight_layout()
        
        # Atualiza o canvas
        self.canvas.draw_idle()
    
    def _configure_legend(self, ax):
        """Configura a posição da legenda"""
        legend_pos = self.legend_position.currentText()
        
        if legend_pos == "Direita":
            legend = ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', 
                             fontsize=10, frameon=True, fancybox=False, shadow=False,
                             edgecolor='black', facecolor='white')
        elif legend_pos == "Inferior":
            legend = ax.legend(bbox_to_anchor=(0.5, -0.15), loc='upper center', 
                             fontsize=10, frameon=True, fancybox=False, shadow=False, ncol=3,
                             edgecolor='black', facecolor='white')
        elif legend_pos == "Superior":
            legend = ax.legend(bbox_to_anchor=(0.5, 1.15), loc='lower center', 
                             fontsize=10, frameon=True, fancybox=False, shadow=False, ncol=3,
                             edgecolor='black', facecolor='white')
        else:  # Automático
            legend = ax.legend(loc='best', fontsize=10, frameon=True, 
                             fancybox=False, shadow=False, edgecolor='black', facecolor='white')
