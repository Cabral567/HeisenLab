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

from ..plotting import MplCanvas, FullScreenPlotDialog
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
import matplotlib.pyplot as plt

# Bibliotecas científicas especializadas
try:
    from scipy import signal
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.decomposition import PCA
    from lmfit import models
    HAS_SCIPY = True
    HAS_SKLEARN = True
    HAS_LMFIT = True
except ImportError:
    HAS_SCIPY = False
    HAS_SKLEARN = False
    HAS_LMFIT = False

try:
    import peakutils
    HAS_PEAKUTILS = True
except ImportError:
    HAS_PEAKUTILS = False

warnings.filterwarnings('ignore')


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
        self.tabs.addTab(self.basic_tab, "Análise Básica")

        # Aba 2: Voltametria Avançada
        if HAS_SCIPY or HAS_LMFIT:
            self.advanced_tab = self._create_advanced_voltammetry_tab()
            self.tabs.addTab(self.advanced_tab, "Voltametria Avançada")

        # Aba 3: Processamento de Sinal
        if HAS_SCIPY:
            self.signal_tab = self._create_signal_processing_tab()
            self.tabs.addTab(self.signal_tab, "Processamento de Sinal")

        # Aba 4: Análise Estatística
        if HAS_SKLEARN:
            self.stats_tab = self._create_statistical_analysis_tab()
            self.tabs.addTab(self.stats_tab, "Análise Estatística")

        # Layout principal
        layout.addWidget(file_group)
        layout.addWidget(self.tabs)

        # Controles de visualização do gráfico
        viz_group = QGroupBox("Controles de Visualização")
        viz_layout = QHBoxLayout(viz_group)

        self.fullscreen_btn = QPushButton("Tela Cheia")
        self.fullscreen_btn.clicked.connect(self._show_fullscreen_plot)
        self.fullscreen_btn.setToolTip("Abrir gráfico em janela separada (F11)")

        self.refresh_btn = QPushButton("Atualizar")
        self.refresh_btn.clicked.connect(self._refresh_plot)
        self.refresh_btn.setToolTip("Atualizar visualização do gráfico")

        self.zoom_fit_btn = QPushButton("Ajustar Zoom")
        self.zoom_fit_btn.clicked.connect(self._zoom_fit)
        self.zoom_fit_btn.setToolTip("Ajustar zoom para mostrar todos os dados")

        viz_layout.addWidget(self.fullscreen_btn)
        viz_layout.addWidget(self.refresh_btn)
        viz_layout.addWidget(self.zoom_fit_btn)
        viz_layout.addStretch()

        layout.addWidget(viz_group)
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

        self.auto_detect_btn = QPushButton("Detectar Pares Potencial-Corrente")
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

        self.plot_btn = QPushButton("Plotar Voltamogramas")
        self.plot_btn.clicked.connect(self._plot_voltammograms)
        self.plot_btn.setEnabled(False)
        fit_layout.addWidget(self.plot_btn, 1, 0, 1, 2)

        # Botão de teste (temporário)
        self.test_btn = QPushButton("Teste Gráfico")
        self.test_btn.clicked.connect(self._test_plot)
        fit_layout.addWidget(self.test_btn, 2, 0, 1, 2)

        layout.addWidget(detection_group)
        layout.addWidget(fit_group)
        layout.addStretch()

        return tab

    def _create_advanced_voltammetry_tab(self):
        """Cria aba de voltametria avançada com análises específicas"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Análise de Picos
        peak_group = QGroupBox("Análise de Picos")
        peak_layout = QGridLayout(peak_group)

        peak_layout.addWidget(QLabel("Altura mínima:"), 0, 0)
        self.peak_height_spin = QDoubleSpinBox()
        self.peak_height_spin.setRange(0.001, 1000.0)
        self.peak_height_spin.setValue(0.1)
        self.peak_height_spin.setSuffix("µA")
        peak_layout.addWidget(self.peak_height_spin, 0, 1)

        peak_layout.addWidget(QLabel("Distância mínima:"), 1, 0)
        self.peak_distance_spin = QSpinBox()
        self.peak_distance_spin.setRange(1, 100)
        self.peak_distance_spin.setValue(10)
        self.peak_distance_spin.setSuffix("pontos")
        peak_layout.addWidget(self.peak_distance_spin, 1, 1)

        self.find_peaks_btn = QPushButton("Encontrar Picos")
        self.find_peaks_btn.clicked.connect(self._find_peaks)
        peak_layout.addWidget(self.find_peaks_btn, 2, 0, 1, 2)

        # Análise Cinética
        kinetic_group = QGroupBox("Análise Cinética")
        kinetic_layout = QGridLayout(kinetic_group)

        kinetic_layout.addWidget(QLabel("Velocidade de varredura (V/s):"), 0, 0)
        self.scan_rate_spin = QDoubleSpinBox()
        self.scan_rate_spin.setRange(0.001, 10.0)
        self.scan_rate_spin.setValue(0.1)
        kinetic_layout.addWidget(self.scan_rate_spin, 0, 1)

        self.kinetic_analysis_btn = QPushButton("Análise Randles-Sevcik")
        self.kinetic_analysis_btn.clicked.connect(self._kinetic_analysis)
        kinetic_layout.addWidget(self.kinetic_analysis_btn, 1, 0, 1, 2)

        layout.addWidget(peak_group)
        layout.addWidget(kinetic_group)
        layout.addStretch()

        return tab

    def _create_signal_processing_tab(self):
        """Cria aba de processamento de sinal"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Filtros
        filter_group = QGroupBox("Filtros")
        filter_layout = QGridLayout(filter_group)

        filter_layout.addWidget(QLabel("Tipo de filtro:"), 0, 0)
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "Savitzky-Golay",
            "Mediana",
            "Gaussiano"
        ])
        filter_layout.addWidget(self.filter_combo, 0, 1)

        filter_layout.addWidget(QLabel("Parâmetro:"), 1, 0)
        self.filter_param_spin = QSpinBox()
        self.filter_param_spin.setRange(3, 51)
        self.filter_param_spin.setValue(11)
        filter_layout.addWidget(self.filter_param_spin, 1, 1)

        self.apply_filter_btn = QPushButton("Aplicar Filtro")
        self.apply_filter_btn.clicked.connect(self._apply_filter)
        filter_layout.addWidget(self.apply_filter_btn, 2, 0, 1, 2)

        layout.addWidget(filter_group)
        layout.addStretch()

        return tab

    def _create_statistical_analysis_tab(self):
        """Cria aba de análise estatística"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # PCA
        pca_group = QGroupBox("Análise de Componentes Principais (PCA)")
        pca_layout = QGridLayout(pca_group)

        pca_layout.addWidget(QLabel("Componentes:"), 0, 0)
        self.pca_components_spin = QSpinBox()
        self.pca_components_spin.setRange(2, 10)
        self.pca_components_spin.setValue(2)
        pca_layout.addWidget(self.pca_components_spin, 0, 1)

        self.pca_btn = QPushButton("Executar PCA")
        self.pca_btn.clicked.connect(self._perform_pca)
        pca_layout.addWidget(self.pca_btn, 1, 0, 1, 2)

        # Estatísticas Descritivas
        stats_group = QGroupBox("Estatísticas Descritivas")
        stats_layout = QVBoxLayout(stats_group)

        self.stats_btn = QPushButton("📋 Gerar Relatório Estatístico")
        self.stats_btn.clicked.connect(self._generate_stats_report)
        stats_layout.addWidget(self.stats_btn)

        self.stats_text = QTextEdit()
        self.stats_text.setMaximumHeight(200)
        stats_layout.addWidget(self.stats_text)

        # Exportação
        export_group = QGroupBox("Exportação")
        export_layout = QGridLayout(export_group)

        self.export_excel_btn = QPushButton("Exportar Excel")
        self.export_excel_btn.clicked.connect(self._export_excel)
        export_layout.addWidget(self.export_excel_btn, 0, 0)

        self.export_csv_btn = QPushButton("Exportar CSV")
        self.export_csv_btn.clicked.connect(self._export_csv)
        export_layout.addWidget(self.export_csv_btn, 0, 1)

        self.export_plot_btn = QPushButton("Exportar Gráfico")
        self.export_plot_btn.clicked.connect(self._export_plot)
        export_layout.addWidget(self.export_plot_btn, 1, 0, 1, 2)

        layout.addWidget(pca_group)
        layout.addWidget(stats_group)
        layout.addWidget(export_group)
        layout.addStretch()

        return tab

    # === MÉTODOS DA ABA ANÁLISE BÁSICA ===

    def _load_file(self):
        """Carrega arquivo Excel com dados de voltametria"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Carregar arquivo Excel", "",
            "Excel files (*.xlsx *.xls);;All files (*.*)"
        )

        if file_path:
            try:
                # Carregar Excel
                self.df = pd.read_excel(file_path, header=0)

                # Extrair nomes das amostras se houver padrão
                self.sample_names = self._extract_sample_names(self.df.columns)

                self.file_label.setText(f"Arquivo carregado: {file_path.split('/')[-1]}")
                self.file_label.setStyleSheet("color: #2e7d32; font-weight: bold;")
                self.info_label.setText(f"📊 {len(self.df.columns)} colunas, {len(self.df)} linhas")

                # Resetar componentes relacionados a dados
                if hasattr(self, 'pairs_list'):
                    self.pairs_list.clear()
                if hasattr(self, 'plot_btn'):
                    self.plot_btn.setEnabled(False)

            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao carregar arquivo:\n{str(e)}")
                self.file_label.setText("❌ Erro no carregamento")
                self.file_label.setStyleSheet("color: #d32f2f;")

    def _extract_sample_names(self, columns):
        """Extrai nomes das amostras dos cabeçalhos das colunas"""
        # Procurar padrões como "Sample1_Potential", "Amostra1_Corrente", etc.
        sample_names = set()
        for col in columns:
            # Padrões comuns
            if '_' in col:
                parts = col.split('_')
                if len(parts) >= 2:
                    potential_sample = parts[0]
                    sample_names.add(potential_sample)

        if sample_names:
            return sorted(list(sample_names))
        return None

    def _auto_detect_pairs(self):
        """Detecta automaticamente pares de colunas Potencial-Corrente"""
        if self.df is None:
            # Se não há arquivo, criar dados de teste
            reply = QMessageBox.question(self, "Sem dados",
                "Nenhum arquivo carregado. Deseja criar dados de teste?",
                QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self._create_test_data()
                return
            else:
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

        # Se não encontrou pares, dar sugestões
        if len(pairs) == 0:
            msg = "❌ Nenhum par Potencial-Corrente detectado!\n\n"
            msg += "Colunas disponíveis:\n"
            for i, col in enumerate(self.df.columns):
                msg += f"{i+1}. {col}\n"
            msg += "\nVerifique se as colunas têm nomes como:\n"
            msg += "- Potencial, Voltage, V, E\n"
            msg += "- Corrente, Current, I, A"

            QMessageBox.information(self, "Info - Detecção de Pares", msg)

    def _create_test_data(self):
        """Cria dados de teste para demonstração"""
        try:
            # Criar dados de voltametria simulados
            potential = np.linspace(-1.5, 1.5, 100)

            # Amostra 1: Pico em 0.2V
            current1 = 2.5 * np.exp(-((potential - 0.2) / 0.3) ** 2) + np.random.normal(0, 0.05, 100)

            # Amostra 2: Pico em -0.3V
            current2 = 3.2 * np.exp(-((potential + 0.3) / 0.25) ** 2) + np.random.normal(0, 0.07, 100)

            # Amostra 3: Dois picos
            current3 = (1.8 * np.exp(-((potential - 0.5) / 0.2) ** 2) +
                       2.1 * np.exp(-((potential + 0.7) / 0.3) ** 2) +
                       np.random.normal(0, 0.04, 100))

            # Criar DataFrame
            self.df = pd.DataFrame({
                'Potencial_1': potential,
                'Corrente_1': current1,
                'Potencial_2': potential,
                'Corrente_2': current2,
                'Potencial_3': potential,
                'Corrente_3': current3
            })

            self.sample_names = ['Teste_1', 'Teste_2', 'Teste_3']

            self.file_label.setText("✅ Dados de teste criados")
            self.file_label.setStyleSheet("color: #2e7d32; font-weight: bold;")
            self.info_label.setText("📊 Dados de teste carregados: 3 amostras simuladas")

            # Auto-detectar os pares criados
            pairs = self._detect_voltage_pairs_from_structure(self.df)

            self.pairs_list.clear()
            for i, (potential_col, current_col) in enumerate(pairs):
                sample_name = self.sample_names[i] if i < len(self.sample_names) else f"Amostra {i+1}"
                item_text = f"{sample_name}: {potential_col} vs {current_col}"
                self.pairs_list.addItem(item_text)

            self.voltage_pairs = pairs
            self.plot_btn.setEnabled(True)
            self.info_label.setText(f"✅ {len(pairs)} pares de teste detectados")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao criar dados de teste: {str(e)}")
            print(f"Erro detalhado: {e}")
            import traceback
            traceback.print_exc()

    def _detect_voltage_pairs_from_structure(self, df):
        """Detecta pares Potencial-Corrente baseado na estrutura das colunas"""
        pairs = []
        columns = df.columns.tolist()

        # Estratégia 1: Buscar padrões com palavras-chave
        potential_keywords = ['potential', 'potencial', 'voltage', 'volt', 'v', 'e']
        current_keywords = ['current', 'corrente', 'ampere', 'amp', 'i', 'a']

        potential_cols = []
        current_cols = []

        for col in columns:
            col_lower = col.lower()

            # Verificar se é coluna de potencial
            if any(keyword in col_lower for keyword in potential_keywords):
                potential_cols.append(col)
            # Verificar se é coluna de corrente
            elif any(keyword in col_lower for keyword in current_keywords):
                current_cols.append(col)

        # Estratégia 2: Se não encontrou com palavras-chave, usar posição alternada
        if not potential_cols and not current_cols:
            # Assumir que colunas estão alternadas: Potencial, Corrente, Potencial, Corrente...
            for i in range(0, len(columns) - 1, 2):
                potential_cols.append(columns[i])
                if i + 1 < len(columns):
                    current_cols.append(columns[i + 1])

        # Parear as colunas
        min_len = min(len(potential_cols), len(current_cols))
        for i in range(min_len):
            pairs.append((potential_cols[i], current_cols[i]))

        return pairs

    def _plot_voltammograms(self):
        """Plota voltamogramas com ajuste polinomial"""
        if not hasattr(self, 'voltage_pairs'):
            QMessageBox.warning(self, "Erro", "Detecte os pares primeiro!")
            return

        self._plot_voltage_pairs(self.voltage_pairs, degree=self.degree_spin.value())

    def _plot_voltage_pairs(self, pairs, degree=4):
        """Plota pares de voltagem com ajuste polinomial"""
        self.canvas.ax.clear()

        colors = plt.cm.Set1(np.linspace(0, 1, len(pairs)))

        for i, (potential_col, current_col) in enumerate(pairs):
            color = colors[i]

            # Extrair dados
            potential = self.df[potential_col].dropna().values
            current = self.df[current_col].dropna().values

            # Garantir que tenham o mesmo tamanho
            min_len = min(len(potential), len(current))
            potential = potential[:min_len]
            current = current[:min_len]

            if len(potential) == 0:
                continue

            # Plot pontos experimentais
            label_exp = f'Amostra {i+1}' if self.sample_names is None else self.sample_names[i] if i < len(self.sample_names) else f'Amostra {i+1}'

            self.canvas.ax.plot(potential, current, 'o', color=color,
                                alpha=0.7, markersize=4, label=f'Exp. {label_exp}')

            # Ajuste polinomial
            try:
                coeffs = np.polyfit(potential, current, degree)
                potential_fit = np.linspace(potential.min(), potential.max(), 300)
                current_fit = np.polyval(coeffs, potential_fit)

                self.canvas.ax.plot(potential_fit, current_fit, '-', color=color,
                                    linewidth=2, alpha=0.8, label=f'Ajuste Poli. {label_exp}')

            except Exception as e:
                print(f"Erro no ajuste polinomial para {potential_col}: {e}")

        self._configure_plot()
        self.info_label.setText(f"✅ {len(pairs)} voltamogramas plotados com ajuste polinomial (grau {degree})")

    def _configure_plot(self):
        """Configura aparência do gráfico"""
        ax = self.canvas.ax

        # Labels e título
        ax.set_xlabel('Potencial (V)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Corrente (µA)', fontsize=12, fontweight='bold')
        ax.set_title('Voltamogramas', fontsize=14, fontweight='bold', pad=20)

        # Grid
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

        # Estilo dos eixos
        ax.tick_params(axis='both', which='major', labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(1.2)
        ax.spines['bottom'].set_linewidth(1.2)

        # Configurar legenda
        self._configure_legend(ax, "Direita")

        # Ajustar layout para acomodar legenda
        plt.subplots_adjust(right=0.75)

        self.canvas.draw()

    def _configure_legend(self, ax, legend_pos):
        """Configura a legenda do gráfico"""
        if not ax.get_legend_handles_labels()[0]:  # Se não há elementos para legenda
            return

        if legend_pos == "Direita":
            legend = ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left',
                              fontsize=10, frameon=True, fancybox=False, shadow=False,
                              edgecolor='black', facecolor='white')
        else:  # Automático
            legend = ax.legend(loc='best', fontsize=10, frameon=True,
                              fancybox=False, shadow=False, edgecolor='black', facecolor='white')

    # === MÉTODOS DAS ABAS AVANÇADAS (apenas stubs se bibliotecas não disponíveis) ===

    def _find_peaks(self):
        """Encontra picos nos voltamogramas"""
        if not HAS_SCIPY:
            QMessageBox.warning(self, "Funcionalidade Indisponível",
                "Instale 'scipy' para usar esta funcionalidade:\npip install scipy")
            return

        QMessageBox.information(self, "Info", "Funcionalidade de detecção de picos em desenvolvimento")

    def _kinetic_analysis(self):
        """Análise cinética Randles-Sevcik"""
        QMessageBox.information(self, "Info", "Análise cinética em desenvolvimento")

    def _apply_filter(self):
        """Aplica filtro nos dados"""
        if not HAS_SCIPY:
            QMessageBox.warning(self, "Funcionalidade Indisponível",
                "Instale 'scipy' para usar esta funcionalidade:\npip install scipy")
            return

        QMessageBox.information(self, "Info", "Filtros em desenvolvimento")

    def _perform_pca(self):
        """Realiza análise PCA"""
        if not HAS_SKLEARN:
            QMessageBox.warning(self, "Funcionalidade Indisponível",
                "Instale 'scikit-learn' para usar esta funcionalidade:\npip install scikit-learn")
            return

        QMessageBox.information(self, "Info", "PCA em desenvolvimento")

    def _generate_stats_report(self):
        """Gera relatório estatístico básico"""
        if self.df is None:
            QMessageBox.warning(self, "Erro", "Carregue dados primeiro!")
            return

        report = "📈 RELATÓRIO ESTATÍSTICO BÁSICO\n"
        report += "=" * 50 + "\n\n"
        report += f"Arquivo carregado com {len(self.df.columns)} colunas e {len(self.df)} linhas\n\n"

        for col in self.df.columns:
            if self.df[col].dtype in ['float64', 'int64']:
                data = self.df[col].dropna()
                if len(data) > 0:
                    report += f"{col}:\n"
                    report += f"Média: {data.mean():.4f}\n"
                    report += f"Desvio: {data.std():.4f}\n"
                    report += f"Min-Max: {data.min():.4f} - {data.max():.4f}\n\n"

        self.stats_text.setPlainText(report)
        self.info_label.setText("✅ Relatório estatístico gerado")

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

    # === MÉTODOS DE CONTROLE DE VISUALIZAÇÃO ===

    def _show_fullscreen_plot(self):
        """Abre gráfico em janela de tela cheia"""
        try:
            # Criar e mostrar janela em tela cheia
            self.fullscreen_dialog = FullScreenPlotDialog(self, self.canvas.figure)
            self.fullscreen_dialog.show()
            self.info_label.setText("🔍 Gráfico aberto em tela cheia - Pressione ESC para fechar")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir tela cheia: {str(e)}")

    def _refresh_plot(self):
        """Atualiza a visualização do gráfico"""
        try:
            # Redesenhar canvas
            self.canvas.figure.tight_layout(pad=1.5)
            self.canvas.draw()
            self.info_label.setText("🔄 Gráfico atualizado")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao atualizar: {str(e)}")

    def _zoom_fit(self):
        """Ajusta zoom para mostrar todos os dados"""
        try:
            # Auto-escalar eixos
            self.canvas.ax.relim()
            self.canvas.ax.autoscale_view()
            self.canvas.draw()
            self.info_label.setText("Zoom ajustado para todos os dados")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro no zoom: {str(e)}")

    def keyPressEvent(self, event):
        """Teclas de atalho para controles rápidos"""
        try:
            from PySide6.QtCore import Qt

            if event.key() == Qt.Key_F11:
                self._show_fullscreen_plot()
            elif event.key() == Qt.Key_F5:
                self._refresh_plot()
            elif event.key() == Qt.Key_F:
                self._zoom_fit()
            else:
                super().keyPressEvent(event)
        except:
            super().keyPressEvent(event)

    def _test_plot(self):
        """Método de teste para verificar se o gráfico funciona"""
        try:
            # Limpar gráfico
            self.canvas.ax.clear()

            # Criar dados de teste
            x = np.linspace(-2, 2, 100)
            y1 = np.exp(-x ** 2) * np.cos(5 * x)  # Curva tipo voltamograma
            y2 = 0.8 * np.exp(-(x - 0.5) ** 2) * np.sin(3 * x)  # Segunda curva

            # Plotar dados de teste
            self.canvas.ax.plot(x, y1, 'o-', label='Teste Amostra 1', markersize=3, alpha=0.7)
            self.canvas.ax.plot(x, y2, 's-', label='Teste Amostra 2', markersize=3, alpha=0.7)

            # Configurar gráfico
            self.canvas.ax.set_xlabel('Potencial (V)', fontsize=12, fontweight='bold')
            self.canvas.ax.set_ylabel('Corrente (µA)', fontsize=12, fontweight='bold')
            self.canvas.ax.set_title('Teste - Voltamogramas Simulados', fontsize=14, fontweight='bold')
            self.canvas.ax.grid(True, alpha=0.3)
            self.canvas.ax.legend()

            # Atualizar canvas
            self.canvas.figure.tight_layout()
            self.canvas.draw()

            self.info_label.setText("🧪 Teste de gráfico executado com sucesso!")

        except Exception as e:
            self.info_label.setText(f"❌ Erro no teste: {str(e)}")
            print(f"Erro detalhado no teste: {e}")
            import traceback
            traceback.print_exc()
