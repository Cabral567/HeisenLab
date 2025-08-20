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
    QTableWidgetItem, QHeaderView, QDialog
)
from scipy import stats
import pandas as pd


class RegressionAnalysisTab(QWidget):
    """Aba para análise de regressão linear e análise de dados."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.x_data = []
        self.y_data = []
        
    def setup_ui(self):
        """Configura a interface principal."""
        main_layout = QVBoxLayout(self)
        
        # Criar abas internas
        tabs = QTabWidget()
        
        # Aba 1: Regressão Linear
        tabs.addTab(self.create_linear_regression_tab(), "Regressão Linear")
        
        # Aba 2: Análise de Resíduos
        tabs.addTab(self.create_residuals_tab(), "Análise de Resíduos")
        
        # Aba 3: Validação do Modelo
        tabs.addTab(self.create_validation_tab(), "Validação do Modelo")
        
        # Aba 4: Curvas de Calibração
        tabs.addTab(self.create_calibration_tab(), "Curvas de Calibração")
        
        main_layout.addWidget(tabs)
    
    def create_linear_regression_tab(self):
        """Cria a aba de regressão linear."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Seção de entrada de dados
        data_group = QGroupBox("Entrada de Dados")
        data_layout = QVBoxLayout(data_group)
        
        # Método de entrada
        method_layout = QHBoxLayout()
        self.data_method = QComboBox()
        self.data_method.addItems(["Manual (X,Y)", "Importar CSV", "Dados de Exemplo"])
        self.data_method.currentTextChanged.connect(self.on_data_method_changed)
        method_layout.addWidget(QLabel("Método de entrada:"))
        method_layout.addWidget(self.data_method)
        method_layout.addStretch()
        data_layout.addLayout(method_layout)
        
        # Área de entrada manual
        self.manual_input_widget = QWidget()
        manual_layout = QHBoxLayout(self.manual_input_widget)
        
        # Dados X
        x_layout = QVBoxLayout()
        x_layout.addWidget(QLabel("Valores X (Variável Independente):"))
        self.x_input = QTextEdit()
        self.x_input.setPlaceholderText("1.0\n2.0\n3.0\n4.0\n5.0")
        self.x_input.setMaximumHeight(120)
        x_layout.addWidget(self.x_input)
        manual_layout.addLayout(x_layout)
        
        # Dados Y
        y_layout = QVBoxLayout()
        y_layout.addWidget(QLabel("Valores Y (Variável Dependente):"))
        self.y_input = QTextEdit()
        self.y_input.setPlaceholderText("2.1\n4.2\n6.1\n8.3\n10.2")
        self.y_input.setMaximumHeight(120)
        y_layout.addWidget(self.y_input)
        manual_layout.addLayout(y_layout)
        
        data_layout.addWidget(self.manual_input_widget)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        load_example_btn = QPushButton("Carregar Dados de Exemplo")
        load_example_btn.clicked.connect(self.load_example_data)
        button_layout.addWidget(load_example_btn)
        
        calculate_btn = QPushButton("Calcular Regressão Linear")
        calculate_btn.clicked.connect(self.calculate_linear_regression)
        button_layout.addWidget(calculate_btn)
        
        data_layout.addLayout(button_layout)
        main_layout.addWidget(data_group)
        
        # Seção de resultados
        results_group = QGroupBox("Resultados da Regressão")
        results_layout = QVBoxLayout(results_group)
        
        # Tabela de resultados
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["Parâmetro", "Valor"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setMaximumHeight(300)
        results_layout.addWidget(self.results_table)
        
        # Área de texto para equação
        self.equation_label = QLabel()
        self.equation_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; padding: 10px;")
        self.equation_label.setAlignment(Qt.AlignCenter)
        results_layout.addWidget(self.equation_label)
        
        main_layout.addWidget(results_group)
        
        # Seção de gráfico
        graph_group = QGroupBox("Gráfico da Regressão")
        graph_layout = QVBoxLayout(graph_group)
        
        # Canvas do matplotlib
        self.figure1 = Figure(figsize=(10, 6))
        self.canvas1 = FigureCanvas(self.figure1)
        graph_layout.addWidget(self.canvas1)
        
        # Opções do gráfico
        graph_options_layout = QHBoxLayout()
        self.show_confidence_cb = QCheckBox("Mostrar Intervalos de Confiança")
        self.show_confidence_cb.setChecked(True)
        graph_options_layout.addWidget(self.show_confidence_cb)
        
        self.show_prediction_cb = QCheckBox("Mostrar Intervalos de Predição")
        graph_options_layout.addWidget(self.show_prediction_cb)
        
        update_graph_btn = QPushButton("Atualizar Gráfico")
        update_graph_btn.clicked.connect(self.update_regression_plot)
        graph_options_layout.addWidget(update_graph_btn)
        
        graph_layout.addLayout(graph_options_layout)
        main_layout.addWidget(graph_group)
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
        return widget
    
    def create_residuals_tab(self):
        """Cria a aba de análise de resíduos."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Informações sobre resíduos
        info_group = QGroupBox("Análise de Resíduos")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel("""
        <b>Análise de Resíduos:</b> Os resíduos são as diferenças entre os valores observados e os valores preditos pelo modelo.
        
        <b>Importância:</b>
        • Verificar se os pressupostos da regressão linear são atendidos
        • Identificar outliers e pontos influentes
        • Avaliar a adequação do modelo
        
        <b>Padrões a observar:</b>
        • Resíduos devem estar distribuídos aleatoriamente
        • Não deve haver padrões sistemáticos
        • Variância deve ser constante (homocedasticidade)
        """)
        info_text.setWordWrap(True)
        info_text.setStyleSheet("padding: 10px; background-color: #f8f9fa; border-radius: 5px;")
        info_layout.addWidget(info_text)
        
        main_layout.addWidget(info_group)
        
        # Gráficos de resíduos
        plots_group = QGroupBox("Gráficos de Resíduos")
        plots_layout = QVBoxLayout(plots_group)
        
        # Canvas para múltiplos gráficos de resíduos
        self.figure2 = Figure(figsize=(12, 10))
        self.canvas2 = FigureCanvas(self.figure2)
        plots_layout.addWidget(self.canvas2)
        
        # Botão para gerar análise de resíduos
        residuals_btn = QPushButton("Gerar Análise de Resíduos")
        residuals_btn.clicked.connect(self.generate_residuals_analysis)
        plots_layout.addWidget(residuals_btn)
        
        main_layout.addWidget(plots_group)
        
        # Estatísticas dos resíduos
        stats_group = QGroupBox("Estatísticas dos Resíduos")
        stats_layout = QVBoxLayout(stats_group)
        
        self.residuals_stats = QTextEdit()
        self.residuals_stats.setReadOnly(True)
        self.residuals_stats.setMaximumHeight(200)
        self.residuals_stats.setStyleSheet("font-family: monospace; font-size: 11px;")
        stats_layout.addWidget(self.residuals_stats)
        
        main_layout.addWidget(stats_group)
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
        return widget
    
    def create_validation_tab(self):
        """Cria a aba de validação do modelo."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Seção de testes estatísticos
        tests_group = QGroupBox("Testes de Validação do Modelo")
        tests_layout = QVBoxLayout(tests_group)
        
        # Configurações dos testes
        config_layout = QFormLayout()
        
        self.alpha_level = QDoubleSpinBox()
        self.alpha_level.setRange(0.001, 0.1)
        self.alpha_level.setValue(0.05)
        self.alpha_level.setSingleStep(0.01)
        self.alpha_level.setDecimals(3)
        config_layout.addRow("Nível de significância (α):", self.alpha_level)
        
        tests_layout.addLayout(config_layout)
        
        # Botão para executar testes
        run_tests_btn = QPushButton("Executar Testes de Validação")
        run_tests_btn.clicked.connect(self.run_validation_tests)
        tests_layout.addWidget(run_tests_btn)
        
        # Resultados dos testes
        self.validation_results = QTextEdit()
        self.validation_results.setReadOnly(True)
        self.validation_results.setMinimumHeight(300)
        self.validation_results.setStyleSheet("font-family: monospace; font-size: 11px;")
        tests_layout.addWidget(self.validation_results)
        
        main_layout.addWidget(tests_group)
        
        # Seção de métricas de qualidade
        quality_group = QGroupBox("Métricas de Qualidade do Modelo")
        quality_layout = QVBoxLayout(quality_group)
        
        self.quality_metrics = QTextEdit()
        self.quality_metrics.setReadOnly(True)
        self.quality_metrics.setMaximumHeight(200)
        self.quality_metrics.setStyleSheet("font-family: monospace; font-size: 11px;")
        quality_layout.addWidget(self.quality_metrics)
        
        main_layout.addWidget(quality_group)
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
        return widget
    
    def create_calibration_tab(self):
        """Cria a aba de curvas de calibração."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Informações sobre calibração
        info_group = QGroupBox("Curvas de Calibração Analítica")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel("""
        <b>Curvas de Calibração:</b> Fundamentais em química analítica para correlacionar concentração com resposta do instrumento.
        
        <b>Aplicações típicas:</b>
        • Espectrofotometria (Absorbância vs Concentração)
        • Cromatografia (Área do pico vs Concentração)
        • Potenciometria (Potencial vs log[Concentração])
        • Análise elementar (Sinal vs Concentração)
        """)
        info_text.setWordWrap(True)
        info_text.setStyleSheet("padding: 10px; background-color: #e8f5e8; border-radius: 5px;")
        info_layout.addWidget(info_text)
        
        main_layout.addWidget(info_group)
        
        # Seção de predição
        prediction_group = QGroupBox("Predição de Concentrações")
        prediction_layout = QVBoxLayout(prediction_group)
        
        # Entrada para predição
        pred_form_layout = QFormLayout()
        
        self.prediction_value = QDoubleSpinBox()
        self.prediction_value.setRange(-9999.99, 9999.99)
        self.prediction_value.setDecimals(6)
        pred_form_layout.addRow("Valor observado (Y):", self.prediction_value)
        
        prediction_layout.addLayout(pred_form_layout)
        
        # Botões
        pred_button_layout = QHBoxLayout()
        
        predict_btn = QPushButton("Calcular Concentração")
        predict_btn.clicked.connect(self.predict_concentration)
        pred_button_layout.addWidget(predict_btn)
        
        pred_button_layout.addStretch()
        prediction_layout.addLayout(pred_button_layout)
        
        # Resultado da predição
        self.prediction_result = QTextEdit()
        self.prediction_result.setReadOnly(True)
        self.prediction_result.setMaximumHeight(150)
        self.prediction_result.setStyleSheet("font-family: monospace; font-size: 12px; font-weight: bold;")
        prediction_layout.addWidget(self.prediction_result)
        
        main_layout.addWidget(prediction_group)
        
        # Seção de limites analíticos
        limits_group = QGroupBox("Limites Analíticos")
        limits_layout = QVBoxLayout(limits_group)
        
        # Configurações para limites
        limits_form_layout = QFormLayout()
        
        self.blank_replicates = QSpinBox()
        self.blank_replicates.setRange(3, 20)
        self.blank_replicates.setValue(10)
        limits_form_layout.addRow("Número de replicatas do branco:", self.blank_replicates)
        
        self.blank_std_dev = QDoubleSpinBox()
        self.blank_std_dev.setRange(0.001, 999.99)
        self.blank_std_dev.setValue(0.01)
        self.blank_std_dev.setDecimals(6)
        limits_form_layout.addRow("Desvio padrão do branco:", self.blank_std_dev)
        
        limits_layout.addLayout(limits_form_layout)
        
        # Botão para calcular limites
        limits_btn = QPushButton("Calcular LOD e LOQ")
        limits_btn.clicked.connect(self.calculate_analytical_limits)
        limits_layout.addWidget(limits_btn)
        
        # Resultado dos limites
        self.limits_result = QTextEdit()
        self.limits_result.setReadOnly(True)
        self.limits_result.setMaximumHeight(150)
        self.limits_result.setStyleSheet("font-family: monospace; font-size: 11px;")
        limits_layout.addWidget(self.limits_result)
        
        main_layout.addWidget(limits_group)
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
        return widget
    
    # Métodos de implementação
    def on_data_method_changed(self, method):
        """Responde à mudança do método de entrada de dados."""
        if method == "Dados de Exemplo":
            self.load_example_data()
    
    def load_example_data(self):
        """Carrega dados de exemplo para demonstração."""
        # Dados de exemplo: Calibração de espectrofotometria
        x_example = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]  # Concentração (mg/L)
        y_example = [0.003, 0.127, 0.251, 0.390, 0.515, 0.638]  # Absorbância
        
        self.x_input.setPlainText('\n'.join(map(str, x_example)))
        self.y_input.setPlainText('\n'.join(map(str, y_example)))
    
    def parse_data_input(self):
        """Converte os dados de entrada em arrays numpy."""
        try:
            x_text = self.x_input.toPlainText().strip()
            y_text = self.y_input.toPlainText().strip()
            
            if not x_text or not y_text:
                raise ValueError("Dados X ou Y estão vazios")
            
            # Converter para listas
            x_values = [float(x.strip()) for x in x_text.split('\n') if x.strip()]
            y_values = [float(y.strip()) for y in y_text.split('\n') if y.strip()]
            
            if len(x_values) != len(y_values):
                raise ValueError("Número de valores X e Y deve ser igual")
            
            if len(x_values) < 3:
                raise ValueError("São necessários pelo menos 3 pontos de dados")
            
            self.x_data = np.array(x_values)
            self.y_data = np.array(y_values)
            
            return True
            
        except Exception as e:
            self.show_error_dialog(f"Erro ao processar dados: {str(e)}")
            return False
    
    def calculate_linear_regression(self):
        """Calcula a regressão linear e atualiza os resultados."""
        if not self.parse_data_input():
            return
        
        try:
            # Cálculos de regressão linear
            n = len(self.x_data)
            
            # Estatísticas básicas
            slope, intercept, r_value, p_value, std_err = stats.linregress(self.x_data, self.y_data)
            
            # Valores preditos
            y_pred = slope * self.x_data + intercept
            
            # Resíduos
            residuals = self.y_data - y_pred
            
            # Estatísticas adicionais
            ss_res = np.sum(residuals ** 2)  # Soma dos quadrados dos resíduos
            ss_tot = np.sum((self.y_data - np.mean(self.y_data)) ** 2)  # Soma total dos quadrados
            r_squared = r_value ** 2
            
            # Graus de liberdade
            df = n - 2
            
            # Erro padrão dos resíduos
            s_yx = np.sqrt(ss_res / df)
            
            # Erro padrão da inclinação e intercepto
            s_slope = std_err
            s_intercept = s_yx * np.sqrt(1/n + (np.mean(self.x_data)**2) / np.sum((self.x_data - np.mean(self.x_data))**2))
            
            # Intervalos de confiança (95%)
            t_critical = stats.t.ppf(0.975, df)
            slope_ci = t_critical * s_slope
            intercept_ci = t_critical * s_intercept
            
            # Armazenar resultados para outras abas
            self.regression_results = {
                'slope': slope,
                'intercept': intercept,
                'r_value': r_value,
                'r_squared': r_squared,
                'p_value': p_value,
                'std_err': std_err,
                'n': n,
                'df': df,
                's_yx': s_yx,
                's_slope': s_slope,
                's_intercept': s_intercept,
                'slope_ci': slope_ci,
                'intercept_ci': intercept_ci,
                'y_pred': y_pred,
                'residuals': residuals,
                'ss_res': ss_res,
                'ss_tot': ss_tot
            }
            
            # Atualizar tabela de resultados
            self.update_results_table()
            
            # Atualizar gráfico
            self.update_regression_plot()
            
        except Exception as e:
            self.show_error_dialog(f"Erro no cálculo: {str(e)}")
    
    def update_results_table(self):
        """Atualiza a tabela de resultados."""
        if not hasattr(self, 'regression_results'):
            return
        
        results = self.regression_results
        
        # Dados para a tabela
        table_data = [
            ("Equação da reta", f"y = {results['slope']:.6f}x + {results['intercept']:.6f}"),
            ("Inclinação (slope)", f"{results['slope']:.6f} ± {results['slope_ci']:.6f}"),
            ("Intercepto", f"{results['intercept']:.6f} ± {results['intercept_ci']:.6f}"),
            ("Coeficiente de correlação (r)", f"{results['r_value']:.6f}"),
            ("R² (coef. determinação)", f"{results['r_squared']:.6f} ({results['r_squared']*100:.2f}%)"),
            ("Valor p", f"{results['p_value']:.2e}"),
            ("Erro padrão dos resíduos (Syx)", f"{results['s_yx']:.6f}"),
            ("Número de pontos", f"{results['n']}"),
            ("Graus de liberdade", f"{results['df']}"),
            ("Soma dos quadrados dos resíduos", f"{results['ss_res']:.6f}"),
            ("Erro padrão da inclinação", f"{results['s_slope']:.6f}"),
            ("Erro padrão do intercepto", f"{results['s_intercept']:.6f}")
        ]
        
        # Configurar tabela
        self.results_table.setRowCount(len(table_data))
        
        for i, (param, value) in enumerate(table_data):
            self.results_table.setItem(i, 0, QTableWidgetItem(param))
            self.results_table.setItem(i, 1, QTableWidgetItem(value))
        
        # Redimensionar colunas
        self.results_table.resizeColumnsToContents()
        
        # Atualizar equação
        equation_text = f"<b>Equação da Reta:</b> y = {results['slope']:.6f}x + {results['intercept']:.6f}"
        equation_text += f"<br><b>R² = {results['r_squared']:.6f}</b>"
        self.equation_label.setText(equation_text)
    
    def update_regression_plot(self):
        """Atualiza o gráfico da regressão."""
        if not hasattr(self, 'regression_results'):
            return
        
        self.figure1.clear()
        ax = self.figure1.add_subplot(111)
        
        results = self.regression_results
        
        # Dados experimentais
        ax.scatter(self.x_data, self.y_data, color='blue', s=50, alpha=0.7, label='Dados experimentais')
        
        # Linha de regressão
        x_line = np.linspace(self.x_data.min(), self.x_data.max(), 100)
        y_line = results['slope'] * x_line + results['intercept']
        ax.plot(x_line, y_line, 'r-', linewidth=2, label='Regressão linear')
        
        # Intervalos de confiança
        if self.show_confidence_cb.isChecked():
            # Calcular intervalos de confiança
            t_critical = stats.t.ppf(0.975, results['df'])
            
            # Erro padrão para predição da média
            s_y_pred = results['s_yx'] * np.sqrt(1/results['n'] + 
                                              (x_line - np.mean(self.x_data))**2 / 
                                              np.sum((self.x_data - np.mean(self.x_data))**2))
            
            ci_upper = y_line + t_critical * s_y_pred
            ci_lower = y_line - t_critical * s_y_pred
            
            ax.fill_between(x_line, ci_lower, ci_upper, alpha=0.2, color='red', 
                          label='Intervalo de confiança (95%)')
        
        # Intervalos de predição
        if self.show_prediction_cb.isChecked():
            # Erro padrão para predição individual
            t_critical = stats.t.ppf(0.975, results['df'])
            s_y_new = results['s_yx'] * np.sqrt(1 + 1/results['n'] + 
                                              (x_line - np.mean(self.x_data))**2 / 
                                              np.sum((self.x_data - np.mean(self.x_data))**2))
            
            pi_upper = y_line + t_critical * s_y_new
            pi_lower = y_line - t_critical * s_y_new
            
            ax.fill_between(x_line, pi_lower, pi_upper, alpha=0.1, color='orange', 
                          label='Intervalo de predição (95%)')
        
        # Formatação do gráfico
        ax.set_xlabel('X (Variável Independente)')
        ax.set_ylabel('Y (Variável Dependente)')
        ax.set_title('Regressão Linear')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Adicionar equação no gráfico
        equation_text = f'y = {results["slope"]:.4f}x + {results["intercept"]:.4f}\nR² = {results["r_squared"]:.6f}'
        ax.text(0.05, 0.95, equation_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        self.figure1.tight_layout()
        self.canvas1.draw()
    
    def generate_residuals_analysis(self):
        """Gera a análise completa de resíduos."""
        if not hasattr(self, 'regression_results'):
            self.show_error_dialog("Execute primeiro a regressão linear")
            return
        
        results = self.regression_results
        residuals = results['residuals']
        y_pred = results['y_pred']
        
        # Limpar figura
        self.figure2.clear()
        
        # Subplot 1: Resíduos vs Valores Preditos
        ax1 = self.figure2.add_subplot(2, 2, 1)
        ax1.scatter(y_pred, residuals, alpha=0.7)
        ax1.axhline(y=0, color='red', linestyle='--')
        ax1.set_xlabel('Valores Preditos')
        ax1.set_ylabel('Resíduos')
        ax1.set_title('Resíduos vs Valores Preditos')
        ax1.grid(True, alpha=0.3)
        
        # Subplot 2: Q-Q Plot (Normalidade dos resíduos)
        ax2 = self.figure2.add_subplot(2, 2, 2)
        stats.probplot(residuals, dist="norm", plot=ax2)
        ax2.set_title('Q-Q Plot (Teste de Normalidade)')
        
        # Subplot 3: Histograma dos resíduos
        ax3 = self.figure2.add_subplot(2, 2, 3)
        ax3.hist(residuals, bins=10, density=True, alpha=0.7, color='skyblue')
        
        # Sobreposição da distribuição normal
        mu, sigma = stats.norm.fit(residuals)
        x = np.linspace(residuals.min(), residuals.max(), 100)
        p = stats.norm.pdf(x, mu, sigma)
        ax3.plot(x, p, 'r-', linewidth=2, label='Normal ajustada')
        ax3.set_xlabel('Resíduos')
        ax3.set_ylabel('Densidade')
        ax3.set_title('Distribuição dos Resíduos')
        ax3.legend()
        
        # Subplot 4: Resíduos vs Ordem
        ax4 = self.figure2.add_subplot(2, 2, 4)
        ax4.plot(range(1, len(residuals)+1), residuals, 'o-', alpha=0.7)
        ax4.axhline(y=0, color='red', linestyle='--')
        ax4.set_xlabel('Ordem dos Dados')
        ax4.set_ylabel('Resíduos')
        ax4.set_title('Resíduos vs Ordem')
        ax4.grid(True, alpha=0.3)
        
        self.figure2.tight_layout()
        self.canvas2.draw()
        
        # Calcular estatísticas dos resíduos
        self.calculate_residuals_statistics(residuals)
    
    def calculate_residuals_statistics(self, residuals):
        """Calcula estatísticas detalhadas dos resíduos."""
        # Estatísticas básicas
        mean_res = np.mean(residuals)
        std_res = np.std(residuals, ddof=1)
        min_res = np.min(residuals)
        max_res = np.max(residuals)
        
        # Teste de normalidade Shapiro-Wilk
        shapiro_stat, shapiro_p = stats.shapiro(residuals)
        
        # Teste de Durbin-Watson (autocorrelação)
        def durbin_watson(residuals):
            diff = np.diff(residuals)
            return np.sum(diff**2) / np.sum(residuals**2)
        
        dw_stat = durbin_watson(residuals)
        
        # Outliers (usando critério de 2 desvios padrão)
        outliers = np.abs(residuals) > 2 * std_res
        n_outliers = np.sum(outliers)
        
        # Formatação dos resultados
        stats_text = f"ESTATÍSTICAS DOS RESÍDUOS\n"
        stats_text += f"{'='*40}\n"
        stats_text += f"Média dos resíduos: {mean_res:.6f}\n"
        stats_text += f"Desvio padrão: {std_res:.6f}\n"
        stats_text += f"Mínimo: {min_res:.6f}\n"
        stats_text += f"Máximo: {max_res:.6f}\n"
        stats_text += f"Amplitude: {max_res - min_res:.6f}\n"
        stats_text += f"\nTESTE DE NORMALIDADE (Shapiro-Wilk):\n"
        stats_text += f"Estatística W: {shapiro_stat:.6f}\n"
        stats_text += f"Valor p: {shapiro_p:.6f}\n"
        stats_text += f"Resultado: {'Normal' if shapiro_p > 0.05 else 'Não normal'} (α = 0.05)\n"
        stats_text += f"\nTESTE DE AUTOCORRELAÇÃO (Durbin-Watson):\n"
        stats_text += f"Estatística DW: {dw_stat:.6f}\n"
        stats_text += f"Interpretação: "
        if dw_stat < 1.5:
            stats_text += "Autocorrelação positiva"
        elif dw_stat > 2.5:
            stats_text += "Autocorrelação negativa"
        else:
            stats_text += "Sem autocorrelação significativa"
        stats_text += f"\n\nOUTLIERS (|resíduo| > 2σ):\n"
        stats_text += f"Número de outliers: {n_outliers}\n"
        if n_outliers > 0:
            outlier_indices = np.where(outliers)[0]
            stats_text += f"Posições: {outlier_indices + 1}\n"  # +1 para indexação humana
        
        self.residuals_stats.setText(stats_text)
    
    def run_validation_tests(self):
        """Executa testes de validação do modelo."""
        if not hasattr(self, 'regression_results'):
            self.show_error_dialog("Execute primeiro a regressão linear")
            return
        
        results = self.regression_results
        alpha = self.alpha_level.value()
        
        # Teste t para a inclinação (H0: slope = 0)
        t_slope = results['slope'] / results['s_slope']
        t_critical = stats.t.ppf(1 - alpha/2, results['df'])
        p_slope = 2 * (1 - stats.t.cdf(abs(t_slope), results['df']))
        
        # Teste F para a regressão (ANOVA)
        ms_reg = results['ss_tot'] - results['ss_res']  # Soma dos quadrados da regressão
        ms_res = results['ss_res'] / results['df']
        f_stat = ms_reg / ms_res
        f_critical = stats.f.ppf(1 - alpha, 1, results['df'])
        p_f = 1 - stats.f.cdf(f_stat, 1, results['df'])
        
        # Formatação dos resultados
        validation_text = f"TESTES DE VALIDAÇÃO DO MODELO\n"
        validation_text += f"{'='*50}\n"
        validation_text += f"Nível de significância (α): {alpha}\n"
        validation_text += f"Graus de liberdade: {results['df']}\n\n"
        
        validation_text += f"1. TESTE t PARA A INCLINAÇÃO\n"
        validation_text += f"{'-'*30}\n"
        validation_text += f"H₀: β₁ = 0 (não há relação linear)\n"
        validation_text += f"H₁: β₁ ≠ 0 (há relação linear)\n"
        validation_text += f"Estatística t: {t_slope:.6f}\n"
        validation_text += f"t crítico: ±{t_critical:.4f}\n"
        validation_text += f"Valor p: {p_slope:.6e}\n"
        validation_text += f"Decisão: {'Rejeitar H₀' if abs(t_slope) > t_critical else 'Não rejeitar H₀'}\n"
        validation_text += f"Conclusão: {'Há' if abs(t_slope) > t_critical else 'Não há'} relação linear significativa\n\n"
        
        validation_text += f"2. TESTE F PARA A REGRESSÃO (ANOVA)\n"
        validation_text += f"{'-'*30}\n"
        validation_text += f"H₀: O modelo não é significativo\n"
        validation_text += f"H₁: O modelo é significativo\n"
        validation_text += f"Estatística F: {f_stat:.6f}\n"
        validation_text += f"F crítico: {f_critical:.4f}\n"
        validation_text += f"Valor p: {p_f:.6e}\n"
        validation_text += f"Decisão: {'Rejeitar H₀' if f_stat > f_critical else 'Não rejeitar H₀'}\n"
        validation_text += f"Conclusão: O modelo {'é' if f_stat > f_critical else 'não é'} estatisticamente significativo\n\n"
        
        validation_text += f"3. ANÁLISE DE VARIÂNCIA (ANOVA)\n"
        validation_text += f"{'-'*30}\n"
        validation_text += f"Fonte de Variação | GL | SQ | QM | F | p-valor\n"
        validation_text += f"Regressão | 1 | {ms_reg:.6f} | {ms_reg:.6f} | {f_stat:.6f} | {p_f:.6e}\n"
        validation_text += f"Resíduos | {results['df']} | {results['ss_res']:.6f} | {ms_res:.6f} | - | -\n"
        validation_text += f"Total | {results['n']-1} | {results['ss_tot']:.6f} | - | - | -\n"
        
        self.validation_results.setText(validation_text)
        
        # Calcular métricas de qualidade
        self.calculate_quality_metrics()
    
    def calculate_quality_metrics(self):
        """Calcula métricas de qualidade do modelo."""
        if not hasattr(self, 'regression_results'):
            return
        
        results = self.regression_results
        y_pred = results['y_pred']
        
        # Métricas de qualidade
        mae = np.mean(np.abs(results['residuals']))  # Erro Absoluto Médio
        mse = np.mean(results['residuals']**2)  # Erro Quadrático Médio
        rmse = np.sqrt(mse)  # Raiz do Erro Quadrático Médio
        mape = np.mean(np.abs(results['residuals'] / self.y_data)) * 100  # Erro Percentual Absoluto Médio
        
        # Coeficiente de eficiência de Nash-Sutcliffe
        nse = 1 - (results['ss_res'] / results['ss_tot'])
        
        # Bias
        bias = np.mean(results['residuals'])
        
        # Formatação dos resultados
        quality_text = f"MÉTRICAS DE QUALIDADE DO MODELO\n"
        quality_text += f"{'='*40}\n"
        quality_text += f"R² (Coeficiente de Determinação): {results['r_squared']:.6f}\n"
        quality_text += f"R² Ajustado: {1 - (1 - results['r_squared']) * (results['n'] - 1) / results['df']:.6f}\n"
        quality_text += f"Erro Absoluto Médio (MAE): {mae:.6f}\n"
        quality_text += f"Erro Quadrático Médio (MSE): {mse:.6f}\n"
        quality_text += f"Raiz do Erro Quadrático Médio (RMSE): {rmse:.6f}\n"
        quality_text += f"Erro Percentual Absoluto Médio (MAPE): {mape:.2f}%\n"
        quality_text += f"Coeficiente de Nash-Sutcliffe: {nse:.6f}\n"
        quality_text += f"Bias: {bias:.6f}\n"
        quality_text += f"Erro Padrão dos Resíduos: {results['s_yx']:.6f}\n\n"
        
        quality_text += f"INTERPRETAÇÃO:\n"
        quality_text += f"{'-'*20}\n"
        if results['r_squared'] > 0.95:
            quality_text += f"• Excelente ajuste (R² > 0.95)\n"
        elif results['r_squared'] > 0.90:
            quality_text += f"• Bom ajuste (R² > 0.90)\n"
        elif results['r_squared'] > 0.70:
            quality_text += f"• Ajuste moderado (R² > 0.70)\n"
        else:
            quality_text += f"• Ajuste fraco (R² < 0.70)\n"
        
        if mape < 5:
            quality_text += f"• Excelente precisão (MAPE < 5%)\n"
        elif mape < 10:
            quality_text += f"• Boa precisão (MAPE < 10%)\n"
        elif mape < 20:
            quality_text += f"• Precisão moderada (MAPE < 20%)\n"
        else:
            quality_text += f"• Baixa precisão (MAPE > 20%)\n"
        
        self.quality_metrics.setText(quality_text)
    
    def predict_concentration(self):
        """Calcula a concentração baseada no valor observado."""
        if not hasattr(self, 'regression_results'):
            self.show_error_dialog("Execute primeiro a regressão linear")
            return
        
        results = self.regression_results
        y_obs = self.prediction_value.value()
        
        # Calcular concentração (X) a partir de Y observado
        x_pred = (y_obs - results['intercept']) / results['slope']
        
        # Intervalo de confiança para a predição
        t_critical = stats.t.ppf(0.975, results['df'])
        
        # Erro padrão para predição inversa
        s_x = (results['s_yx'] / abs(results['slope'])) * np.sqrt(
            1 + 1/results['n'] + 
            (y_obs - np.mean(self.y_data))**2 / 
            (results['slope']**2 * np.sum((self.x_data - np.mean(self.x_data))**2))
        )
        
        x_ci = t_critical * s_x
        
        # Formatação do resultado
        pred_text = f"PREDIÇÃO DE CONCENTRAÇÃO\n"
        pred_text += f"{'='*30}\n"
        pred_text += f"Valor observado (Y): {y_obs:.6f}\n"
        pred_text += f"Concentração predita (X): {x_pred:.6f}\n"
        pred_text += f"Intervalo de confiança (95%): [{x_pred - x_ci:.6f}, {x_pred + x_ci:.6f}]\n"
        pred_text += f"Margem de erro: ±{x_ci:.6f}\n"
        pred_text += f"Erro relativo: ±{(x_ci/x_pred)*100:.2f}%\n"
        
        self.prediction_result.setText(pred_text)
    
    def calculate_analytical_limits(self):
        """Calcula limites de detecção e quantificação."""
        if not hasattr(self, 'regression_results'):
            self.show_error_dialog("Execute primeiro a regressão linear")
            return
        
        results = self.regression_results
        blank_std = self.blank_std_dev.value()
        n_blanks = self.blank_replicates.value()
        
        # Limite de Detecção (LOD) = 3.3 * σ / S
        # Limite de Quantificação (LOQ) = 10 * σ / S
        # onde σ = desvio padrão do branco e S = sensibilidade (inclinação)
        
        lod = 3.3 * blank_std / results['slope']
        loq = 10 * blank_std / results['slope']
        
        # Sinal correspondente aos limites
        signal_lod = results['slope'] * lod + results['intercept']
        signal_loq = results['slope'] * loq + results['intercept']
        
        # Formatação dos resultados
        limits_text = f"LIMITES ANALÍTICOS\n"
        limits_text += f"{'='*25}\n"
        limits_text += f"Parâmetros utilizados:\n"
        limits_text += f"• Desvio padrão do branco: {blank_std:.6f}\n"
        limits_text += f"• Número de replicatas: {n_blanks}\n"
        limits_text += f"• Sensibilidade (inclinação): {results['slope']:.6f}\n\n"
        
        limits_text += f"RESULTADOS:\n"
        limits_text += f"Limite de Detecção (LOD):\n"
        limits_text += f"  Concentração: {lod:.6f}\n"
        limits_text += f"  Sinal correspondente: {signal_lod:.6f}\n\n"
        
        limits_text += f"Limite de Quantificação (LOQ):\n"
        limits_text += f"  Concentração: {loq:.6f}\n"
        limits_text += f"  Sinal correspondente: {signal_loq:.6f}\n\n"
        
        limits_text += f"INTERPRETAÇÃO:\n"
        limits_text += f"• LOD: Menor concentração detectável\n"
        limits_text += f"• LOQ: Menor concentração quantificável com precisão adequada\n"
        limits_text += f"• Razão LOQ/LOD: {loq/lod:.1f} (deve ser ≈ 3.0)\n"
        
        self.limits_result.setText(limits_text)
    
    def show_error_dialog(self, message):
        """Mostra uma caixa de diálogo de erro."""
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Erro")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
