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
    """Obtém dados do elemento usando Mendeleev"""
    if not HAS_MENDELEEV:
        print("Biblioteca Mendeleev não disponível!")
        return None
        
    try:
        elem = element(atomic_number)
        
        # Tratar oxidation_states de forma segura
        oxidation_states = []
        try:
            if hasattr(elem, 'oxidation_states') and elem.oxidation_states:
                oxidation_states = list(elem.oxidation_states)
        except:
            oxidation_states = []
        
        # Tratar eletronegatividade (Pauling scale)
        electronegativity = None
        try:
            if hasattr(elem, 'electronegativity'):
                if callable(elem.electronegativity):
                    electronegativity = elem.electronegativity('pauling')
                else:
                    electronegativity = elem.electronegativity
        except:
            electronegativity = None
        
        # Tratar energias de ionização
        ionization_energies = []
        try:
            if hasattr(elem, 'ionization_energies') and elem.ionization_energies:
                # Pega as primeiras 3 energias de ionização
                for ie in elem.ionization_energies[:3]:
                    if hasattr(ie, 'energy'):
                        ionization_energies.append(ie.energy)
                    else:
                        ionization_energies.append(ie)
        except:
            ionization_energies = []
        
        return {
            'symbol': elem.symbol,
            'name': elem.name,
            'mass': round(elem.atomic_weight or 0, 3),
            'electrons': elem.atomic_number,
            'period': elem.period,
            'group': getattr(elem, 'group_id', None),
            'block': getattr(elem, 'block', ''),
            'density': getattr(elem, 'density', None),
            'melting_point': getattr(elem, 'melting_point', None),
            'boiling_point': getattr(elem, 'boiling_point', None),
            'electron_configuration': getattr(elem, 'electron_configuration', ''),
            'atomic_radius': getattr(elem, 'atomic_radius', None),
            'covalent_radius': getattr(elem, 'covalent_radius', None),
            'electronegativity': electronegativity,
            'ionization_energies': ionization_energies,
            'electron_affinity': getattr(elem, 'electron_affinity', None),
            'oxidation_states': oxidation_states,
            'discovery_year': getattr(elem, 'discovery_year', None),
            'discoverers': getattr(elem, 'discoverers', None),
            'crystal_structure': getattr(elem, 'crystal_structure', None),
            'thermal_conductivity': getattr(elem, 'thermal_conductivity', None),
            'electrical_resistivity': getattr(elem, 'electrical_resistivity', None),
            'specific_heat': getattr(elem, 'specific_heat', None),
            'abundance_crust': getattr(elem, 'abundance_crust', None),
            'abundance_sea': getattr(elem, 'abundance_sea', None),
            'vdw_radius': getattr(elem, 'vdw_radius', None),
            'metallic_radius': getattr(elem, 'metallic_radius', None),
            'is_radioactive': getattr(elem, 'is_radioactive', False),
            'ground_state_term_symbol': getattr(elem, 'ground_state_term_symbol', None)
        }
    except Exception as e:
        print(f"Erro ao obter dados do elemento {atomic_number}: {e}")
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
        properties_layout.setSpacing(0)
        properties_layout.setContentsMargins(0, 0, 0, 0)
        
        # Adiciona o widget de propriedades detalhadas ocupando toda a aba
        detailed_props_group = self.create_detailed_properties_section()
        properties_layout.addWidget(detailed_props_group, stretch=1)
        
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
        
        # CRÍTICO: Adicionar as tabs ao layout principal
        layout.addWidget(main_tabs)
        self.setLayout(layout)
        
        print("Layout configurado com sucesso!")  # Debug
        print(f"Número de abas criadas: {main_tabs.count()}")  # Debug
        
        # Verifica se as labels foram criadas antes de selecionar elemento
        print(f"Labels básicas criadas: {self.name_label is not None}")  # Debug
        print(f"Labels de propriedades criadas: {self.electron_config_label is not None}")  # Debug
        
        # Aguarda um momento para garantir que todas as abas foram criadas
        QTimer.singleShot(100, lambda: self.select_element(6))  # Carbono como exemplo
        
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
        self.grid.setSpacing(1)  # Espaçamento mínimo como na imagem
        self.grid.setContentsMargins(2, 2, 2, 2)  # Margens mínimas
        
        # Criar elementos da tabela periódica
        self.create_element_buttons()
        
        grid_widget.setLayout(self.grid)
        
        # Scroll area para a tabela
        table_scroll = QScrollArea()
        table_scroll.setWidget(grid_widget)
        table_scroll.setWidgetResizable(True)
        table_scroll.setMinimumHeight(420)  # Altura ajustada para mostrar todos os elementos
        table_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        main_layout.addWidget(table_scroll)
        group.setLayout(main_layout)
        return group
    
    def create_element_buttons(self):
        """Cria os botões dos elementos da tabela periódica exatamente como na imagem"""
        print("Criando botões dos elementos...")  # Debug

        # Lista para armazenar apenas os botões de elementos
        self.element_buttons = []

        # Layout correto da tabela periódica baseado na imagem
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
                (5, 15, 84), (5, 16, 85), (5, 17, 86)],  # Cs-Rn
            7: [(6, 0, 87), (6, 1, 88), (6, 2, 89), (6, 3, 104), (6, 4, 105), (6, 5, 106), (6, 6, 107), (6, 7, 108), 
                (6, 8, 109), (6, 9, 110), (6, 10, 111), (6, 11, 112), (6, 12, 113), (6, 13, 114), (6, 14, 115), 
                (6, 15, 116), (6, 16, 117), (6, 17, 118)]  # Fr-Og
        }
        
        # Lantanídeos (período 8) - incluindo La (57) 
        lanthanides = [(8, i+2, 57+i) for i in range(15)]  # La-Lu (57-71)
        
        # Actinídeos (período 9) - incluindo Ac (89)
        actinides = [(9, i+2, 89+i) for i in range(15)]    # Ac-Lr (89-103)
        
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
                btn.setMinimumSize(45, 45)  # Aumentado um pouco para melhor legibilidade
                btn.setMaximumSize(45, 45)
                
                # Texto do botão: número atômico + símbolo (como na imagem)
                btn.setText(f"{atomic_num}\n{element_data['symbol']}")
                
                # Aplicar estilo mais parecido com a imagem
                color = self.get_element_color(element_data)
                hover_color = self.lighten_color(color)
                
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        color: white;
                        font-size: 10px;
                        font-weight: bold;
                        border: 1px solid #555555;
                        border-radius: 4px;
                        text-align: center;
                        padding: 1px;
                        margin: 0px;
                    }}
                    QPushButton:hover {{
                        border: 2px solid #ffffff;
                        background-color: {hover_color};
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
                
                # Tooltip com informações completas
                btn.setToolTip(f"{element_data['name']} ({element_data['symbol']})\n"
                              f"Número Atômico: {atomic_num}\n"
                              f"Massa: {element_data['mass']} u\n"
                              f"Bloco: {element_data.get('block', 'N/A')}\n"
                              f"Período: {element_data.get('period', 'N/A')}\n"
                              f"Grupo: {element_data.get('group', 'N/A')}")
                
                # Adicionar referência aos dados do elemento para facilitar busca e filtros
                btn.element_data = element_data
                btn.atomic_number = atomic_num
                
                # Adicionar ao grid
                self.grid.addWidget(btn, row, col)
                self.element_buttons.append(btn)
                created_count += 1
            else:
                print(f"Dados não encontrados para elemento {atomic_num}")  # Debug
        
        print(f"Total de elementos criados: {created_count}")  # Debug
        
        # Adicionar labels para lantanídeos e actinídeos
        self.add_series_labels()
    
    def add_series_labels(self):
        """Adiciona labels para lantanídeos e actinídeos nas posições originais"""
        # Label para lantanídeos (posição do La original no período 6, coluna 2)
        lanthanides_label = QLabel("57-71")
        lanthanides_label.setAlignment(Qt.AlignCenter)
        lanthanides_label.setStyleSheet("""
            QLabel {
                background-color: #BDC3C7;
                color: #2C3E50;
                border: 1px solid #95A5A6;
                border-radius: 4px;
                font-size: 8px;
                font-weight: bold;
                padding: 2px;
            }
        """)
        lanthanides_label.setFixedSize(45, 45)
        self.grid.addWidget(lanthanides_label, 5, 2)  # Posição do La
        
        # Label para actinídeos (posição do Ac original no período 7, coluna 2)  
        actinides_label = QLabel("89-103")
        actinides_label.setAlignment(Qt.AlignCenter)
        actinides_label.setStyleSheet("""
            QLabel {
                background-color: #BDC3C7;
                color: #2C3E50;
                border: 1px solid #95A5A6;
                border-radius: 4px;
                font-size: 8px;
                font-weight: bold;
                padding: 2px;
            }
        """)
        actinides_label.setFixedSize(45, 45)
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
        if not hasattr(self, 'element_buttons'):
            return

        text = text.lower().strip()

        # Percorre apenas os botões de elementos
        for widget in self.element_buttons:
            tooltip = widget.toolTip()
            button_text = widget.text().lower()

            should_show = True

            if text != "":
                should_show = False
                
                # Verifica se o texto está no tooltip
                if tooltip:
                    lines = tooltip.split('\n')
                    if len(lines) > 0:
                        # Extrai nome e símbolo da primeira linha do tooltip
                        first_line = lines[0].lower()
                        # Formato esperado: "Nome (Símbolo)"
                        if '(' in first_line and ')' in first_line:
                            element_name = first_line.split(' (')[0].strip().lower()
                            element_symbol = first_line.split('(')[1].split(')')[0].strip().lower()
                            
                            # Verifica se o texto de busca está no nome ou símbolo
                            if (text in element_name or 
                                text in element_symbol or 
                                text in button_text):
                                should_show = True
                
                # Também verifica no texto do botão (número + símbolo)
                if text in button_text:
                    should_show = True

            # Aplica a visibilidade
            widget.setVisible(should_show)

    def keyPressEvent(self, event):
        """Permite pesquisar ao pressionar Enter no campo de busca"""
        if hasattr(self, 'search_input') and self.search_input.hasFocus():
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.search_elements(self.search_input.text())
        super().keyPressEvent(event)
    
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
            item = self.grid.itemAt(i)
            if item is None:
                continue
                
            widget = item.widget()
            if isinstance(widget, QPushButton):
                widget.setVisible(True)
                current_style = widget.styleSheet()
                if "opacity: 0.3" in current_style:
                    new_style = current_style.replace("opacity: 0.3;", "")
                    widget.setStyleSheet(new_style)
    
    def apply_block_filter(self, block):
        """Aplica filtro visual por bloco"""
        if not hasattr(self, 'grid'):
            return
            
        for i in range(self.grid.count()):
            item = self.grid.itemAt(i)
            if item is None:
                continue
                
            widget = item.widget()
            if isinstance(widget, QPushButton):
                # Extrai número atômico do texto do botão
                button_text = widget.text()
                if button_text and '\n' in button_text:
                    try:
                        atomic_num = int(button_text.split('\n')[0])
                        element_data = get_element_data(atomic_num)
                        
                        if element_data:
                            element_block = element_data.get('block', '').lower()
                            
                            if element_block == block:
                                # Mostrar elemento
                                current_style = widget.styleSheet()
                                if "opacity: 0.3" in current_style:
                                    new_style = current_style.replace("opacity: 0.3;", "")
                                    widget.setStyleSheet(new_style)
                            else:
                                # Escurecer elemento
                                current_style = widget.styleSheet()
                                if "opacity: 0.3" not in current_style:
                                    if current_style.endswith("}"):
                                        new_style = current_style[:-1] + "opacity: 0.3;}"
                                    else:
                                        new_style = current_style + "opacity: 0.3;"
                                    widget.setStyleSheet(new_style)
                    except (ValueError, IndexError):
                        continue
    
    def apply_state_filter(self, state):
        """Aplica filtro visual por estado físico usando dados do Mendeleev"""
        if not hasattr(self, 'grid') or not HAS_MENDELEEV:
            return
            
        for i in range(self.grid.count()):
            item = self.grid.itemAt(i)
            if item is None:
                continue
                
            widget = item.widget()
            if isinstance(widget, QPushButton):
                # Extrai número atômico do texto do botão
                button_text = widget.text()
                if button_text and '\n' in button_text:
                    try:
                        atomic_num = int(button_text.split('\n')[0])
                        element_data = get_element_data(atomic_num)
                        
                        if element_data:
                            # Determinar estado baseado em propriedades do Mendeleev
                            melting_point = element_data.get('melting_point')
                            boiling_point = element_data.get('boiling_point')
                            
                            element_state = "Desconhecido"
                            if melting_point and boiling_point:
                                if melting_point > 298:  # > 25°C
                                    element_state = "Sólido"
                                elif boiling_point < 298:  # < 25°C
                                    element_state = "Gasoso"
                                else:
                                    element_state = "Líquido"
                            elif atomic_num >= 93:  # Elementos sintéticos
                                element_state = "Sintético"
                            
                            if element_state == state or state == "Todos":
                                # Mostrar elemento
                                current_style = widget.styleSheet()
                                if "opacity: 0.3" in current_style:
                                    new_style = current_style.replace("opacity: 0.3;", "")
                                    widget.setStyleSheet(new_style)
                            else:
                                # Escurecer elemento
                                current_style = widget.styleSheet()
                                if "opacity: 0.3" not in current_style:
                                    if current_style.endswith("}"):
                                        new_style = current_style[:-1] + "opacity: 0.3;}"
                                    else:
                                        new_style = current_style + "opacity: 0.3;"
                                    widget.setStyleSheet(new_style)
                    except (ValueError, IndexError):
                        continue
    
    def create_basic_element_info(self):
        """Cria a seção de informações básicas do elemento"""
        group = QGroupBox("Informações do Elemento")
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
        
        # Inicializar labels com valores padrão e estilo
        self.name_label = QLabel("Clique em um elemento")
        self.name_label.setStyleSheet("font-weight: bold; color: #2E86C1;")
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
        
        # DEBUG: Confirmar que as labels foram criadas
        print(f"Labels básicas criadas: {self.name_label is not None}")
        return group

    def create_detailed_properties_section(self):
        """Cria a seção de propriedades detalhadas seguindo o padrão da aba de exemplo"""
        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: #3c3c3c;")
        
        # Layout principal que ocupa toda a tela
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # === TODAS AS PROPRIEDADES EM UMA ÚNICA ÁREA ===
        properties_panel = QWidget()
        properties_panel.setStyleSheet("""
            QWidget {
                background-color: #2c2c2c;
                padding: 20px;
            }
        """)
        
        # Layout de grid para organizar as propriedades em colunas
        properties_layout = QGridLayout()
        properties_layout.setSpacing(30)
        properties_layout.setContentsMargins(20, 20, 20, 20)
        
        # === PROPRIEDADES BÁSICAS ===
        basic_group = QGroupBox("Propriedades Básicas")
        basic_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                min-width: 300px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        basic_layout = QFormLayout()
        basic_layout.setSpacing(8)
        basic_layout.setLabelAlignment(Qt.AlignLeft)
        
        # Labels para propriedades básicas
        self.electron_config_label = QLabel("-")
        self.oxidation_states_label = QLabel("-")
        self.electronegativity_label = QLabel("-")
        self.atomic_radius_label = QLabel("-")
        
        # Estilo para as labels
        label_style = "color: #ffffff; font-weight: normal; padding: 3px; background-color: transparent;"
        field_label_style = "color: #cccccc; font-weight: bold; padding: 3px;"
        
        self.electron_config_label.setStyleSheet(label_style)
        self.oxidation_states_label.setStyleSheet(label_style)
        self.electronegativity_label.setStyleSheet(label_style)
        self.atomic_radius_label.setStyleSheet(label_style)
        
        # Labels de campo
        config_label = QLabel("Configuração Eletrônica:")
        config_label.setStyleSheet(field_label_style)
        oxidation_label = QLabel("Estados de Oxidação:")
        oxidation_label.setStyleSheet(field_label_style)
        electro_label = QLabel("Eletronegatividade:")
        electro_label.setStyleSheet(field_label_style)
        radius_label = QLabel("Raio Atômico:")
        radius_label.setStyleSheet(field_label_style)
        
        basic_layout.addRow(config_label, self.electron_config_label)
        basic_layout.addRow(oxidation_label, self.oxidation_states_label)
        basic_layout.addRow(electro_label, self.electronegativity_label)
        basic_layout.addRow(radius_label, self.atomic_radius_label)
        
        basic_group.setLayout(basic_layout)
        
        # === PROPRIEDADES FÍSICAS ===
        physical_group = QGroupBox("Propriedades Físicas")
        physical_group.setStyleSheet(basic_group.styleSheet())
        
        physical_layout = QFormLayout()
        physical_layout.setSpacing(8)
        physical_layout.setLabelAlignment(Qt.AlignLeft)
        
        self.melting_point_label = QLabel("-")
        self.boiling_point_label = QLabel("-")
        self.density_label = QLabel("-")
        self.thermal_conductivity_label = QLabel("-")
        
        self.melting_point_label.setStyleSheet(label_style)
        self.boiling_point_label.setStyleSheet(label_style)
        self.density_label.setStyleSheet(label_style)
        self.thermal_conductivity_label.setStyleSheet(label_style)
        
        melting_label = QLabel("Ponto de Fusão:")
        melting_label.setStyleSheet(field_label_style)
        boiling_label = QLabel("Ponto de Ebulição:")
        boiling_label.setStyleSheet(field_label_style)
        density_label = QLabel("Densidade:")
        density_label.setStyleSheet(field_label_style)
        thermal_label = QLabel("Condutividade Térmica:")
        thermal_label.setStyleSheet(field_label_style)
        
        physical_layout.addRow(melting_label, self.melting_point_label)
        physical_layout.addRow(boiling_label, self.boiling_point_label)
        physical_layout.addRow(density_label, self.density_label)
        physical_layout.addRow(thermal_label, self.thermal_conductivity_label)
        
        physical_group.setLayout(physical_layout)
        
        # === INFORMAÇÕES HISTÓRICAS ===
        historical_group = QGroupBox("Informações Históricas")
        historical_group.setStyleSheet(basic_group.styleSheet())
        
        historical_layout = QFormLayout()
        historical_layout.setSpacing(8)
        historical_layout.setLabelAlignment(Qt.AlignLeft)
        
        self.discovery_year_label = QLabel("-")
        self.discoverers_label = QLabel("-")
        self.abundance_crust_label = QLabel("-")
        self.is_radioactive_label = QLabel("-")
        
        self.discovery_year_label.setStyleSheet(label_style)
        self.discoverers_label.setStyleSheet(label_style)
        self.abundance_crust_label.setStyleSheet(label_style)
        self.is_radioactive_label.setStyleSheet(label_style)
        
        # Permitir quebra de linha para discoverers
        self.discoverers_label.setWordWrap(True)
        
        year_label = QLabel("Ano de Descoberta:")
        year_label.setStyleSheet(field_label_style)
        discoverers_field_label = QLabel("Descobridores:")
        discoverers_field_label.setStyleSheet(field_label_style)
        abundance_label = QLabel("Abundância na Crosta:")
        abundance_label.setStyleSheet(field_label_style)
        radioactive_label = QLabel("Radioativo:")
        radioactive_label.setStyleSheet(field_label_style)
        
        historical_layout.addRow(year_label, self.discovery_year_label)
        historical_layout.addRow(discoverers_field_label, self.discoverers_label)
        historical_layout.addRow(abundance_label, self.abundance_crust_label)
        historical_layout.addRow(radioactive_label, self.is_radioactive_label)
        
        historical_group.setLayout(historical_layout)
        
        # Organizar em grid: 2 colunas na primeira linha, 1 na segunda
        properties_layout.addWidget(basic_group, 0, 0)
        properties_layout.addWidget(physical_group, 0, 1)
        properties_layout.addWidget(historical_group, 1, 0, 1, 2)  # Span 2 colunas
        
        # Adicionar stretch para expandir verticalmente
        properties_layout.setRowStretch(2, 1)
        
        properties_panel.setLayout(properties_layout)
        main_layout.addWidget(properties_panel)
        
        main_widget.setLayout(main_layout)
        
        # DEBUG: Confirmar que as labels foram criadas
        print(f"Labels de propriedades criadas: {self.electron_config_label is not None}")
        return main_widget
    
    def select_element(self, atomic_num):
        """Seleciona um elemento para visualização"""
        element_data = get_element_data(atomic_num)
        if not element_data:
            print(f"Dados não encontrados para elemento {atomic_num}")
            return
            
        self.current_element = atomic_num
        print(f"Selecionando elemento: {element_data['name']} ({atomic_num})")  # Debug
        
        # Verifica se as labels existem antes de atualizar
        if not hasattr(self, 'name_label') or self.name_label is None:
            print("Labels não foram criadas ainda!")
            return
        
        # Atualiza informações básicas
        try:
            self.name_label.setText(element_data['name'])
            self.symbol_label.setText(element_data['symbol'])
            self.atomic_number_label.setText(str(atomic_num))
            self.mass_label.setText(f"{element_data['mass']} u")
            
            period = element_data.get('period', 'N/A')
            self.period_label.setText(str(period) if period else 'N/A')
            
            group = element_data.get('group')
            if group is not None and str(group).strip() and group != 'N/A':
                try:
                    group_num = int(float(group))
                    self.group_label.setText(str(group_num))
                except (ValueError, TypeError):
                    self.group_label.setText(str(group))
            else:
                self.group_label.setText('N/A')
                
            block = element_data.get('block', 'N/A')
            self.block_label.setText(block.upper() if block else 'N/A')
            
            category = self.get_element_category(element_data)
            self.category_label.setText(category)
            
            # Atualiza info rápida se existir
            if hasattr(self, 'quick_info') and self.quick_info is not None:
                self.quick_info.setText(f"{element_data['name']} - {category}")
        except Exception as e:
            print(f"Erro ao atualizar informações básicas: {e}")
        
        # Atualiza propriedades detalhadas se as labels existem
        if hasattr(self, 'electron_config_label') and self.electron_config_label is not None:
            try:
                # Configuração eletrônica
                config = element_data.get('electron_configuration', 'N/A')
                if config and config != 'N/A' and str(config).strip():
                    self.electron_config_label.setText(str(config))
                else:
                    shells = get_electron_configuration(atomic_num)
                    if shells:
                        config_text = f"Camadas: {', '.join(map(str, shells))}"
                        self.electron_config_label.setText(config_text)
                    else:
                        self.electron_config_label.setText('N/A')
                
                # Estados de oxidação
                oxidation_states = element_data.get('oxidation_states', [])
                if oxidation_states and len(oxidation_states) > 0:
                    # Formatar estados de oxidação com sinais + ou -
                    formatted_states = []
                    for state in oxidation_states:
                        if isinstance(state, (int, float)):
                            if state > 0:
                                formatted_states.append(f"+{int(state)}")
                            elif state < 0:
                                formatted_states.append(f"{int(state)}")
                            else:
                                formatted_states.append("0")
                    if formatted_states:
                        self.oxidation_states_label.setText(', '.join(formatted_states))
                    else:
                        self.oxidation_states_label.setText('N/A')
                else:
                    self.oxidation_states_label.setText('N/A')
                
                # Eletronegatividade
                electronegativity = element_data.get('electronegativity')
                if electronegativity and isinstance(electronegativity, (int, float)):
                    self.electronegativity_label.setText(f"{electronegativity:.2f}")
                else:
                    self.electronegativity_label.setText('N/A')
                
                # Raio atômico
                atomic_radius = element_data.get('atomic_radius')
                if atomic_radius and isinstance(atomic_radius, (int, float)):
                    self.atomic_radius_label.setText(f"{atomic_radius:.0f} pm")
                else:
                    self.atomic_radius_label.setText('N/A')
                
                # Pontos de fusão e ebulição
                melting_point = element_data.get('melting_point')
                if melting_point and isinstance(melting_point, (int, float)):
                    self.melting_point_label.setText(f"{melting_point:.1f} K ({melting_point-273.15:.1f} °C)")
                else:
                    self.melting_point_label.setText('N/A')
                
                boiling_point = element_data.get('boiling_point')
                if boiling_point and isinstance(boiling_point, (int, float)):
                    self.boiling_point_label.setText(f"{boiling_point:.1f} K ({boiling_point-273.15:.1f} °C)")
                else:
                    self.boiling_point_label.setText('N/A')
                
                # Densidade
                density = element_data.get('density')
                if density and isinstance(density, (int, float)):
                    self.density_label.setText(f"{density:.3f} g/cm³")
                else:
                    self.density_label.setText('N/A')
                
                # Propriedades estendidas se existirem
                if hasattr(self, 'ionization_energy_label'):
                    ionization_energies = element_data.get('ionization_energies', [])
                    if ionization_energies and len(ionization_energies) > 0:
                        first_ie = ionization_energies[0]
                        if isinstance(first_ie, (int, float)):
                            self.ionization_energy_label.setText(f"{first_ie:.1f} eV")
                        else:
                            self.ionization_energy_label.setText('N/A')
                    else:
                        self.ionization_energy_label.setText('N/A')
                
                if hasattr(self, 'electron_affinity_label'):
                    electron_affinity = element_data.get('electron_affinity')
                    if electron_affinity and isinstance(electron_affinity, (int, float)):
                        self.electron_affinity_label.setText(f"{electron_affinity:.1f} eV")
                    else:
                        self.electron_affinity_label.setText('N/A')
                
                if hasattr(self, 'thermal_conductivity_label'):
                    thermal_conductivity = element_data.get('thermal_conductivity')
                    if thermal_conductivity and isinstance(thermal_conductivity, (int, float)):
                        self.thermal_conductivity_label.setText(f"{thermal_conductivity:.1f} W/(m·K)")
                    else:
                        self.thermal_conductivity_label.setText('N/A')
                
                if hasattr(self, 'specific_heat_label'):
                    specific_heat = element_data.get('specific_heat')
                    if specific_heat and isinstance(specific_heat, (int, float)):
                        self.specific_heat_label.setText(f"{specific_heat:.1f} J/(kg·K)")
                    else:
                        self.specific_heat_label.setText('N/A')
                
                if hasattr(self, 'discovery_year_label'):
                    discovery_year = element_data.get('discovery_year')
                    if discovery_year:
                        self.discovery_year_label.setText(str(discovery_year))
                    else:
                        self.discovery_year_label.setText('N/A')
                
                if hasattr(self, 'discoverers_label'):
                    discoverers = element_data.get('discoverers')
                    if discoverers:
                        # Tratar caso seja uma lista ou string
                        if isinstance(discoverers, list):
                            self.discoverers_label.setText(', '.join(discoverers))
                        else:
                            self.discoverers_label.setText(str(discoverers))
                    else:
                        self.discoverers_label.setText('N/A')
                
                if hasattr(self, 'abundance_crust_label'):
                    abundance_crust = element_data.get('abundance_crust')
                    if abundance_crust and isinstance(abundance_crust, (int, float)):
                        self.abundance_crust_label.setText(f"{abundance_crust:.2e} mg/kg")
                    else:
                        self.abundance_crust_label.setText('N/A')
                
                if hasattr(self, 'crystal_structure_label'):
                    crystal_structure = element_data.get('crystal_structure')
                    if crystal_structure:
                        self.crystal_structure_label.setText(str(crystal_structure))
                    else:
                        self.crystal_structure_label.setText('N/A')
                
                if hasattr(self, 'is_radioactive_label'):
                    is_radioactive = element_data.get('is_radioactive', False)
                    self.is_radioactive_label.setText('Sim' if is_radioactive else 'Não')
                
            except Exception as e:
                print(f"Erro ao atualizar propriedades detalhadas: {e}")
        
        # Atualiza modelo de Bohr
        if hasattr(self, 'bohr_widget') and self.bohr_widget is not None:
            try:
                self.bohr_widget.set_element(atomic_num)
            except Exception as e:
                print(f"Erro ao atualizar widget Bohr: {e}")
        
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
    
    def get_element_color(self, element_data):
        """Retorna cor do elemento baseada na categoria usando Mendeleev"""
        atomic_num = element_data.get('electrons', 1)
        
        # Cores otimizadas baseadas nas categorias
        color_map = {
            1: "#5DADE2",  # Hidrogênio - azul claro
            2: "#BB8FCE",  # Hélio - roxo claro
            **{n: "#52C41A" for n in [3, 11, 19, 37, 55, 87]},  # Metais alcalinos - verde escuro
            **{n: "#73D13D" for n in [4, 12, 20, 38, 56, 88]},  # Metais alcalino-terrosos - verde claro
            **{n: "#4A90E2" for n in list(range(21, 31)) + list(range(39, 49)) + list(range(72, 81)) + list(range(104, 113))},  # Metais de transição - azul
            **{n: "#85C1E9" for n in range(57, 72)},  # Lantanídeos - azul claro
            **{n: "#5499C7" for n in range(89, 104)},  # Actinídeos - azul escuro
            **{n: "#7FB3D3" for n in [13, 31, 49, 50, 81, 82, 83, 113, 114, 115, 116]},  # Metais pós-transição
            **{n: "#F7DC6F" for n in [5, 14, 32, 33, 51, 52]},  # Metaloides - amarelo
            **{n: "#F1948A" for n in [6, 7, 8, 15, 16, 34, 84]},  # Não-metais - rosa
            **{n: "#F8C471" for n in [9, 17, 35, 53, 85, 117]},  # Halogênios - laranja
            **{n: "#D2B4DE" for n in [10, 18, 36, 54, 86, 118]},  # Gases nobres - roxo
        }
        
        return color_map.get(atomic_num, "#6c757d")  # Cinza padrão
    
    def lighten_color(self, color):
        """Clareia uma cor para efeito hover"""
        # Remove o # se existir
        color = color.lstrip('#')
        
        # Converte para RGB
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        
        # Clareia adicionando 30 a cada componente (máximo 255)
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        
        # Converte de volta para hex
        return f"#{r:02x}{g:02x}{b:02x}"
