"""
Aba da Tabela Periódica com visualização 3D dos elementos usando Mendeleev
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                               QPushButton, QLabel, QTabWidget, QFrame, QSlider, 
                               QCheckBox, QComboBox, QSpinBox, QTextEdit, QGroupBox,
                               QSplitter, QScrollArea, QFormLayout, QLineEdit,
                               QButtonGroup, QRadioButton)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPainter, QPen, QBrush, QColor

import numpy as np

# Importações da biblioteca Mendeleev
try:
    from mendeleev import element
    HAS_MENDELEEV = True
except ImportError:
    HAS_MENDELEEV = False
    print("Biblioteca Mendeleev não encontrada. Usando dados limitados.")

# Importações opcionais para 3D
try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    from mpl_toolkits.mplot3d import Axes3D
    HAS_MATPLOTLIB_3D = True
except ImportError:
    HAS_MATPLOTLIB_3D = False
    FigureCanvas = QWidget  # Fallback

def get_element_data(atomic_number):
    """Obtém dados do elemento usando Mendeleev ou dados de fallback"""
    if HAS_MENDELEEV:
        try:
            elem = element(atomic_number)
            
            # Tratar oxidation_states especialmente
            oxidation_states = getattr(elem, 'oxidation_states', None)
            if oxidation_states and hasattr(oxidation_states, '__call__'):
                # Se for um método, chama ele
                try:
                    oxidation_states = oxidation_states()
                except:
                    oxidation_states = None
            elif oxidation_states and hasattr(oxidation_states, '__iter__'):
                # Se for iterável, converte para lista
                try:
                    oxidation_states = list(oxidation_states)
                except:
                    oxidation_states = None
            
            return {
                'symbol': elem.symbol,
                'name': elem.name,
                'mass': round(elem.atomic_weight or 0, 3),
                'electrons': elem.atomic_number,
                'period': elem.period,
                'group': elem.group,
                'block': getattr(elem, 'block', ''),
                'density': getattr(elem, 'density', None),
                'melting_point': getattr(elem, 'melting_point', None),
                'boiling_point': getattr(elem, 'boiling_point', None),
                'electron_configuration': getattr(elem, 'electron_configuration', ''),
                'atomic_radius': getattr(elem, 'atomic_radius', None),
                'covalent_radius': getattr(elem, 'covalent_radius', None),
                'electronegativity': getattr(elem, 'electronegativity', None),
                'ionization_energy': getattr(elem, 'ionization_energy', None),
                'electron_affinity': getattr(elem, 'electron_affinity', None),
                'oxidation_states': oxidation_states,
                'discovered': getattr(elem, 'discovered', None),
                'discoverer': getattr(elem, 'discoverers', None),
                'crystal_structure': getattr(elem, 'crystal_structure', None),
                'thermal_conductivity': getattr(elem, 'thermal_conductivity', None),
                'electrical_resistivity': getattr(elem, 'electrical_resistivity', None),
                'magnetic_susceptibility': getattr(elem, 'magnetic_susceptibility', None),
                'abundance_crust': getattr(elem, 'abundance_crust', None),
                'abundance_sea': getattr(elem, 'abundance_sea', None),
                'vdw_radius': getattr(elem, 'vdw_radius', None),
                'metallic_radius': getattr(elem, 'metallic_radius', None)
            }
        except Exception as e:
            print(f"Erro ao obter dados do elemento {atomic_number}: {e}")
            pass
    
    # Dados de fallback para os primeiros 118 elementos
    fallback_data = {
        1: {'symbol': 'H', 'name': 'Hidrogênio', 'mass': 1.008, 'period': 1, 'group': 1, 'block': 's'},
        2: {'symbol': 'He', 'name': 'Hélio', 'mass': 4.003, 'period': 1, 'group': 18, 'block': 's'},
        3: {'symbol': 'Li', 'name': 'Lítio', 'mass': 6.94, 'period': 2, 'group': 1, 'block': 's'},
        4: {'symbol': 'Be', 'name': 'Berílio', 'mass': 9.012, 'period': 2, 'group': 2, 'block': 's'},
        5: {'symbol': 'B', 'name': 'Boro', 'mass': 10.81, 'period': 2, 'group': 13, 'block': 'p'},
        6: {'symbol': 'C', 'name': 'Carbono', 'mass': 12.01, 'period': 2, 'group': 14, 'block': 'p'},
        7: {'symbol': 'N', 'name': 'Nitrogênio', 'mass': 14.01, 'period': 2, 'group': 15, 'block': 'p'},
        8: {'symbol': 'O', 'name': 'Oxigênio', 'mass': 16.00, 'period': 2, 'group': 16, 'block': 'p'},
        9: {'symbol': 'F', 'name': 'Flúor', 'mass': 19.00, 'period': 2, 'group': 17, 'block': 'p'},
        10: {'symbol': 'Ne', 'name': 'Neônio', 'mass': 20.18, 'period': 2, 'group': 18, 'block': 'p'},
        11: {'symbol': 'Na', 'name': 'Sódio', 'mass': 22.99, 'period': 3, 'group': 1, 'block': 's'},
        12: {'symbol': 'Mg', 'name': 'Magnésio', 'mass': 24.31, 'period': 3, 'group': 2, 'block': 's'},
        13: {'symbol': 'Al', 'name': 'Alumínio', 'mass': 26.98, 'period': 3, 'group': 13, 'block': 'p'},
        14: {'symbol': 'Si', 'name': 'Silício', 'mass': 28.09, 'period': 3, 'group': 14, 'block': 'p'},
        15: {'symbol': 'P', 'name': 'Fósforo', 'mass': 30.97, 'period': 3, 'group': 15, 'block': 'p'},
        16: {'symbol': 'S', 'name': 'Enxofre', 'mass': 32.07, 'period': 3, 'group': 16, 'block': 'p'},
        17: {'symbol': 'Cl', 'name': 'Cloro', 'mass': 35.45, 'period': 3, 'group': 17, 'block': 'p'},
        18: {'symbol': 'Ar', 'name': 'Argônio', 'mass': 39.95, 'period': 3, 'group': 18, 'block': 'p'},
        19: {'symbol': 'K', 'name': 'Potássio', 'mass': 39.10, 'period': 4, 'group': 1, 'block': 's'},
        20: {'symbol': 'Ca', 'name': 'Cálcio', 'mass': 40.08, 'period': 4, 'group': 2, 'block': 's'},
        # Metais de transição período 4
        21: {'symbol': 'Sc', 'name': 'Escândio', 'mass': 44.96, 'period': 4, 'group': 3, 'block': 'd'},
        22: {'symbol': 'Ti', 'name': 'Titânio', 'mass': 47.87, 'period': 4, 'group': 4, 'block': 'd'},
        23: {'symbol': 'V', 'name': 'Vanádio', 'mass': 50.94, 'period': 4, 'group': 5, 'block': 'd'},
        24: {'symbol': 'Cr', 'name': 'Cromo', 'mass': 51.99, 'period': 4, 'group': 6, 'block': 'd'},
        25: {'symbol': 'Mn', 'name': 'Manganês', 'mass': 54.94, 'period': 4, 'group': 7, 'block': 'd'},
        26: {'symbol': 'Fe', 'name': 'Ferro', 'mass': 55.85, 'period': 4, 'group': 8, 'block': 'd'},
        27: {'symbol': 'Co', 'name': 'Cobalto', 'mass': 58.93, 'period': 4, 'group': 9, 'block': 'd'},
        28: {'symbol': 'Ni', 'name': 'Níquel', 'mass': 58.69, 'period': 4, 'group': 10, 'block': 'd'},
        29: {'symbol': 'Cu', 'name': 'Cobre', 'mass': 63.55, 'period': 4, 'group': 11, 'block': 'd'},
        30: {'symbol': 'Zn', 'name': 'Zinco', 'mass': 65.38, 'period': 4, 'group': 12, 'block': 'd'},
        # Continuação período 4
        31: {'symbol': 'Ga', 'name': 'Gálio', 'mass': 69.72, 'period': 4, 'group': 13, 'block': 'p'},
        32: {'symbol': 'Ge', 'name': 'Germânio', 'mass': 72.63, 'period': 4, 'group': 14, 'block': 'p'},
        33: {'symbol': 'As', 'name': 'Arsênio', 'mass': 74.92, 'period': 4, 'group': 15, 'block': 'p'},
        34: {'symbol': 'Se', 'name': 'Selênio', 'mass': 78.97, 'period': 4, 'group': 16, 'block': 'p'},
        35: {'symbol': 'Br', 'name': 'Bromo', 'mass': 79.90, 'period': 4, 'group': 17, 'block': 'p'},
        36: {'symbol': 'Kr', 'name': 'Criptônio', 'mass': 83.80, 'period': 4, 'group': 18, 'block': 'p'},
    }
    
    if atomic_number in fallback_data:
        data = fallback_data[atomic_number].copy()
        data['electrons'] = atomic_number
        return data
    
    return None

def get_electron_configuration(atomic_number):
    """Calcula configuração eletrônica simplificada"""
    if atomic_number <= 0:
        return []
    
    # Configurações eletrônicas por camadas (K, L, M, N, O, P, Q)
    max_electrons_per_shell = [2, 8, 18, 32, 32, 18, 8]
    shells = []
    remaining = atomic_number
    
    for max_electrons in max_electrons_per_shell:
        if remaining <= 0:
            break
        electrons_in_shell = min(remaining, max_electrons)
        shells.append(electrons_in_shell)
        remaining -= electrons_in_shell
    
    return shells


class Atom3DWidget(FigureCanvas if HAS_MATPLOTLIB_3D else QWidget):
    """Widget para visualização 3D de átomos"""
    
    def __init__(self, parent=None):
        if HAS_MATPLOTLIB_3D:
            self.fig = Figure(figsize=(8, 8), dpi=100, facecolor='#3c3c3c')
            super().__init__(self.fig)
            self.ax = self.fig.add_subplot(111, projection='3d')
        else:
            super().__init__(parent)
            self.setMinimumSize(400, 400)
            
        self.atomic_num = 16  # Padrão: Enxofre
        
        # Removido timer para eliminar animação automática
        # A visualização será estática e manipulável apenas com mouse
        
        # Configurar layout se não tiver matplotlib
        if not HAS_MATPLOTLIB_3D:
            layout = QVBoxLayout()
            info_label = QLabel("Visualização 3D não disponível\nInstale matplotlib com suporte 3D")
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("color: red; font-size: 14px; padding: 20px;")
            layout.addWidget(info_label)
            self.setLayout(layout)
        else:
            self.setup_3d_view()
    
    def setup_3d_view(self):
        """Configura a visualização 3D inicial"""
        if not HAS_MATPLOTLIB_3D:
            return
            
        # Configuração da aparência com tema da imagem
        self.ax.set_facecolor('#3c3c3c')
        self.fig.patch.set_facecolor('#3c3c3c')
        
        # Remove eixos e grade para visual limpo
        self.ax.set_axis_off()
        
        # Define limites proporcionais
        self.ax.set_xlim([-3, 3])
        self.ax.set_ylim([-3, 3])
        self.ax.set_zlim([-3, 3])
        
        # Melhora a projeção 3D
        self.ax.view_init(elev=20, azim=45)
        
        # Desenha o átomo inicial
        self.draw_3d_atom()
    
    def set_element(self, atomic_num):
        """Define o elemento a ser visualizado"""
        self.atomic_num = atomic_num
        if HAS_MATPLOTLIB_3D:
            self.draw_3d_atom()
    
    def draw_3d_atom(self):
        """Desenha átomo 3D estático (sem animação)"""
        if not HAS_MATPLOTLIB_3D:
            return
            
        # Limpa o plot anterior
        self.ax.clear()
        
        # Configura aparência
        self.ax.set_facecolor('#3c3c3c')
        self.ax.set_axis_off()
        self.ax.set_xlim([-3, 3])
        self.ax.set_ylim([-3, 3])
        self.ax.set_zlim([-3, 3])
        
        # Desenha núcleo estático
        self.draw_nucleus_static()
        
        # Desenha camadas eletrônicas estáticas
        self.draw_electron_shells_static()
        
        # Atualiza o canvas
        self.draw()
    
    def draw_nucleus_static(self):
        """Desenha núcleo estático"""
        if not HAS_MATPLOTLIB_3D:
            return
            
        # Prótons (vermelhos) e nêutrons (azuis) no núcleo
        protons = self.atomic_num
        neutrons = max(self.atomic_num, 2)  # Aproximação simples
        
        # Posições fixas para prótons e nêutrons (sem aleatoriedade)
        np.random.seed(42)  # Seed fixo para posições consistentes
        
        # Prótons (esferas vermelhas)
        for i in range(protons):
            angle = (2 * np.pi * i / protons)
            radius = 0.1
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            z = 0
            
            self.ax.scatter([x], [y], [z], c='#e74c3c', s=200, alpha=0.9, 
                          edgecolors='#c0392b', linewidth=1)
        
        # Nêutrons (esferas azuis)
        for i in range(neutrons):
            angle = (2 * np.pi * i / neutrons) + (np.pi/neutrons)
            radius = 0.08
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            z = 0
            
            self.ax.scatter([x], [y], [z], c='#3498db', s=200, alpha=0.9, 
                          edgecolors='#2980b9', linewidth=1)
    
    def draw_electron_shells_static(self):
        """Desenha camadas eletrônicas estáticas (versão leve)"""
        if not HAS_MATPLOTLIB_3D:
            return
            
        shells = get_electron_configuration(self.atomic_num)
        if not shells:
            return
        
        # Raios das camadas (reduzidos para performance)
        shell_radii = [0.6, 1.0, 1.4, 1.8]
        
        for shell_index, electrons in enumerate(shells):
            if shell_index >= len(shell_radii):
                continue
                
            radius = shell_radii[shell_index]
            
            # Desenha apenas anel orbital principal (sem anel vertical para performance)
            theta = np.linspace(0, 2 * np.pi, 50)  # Reduzido de 100 para 50 pontos
            
            # Anel horizontal simplificado
            x_ring = radius * np.cos(theta)
            y_ring = radius * np.sin(theta)
            z_ring = np.zeros_like(theta)
            self.ax.plot(x_ring, y_ring, z_ring, color='#2ecc71', linewidth=1, alpha=0.5)
            
            # Desenha apenas alguns elétrons (máximo 8 por camada para performance)
            max_electrons_to_show = min(electrons, 8)
            for electron in range(max_electrons_to_show):
                # Posição fixa do elétron na órbita
                electron_angle = (2 * np.pi * electron / max_electrons_to_show)
                
                x = radius * np.cos(electron_angle)
                y = radius * np.sin(electron_angle)
                z = 0
                
                # Elétron como ponto menor para performance
                self.ax.scatter([x], [y], [z], c='#2ecc71', s=30, alpha=0.8)


class BohrWidget(QWidget):
    """Widget simples que desenha um modelo de Bohr estilizado"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.atomic_num = 1  # Padrão: Hidrogênio
        self.setMinimumSize(200, 200)  # Ainda menor
        self.setStyleSheet("background-color: #3c3c3c; border-radius: 5px;")
    
    def set_element(self, atomic_num):
        """Define o elemento a ser visualizado"""
        self.atomic_num = atomic_num
        self.update()
    
    def paintEvent(self, event):
        """Desenha o modelo de Bohr 2D melhorado"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fundo seguindo o padrão da imagem
        painter.fillRect(self.rect(), QColor(60, 60, 60))
        
        # Centro
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # Desenha núcleo maior e mais visível
        nucleus_size = 20  # Ainda menor
        painter.setBrush(QBrush(QColor(220, 20, 20)))  # Vermelho para núcleo
        painter.setPen(QPen(QColor(180, 0, 0), 2))
        painter.drawEllipse(center_x - nucleus_size//2, center_y - nucleus_size//2, 
                          nucleus_size, nucleus_size)
        
        # Label do núcleo
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))  # Menor ainda
        painter.drawText(center_x - 6, center_y + 3, f"{self.atomic_num}")
        
        # Desenha órbitas e elétrons usando Mendeleev
        element_data = get_element_data(self.atomic_num)
        if element_data:
            shells = get_electron_configuration(self.atomic_num)
            
            for shell_index, electrons in enumerate(shells):
                # Raio da órbita proporcional - mais compacto
                orbit_radius = 30 + (shell_index * 25)  # Ainda mais reduzido
                
                # Desenha órbita com cor cinza claro
                painter.setBrush(QBrush())
                painter.setPen(QPen(QColor(150, 150, 150), 2, Qt.DashLine))
                painter.drawEllipse(center_x - orbit_radius, center_y - orbit_radius,
                                  orbit_radius * 2, orbit_radius * 2)
                
                # Desenha elétrons
                for electron in range(electrons):
                    angle = (2 * np.pi * electron / electrons)
                    electron_x = center_x + orbit_radius * np.cos(angle)
                    electron_y = center_y + orbit_radius * np.sin(angle)
                    
                    # Elétron azul
                    painter.setBrush(QBrush(QColor(30, 130, 255)))
                    painter.setPen(QPen(QColor(0, 100, 200), 2))
                    painter.drawEllipse(int(electron_x - 6), int(electron_y - 6), 12, 12)  # Reduzido de 8 pixels
                    
                    # Símbolo do elétron
                    painter.setPen(QPen(QColor(255, 255, 255), 1))
                    painter.setFont(QFont("Segoe UI", 7, QFont.Bold))  # Reduzido de 8
                    painter.drawText(int(electron_x - 3), int(electron_y + 2), "e⁻")
        
        # Informações do elemento no canto
        element_data = get_element_data(self.atomic_num)
        if element_data:
            info_text = f"{element_data['name']} ({element_data['symbol']})"
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.setFont(QFont("Segoe UI", 11, QFont.Bold))  # Reduzido de 12
            painter.drawText(10, 20, info_text)  # Reduzido de 25


class PeriodicTableTabFinal(QWidget):
    """Aba final da tabela periódica com visualização 2D e 3D"""
    
    element_selected = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_element = 16  # Padrão: Enxofre
        
        # Inicializar labels como None primeiro
        self.name_label = None
        self.symbol_label = None
        self.atomic_number_label = None
        self.mass_label = None
        self.category_label = None
        self.electron_config_label = None
        self.oxidation_states_label = None
        self.electronegativity_label = None
        self.atomic_radius_label = None
        self.melting_point_label = None
        self.boiling_point_label = None
        self.density_label = None
        self.bohr_canvas = None
        self.atom_3d_canvas = None
        
        self.init_ui()
    
    def init_ui(self):
        """Configura a interface seguindo exatamente o padrão das outras abas"""
        layout = QVBoxLayout()
        layout.setSpacing(5)  # Ainda mais reduzido
        layout.setContentsMargins(5, 5, 5, 5)  # Margens bem menores
        
        # Criar tabs principais para melhor organização (sem scroll externo)
        main_tabs = QTabWidget()
        # Removido setMaximumHeight para permitir expansão
        
        # === ABA 1: TABELA PERIÓDICA ===
        table_tab = QWidget()
        table_layout = QVBoxLayout()
        table_layout.setSpacing(5)
        table_layout.setContentsMargins(5, 5, 5, 5)
        
        # Periodic Table Section - mais compacta
        table_group = self.create_periodic_table()
        table_layout.addWidget(table_group)
        
        # Controles de busca e filtros
        controls_group = self.create_search_controls()
        table_layout.addWidget(controls_group)
        
        # Legenda de cores
        legend_group = self.create_color_legend()
        table_layout.addWidget(legend_group)
        
        # Element Basic Info (na mesma aba da tabela) - lado a lado
        basic_info_group = self.create_basic_element_info()
        table_layout.addWidget(basic_info_group)
        
        table_tab.setLayout(table_layout)
        main_tabs.addTab(table_tab, "Tabela")
        
        # === ABA 2: PROPRIEDADES DETALHADAS ===
        properties_tab = QWidget()
        properties_layout = QVBoxLayout()
        properties_layout.setSpacing(5)
        properties_layout.setContentsMargins(5, 5, 5, 5)
        
        detailed_props_group = self.create_detailed_properties_section()
        properties_layout.addWidget(detailed_props_group)
        
        properties_tab.setLayout(properties_layout)
        main_tabs.addTab(properties_tab, "Propriedades")
        
        # === ABA 3: VISUALIZAÇÃO 2D ===
        viz_2d_tab = QWidget()
        viz_2d_layout = QVBoxLayout()
        viz_2d_layout.setSpacing(5)
        viz_2d_layout.setContentsMargins(5, 5, 5, 5)
        
        # Widget Bohr direto, sem GroupBox extra
        self.bohr_widget = BohrWidget()
        self.bohr_widget.setMinimumSize(400, 300)  # Tamanho mínimo em vez de fixo
        
        # Centralizar o widget
        bohr_container = QWidget()
        bohr_container_layout = QHBoxLayout()
        bohr_container_layout.addStretch()
        bohr_container_layout.addWidget(self.bohr_widget)
        bohr_container_layout.addStretch()
        bohr_container.setLayout(bohr_container_layout)
        
        viz_2d_layout.addWidget(bohr_container)
        viz_2d_tab.setLayout(viz_2d_layout)
        main_tabs.addTab(viz_2d_tab, "Bohr 2D")
        
        # === ABA 4: VISUALIZAÇÃO 3D ===
        viz_3d_tab = QWidget()
        viz_3d_layout = QVBoxLayout()
        viz_3d_layout.setSpacing(5)
        viz_3d_layout.setContentsMargins(5, 5, 5, 5)
        
        # Widget 3D direto, sem GroupBox extra
        self.atom_3d_widget = Atom3DWidget()
        self.atom_3d_widget.setMinimumSize(400, 300)  # Tamanho mínimo em vez de fixo
        
        # Centralizar o widget
        viz_3d_container = QWidget()
        viz_3d_container_layout = QHBoxLayout()
        viz_3d_container_layout.addStretch()
        viz_3d_container_layout.addWidget(self.atom_3d_widget)
        viz_3d_container_layout.addStretch()
        viz_3d_container.setLayout(viz_3d_container_layout)
        
        viz_3d_layout.addWidget(viz_3d_container)
        viz_3d_tab.setLayout(viz_3d_layout)
        main_tabs.addTab(viz_3d_tab, "3D")
        
        # CRÍTICO: Adicionar as tabs ao layout principal
        layout.addWidget(main_tabs)
        self.setLayout(layout)
        
        print("Layout configurado com sucesso!")  # Debug
        print(f"Número de abas criadas: {main_tabs.count()}")  # Debug
        
        # Verifica se as labels foram criadas antes de selecionar elemento
        print(f"Labels básicas criadas: {self.name_label is not None}")  # Debug
        print(f"Labels de propriedades criadas: {self.electron_config_label is not None}")  # Debug
        
        # Aguarda um momento para garantir que todas as abas foram criadas
        QTimer.singleShot(100, lambda: self.select_element(1))  # Hidrogênio
        
    def create_periodic_table(self):
        """Cria a seção da tabela periódica seguindo exatamente o padrão das outras abas"""
        group = QGroupBox("Tabela Periódica")
        # Removido setMaximumHeight para permitir expansão
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(3, 3, 3, 3)
        
        # Grid da tabela com layout correto da tabela periódica
        grid_widget = QWidget()
        self.grid = QGridLayout()
        self.grid.setSpacing(2)  # Espaçamento pequeno como na imagem
        self.grid.setContentsMargins(5, 5, 5, 5)  # Margens pequenas
        
        # Criar elementos da tabela periódica
        self.create_element_buttons()
        
        grid_widget.setLayout(self.grid)
        
        # Scroll area para a tabela
        table_scroll = QScrollArea()
        table_scroll.setWidget(grid_widget)
        table_scroll.setWidgetResizable(True)
        table_scroll.setMinimumHeight(280)  # Altura mínima ajustada
        table_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        main_layout.addWidget(table_scroll)
        group.setLayout(main_layout)
        return group
    
    def create_element_buttons(self):
        """Cria os botões dos elementos da tabela periódica"""
        print("Criando botões dos elementos...")  # Debug
        
        # Layouts por períodos seguindo a referência correta
        period_layouts = {
            1: [(0, 0, 1), (0, 17, 2)],  # H, He
            2: [(1, 0, 3), (1, 1, 4), (1, 12, 5), (1, 13, 6), (1, 14, 7), (1, 15, 8), (1, 16, 9), (1, 17, 10)],  # Li-Ne
            3: [(2, 0, 11), (2, 1, 12), (2, 12, 13), (2, 13, 14), (2, 14, 15), (2, 15, 16), (2, 16, 17), (2, 17, 18)],  # Na-Ar
            4: [(3, 0, 19), (3, 1, 20), (3, 2, 21), (3, 3, 22), (3, 4, 23), (3, 5, 24), (3, 6, 25), 
                (3, 7, 26), (3, 8, 27), (3, 9, 28), (3, 10, 29), (3, 11, 30), (3, 12, 31), (3, 13, 32), 
                (3, 14, 33), (3, 15, 34), (3, 16, 35), (3, 17, 36)],  # K-Kr
            5: [(4, 0, 37), (4, 1, 38), (4, 2, 39), (4, 3, 40), (4, 4, 41), (4, 5, 42), (4, 6, 43), 
                (4, 7, 44), (4, 8, 45), (4, 9, 46), (4, 10, 47), (4, 11, 48), (4, 12, 49), (4, 13, 50), 
                (4, 14, 51), (4, 15, 52), (4, 16, 53), (4, 17, 54)],  # Rb-Xe
            6: [(5, 0, 55), (5, 1, 56), (5, 2, 57), (5, 3, 72), (5, 4, 73), (5, 5, 74), (5, 6, 75), (5, 7, 76), 
                (5, 8, 77), (5, 9, 78), (5, 10, 79), (5, 11, 80), (5, 12, 81), (5, 13, 82), (5, 14, 83), 
                (5, 15, 84), (5, 16, 85), (5, 17, 86)],  # Cs-Rn (Po no grupo 16, At no grupo 17)
            7: [(6, 0, 87), (6, 1, 88), (6, 2, 89), (6, 3, 104), (6, 4, 105), (6, 5, 106), (6, 6, 107), (6, 7, 108), 
                (6, 8, 109), (6, 9, 110), (6, 10, 111), (6, 11, 112), (6, 12, 113), (6, 13, 114), (6, 14, 115), 
                (6, 15, 116), (6, 16, 117), (6, 17, 118)]  # Fr-Og (Ac no lugar correto)
        }
        
        # Lantanídeos (separados embaixo) - Período 8, centralizados
        lanthanides = [(8, i+2, 58+i) for i in range(14)]  # Ce-Lu (58-71), começando na coluna 2
        
        # Actinídeos (separados embaixo) - Período 9, centralizados  
        actinides = [(9, i+2, 90+i) for i in range(14)]    # Th-Lr (90-103), começando na coluna 2
        
        # Criar todos os elementos
        all_positions = []
        for positions in period_layouts.values():
            all_positions.extend(positions)
        all_positions.extend(lanthanides)
        all_positions.extend(actinides)
        
        created_count = 0
        for row, col, atomic_num in all_positions:
            element_data = get_element_data(atomic_num)
            if element_data:
                btn = QPushButton()
                btn.setMinimumSize(40, 40)  # Tamanho único padronizado
                btn.setMaximumSize(40, 40)
                
                # Texto do botão: número atômico + símbolo (como na imagem)
                btn.setText(f"{atomic_num}\n{element_data['symbol']}")
                
                # Aplicar estilo mais parecido com a imagem
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.get_element_color(element_data)};
                        color: white;
                        font-size: 9px;
                        font-weight: bold;
                        border: 1px solid #333333;
                        border-radius: 3px;
                        text-align: center;
                        padding: 2px;
                        margin: 0px;
                    }}
                    QPushButton:hover {{
                        border: 2px solid #ffffff;
                        background-color: {self.get_element_color(element_data, hover=True)};
                        transform: scale(1.05);
                    }}
                    QPushButton:pressed {{
                        background-color: #2c3e50;
                    }}
                """)
                
                # Tooltip com informações completas
                btn.setToolTip(f"{element_data['name']} ({element_data['symbol']})\n"
                              f"Número Atômico: {atomic_num}\n"
                              f"Massa: {element_data['mass']} u\n"
                              f"Bloco: {element_data.get('block', 'N/A')}\n"
                              f"Período: {element_data.get('period', 'N/A')}\n"
                              f"Grupo: {element_data.get('group', 'N/A')}")
                
                # Conectar clique
                btn.clicked.connect(lambda checked, num=atomic_num: self.select_element(num))
                
                # Adicionar ao grid
                self.grid.addWidget(btn, row, col)
                created_count += 1
            else:
                print(f"Dados não encontrados para elemento {atomic_num}")  # Debug
        
        print(f"Total de elementos criados: {created_count}")  # Debug
        
        # Adicionar labels para lantanídeos e actinídeos
        self.add_series_labels()
    
    def add_series_labels(self):
        """Adiciona labels 57-71 e 89-103 nas posições originais"""
        # Label para lantanídeos (posição do La original no período 6, coluna 2)
        lanthanides_label = QLabel("57-71")
        lanthanides_label.setAlignment(Qt.AlignCenter)
        lanthanides_label.setStyleSheet("""
            QLabel {
                background-color: #BDC3C7;
                color: #2C3E50;
                border: 1px solid #95A5A6;
                border-radius: 3px;
                font-size: 8px;
                font-weight: bold;
                padding: 2px;
            }
        """)
        lanthanides_label.setFixedSize(40, 40)
        self.grid.addWidget(lanthanides_label, 5, 2)  # Posição do La
        
        # Label para actinídeos (posição do Ac original no período 7, coluna 2)  
        actinides_label = QLabel("89-103")
        actinides_label.setAlignment(Qt.AlignCenter)
        actinides_label.setStyleSheet("""
            QLabel {
                background-color: #BDC3C7;
                color: #2C3E50;
                border: 1px solid #95A5A6;
                border-radius: 3px;
                font-size: 8px;
                font-weight: bold;
                padding: 2px;
            }
        """)
        actinides_label.setFixedSize(40, 40)
        self.grid.addWidget(actinides_label, 6, 2)  # Posição do Ac
    
    def create_color_legend(self):
        """Cria legenda de cores da tabela periódica"""
        group = QGroupBox("Legenda")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Grid layout para organizar a legenda em colunas
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)
        
        # Definir categorias e cores (baseado na imagem de referência)
        categories = [
            ("H", "Hidrogênio", "#5DADE2"),
            ("Li", "Metais alcalinos", "#1E8449"),
            ("Be", "Metais alcalino-terrosos", "#52C41A"),
            ("B", "Semimetais", "#F1C40F"),
            ("C", "Ametais reativos", "#1B2631"),
            ("F", "Halogênios", "#9ACD32"),
            ("He", "Gases nobres", "#BB8FCE"),
            ("Sc", "Metais de transição", "#3498DB"),
            ("La", "Lantanídeos", "#5DADE2"),
            ("Ac", "Actinídeos", "#E67E22"),
            ("Al", "Metais pós-transição", "#5D6D7E"),
        ]
        
        # Organizar em 2 linhas
        for i, (symbol, name, color) in enumerate(categories):
            row = i // 6  # Até 6 itens por linha
            col = i % 6
            
            # Container para cada item da legenda
            item_widget = QWidget()
            item_layout = QHBoxLayout()
            item_layout.setSpacing(3)
            item_layout.setContentsMargins(0, 0, 0, 0)
            
            # Quadrado colorido
            color_box = QLabel()
            color_box.setFixedSize(12, 12)
            color_box.setStyleSheet(f"background-color: {color}; border: 1px solid #333;")
            
            # Texto da categoria
            text_label = QLabel(name)
            text_label.setStyleSheet("font-size: 8px; color: white;")  # Mudado para branco
            
            item_layout.addWidget(color_box)
            item_layout.addWidget(text_label)
            item_widget.setLayout(item_layout)
            
            grid_layout.addWidget(item_widget, row, col)
        
        main_layout.addLayout(grid_layout)
        group.setLayout(main_layout)
        group.setMaximumHeight(70)  # Altura um pouco maior para 2 linhas
        return group
    
    def create_search_controls(self):
        """Cria controles de busca e filtros"""
        group = QGroupBox("Busca e Filtros")
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Campo de busca
        search_label = QLabel("Buscar:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite nome ou símbolo...")
        self.search_input.textChanged.connect(self.search_elements)
        self.search_input.setMaximumWidth(150)
        
        # Filtro por bloco
        block_label = QLabel("Bloco:")
        self.block_filter = QComboBox()
        self.block_filter.addItems(["Todos", "s", "p", "d", "f"])
        self.block_filter.currentTextChanged.connect(self.filter_by_block)
        self.block_filter.setMaximumWidth(80)
        
        # Filtro por estado
        state_label = QLabel("Estado:")
        self.state_filter = QComboBox()
        self.state_filter.addItems(["Todos", "Sólido", "Líquido", "Gasoso", "Sintético"])
        self.state_filter.currentTextChanged.connect(self.filter_by_state)
        self.state_filter.setMaximumWidth(100)
        
        # Botão reset
        reset_btn = QPushButton("Limpar")
        reset_btn.clicked.connect(self.reset_filters)
        reset_btn.setMaximumWidth(60)
        
        # Info rápida
        self.quick_info = QLabel("Clique em um elemento para ver detalhes")
        self.quick_info.setStyleSheet("color: #666; font-style: italic;")
        
        layout.addWidget(search_label)
        layout.addWidget(self.search_input)
        layout.addWidget(block_label)
        layout.addWidget(self.block_filter)
        layout.addWidget(state_label)
        layout.addWidget(self.state_filter)
        layout.addWidget(reset_btn)
        layout.addStretch()
        layout.addWidget(self.quick_info)
        
        group.setLayout(layout)
        group.setMaximumHeight(60)
        return group
    
    def search_elements(self, text):
        """Busca elementos por nome ou símbolo"""
        if not hasattr(self, 'grid'):
            return
            
        text = text.lower().strip()
        
        # Percorre todos os widgets do grid
        for i in range(self.grid.count()):
            widget = self.grid.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                # Pega informações do elemento do tooltip
                tooltip = widget.toolTip()
                if tooltip:
                    lines = tooltip.split('\n')
                    element_name = lines[0].split(' (')[0].lower()  # Nome do elemento
                    element_symbol = lines[0].split('(')[1].split(')')[0].lower()  # Símbolo
                    
                    # Verifica se o texto de busca está no nome ou símbolo
                    if text == "" or text in element_name or text in element_symbol:
                        widget.setVisible(True)
                        widget.setStyleSheet(widget.styleSheet().replace("opacity: 0.3;", ""))
                    else:
                        widget.setVisible(True)  # Mantém visível mas com opacidade
                        if "opacity: 0.3;" not in widget.styleSheet():
                            widget.setStyleSheet(widget.styleSheet().replace("}", "opacity: 0.3;}"))
    
    def filter_by_block(self, block):
        """Filtra elementos por bloco"""
        if not hasattr(self, 'grid') or block == "Todos":
            self.reset_visual_filters()
            return
            
        # Implementar filtro por bloco
        self.apply_block_filter(block.lower())
    
    def filter_by_state(self, state):
        """Filtra elementos por estado físico"""
        if not hasattr(self, 'grid') or state == "Todos":
            self.reset_visual_filters()
            return
            
        # Implementar filtro por estado
        self.apply_state_filter(state)
    
    def reset_filters(self):
        """Reset todos os filtros"""
        if hasattr(self, 'search_input'):
            self.search_input.setText("")
        if hasattr(self, 'block_filter'):
            self.block_filter.setCurrentText("Todos")
        if hasattr(self, 'state_filter'):
            self.state_filter.setCurrentText("Todos")
        self.reset_visual_filters()
    
    def reset_visual_filters(self):
        """Remove filtros visuais dos elementos"""
        if not hasattr(self, 'grid'):
            return
            
        for i in range(self.grid.count()):
            widget = self.grid.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setVisible(True)
                widget.setStyleSheet(widget.styleSheet().replace("opacity: 0.3;", ""))
    
    def apply_block_filter(self, block):
        """Aplica filtro visual por bloco"""
        for i in range(self.grid.count()):
            widget = self.grid.itemAt(i).widget()
            if isinstance(widget, QPushButton) and hasattr(widget, 'element_data'):
                element_block = widget.element_data.get('block', '').lower()
                if element_block == block:
                    widget.setStyleSheet(widget.styleSheet().replace("opacity: 0.3;", ""))
                else:
                    if "opacity: 0.3;" not in widget.styleSheet():
                        widget.setStyleSheet(widget.styleSheet().replace("}", "opacity: 0.3;}"))
    
    def apply_state_filter(self, state):
        """Aplica filtro visual por estado"""
        # Implementação básica - pode ser expandida com dados de estado físico
        pass
    
    def create_basic_element_info(self):
        """Cria a seção de informações básicas do elemento"""
        group = QGroupBox("Informações do Elemento")
        # Removido setMaximumHeight para permitir expansão
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding: 3px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Layout horizontal para usar menos espaço vertical
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        
        # Coluna 1
        col1_layout = QFormLayout()
        col1_layout.setSpacing(4)
        
        self.name_label = QLabel("-")
        self.symbol_label = QLabel("-")
        self.atomic_number_label = QLabel("-")
        self.period_label = QLabel("-")
        
        col1_layout.addRow(QLabel("Nome:"), self.name_label)
        col1_layout.addRow(QLabel("Símbolo:"), self.symbol_label)
        col1_layout.addRow(QLabel("Nº Atômico:"), self.atomic_number_label)
        col1_layout.addRow(QLabel("Período:"), self.period_label)
        
        # Coluna 2
        col2_layout = QFormLayout()
        col2_layout.setSpacing(4)
        
        self.mass_label = QLabel("-")
        self.group_label = QLabel("-")
        self.block_label = QLabel("-")
        self.category_label = QLabel("-")
        
        col2_layout.addRow(QLabel("Massa:"), self.mass_label)
        col2_layout.addRow(QLabel("Grupo:"), self.group_label)
        col2_layout.addRow(QLabel("Bloco:"), self.block_label)
        col2_layout.addRow(QLabel("Categoria:"), self.category_label)
        
        main_layout.addLayout(col1_layout)
        main_layout.addLayout(col2_layout)
        
        group.setLayout(main_layout)
        return group

    def create_detailed_properties_section(self):
        """Cria a seção de propriedades detalhadas"""
        group = QGroupBox("Propriedades Físicas e Químicas")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        layout = QFormLayout()
        layout.setSpacing(6)  # Reduzido de 8
        
        # Labels para propriedades detalhadas
        self.electron_config_label = QLabel("-")
        self.oxidation_states_label = QLabel("-")
        self.electronegativity_label = QLabel("-")
        self.atomic_radius_label = QLabel("-")
        self.melting_point_label = QLabel("-")
        self.boiling_point_label = QLabel("-")
        self.density_label = QLabel("-")
        
        # Adicionar ao layout de forma mais compacta
        layout.addRow(QLabel("Config. Eletrônica:"), self.electron_config_label)
        layout.addRow(QLabel("Est. Oxidação:"), self.oxidation_states_label)  # Texto mais curto
        layout.addRow(QLabel("Eletronegatividade:"), self.electronegativity_label)
        layout.addRow(QLabel("Raio Atômico:"), self.atomic_radius_label)
        layout.addRow(QLabel("P. Fusão:"), self.melting_point_label)  # Texto mais curto
        layout.addRow(QLabel("P. Ebulição:"), self.boiling_point_label)  # Texto mais curto
        layout.addRow(QLabel("Densidade:"), self.density_label)
        
        group.setLayout(layout)
        return group

    def get_element_color(self, element_data, hover=False):
        """Retorna a cor do elemento baseada na categoria (seguindo imagem de referência)"""
        atomic_num = element_data.get('electrons', 1)
        block = element_data.get('block', '')
        
        # Cores baseadas exatamente na imagem de referência
        if atomic_num == 1:  # Hidrogênio - azul claro
            return '#5DADE2' if not hover else '#3498DB'
        elif atomic_num == 2:  # Hélio - gases nobres roxo suave
            return '#BB8FCE' if not hover else '#A569BD'
        elif atomic_num in [3, 11, 19, 37, 55, 87]:  # Metais alcalinos - verde bem forte
            return '#1E8449' if not hover else '#196F3D'
        elif atomic_num in [4, 12, 20, 38, 56, 88]:  # Metais alcalino-terrosos - verde claro
            return '#52C41A' if not hover else '#45B715'
        elif block == 'd':  # Metais de transição - azul médio
            return '#3498DB' if not hover else '#2980B9'
        elif 57 <= atomic_num <= 71:  # Lantanídeos - azul claro (igual ao hidrogênio)
            return '#5DADE2' if not hover else '#3498DB'
        elif 89 <= atomic_num <= 103:  # Actinídeos - laranja/marrom
            return '#E67E22' if not hover else '#D35400'
        elif atomic_num in [5, 14, 32, 33, 51, 52]:  # Semimetais - amarelo
            return '#F1C40F' if not hover else '#F39C12'
        elif atomic_num in [6, 7, 8, 15, 16, 34]:  # Ametais reativos - azul bem escuro
            return '#1B2631' if not hover else '#17202A'
        elif atomic_num in [9, 17, 35, 53, 85]:  # Halogênios - amarelo-esverdeado
            return '#9ACD32' if not hover else '#8FBC8F'
        elif atomic_num in [10, 18, 36, 54, 86, 118]:  # Gases nobres - roxo suave
            return '#BB8FCE' if not hover else '#A569BD'
        elif block == 'p' and atomic_num in [13, 31, 49, 50, 81, 82, 83, 113, 114, 115, 116]:  # Metais pós-transição - cinza azulado
            return '#5D6D7E' if not hover else '#566573'
        else:
            return '#95A5A6' if not hover else '#7F8C8D'
    
    def create_visualization_section(self):
        """Cria a seção de visualização seguindo o padrão das outras abas"""
        group = QGroupBox("Visualização e Propriedades Detalhadas")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # Divisão em subgrupos como nas outras abas
        
        # === MODELO DE BOHR ===
        bohr_group = QGroupBox("Modelo de Bohr (2D)")
        bohr_layout = QVBoxLayout()
        self.bohr_widget = BohrWidget()
        self.bohr_widget.setMinimumHeight(250)
        bohr_layout.addWidget(self.bohr_widget)
        bohr_group.setLayout(bohr_layout)
        
        # === VISUALIZAÇÃO 3D ===
        viz_3d_group = QGroupBox("Visualização 3D do Átomo")
        viz_3d_layout = QVBoxLayout()
        self.atom_3d_widget = Atom3DWidget()
        self.atom_3d_widget.setMinimumHeight(300)
        viz_3d_layout.addWidget(self.atom_3d_widget)
        viz_3d_group.setLayout(viz_3d_layout)
        
        # === PROPRIEDADES DETALHADAS ===
        props_group = QGroupBox("Propriedades Detalhadas")
        props_layout = QVBoxLayout()
        
        self.detailed_properties = QTextEdit()
        self.detailed_properties.setReadOnly(True)
        self.detailed_properties.setMinimumHeight(200)
        self.detailed_properties.setStyleSheet("font-family: monospace; font-size: 11px;")
        self.detailed_properties.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.detailed_properties.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        props_layout.addWidget(self.detailed_properties)
        props_group.setLayout(props_layout)
        
        # Adicionar subgrupos ao grupo principal
        main_layout.addWidget(bohr_group)
        main_layout.addWidget(viz_3d_group) 
        main_layout.addWidget(props_group)
        
        group.setLayout(main_layout)
        return group
        """Cria a tabela periódica interativa organizada"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Grid da tabela com layout correto da tabela periódica
        grid = QGridLayout()
        grid.setSpacing(2)
        
        # Cria tabela completa usando dados da biblioteca Mendeleev
        # Layouts por períodos seguindo a referência correta
        period_layouts = {
            1: [(0, 0, 1), (0, 17, 2)],  # H, He
            2: [(1, 0, 3), (1, 1, 4), (1, 12, 5), (1, 13, 6), (1, 14, 7), (1, 15, 8), (1, 16, 9), (1, 17, 10)],  # Li-Ne
            3: [(2, 0, 11), (2, 1, 12), (2, 12, 13), (2, 13, 14), (2, 14, 15), (2, 15, 16), (2, 16, 17), (2, 17, 18)],  # Na-Ar
            4: [(3, 0, 19), (3, 1, 20), (3, 2, 21), (3, 3, 22), (3, 4, 23), (3, 5, 24), (3, 6, 25), 
                (3, 7, 26), (3, 8, 27), (3, 9, 28), (3, 10, 29), (3, 11, 30), (3, 12, 31), (3, 13, 32), 
                (3, 14, 33), (3, 15, 34), (3, 16, 35), (3, 17, 36)],  # K-Kr
            5: [(4, 0, 37), (4, 1, 38), (4, 2, 39), (4, 3, 40), (4, 4, 41), (4, 5, 42), (4, 6, 43), 
                (4, 7, 44), (4, 8, 45), (4, 9, 46), (4, 10, 47), (4, 11, 48), (4, 12, 49), (4, 13, 50), 
                (4, 14, 51), (4, 15, 52), (4, 16, 53), (4, 17, 54)],  # Rb-Xe
            6: [(5, 0, 55), (5, 1, 56), (5, 2, 57), (5, 3, 72), (5, 4, 73), (5, 5, 74), (5, 6, 75), (5, 7, 76), 
                (5, 8, 77), (5, 9, 78), (5, 10, 79), (5, 11, 80), (5, 12, 81), (5, 13, 82), (5, 14, 83), 
                (5, 15, 84), (5, 16, 85), (5, 17, 86)],  # Cs-Rn (Po no grupo 16, At no grupo 17)
            7: [(6, 0, 87), (6, 1, 88), (6, 2, 89), (6, 3, 104), (6, 4, 105), (6, 5, 106), (6, 6, 107), (6, 7, 108), 
                (6, 8, 109), (6, 9, 110), (6, 10, 111), (6, 11, 112), (6, 12, 113), (6, 13, 114), (6, 14, 115), 
                (6, 15, 116), (6, 16, 117), (6, 17, 118)]  # Fr-Og (Ac no lugar correto)
        }
        
        # Lantanídeos (separados embaixo) - Período 8, centralizados
        lanthanides = [(8, i+2, 58+i) for i in range(14)]  # Ce-Lu (58-71), começando na coluna 2
        
        # Actinídeos (separados embaixo) - Período 9, centralizados  
        actinides = [(9, i+2, 90+i) for i in range(14)]    # Th-Lr (90-103), começando na coluna 2
        
        all_positions = []
        for period_data in period_layouts.values():
            all_positions.extend(period_data)
        all_positions.extend(lanthanides)
        all_positions.extend(actinides)
        
        # Aplica layout
        for row, col, atomic_num in all_positions:
            element_data = get_element_data(atomic_num)
            if element_data:
                btn = QPushButton()
                btn.setText(f"{element_data['symbol']}\n{atomic_num}")
                btn.setMinimumSize(40, 40)
                btn.setMaximumSize(40, 40)
                btn.setFont(QFont("Segoe UI", 8, QFont.Bold))
                btn.clicked.connect(lambda checked, num=atomic_num: self.select_element(num))
                
                # Cores seguindo o padrão da interface mostrada na imagem
                block = element_data.get('block', '')
                group = element_data.get('group', 0)
                period = element_data.get('period', 0)
                
                # Cores baseadas na imagem de referência da tabela periódica
                if atomic_num == 1:  # Hidrogênio - azul claro
                    color = "#5DADE2"
                elif atomic_num == 2:  # Hélio - rosa/roxo
                    color = "#BB8FCE"
                elif atomic_num in [3, 11, 19, 37, 55, 87]:  # Metais alcalinos - verde escuro
                    color = "#52C41A"
                elif atomic_num in [4, 12, 20, 38, 56, 88]:  # Metais alcalino-terrosos - verde claro
                    color = "#73D13D"
                elif 21 <= atomic_num <= 30 or 39 <= atomic_num <= 48 or atomic_num in [72, 73, 74, 75, 76, 77, 78, 79, 80] or 104 <= atomic_num <= 112:  # Metais de transição - azul
                    color = "#4A90E2"
                elif 57 <= atomic_num <= 71:  # Lantanídeos - azul claro
                    color = "#85C1E9"
                elif 89 <= atomic_num <= 103:  # Actinídeos - azul escuro
                    color = "#5499C7"
                elif atomic_num in [13, 31, 49, 50, 81, 82, 83, 113, 114, 115, 116]:  # Metais do bloco p - cinza azulado
                    color = "#7FB3D3"
                elif atomic_num in [5, 14, 32, 33, 51, 52]:  # Metaloides - amarelo/laranja
                    color = "#F7DC6F"
                elif atomic_num in [6, 7, 8, 15, 16, 34, 84]:  # Não-metais e calcogênios (incluindo Po)
                    color = "#F1948A"
                elif atomic_num in [9, 17, 35, 53, 85, 117]:  # Halogênios (At no lugar correto)
                    color = "#F8C471"
                elif atomic_num in [10, 18, 36, 54, 86, 118]:  # Gases nobres - roxo
                    color = "#D2B4DE"
                else:  # Outros elementos - cinza padrão
                    color = "#6c757d"
                
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color}; 
                        color: #ffffff; 
                        border: 1px solid #5a5a5a;
                        border-radius: 3px;
                        font-weight: bold;
                        font-size: 10px;
                    }}
                    QPushButton:hover {{
                        background-color: #7a7a7a;
                        border: 1px solid #ffffff;
                    }}
                    QPushButton:pressed {{
                        background-color: #5a5a5a;
                    }}
                """)
                
                grid.addWidget(btn, row, col)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        widget.setLayout(layout)
        widget.setStyleSheet("""
            QWidget {
                background-color: #3c3c3c;
                border-radius: 5px;
            }
        """)
        return widget
    
    def create_element_info_panel(self):
        """Cria painel de informações básicas do elemento seguindo padrão das outras abas"""
        group = QGroupBox("Informações do Elemento")
        layout = QFormLayout()
        layout.setVerticalSpacing(10)
        layout.setHorizontalSpacing(15)
        
        # Informações básicas do elemento
        self.element_name_label = QLabel("Selecione um elemento")
        self.element_name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addRow("Elemento:", self.element_name_label)
        
        # Número atômico
        self.atomic_number_label = QLabel("-")
        layout.addRow("Número Atômico:", self.atomic_number_label)
        
        # Massa atômica
        self.atomic_mass_label = QLabel("-")
        layout.addRow("Massa Atômica:", self.atomic_mass_label)
        
        # Período e grupo
        self.period_label = QLabel("-")
        layout.addRow("Período:", self.period_label)
        
        self.group_label = QLabel("-")
        layout.addRow("Grupo:", self.group_label)
        
        # Configuração eletrônica
        self.electron_config_label = QLabel("-")
        self.electron_config_label.setWordWrap(True)
        layout.addRow("Config. Eletrônica:", self.electron_config_label)
        
        # Propriedades físicas básicas
        self.density_label = QLabel("-")
        layout.addRow("Densidade:", self.density_label)
        
        self.melting_point_label = QLabel("-")
        layout.addRow("Ponto de Fusão:", self.melting_point_label)
        
        self.boiling_point_label = QLabel("-")
        layout.addRow("Ponto de Ebulição:", self.boiling_point_label)
        
        group.setLayout(layout)
        return group
    
    def create_detailed_properties_panel(self):
        """Cria painel de propriedades detalhadas seguindo padrão das outras abas"""
        group = QGroupBox("Propriedades Detalhadas")
        layout = QVBoxLayout()
        
        # Text widget para propriedades detalhadas
        self.detailed_properties = QTextEdit()
        self.detailed_properties.setReadOnly(True)
        self.detailed_properties.setMinimumHeight(300)
        self.detailed_properties.setStyleSheet("""
            QTextEdit {
                font-family: monospace;
                font-size: 11px;
                line-height: 1.4;
            }
        """)
        layout.addWidget(self.detailed_properties)
        
        group.setLayout(layout)
        return group
    
    def create_visualization_panel(self):
        """Cria painel de visualizações"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Informações básicas do elemento
        self.info_label = QLabel()
        self.info_label.setFont(QFont("Segoe UI", 10))
        self.info_label.setAlignment(Qt.AlignLeft)
        self.info_label.setStyleSheet("""
            QLabel {
                background-color: #4a4a4a; 
                color: #ffffff;
                padding: 15px; 
                border-radius: 8px; 
                border: 1px solid #666666;
                margin: 5px;
                line-height: 1.6;
            }
        """)
        layout.addWidget(self.info_label)
        
        # Abas para diferentes tipos de informações
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #666666;
                border-radius: 8px;
                background-color: #4a4a4a;
                margin-top: 5px;
            }
            QTabBar::tab {
                background-color: #5a5a5a;
                color: #ffffff;
                padding: 8px 12px;
                margin: 1px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 10px;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #007ACC;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #6a6a6a;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
        """)
        
        # Aba 2D
        self.bohr_widget = BohrWidget()
        self.tab_widget.addTab(self.bohr_widget, "Modelo 2D")
        
        # Aba 3D  
        self.atom_3d_widget = Atom3DWidget()
        self.tab_widget.addTab(self.atom_3d_widget, "Modelo 3D")
        
        # Aba de Propriedades Detalhadas
        self.properties_widget = self.create_properties_widget()
        self.tab_widget.addTab(self.properties_widget, "Propriedades")
        
        layout.addWidget(self.tab_widget)
        
        # Atualiza com elemento padrão
        self.select_element(self.current_element)
        
        widget.setLayout(layout)
        widget.setStyleSheet("""
            QWidget {
                background-color: #4a4a4a;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        return widget
    
    def create_properties_widget(self):
        """Cria widget com propriedades detalhadas do elemento"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Text area com scroll para propriedades detalhadas
        self.properties_text = QTextEdit()
        self.properties_text.setReadOnly(True)
        self.properties_text.setFont(QFont("Segoe UI", 10))
        self.properties_text.setStyleSheet("""
            QTextEdit {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #666666;
                border-radius: 8px;
                padding: 10px;
            }
            QScrollBar:vertical {
                background-color: #5a5a5a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #007ACC;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #0099FF;
            }
        """)
        
        layout.addWidget(self.properties_text)
        widget.setLayout(layout)
        return widget
    
    def create_3d_controls(self):
        """Cria controles para visualização 3D"""
        # Removido - sem controles necessários
        pass
    
    def select_element(self, atomic_num):
        """Seleciona um elemento para visualização"""
        element_data = get_element_data(atomic_num)
        if not element_data:
            return
            
        self.current_element = atomic_num
        print(f"Selecionando elemento: {element_data['name']} ({atomic_num})")  # Debug
        
        # Atualiza informações básicas - verificação segura
        if hasattr(self, 'name_label') and self.name_label is not None:
            self.name_label.setText(element_data['name'])
        if hasattr(self, 'symbol_label') and self.symbol_label is not None:
            self.symbol_label.setText(element_data['symbol'])
        if hasattr(self, 'atomic_number_label') and self.atomic_number_label is not None:
            self.atomic_number_label.setText(str(atomic_num))
        if hasattr(self, 'mass_label') and self.mass_label is not None:
            self.mass_label.setText(f"{element_data['mass']} u")
        if hasattr(self, 'period_label') and self.period_label is not None:
            period = element_data.get('period', 'N/A')
            self.period_label.setText(str(period) if period else 'N/A')
        if hasattr(self, 'group_label') and self.group_label is not None:
            group = element_data.get('group')
            if group is not None and str(group).strip() and group != 'N/A':
                try:
                    # Tenta converter para inteiro
                    group_num = int(float(group))
                    self.group_label.setText(str(group_num))
                except (ValueError, TypeError):
                    # Se não conseguir converter, mostra como string
                    self.group_label.setText(str(group))
            else:
                self.group_label.setText('N/A')
        if hasattr(self, 'block_label') and self.block_label is not None:
            block = element_data.get('block', 'N/A')
            self.block_label.setText(block.upper() if block else 'N/A')
        if hasattr(self, 'category_label') and self.category_label is not None:
            category = self.get_element_category(element_data)
            self.category_label.setText(category)
        
        # Atualiza info rápida
        if hasattr(self, 'quick_info') and self.quick_info is not None:
            self.quick_info.setText(f"{element_data['name']} - {self.get_element_category(element_data)}")
        
        # Atualiza propriedades detalhadas
        if hasattr(self, 'electron_config_label') and self.electron_config_label is not None:
            config = element_data.get('electron_configuration', 'N/A')
            if config and config != 'N/A' and str(config).strip():
                self.electron_config_label.setText(str(config))
            else:
                # Fallback para configuração básica se não houver dados
                shells = get_electron_configuration(atomic_num)
                if shells:
                    config_text = f"Camadas: {', '.join(map(str, shells))}"
                    self.electron_config_label.setText(config_text)
                else:
                    self.electron_config_label.setText('N/A')
        
        if hasattr(self, 'oxidation_states_label') and self.oxidation_states_label is not None:
            oxidation_states = element_data.get('oxidation_states', [])
            if oxidation_states:
                # Trata oxidation_states de forma segura
                if hasattr(oxidation_states, '__call__'):
                    try:
                        oxidation_states = oxidation_states()
                    except:
                        oxidation_states = []
                
                if isinstance(oxidation_states, (list, tuple)):
                    clean_states = []
                    for state in oxidation_states:
                        if isinstance(state, (int, float)):
                            clean_states.append(str(int(state)))
                        elif isinstance(state, str):
                            clean_state = state.replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace("'", '').replace('"', '').strip()
                            if clean_state and clean_state not in ['None', 'N/A', '']:
                                clean_states.append(clean_state)
                    if clean_states:
                        self.oxidation_states_label.setText(', '.join(clean_states))
                    else:
                        self.oxidation_states_label.setText('N/A')
                else:
                    self.oxidation_states_label.setText('N/A')
            else:
                self.oxidation_states_label.setText('N/A')
        
        if hasattr(self, 'electronegativity_label') and self.electronegativity_label is not None:
            electronegativity = element_data.get('electronegativity')
            if electronegativity and isinstance(electronegativity, (int, float)):
                self.electronegativity_label.setText(f"{electronegativity:.2f}")
            else:
                self.electronegativity_label.setText('N/A')
        
        if hasattr(self, 'atomic_radius_label') and self.atomic_radius_label is not None:
            atomic_radius = element_data.get('atomic_radius')
            self.atomic_radius_label.setText(f"{atomic_radius} pm" if atomic_radius else 'N/A')
        
        if hasattr(self, 'melting_point_label') and self.melting_point_label is not None:
            melting_point = element_data.get('melting_point')
            if melting_point and isinstance(melting_point, (int, float)):
                melting_celsius = melting_point - 273.15 if melting_point > 0 else melting_point
                self.melting_point_label.setText(f"{melting_celsius:.1f} °C")
            else:
                self.melting_point_label.setText('N/A')
        
        if hasattr(self, 'boiling_point_label') and self.boiling_point_label is not None:
            boiling_point = element_data.get('boiling_point')
            if boiling_point and isinstance(boiling_point, (int, float)):
                boiling_celsius = boiling_point - 273.15 if boiling_point > 0 else boiling_point
                self.boiling_point_label.setText(f"{boiling_celsius:.1f} °C")
            else:
                self.boiling_point_label.setText('N/A')
        
        if hasattr(self, 'density_label') and self.density_label is not None:
            density = element_data.get('density')
            self.density_label.setText(f"{density} g/cm³" if density else 'N/A')
        
        # Atualiza modelos de Bohr e 3D
        if hasattr(self, 'bohr_widget') and self.bohr_widget is not None:
            self.bohr_widget.set_element(atomic_num)
        if hasattr(self, 'atom_3d_widget') and self.atom_3d_widget is not None:
            self.atom_3d_widget.set_element(atomic_num)
        
        # Emite sinal
        self.element_selected.emit(atomic_num)
    
    def get_element_category(self, element_data):
        """Retorna a categoria do elemento (baseado na imagem de referência)"""
        atomic_num = element_data.get('electrons', 1)
        block = element_data.get('block', '')
        
        if atomic_num == 1:
            return "Hidrogênio"
        elif atomic_num == 2:
            return "Gases nobres"
        elif atomic_num in [3, 11, 19, 37, 55, 87]:
            return "Metais alcalinos"
        elif atomic_num in [4, 12, 20, 38, 56, 88]:
            return "Metais alcalino-terrosos"
        elif block == 'd':
            return "Metais de transição"
        elif 57 <= atomic_num <= 71:
            return "Lantanídeos"
        elif 89 <= atomic_num <= 103:
            return "Actinídeos"
        elif atomic_num in [5, 14, 32, 33, 51, 52]:
            return "Semimetais"
        elif atomic_num in [6, 7, 8, 15, 16, 34]:
            return "Ametais reativos"
        elif atomic_num in [9, 17, 35, 53, 85]:
            return "Halogênios"
        elif atomic_num in [10, 18, 36, 54, 86, 118]:
            return "Gases nobres"
        elif block == 'p' and atomic_num in [13, 31, 49, 50, 81, 82, 83, 113, 114, 115, 116]:
            return "Metais pós-transição"
        else:
            return "Propriedades desconhecidas"
