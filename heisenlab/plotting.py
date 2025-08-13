from __future__ import annotations

from typing import Iterable, Tuple

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT


class MplCanvas(FigureCanvas):
    def __init__(self, width: float = 14.0, height: float = 8.0, dpi: int = 100):
        self.figure = Figure(figsize=(width, height), dpi=dpi, facecolor='white')
        self.ax = self.figure.add_subplot(111)
        super().__init__(self.figure)
        
        # Configurações iniciais para melhor aparência
        self.figure.patch.set_facecolor('white')
        self.ax.set_facecolor('white')
        
        # Melhorar layout para aproveitar melhor o espaço
        self.figure.tight_layout(pad=1.5)

    def clear(self):
        self.ax.clear()
        self.draw_idle()


class FullScreenPlotDialog(QDialog):
    """Janela para visualizar gráfico em tela cheia"""
    
    def __init__(self, parent=None, figure=None):
        super().__init__(parent)
        self.setWindowTitle("Gráfico - Visualização em Tela Cheia")
        self.setModal(False)
        
        # Configurar janela
        self.resize(1200, 800)
        self.setWindowState(Qt.WindowMaximized)
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Barra de informações
        info_layout = QHBoxLayout()
        self.info_label = QLabel("Use os controles da barra de ferramentas para navegar, ampliar e salvar o gráfico")
        self.info_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        
        close_btn = QPushButton("✕ Fechar")
        close_btn.clicked.connect(self.close)
        close_btn.setMaximumWidth(80)
        
        info_layout.addWidget(self.info_label)
        info_layout.addStretch()
        info_layout.addWidget(close_btn)
        
        # Canvas para o gráfico
        self.canvas = MplCanvas(width=16, height=10, dpi=100)
        
        # Barra de ferramentas do matplotlib
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        
        # Se uma figura foi fornecida, copiar os dados
        if figure is not None:
            self._copy_figure_data(figure)
        
        # Adicionar widgets ao layout
        layout.addLayout(info_layout)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # Configurar teclas de atalho
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QPushButton {
                padding: 5px 10px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #e7e7e7;
            }
        """)
    
    def _copy_figure_data(self, source_figure):
        """Copia dados de uma figura existente"""
        try:
            # Limpar canvas atual
            self.canvas.ax.clear()
            
            # Copiar dados do gráfico original
            source_ax = source_figure.axes[0] if source_figure.axes else None
            
            if source_ax:
                # Copiar todas as linhas plotadas
                for line in source_ax.get_lines():
                    self.canvas.ax.plot(line.get_xdata(), line.get_ydata(), 
                                      color=line.get_color(), 
                                      linestyle=line.get_linestyle(),
                                      marker=line.get_marker(),
                                      markersize=line.get_markersize(),
                                      linewidth=line.get_linewidth(),
                                      alpha=line.get_alpha(),
                                      label=line.get_label())
                
                # Copiar configurações dos eixos
                self.canvas.ax.set_xlabel(source_ax.get_xlabel())
                self.canvas.ax.set_ylabel(source_ax.get_ylabel())
                self.canvas.ax.set_title(source_ax.get_title())
                
                # Copiar limites dos eixos
                self.canvas.ax.set_xlim(source_ax.get_xlim())
                self.canvas.ax.set_ylim(source_ax.get_ylim())
                
                # Copiar grid
                self.canvas.ax.grid(source_ax.get_lines()[0].axes.xaxis._gridOnMajor if source_ax.get_lines() else True, alpha=0.3)
                
                # Copiar legenda se existir
                source_legend = source_ax.get_legend()
                if source_legend:
                    self.canvas.ax.legend(loc='best', fontsize=11)
            
            # Ajustar layout e redesenhar
            self.canvas.figure.tight_layout(pad=2.0)
            self.canvas.draw()
            
        except Exception as e:
            print(f"Erro ao copiar figura: {e}")
            # Se falhar, apenas mostrar um gráfico vazio
            self.canvas.ax.text(0.5, 0.5, 'Erro ao carregar gráfico', 
                              horizontalalignment='center', verticalalignment='center',
                              transform=self.canvas.ax.transAxes)
            self.canvas.draw()
    
    def keyPressEvent(self, event):
        """Teclas de atalho"""
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showMaximized()
            else:
                self.showFullScreen()
        super().keyPressEvent(event)
