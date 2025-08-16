"""
Aba da Tabela Periódica Interativa - Layout Responsivo e Fiel ao Google
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QTextEdit, QGroupBox, QScrollArea, QFrame, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor


class PeriodicTableTab(QWidget):
    """Aba da Tabela Periódica Interativa"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_element = None
        self.element_buttons = {}
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        # Tabela periódica responsiva
        table_widget = self.create_periodic_table_google_style()
        table_widget.setSizePolicy(table_widget.sizePolicy().Expanding, table_widget.sizePolicy().Expanding)
        main_layout.addWidget(table_widget, 3)
        # Painel de informações
        info_widget = self.create_element_info_panel_enhanced()
        info_widget.setSizePolicy(info_widget.sizePolicy().Expanding, info_widget.sizePolicy().Expanding)
        main_layout.addWidget(info_widget, 2)
        self.setLayout(main_layout)
    
    def create_periodic_table(self) -> QWidget:
        """Cria a tabela periódica com layout fiel ao padrão internacional"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Tabela Periódica dos Elementos")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        grid_container = QWidget()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(2)
        
        # Adicionar números dos grupos (colunas) no topo
        for i in range(18):
            group_label = QLabel(str(i + 1))
            group_label.setAlignment(Qt.AlignCenter)
            group_label.setFont(QFont("Arial", 8))
            group_label.setMaximumHeight(20)
            grid_layout.addWidget(group_label, 0, i+1)
        
        # Adicionar números dos períodos (linhas) à esquerda
        for i in range(1, 8):
            period_label = QLabel(str(i))
            period_label.setAlignment(Qt.AlignCenter)
            period_label.setFont(QFont("Arial", 8))
            period_label.setMaximumWidth(20)
            grid_layout.addWidget(period_label, i, 0)
        
        # Adicionar células vazias para layout fiel
        for row in range(1, 8):
            for col in range(1, 19):
                grid_layout.addWidget(QLabel(""), row, col)
        
        # Adicionar lantanídeos e actinídeos em linhas separadas
        for col in range(4, 19):
            grid_layout.addWidget(QLabel(""), 8, col)
            grid_layout.addWidget(QLabel(""), 9, col)
        
        # Dados dos elementos
        elements = self.get_element_data()
        
        # Criar os botões dos elementos
        for atomic_num, data in elements.items():
            button = self.create_element_button(atomic_num, data)
            self.element_buttons[atomic_num] = button
            row, col = data['position']
            grid_layout.addWidget(button, row, col)
        
        grid_container.setLayout(grid_layout)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidget(grid_container)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        widget.setLayout(layout)
        return widget
    
    def get_element_data(self):
        """Retorna os dados dos elementos com suas posições corretas na tabela periódica"""
        element_list = [
            (1, 'H', 'Hidrogênio', 1.008, 'nonmetal', 1, 1),
            (2, 'He', 'Hélio', 4.003, 'noble_gas', 1, 18),
            (3, 'Li', 'Lítio', 6.941, 'alkali_metal', 2, 1),
            (4, 'Be', 'Berílio', 9.012, 'alkaline_earth', 2, 2),
            (5, 'B', 'Boro', 10.811, 'metalloid', 2, 13),
            (6, 'C', 'Carbono', 12.011, 'nonmetal', 2, 14),
            (7, 'N', 'Nitrogênio', 14.007, 'nonmetal', 2, 15),
            (8, 'O', 'Oxigênio', 15.999, 'nonmetal', 2, 16),
            (9, 'F', 'Flúor', 18.998, 'halogen', 2, 17),
            (10, 'Ne', 'Neônio', 20.180, 'noble_gas', 2, 18),
            (11, 'Na', 'Sódio', 22.990, 'alkali_metal', 3, 1),
            (12, 'Mg', 'Magnésio', 24.305, 'alkaline_earth', 3, 2),
            (13, 'Al', 'Alumínio', 26.982, 'post_transition', 3, 13),
            (14, 'Si', 'Silício', 28.086, 'metalloid', 3, 14),
            (15, 'P', 'Fósforo', 30.974, 'nonmetal', 3, 15),
            (16, 'S', 'Enxofre', 32.065, 'nonmetal', 3, 16),
            (17, 'Cl', 'Cloro', 35.453, 'halogen', 3, 17),
            (18, 'Ar', 'Argônio', 39.948, 'noble_gas', 3, 18),
            (19, 'K', 'Potássio', 39.098, 'alkali_metal', 4, 1),
            (20, 'Ca', 'Cálcio', 40.078, 'alkaline_earth', 4, 2),
            (21, 'Sc', 'Escândio', 44.956, 'transition_metal', 4, 3),
            (22, 'Ti', 'Titânio', 47.867, 'transition_metal', 4, 4),
            (23, 'V', 'Vanádio', 50.942, 'transition_metal', 4, 5),
            (24, 'Cr', 'Cromo', 51.996, 'transition_metal', 4, 6),
            (25, 'Mn', 'Manganês', 54.938, 'transition_metal', 4, 7),
            (26, 'Fe', 'Ferro', 55.845, 'transition_metal', 4, 8),
            (27, 'Co', 'Cobalto', 58.933, 'transition_metal', 4, 9),
            (28, 'Ni', 'Níquel', 58.693, 'transition_metal', 4, 10),
            (29, 'Cu', 'Cobre', 63.546, 'transition_metal', 4, 11),
            (30, 'Zn', 'Zinco', 65.38, 'transition_metal', 4, 12),
            (31, 'Ga', 'Gálio', 69.723, 'post_transition', 4, 13),
            (32, 'Ge', 'Germânio', 72.64, 'metalloid', 4, 14),
            (33, 'As', 'Arsênio', 74.922, 'metalloid', 4, 15),
            (34, 'Se', 'Selênio', 78.96, 'nonmetal', 4, 16),
            (35, 'Br', 'Bromo', 79.904, 'halogen', 4, 17),
            (36, 'Kr', 'Criptônio', 83.798, 'noble_gas', 4, 18),
            (37, 'Rb', 'Rubídio', 85.468, 'alkali_metal', 5, 1),
            (38, 'Sr', 'Estrôncio', 87.62, 'alkaline_earth', 5, 2),
            (39, 'Y', 'Ítrio', 88.906, 'transition_metal', 5, 3),
            (40, 'Zr', 'Zircônio', 91.224, 'transition_metal', 5, 4),
            (41, 'Nb', 'Nióbio', 92.906, 'transition_metal', 5, 5),
            (42, 'Mo', 'Molibdênio', 95.95, 'transition_metal', 5, 6),
            (43, 'Tc', 'Tecnécio', 98, 'transition_metal', 5, 7),
            (44, 'Ru', 'Rutênio', 101.07, 'transition_metal', 5, 8),
            (45, 'Rh', 'Ródio', 102.91, 'transition_metal', 5, 9),
            (46, 'Pd', 'Paládio', 106.42, 'transition_metal', 5, 10),
            (47, 'Ag', 'Prata', 107.87, 'transition_metal', 5, 11),
            (48, 'Cd', 'Cádmio', 112.41, 'transition_metal', 5, 12),
            (49, 'In', 'Índio', 114.82, 'post_transition', 5, 13),
            (50, 'Sn', 'Estanho', 118.71, 'post_transition', 5, 14),
            (51, 'Sb', 'Antimônio', 121.76, 'metalloid', 5, 15),
            (52, 'Te', 'Telúrio', 127.60, 'metalloid', 5, 16),
            (53, 'I', 'Iodo', 126.90, 'halogen', 5, 17),
            (54, 'Xe', 'Xenônio', 131.29, 'noble_gas', 5, 18),
            (55, 'Cs', 'Césio', 132.91, 'alkali_metal', 6, 1),
            (56, 'Ba', 'Bário', 137.33, 'alkaline_earth', 6, 2),
            # Lantanídeos
            (57, 'La', 'Lantânio', 138.91, 'lanthanide', 8, 4),
            (58, 'Ce', 'Cério', 140.12, 'lanthanide', 8, 5),
            (59, 'Pr', 'Praseodímio', 140.91, 'lanthanide', 8, 6),
            (60, 'Nd', 'Neodímio', 144.24, 'lanthanide', 8, 7),
            (61, 'Pm', 'Promécio', 145, 'lanthanide', 8, 8),
            (62, 'Sm', 'Samário', 150.36, 'lanthanide', 8, 9),
            (63, 'Eu', 'Európio', 151.96, 'lanthanide', 8, 10),
            (64, 'Gd', 'Gadolínio', 157.25, 'lanthanide', 8, 11),
            (65, 'Tb', 'Térbio', 158.93, 'lanthanide', 8, 12),
            (66, 'Dy', 'Disprósio', 162.50, 'lanthanide', 8, 13),
            (67, 'Ho', 'Hólmio', 164.93, 'lanthanide', 8, 14),
            (68, 'Er', 'Érbio', 167.26, 'lanthanide', 8, 15),
            (69, 'Tm', 'Túlio', 168.93, 'lanthanide', 8, 16),
            (70, 'Yb', 'Itérbio', 173.05, 'lanthanide', 8, 17),
            (71, 'Lu', 'Lutécio', 174.97, 'lanthanide', 8, 18),
            (72, 'Hf', 'Háfnio', 178.49, 'transition_metal', 6, 4),
            (73, 'Ta', 'Tântalo', 180.95, 'transition_metal', 6, 5),
            (74, 'W', 'Tungstênio', 183.84, 'transition_metal', 6, 6),
            (75, 'Re', 'Rênio', 186.21, 'transition_metal', 6, 7),
            (76, 'Os', 'Ósmio', 190.23, 'transition_metal', 6, 8),
            (77, 'Ir', 'Irídio', 192.22, 'transition_metal', 6, 9),
            (78, 'Pt', 'Platina', 195.08, 'transition_metal', 6, 10),
            (79, 'Au', 'Ouro', 196.97, 'transition_metal', 6, 11),
            (80, 'Hg', 'Mercúrio', 200.59, 'transition_metal', 6, 12),
            (81, 'Tl', 'Tálio', 204.38, 'post_transition', 6, 13),
            (82, 'Pb', 'Chumbo', 207.2, 'post_transition', 6, 14),
            (83, 'Bi', 'Bismuto', 208.98, 'post_transition', 6, 15),
            (84, 'Po', 'Polônio', 209, 'post_transition', 6, 16),
            (85, 'At', 'Astato', 210, 'halogen', 6, 17),
            (86, 'Rn', 'Radônio', 222, 'noble_gas', 6, 18),
            (87, 'Fr', 'Frâncio', 223, 'alkali_metal', 7, 1),
            (88, 'Ra', 'Rádio', 226, 'alkaline_earth', 7, 2),
            # Actinídeos
            (89, 'Ac', 'Actínio', 227, 'actinide', 9, 4),
            (90, 'Th', 'Tório', 232.04, 'actinide', 9, 5),
            (91, 'Pa', 'Protactínio', 231.04, 'actinide', 9, 6),
            (92, 'U', 'Urânio', 238.03, 'actinide', 9, 7),
            (93, 'Np', 'Neptúnio', 237, 'actinide', 9, 8),
            (94, 'Pu', 'Plutônio', 244, 'actinide', 9, 9),
            (95, 'Am', 'Amerício', 243, 'actinide', 9, 10),
            (96, 'Cm', 'Cúrio', 247, 'actinide', 9, 11),
            (97, 'Bk', 'Berquélio', 247, 'actinide', 9, 12),
            (98, 'Cf', 'Califórnio', 251, 'actinide', 9, 13),
            (99, 'Es', 'Einstênio', 252, 'actinide', 9, 14),
            (100, 'Fm', 'Férmio', 257, 'actinide', 9, 15),
            (101, 'Md', 'Mendelévio', 258, 'actinide', 9, 16),
            (102, 'No', 'Nobélio', 259, 'actinide', 9, 17),
            (103, 'Lr', 'Laurêncio', 266, 'actinide', 9, 18),
            (104, 'Rf', 'Rutherfórdio', 267, 'transition_metal', 7, 4),
            (105, 'Db', 'Dúbnio', 270, 'transition_metal', 7, 5),
            (106, 'Sg', 'Seabórgio', 271, 'transition_metal', 7, 6),
            (107, 'Bh', 'Bóhrio', 270, 'transition_metal', 7, 7),
            (108, 'Hs', 'Hássio', 277, 'transition_metal', 7, 8),
            (109, 'Mt', 'Meitnério', 278, 'unknown', 7, 9),
            (110, 'Ds', 'Darmstádtio', 281, 'unknown', 7, 10),
            (111, 'Rg', 'Roentgênio', 282, 'unknown', 7, 11),
            (112, 'Cn', 'Copernício', 285, 'unknown', 7, 12),
            (113, 'Nh', 'Nihônio', 286, 'unknown', 7, 13),
            (114, 'Fl', 'Fleróvio', 289, 'unknown', 7, 14),
            (115, 'Mc', 'Moscóvio', 290, 'unknown', 7, 15),
            (116, 'Lv', 'Livermório', 293, 'unknown', 7, 16),
            (117, 'Ts', 'Tenessino', 294, 'halogen', 7, 17),
            (118, 'Og', 'Oganessônio', 294, 'noble_gas', 7, 18)
        ]
        elements = {}
        for num, symbol, name, mass, category, row, col in element_list:
            elements[num] = {
                'symbol': symbol,
                'name': name,
                'mass': mass,
                'category': category,
                'position': (row, col-1)
            }
        return elements
    
    def create_element_button(self, atomic_num, data):
        """Cria o botão para um elemento seguindo o padrão da referência"""
        button = QPushButton()
        button.setFixedSize(60, 60)
        
        # Layout do texto: número pequeno no canto, símbolo grande, nome embaixo
        text = f"{atomic_num}\n{data['symbol']}\n{data['name'][:4]}"
        button.setText(text)
        button.setFont(QFont("Arial", 7, QFont.Bold))
        
        # Tooltip com informações resumidas
        tooltip = f"{data['name']} ({data['symbol']})\nNº Atômico: {atomic_num}\nMassa: {data['mass']} u\nCategoria: {data['category'].replace('_', ' ').title()}"
        button.setToolTip(tooltip)
        
        # Cores fiéis à referência do Google
        colors = {
            'alkali_metal': '#ff9999',      # Rosa claro
            'alkaline_earth': '#66cccc',    # Azul claro
            'transition_metal': '#6699ff',  # Azul médio
            'post_transition': '#99cc99',   # Verde claro
            'metalloid': '#ffcc66',         # Amarelo
            'nonmetal': '#cc99ff',          # Roxo claro
            'halogen': '#ffcc99',           # Laranja claro
            'noble_gas': '#ff99cc',         # Rosa
            'lanthanide': '#cc99cc',        # Roxo médio
            'actinide': '#ffaa80',          # Laranja salmão
            'unknown': '#cccccc'            # Cinza
        }
        
        color = colors.get(data['category'], '#f0f0f0')
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 1px solid #666;
                border-radius: 3px;
                font-weight: bold;
                color: #333;
                text-align: center;
                padding: 2px;
            }}
            QPushButton:hover {{
                background-color: #ffff99;
                border: 2px solid #ff6600;
            }}
            QPushButton:pressed {{
                background-color: #ffd700;
            }}
        """)
        
        button.clicked.connect(lambda checked, num=atomic_num: self.on_element_clicked_new(num))
        return button

    def create_periodic_table_google_style(self) -> QWidget:
        """Cria tabela periódica idêntica à referência do Google"""
        widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Título
        title = QLabel("Tabela Periódica dos Elementos")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        main_layout.addWidget(title)
        
        # Container principal com grid
        grid_widget = QWidget()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(2)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # Elementos organizados por posição exata na tabela
        elements_by_position = {}
        elements = self.get_element_data()
        
        # Mapear elementos por posição
        for num, data in elements.items():
            row, col = data['position']
            elements_by_position[(row, col)] = (num, data)
        
        # Criar grid 9x18 (incluindo lantanídeos/actinídeos)
        for row in range(1, 10):
            for col in range(1, 19):
                if (row, col-1) in elements_by_position:
                    num, data = elements_by_position[(row, col-1)]
                    button = self.create_element_button(num, data)
                    self.element_buttons[num] = button
                    grid_layout.addWidget(button, row, col)
                else:
                    # Célula vazia
                    spacer = QLabel("")
                    spacer.setFixedSize(60, 60)
                    grid_layout.addWidget(spacer, row, col)
        
        # Adicionar labels de grupos (1-18)
        for i in range(18):
            label = QLabel(str(i + 1))
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont("Arial", 9, QFont.Bold))
            grid_layout.addWidget(label, 0, i + 1)
        
        # Adicionar labels de períodos (1-7)
        for i in range(1, 8):
            label = QLabel(str(i))
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont("Arial", 9, QFont.Bold))
            grid_layout.addWidget(label, i, 0)
        
        grid_widget.setLayout(grid_layout)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidget(grid_widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_layout.addWidget(scroll)
        
        widget.setLayout(main_layout)
        return widget

    def create_element_info_panel_enhanced(self):
        """Painel de informações melhorado"""
        info_widget = QGroupBox("Informações do Elemento")
        layout = QVBoxLayout()
        
        # Nome do elemento
        self.element_name = QLabel("Selecione um elemento")
        self.element_name.setFont(QFont("Arial", 14, QFont.Bold))
        self.element_name.setAlignment(Qt.AlignCenter)
        self.element_name.setStyleSheet("color: #2c3e50; margin: 5px;")
        layout.addWidget(self.element_name)
        
        # Símbolo grande
        self.element_symbol = QLabel("")
        self.element_symbol.setFont(QFont("Arial", 32, QFont.Bold))
        self.element_symbol.setAlignment(Qt.AlignCenter)
        self.element_symbol.setStyleSheet("color: #3498db; margin: 10px; background: #ecf0f1; border-radius: 10px; padding: 10px;")
        layout.addWidget(self.element_symbol)
        
        # Informações básicas em grid
        info_grid_widget = QWidget()
        info_grid = QGridLayout()
        
        self.atomic_num_label = QLabel("Número Atômico: -")
        self.mass_label = QLabel("Massa Atômica: -")
        self.category_label = QLabel("Categoria: -")
        self.period_label = QLabel("Período: -")
        self.group_label = QLabel("Grupo: -")
        
        info_grid.addWidget(self.atomic_num_label, 0, 0)
        info_grid.addWidget(self.mass_label, 0, 1)
        info_grid.addWidget(self.category_label, 1, 0)
        info_grid.addWidget(self.period_label, 1, 1)
        info_grid.addWidget(self.group_label, 2, 0)
        
        info_grid_widget.setLayout(info_grid)
        layout.addWidget(info_grid_widget)
        
        # Propriedades detalhadas
        self.element_details = QTextEdit()
        self.element_details.setMaximumHeight(200)
        self.element_details.setReadOnly(True)
        self.element_details.setStyleSheet("background: #f8f9fa; border: 1px solid #dee2e6;")
        layout.addWidget(self.element_details)
        
        # Campo de busca
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Buscar:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite símbolo ou nome...")
        self.search_input.textChanged.connect(self.search_element)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Legenda melhorada
        legend_group = QGroupBox("Legenda de Categorias")
        legend_layout = QVBoxLayout()
        
        categories = [
            ('Metais Alcalinos', '#ff9999'),
            ('Metais Alcalino-terrosos', '#66cccc'),
            ('Metais de Transição', '#6699ff'),
            ('Pós-transição', '#99cc99'),
            ('Metaloides', '#ffcc66'),
            ('Não-metais', '#cc99ff'),
            ('Halogênios', '#ffcc99'),
            ('Gases Nobres', '#ff99cc'),
            ('Lantanídeos', '#cc99cc'),
            ('Actinídeos', '#ffaa80')
        ]
        
        for i, (name, color) in enumerate(categories):
            if i % 2 == 0:
                row_layout = QHBoxLayout()
            
            color_box = QLabel("■")
            color_box.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold;")
            text_label = QLabel(name)
            text_label.setFont(QFont("Arial", 8))
            
            item_layout = QHBoxLayout()
            item_layout.addWidget(color_box)
            item_layout.addWidget(text_label)
            item_layout.addStretch()
            
            if i % 2 == 0:
                row_layout.addLayout(item_layout)
            else:
                row_layout.addLayout(item_layout)
                legend_layout.addLayout(row_layout)
        
        legend_group.setLayout(legend_layout)
        layout.addWidget(legend_group)
        
        info_widget.setLayout(layout)
        return info_widget

    def search_element(self):
        """Busca rápida por símbolo ou nome"""
        text = self.search_input.text().strip().lower()
        if not text:
            return
        elements = self.get_element_data()
        for num, data in elements.items():
            if text == data['symbol'].lower() or text in data['name'].lower():
                self.on_element_clicked(num)
                break

    def on_element_clicked(self, atomic_num):
        """Manipula o clique em um elemento"""
        elements = self.get_element_data()
        if atomic_num in elements:
            element = elements[atomic_num]
            self.selected_element = atomic_num
            
            # Atualizar informações
            self.element_name.setText(element['name'])
            self.element_symbol.setText(element['symbol'])
            
            # Propriedades extras (exemplo para alguns elementos)
            extra = {
                1: {'config': '1s¹', 'estado': 'Gasoso', 'densidade': '0.08988 g/L', 'fusao': '-259.16°C', 'ebulicao': '-252.87°C', 'descoberta': '1766'},
                6: {'config': '1s² 2s² 2p²', 'estado': 'Sólido', 'densidade': '2.267 g/cm³', 'fusao': '3550°C', 'ebulicao': '4027°C', 'descoberta': 'Antiguidade'},
                8: {'config': '1s² 2s² 2p⁴', 'estado': 'Gasoso', 'densidade': '1.429 g/L', 'fusao': '-218.79°C', 'ebulicao': '-182.95°C', 'descoberta': '1774'},
                26: {'config': '[Ar] 4s² 3d⁶', 'estado': 'Sólido', 'densidade': '7.874 g/cm³', 'fusao': '1538°C', 'ebulicao': '2862°C', 'descoberta': 'Antiguidade'},
                79: {'config': '[Xe] 4f¹⁴ 5d¹⁰ 6s¹', 'estado': 'Sólido', 'densidade': '19.32 g/cm³', 'fusao': '1064°C', 'ebulicao': '2856°C', 'descoberta': 'Antiguidade'}
            }
            
            details = f"""
<b>Número Atômico:</b> {atomic_num}<br>
<b>Símbolo:</b> {element['symbol']}<br>
<b>Nome:</b> {element['name']}<br>
<b>Massa Atômica:</b> {element['mass']} u<br>
<b>Categoria:</b> {element['category'].replace('_', ' ').title()}<br>
"""
            if atomic_num in extra:
                e = extra[atomic_num]
                details += f"<b>Configuração Eletrônica:</b> {e['config']}<br>"
                details += f"<b>Estado Físico:</b> {e['estado']}<br>"
                details += f"<b>Densidade:</b> {e['densidade']}<br>"
                details += f"<b>Ponto de Fusão:</b> {e['fusao']}<br>"
                details += f"<b>Ponto de Ebulição:</b> {e['ebulicao']}<br>"
                details += f"<b>Ano de Descoberta:</b> {e['descoberta']}<br>"
            details += f"<br><b>Propriedades:</b><br>• Elemento químico da tabela periódica<br>• Posição: Período {element['position'][0]}, Grupo {element['position'][1]+1}<br><br>"
            applications = {
                1: "Combustível de foguetes, hidrogenação",
                6: "Compostos orgânicos, diamante, grafite",
                8: "Respiração, combustão, oxidação",
                26: "Construção civil, automóveis, ferramentas",
                29: "Fios elétricos, moedas, ligas",
                47: "Joias, moedas, eletrônicos",
                79: "Joias, reserva de valor, eletrônicos"
            }
            if atomic_num in applications:
                details += f"• {applications[atomic_num]}"
            else:
                details += "• Diversas aplicações industriais e científicas"
            self.element_details.setHtml(details)
            
            # Destacar o elemento selecionado e grupo/período
            sel_row, sel_col = element['position']
            for num, button in self.element_buttons.items():
                row, col = elements[num]['position']
                style = button.styleSheet().replace("border: 3px solid #FF0000;", "")
                if num == atomic_num:
                    style += "\nQPushButton { border: 3px solid #FF0000; }"
                elif row == sel_row or col == sel_col:
                    style += "\nQPushButton { border: 2px solid #2E86AB; }"
                button.setStyleSheet(style)
    
    def on_element_clicked_new(self, atomic_num):
        """Manipula o clique em um elemento - versão melhorada"""
        elements = self.get_element_data()
        if atomic_num in elements:
            element = elements[atomic_num]
            self.selected_element = atomic_num
            
            # Atualizar informações básicas
            self.element_name.setText(element['name'])
            self.element_symbol.setText(element['symbol'])
            
            # Informações básicas
            self.atomic_num_label.setText(f"Número Atômico: {atomic_num}")
            self.mass_label.setText(f"Massa Atômica: {element['mass']} u")
            self.category_label.setText(f"Categoria: {element['category'].replace('_', ' ').title()}")
            self.period_label.setText(f"Período: {element['position'][0]}")
            self.group_label.setText(f"Grupo: {element['position'][1]+1}")
            
            # Propriedades detalhadas
            extra_props = {
                1: {'config': '1s¹', 'estado': 'Gasoso', 'densidade': '0.08988 g/L', 'fusao': '-259.16°C', 'ebulicao': '-252.87°C', 'descoberta': '1766'},
                2: {'config': '1s²', 'estado': 'Gasoso', 'densidade': '0.1786 g/L', 'fusao': '-272.2°C', 'ebulicao': '-268.93°C', 'descoberta': '1868'},
                3: {'config': '[He] 2s¹', 'estado': 'Sólido', 'densidade': '0.534 g/cm³', 'fusao': '180.5°C', 'ebulicao': '1342°C', 'descoberta': '1817'},
                4: {'config': '[He] 2s²', 'estado': 'Sólido', 'densidade': '1.85 g/cm³', 'fusao': '1287°C', 'ebulicao': '2469°C', 'descoberta': '1797'},
                6: {'config': '1s² 2s² 2p²', 'estado': 'Sólido', 'densidade': '2.267 g/cm³', 'fusao': '3550°C', 'ebulicao': '4027°C', 'descoberta': 'Antiguidade'},
                8: {'config': '1s² 2s² 2p⁴', 'estado': 'Gasoso', 'densidade': '1.429 g/L', 'fusao': '-218.79°C', 'ebulicao': '-182.95°C', 'descoberta': '1774'},
                26: {'config': '[Ar] 4s² 3d⁶', 'estado': 'Sólido', 'densidade': '7.874 g/cm³', 'fusao': '1538°C', 'ebulicao': '2862°C', 'descoberta': 'Antiguidade'},
                29: {'config': '[Ar] 4s¹ 3d¹⁰', 'estado': 'Sólido', 'densidade': '8.96 g/cm³', 'fusao': '1084.62°C', 'ebulicao': '2562°C', 'descoberta': 'Antiguidade'},
                47: {'config': '[Kr] 5s¹ 4d¹⁰', 'estado': 'Sólido', 'densidade': '10.501 g/cm³', 'fusao': '961.78°C', 'ebulicao': '2162°C', 'descoberta': 'Antiguidade'},
                79: {'config': '[Xe] 6s¹ 4f¹⁴ 5d¹⁰', 'estado': 'Sólido', 'densidade': '19.32 g/cm³', 'fusao': '1064°C', 'ebulicao': '2856°C', 'descoberta': 'Antiguidade'}
            }
            
            details = f"""<b>Propriedades Físicas:</b><br>"""
            
            if atomic_num in extra_props:
                props = extra_props[atomic_num]
                details += f"<b>Configuração Eletrônica:</b> {props['config']}<br>"
                details += f"<b>Estado Físico:</b> {props['estado']}<br>"
                details += f"<b>Densidade:</b> {props['densidade']}<br>"
                details += f"<b>Ponto de Fusão:</b> {props['fusao']}<br>"
                details += f"<b>Ponto de Ebulição:</b> {props['ebulicao']}<br>"
                details += f"<b>Ano de Descoberta:</b> {props['descoberta']}<br><br>"
            
            # Aplicações
            applications = {
                1: "Combustível de foguetes, células de combustível, hidrogenação industrial",
                2: "Balões, refrigeração criogênica, atmosfera inerte para soldagem",
                3: "Baterias de íon-lítio, medicamentos psiquiátricos, ligas metálicas",
                6: "Compostos orgânicos, diamantes, grafite, nanotubos de carbono",
                8: "Respiração, combustão, produção de aço, medicina hiperbárica",
                26: "Construção civil, automóveis, ferramentas, eletroímãs",
                29: "Fios elétricos, encanamentos, moedas, ligas (bronze, latão)",
                47: "Joias, moedas, eletrônicos, fotografia, medicina",
                79: "Joias, reserva de valor, eletrônicos, odontologia"
            }
            
            details += "<b>Principais Aplicações:</b><br>"
            if atomic_num in applications:
                details += f"• {applications[atomic_num]}"
            else:
                details += "• Diversas aplicações industriais, científicas e tecnológicas"
            
            self.element_details.setHtml(details)
            
            # Destacar elemento e grupo/período
            sel_row, sel_col = element['position']
            for num, button in self.element_buttons.items():
                if num in elements:
                    row, col = elements[num]['position']
                    style = button.styleSheet()
                    # Remover destacamento anterior
                    style = style.replace("border: 3px solid #e74c3c;", "").replace("border: 2px solid #3498db;", "")
                    
                    if num == atomic_num:
                        # Destacar elemento selecionado
                        style += "\nQPushButton { border: 3px solid #e74c3c; }"
                    elif row == sel_row or col == sel_col:
                        # Destacar mesmo período ou grupo
                        style += "\nQPushButton { border: 2px solid #3498db; }"
                    
                    button.setStyleSheet(style)
