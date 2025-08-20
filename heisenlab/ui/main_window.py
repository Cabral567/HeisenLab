from __future__ import annotations

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget

from .calculations_tab import CalculationsTab
from .calibration_tab import VoltammogramTab
from .properties_tab import PropertiesTab
from .statistics_tab import StatisticsTab
from .chemical_draw_tab import ChemicalDrawTab
from .periodic_table_tab_final import PeriodicTableTabFinal
from .regression_analysis_tab import RegressionAnalysisTab
from .instrumental_methods_tab import InstrumentalMethodsTab
from .solution_analysis_tab import SolutionAnalysisTab
from .spectroscopy_analysis_tab import SpectroscopyAnalysisTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HeisenLab")

        tabs = QTabWidget()
        tabs.addTab(CalculationsTab(), "Cálculos")
        tabs.addTab(VoltammogramTab(), "Voltamograma")
        tabs.addTab(PropertiesTab(), "Propriedades e Conversões")
        tabs.addTab(StatisticsTab(), "Estatística")
        tabs.addTab(RegressionAnalysisTab(), "Regressão Linear")
        tabs.addTab(InstrumentalMethodsTab(), "Métodos Instrumentais")
        tabs.addTab(SolutionAnalysisTab(), "Análise de Soluções")
        tabs.addTab(SpectroscopyAnalysisTab(), "Análise Espectroscópica")
        tabs.addTab(ChemicalDrawTab(), "Desenho Químico")
        tabs.addTab(PeriodicTableTabFinal(), "Tabela Periódica")

        self.setCentralWidget(tabs)
        self.resize(1200, 800)  # Janela maior para melhor visualização
        self.setMinimumSize(800, 600)  # Tamanho mínimo


def run():
    app = QApplication.instance() or QApplication(sys.argv)
    w = MainWindow()
    w.show()
    return app.exec()
