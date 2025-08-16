"""
Aba da Tabela Periódica Interativa - Estilo Google (Português Brasileiro)
Layout responsivo e fiel à referência visual
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QTextEdit, QGroupBox, QScrollArea, QFrame,
    QLineEdit, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, QSize
from math import sin, cos
from PySide6.QtGui import QFont, QPalette, QColor, QPainter, QBrush, QPen
from PySide6.QtCore import QPoint


class BohrWidget(QWidget):
    """Widget simples que desenha um modelo de Bohr estilizado"""
    def __init__(self, parent=None):
        super().__init__(parent)

    def set_atomic_number(self, z: int):
        """Define o número atômico a ser representado (apenas para desenho aproximado)."""
        try:
            self.atomic_num = int(z)
        except Exception:
            self.atomic_num = 0
        self.update()

    def _compute_shells(self, z: int):
        # Distribuição simples (aproximação): 2,8,18,18,32, etc — apenas para visual
        shells = []
        remaining = z
        pattern = [2, 8, 18, 18, 32, 32]
        for cap in pattern:
            if remaining <= 0:
                break
            take = min(cap, remaining)
            shells.append(take)
            remaining -= take
        return shells

    def paintEvent(self, event):
        # Reuse drawing but overlay electrons per shells if atomic_num set
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        center = QPoint(w // 2, h // 2)

        # Fundo
        painter.fillRect(0, 0, w, h, QBrush(QColor('#f5f7fb')))

        # Núcleo
        core_radius = min(w, h) // 12
        painter.setBrush(QBrush(QColor('#e84a5f')))
        painter.setPen(QPen(Qt.NoPen))
        painter.drawEllipse(center, core_radius, core_radius)

        # Orbitas
        painter.setPen(QPen(QColor('#7f8c8d'), 1))
        orbit_radii = []
        for i, r in enumerate(range(core_radius + 12, min(w, h) // 2 - 4, 18)):
            orbit_radii.append(r)
            painter.drawEllipse(center, r, r)

        # Desenhar elétrons segundo atomic_num
        z = getattr(self, 'atomic_num', 0)
        if z > 0:
            shells = self._compute_shells(z)
            for i, count in enumerate(shells):
                if i >= len(orbit_radii):
                    break
                r = orbit_radii[i]
                for e in range(count):
                    angle = 2 * 3.14159 * e / max(1, count)
                    ex = int(center.x() + r * 0.85 * cos(angle))
                    ey = int(center.y() + r * 0.5 * sin(angle))
                    painter.setBrush(QBrush(QColor('#2e86ab')))
                    painter.setPen(QPen(Qt.NoPen))
                    painter.drawEllipse(QPoint(ex, ey), 4, 4)



class PeriodicTableTab(QWidget):
    """Aba da Tabela Periódica Interativa - Estilo Google"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_element = None
        self.element_buttons = {}
        self.init_ui()

    def init_ui(self):
        """Inicializa a interface da tabela periódica seguindo padrão das outras abas"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Layout horizontal principal
        main_content = QHBoxLayout()
        main_content.setSpacing(15)
        
        # Painel esquerdo - Tabela Periódica
        table_group = self.create_periodic_table_section()
        main_content.addWidget(table_group, 3)
        
        # Painel direito - Informações do elemento
        info_widget = self.create_element_info_panel()
        main_content.addWidget(info_widget, 2)
        
        layout.addLayout(main_content)
        self.setLayout(layout)
    
    def create_periodic_table_section(self) -> QGroupBox:
        """Cria a seção da tabela periódica com QGroupBox seguindo padrão das outras abas"""
        group = QGroupBox("Tabela Periódica Interativa")
        group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Barra de busca
        search_layout = QHBoxLayout()
        search_label = QLabel("Buscar elemento:")
        search_label.setFont(QFont("Segoe UI", 10))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite símbolo, nome ou número atômico...")
        self.search_input.setFont(QFont("Segoe UI", 10))
        self.search_input.setMinimumHeight(30)
        self.search_input.textChanged.connect(self.search_elements)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Container da tabela com scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(400)
        
        # Widget da tabela
        table_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(1)  # Espaçamento mínimo para melhor aproveitamento
        self.grid_layout.setContentsMargins(5, 5, 5, 5)  # Margens reduzidas
        
        # Números dos grupos (1-18)
        for col in range(1, 19):
            group_label = QLabel(str(col))
            group_label.setAlignment(Qt.AlignCenter)
            group_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
            group_label.setStyleSheet("""
                QLabel {
                    color: #5f6368;
                    background: #f8f9fa;
                    border: 1px solid #dadce0;
                    border-radius: 3px;
                    padding: 2px;
                    margin: 1px;
                }
            """)
            group_label.setFixedSize(48, 22)  # Ajustado para o novo tamanho dos botões
            self.grid_layout.addWidget(group_label, 0, col)
        
        # Números dos períodos (1-7)
        for row in range(1, 8):
            period_label = QLabel(str(row))
            period_label.setAlignment(Qt.AlignCenter)
            period_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
            period_label.setStyleSheet("""
                QLabel {
                    color: #5f6368;
                    background: #f8f9fa;
                    border: 1px solid #dadce0;
                    border-radius: 3px;
                    padding: 2px;
                    margin: 1px;
                }
            """)
            period_label.setFixedSize(22, 48)  # Ajustado para o novo tamanho dos botões
            self.grid_layout.addWidget(period_label, row, 0)
        
        # Adicionar elementos
        self.add_all_elements_google_style()
        self.add_lanthanides_actinides()
        
        table_widget.setLayout(self.grid_layout)
        scroll_area.setWidget(table_widget)
        layout.addWidget(scroll_area)
        
        group.setLayout(layout)
        return group
    
    def add_all_elements_google_style(self):
        """Adiciona todos os elementos com estilo idêntico ao Google"""
        elements = self.get_complete_elements_data()
        
        self.element_buttons = {}
        
        for num, data in elements.items():
            if data['position'][0] <= 7:  # Elementos principais (não lantanídeos/actinídeos)
                button = self.create_element_button_google_style(num, data)
                self.element_buttons[num] = button
                row, col = data['position']
                self.grid_layout.addWidget(button, row, col)
    
    def add_lanthanides_actinides(self):
        """Adiciona lantanídeos e actinídeos em linhas separadas"""
        elements = self.get_complete_elements_data()
        
        # Espaçamento
        spacer = QLabel("")
        spacer.setFixedHeight(20)
        self.grid_layout.addWidget(spacer, 8, 1, 1, 18)
        
        # Lantanídeos (elementos 57-71)
        lanthanide_label = QLabel("Lantanídeos")
        lanthanide_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lanthanide_label.setStyleSheet("color: #1a73e8; padding: 5px;")
        self.grid_layout.addWidget(lanthanide_label, 9, 0)
        
        for num in range(57, 72):
            if num in elements:
                button = self.create_element_button_google_style(num, elements[num])
                self.element_buttons[num] = button
                col = num - 57 + 3  # Começar na coluna 3
                self.grid_layout.addWidget(button, 9, col)
        
        # Actinídeos (elementos 89-103)
        actinide_label = QLabel("Actinídeos")
        actinide_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        actinide_label.setStyleSheet("color: #1a73e8; padding: 5px;")
        self.grid_layout.addWidget(actinide_label, 10, 0)
        
        for num in range(89, 104):
            if num in elements:
                button = self.create_element_button_google_style(num, elements[num])
                self.element_buttons[num] = button
                col = num - 89 + 3  # Começar na coluna 3
                self.grid_layout.addWidget(button, 10, col)
    
    def create_element_button_google_style(self, atomic_num, data):
        """Cria botão do elemento seguindo o padrão da imagem de referência"""
        button = QPushButton()
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.setFixedSize(48, 48)  # Tamanho aumentado para melhor visualização
        
        # Texto do botão: número atômico e símbolo
        text = f"{atomic_num}\n{data['symbol']}"
        button.setText(text)
        button.setFont(QFont("Segoe UI", 8, QFont.Bold))
        
        # Cores seguindo a referência visual do Google
        colors = {
            'alkali_metal': '#ff9999',           # Rosa claro como na imagem
            'alkaline_earth': '#66ccff',         # Azul claro 
            'transition_metal': '#6699ff',       # Azul médio
            'post_transition': '#99cc99',        # Verde claro
            'metalloid': '#ffcc66',              # Amarelo
            'nonmetal': '#cc99ff',               # Roxo claro
            'halogen': '#ffcc99',                # Laranja claro
            'noble_gas': '#ff99cc',              # Rosa
            'lanthanide': '#cc99cc',             # Roxo médio
            'actinide': '#ffaa80',               # Laranja salmão
            'unknown': '#cccccc'                 # Cinza
        }
        
        color = colors.get(data['category'], '#f8f9fa')
        
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #333;
                border: 1px solid #999;
                border-radius: 6px;
                font-weight: bold;
                text-align: center;
                font-size: 10px;
                padding: 2px;
                margin: 1px;
            }}
            QPushButton:hover {{
                background-color: #ffffff;
                border: 2px solid #1a73e8;
                box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                transform: scale(1.02);
            }}
            QPushButton:pressed {{
                background-color: #e8f0fe;
                border: 2px solid #1967d2;
            }}
        """)
        
        # Tooltip em português
        tooltip = f"""
        <b>{data['name']}</b><br>
        Símbolo: {data['symbol']}<br>
        Número Atômico: {atomic_num}<br>
        Massa Atômica: {data['mass']} u<br>
        Categoria: {self.translate_category(data['category'])}
        """
        button.setToolTip(tooltip)
        
        # Conectar clique
        button.clicked.connect(lambda checked, num=atomic_num: self.on_element_clicked(num))
        
        return button
    
    def translate_category(self, category):
        """Traduz categorias para português brasileiro"""
        translations = {
            'alkali_metal': 'Metal Alcalino',
            'alkaline_earth': 'Metal Alcalino-terroso',
            'transition_metal': 'Metal de Transição',
            'post_transition': 'Metal Pós-transição',
            'metalloid': 'Metaloide',
            'nonmetal': 'Não Metal',
            'halogen': 'Halogênio',
            'noble_gas': 'Gás Nobre',
            'lanthanide': 'Lantanídeo',
            'actinide': 'Actinídeo',
            'unknown': 'Propriedades Desconhecidas'
        }
        return translations.get(category, category)
    
    def create_element_info_panel(self):
        """Cria painel de informações seguindo padrão das outras abas com QGroupBox"""
        group = QGroupBox("Informações Detalhadas do Elemento")
        group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Seção superior: Nome e dados básicos
        header_section = QGroupBox("Elemento Selecionado")
        header_layout = QVBoxLayout()
        
        self.element_name_label = QLabel("Clique em um elemento para ver suas informações")
        self.element_name_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.element_name_label.setStyleSheet("color: #1a73e8; padding: 5px;")
        self.element_name_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.element_name_label)
        
        # Layout horizontal: símbolo e modelo
        symbol_model_layout = QHBoxLayout()
        
        # Símbolo grande
        self.element_symbol_label = QLabel("")
        self.element_symbol_label.setFont(QFont("Segoe UI", 48, QFont.Bold))
        self.element_symbol_label.setStyleSheet("color: #34a853; border: 2px solid #dadce0; border-radius: 8px; padding: 10px; background: #f8f9fa;")
        self.element_symbol_label.setAlignment(Qt.AlignCenter)
        self.element_symbol_label.setFixedSize(120, 120)
        symbol_model_layout.addWidget(self.element_symbol_label)
        
        # Modelo de Bohr à direita
        self.bohr_widget = BohrWidget()
        self.bohr_widget.setFixedSize(120, 120)
        self.bohr_widget.setStyleSheet("border: 1px solid #dadce0; border-radius: 8px; background: white;")
        symbol_model_layout.addWidget(self.bohr_widget)
        
        symbol_model_layout.addStretch()
        header_layout.addLayout(symbol_model_layout)
        
        # Categoria com ponto colorido
        self.element_category_label = QLabel("")
        self.element_category_label.setFont(QFont("Segoe UI", 11))
        self.element_category_label.setStyleSheet("color: #5f6368; padding: 5px;")
        self.element_category_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.element_category_label)
        
        header_section.setLayout(header_layout)
        layout.addWidget(header_section)
        
        # Seção de propriedades
        props_section = QGroupBox("Propriedades Físicas e Químicas")
        props_layout = QVBoxLayout()
        
        self.props_label = QLabel("")
        self.props_label.setWordWrap(True)
        self.props_label.setFont(QFont("Segoe UI", 10))
        self.props_label.setStyleSheet("""
            QLabel {
                color: #3c4043; 
                background: #f8f9fa; 
                border: 1px solid #dadce0;
                border-radius: 6px;
                padding: 10px;
                line-height: 1.4;
            }
        """)
        self.props_label.setMinimumHeight(200)
        props_layout.addWidget(self.props_label)
        
        props_section.setLayout(props_layout)
        layout.addWidget(props_section)
        
        # Legenda de categorias
        self.create_category_legend(layout)
        
        layout.addStretch()
        group.setLayout(layout)
        return group
    
    def create_category_legend(self, layout):
        """Cria legenda de categorias seguindo padrão de outras abas"""
        legend_group = QGroupBox("Legenda das Categorias")
        legend_layout = QVBoxLayout()
        legend_layout.setSpacing(8)
        
        categories = [
            ("Metal Alcalino", "#ff6b6b"),
            ("Metal Alcalino-terroso", "#ffa726"),
            ("Metal de Transição", "#66bb6a"),
            ("Metal Pós-transição", "#42a5f5"),
            ("Semimetal", "#ab47bc"),
            ("Não-metal", "#26c6da"),
            ("Halogênio", "#ffee58"),
            ("Gás Nobre", "#bdbdbd"),
            ("Lantanídeo", "#a1c181"),
            ("Actinídeo", "#d4a574")
        ]
        
        # Criar grid de legendas
        grid_layout = QVBoxLayout()
        
        for i in range(0, len(categories), 2):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(20)
            
            # Primeira categoria da linha
            cat1 = categories[i]
            cat1_layout = QHBoxLayout()
            cat1_layout.setSpacing(8)
            
            color_square1 = QLabel()
            color_square1.setFixedSize(16, 16)
            color_square1.setStyleSheet(f"background-color: {cat1[1]}; border: 1px solid #dadce0; border-radius: 3px;")
            cat1_layout.addWidget(color_square1)
            
            cat1_label = QLabel(cat1[0])
            cat1_label.setFont(QFont("Segoe UI", 9))
            cat1_label.setStyleSheet("color: #5f6368;")
            cat1_layout.addWidget(cat1_label)
            cat1_layout.addStretch()
            
            row_layout.addLayout(cat1_layout)
            
            # Segunda categoria da linha (se existir)
            if i + 1 < len(categories):
                cat2 = categories[i + 1]
                cat2_layout = QHBoxLayout()
                cat2_layout.setSpacing(8)
                
                color_square2 = QLabel()
                color_square2.setFixedSize(16, 16)
                color_square2.setStyleSheet(f"background-color: {cat2[1]}; border: 1px solid #dadce0; border-radius: 3px;")
                cat2_layout.addWidget(color_square2)
                
                cat2_label = QLabel(cat2[0])
                cat2_label.setFont(QFont("Segoe UI", 9))
                cat2_label.setStyleSheet("color: #5f6368;")
                cat2_layout.addWidget(cat2_label)
                cat2_layout.addStretch()
                
                row_layout.addLayout(cat2_layout)
            else:
                row_layout.addStretch()
            
            grid_layout.addLayout(row_layout)
        
        legend_layout.addLayout(grid_layout)
        legend_group.setLayout(legend_layout)
        layout.addWidget(legend_group)
        layout.addWidget(legend_group)
    
    def search_elements(self, text):
        """Busca elementos por símbolo, nome ou número atômico"""
        if not text:
            # Mostrar todos os elementos
            for button in self.element_buttons.values():
                button.show()
            return
        
        text = text.lower().strip()
        elements = self.get_complete_elements_data()
        
        for num, button in self.element_buttons.items():
            element = elements[num]
            
            # Buscar por número, símbolo ou nome
            if (str(num) == text or 
                element['symbol'].lower() == text or 
                text in element['name'].lower()):
                button.show()
                button.setStyleSheet(button.styleSheet() + "\nQPushButton { border: 3px solid #ea4335; }")
            else:
                button.hide()
    
    def on_element_clicked(self, atomic_num):
        """Manipula clique no elemento"""
        elements = self.get_complete_elements_data()
        if atomic_num in elements:
            element = elements[atomic_num]
            self.selected_element = atomic_num
            # Atualizar informações
            self.element_name_label.setText(element['name'])

            # Categoria com ponto colorido
            color_map = {
                'alkali_metal': '#ff6b6b', 'alkaline_earth': '#4ecdc4', 'transition_metal': '#45b7d1',
                'post_transition': '#96ceb4', 'metalloid': '#ffeaa7', 'nonmetal': '#dda0dd',
                'halogen': '#ffb347', 'noble_gas': '#ff69b4', 'lanthanide': '#87ceeb', 'actinide': '#f0e68c'
            }
            cat = element.get('category', 'unknown')
            dot = f"<span style='color:{color_map.get(cat, '#666')}; font-size:18px;'>●</span>"
            self.element_category_label.setText(f"{dot} {self.translate_category(cat)}")

            # Propriedades detalhadas mostradas na coluna direita
            details = f"""
<b>Propriedades Básicas:</b><br>
Número Atômico: {atomic_num}<br>
Símbolo: {element['symbol']}<br>
Massa Atômica: {element['mass']} u<br>
Categoria: {self.translate_category(cat)}<br><br>
<b>Posição na Tabela:</b><br>
Período: {element['position'][0]} — Grupo: {element['position'][1]}<br><br>
<b>Propriedades Físicas:</b><br>
Estado: {element.get('state', 'N/A')}<br>
Densidade: {element.get('density', 'N/A')} g/cm³<br>
Ponto de Fusão: {element.get('melting_point', 'N/A')}°C — Ebulição: {element.get('boiling_point', 'N/A')}°C<br><br>
<b>Configuração Eletrônica:</b> {element.get('electron_config', 'N/A')}<br><br>
<b>Aplicações Principais:</b><br>
{element.get('applications', 'Diversas aplicações')}
"""

            self.props_label.setText(details)

            # Atualizar BohrWidget
            try:
                self.bohr_widget.set_atomic_number(int(atomic_num))
            except Exception:
                self.bohr_widget.set_atomic_number(0)

            # Destacar elemento selecionado
            self.highlight_selected_element(atomic_num)
    
    def highlight_selected_element(self, selected_num):
        """Destaca o elemento selecionado"""
        for num, button in self.element_buttons.items():
            if num == selected_num:
                # Destacar elemento selecionado
                current_style = button.styleSheet()
                if "border: 3px solid #ea4335" not in current_style:
                    button.setStyleSheet(current_style + "\nQPushButton { border: 3px solid #ea4335 !important; }")
            else:
                # Remover destaque dos outros
                style = button.styleSheet().replace("border: 3px solid #ea4335 !important;", "")
                style = style.replace("border: 3px solid #ea4335;", "")
                button.setStyleSheet(style)
    
    def get_complete_elements_data(self):
        """Retorna dados completos de todos os 118 elementos em português"""
        elements_data = [
            # Período 1
            (1, 'H', 'Hidrogênio', 1.008, 'nonmetal', 1, 1, 'Gás', 0.0899, -259, -253, 1766, '1s¹', 'Combustível, síntese química, hidrogenação'),
            (2, 'He', 'Hélio', 4.003, 'noble_gas', 1, 18, 'Gás', 0.1786, -272, -269, 1895, '1s²', 'Balões, criogenia, soldagem'),
            
            # Período 2
            (3, 'Li', 'Lítio', 6.941, 'alkali_metal', 2, 1, 'Sólido', 0.534, 181, 1342, 1817, '[He] 2s¹', 'Baterias, medicamentos, ligas'),
            (4, 'Be', 'Berílio', 9.012, 'alkaline_earth', 2, 2, 'Sólido', 1.85, 1287, 2470, 1798, '[He] 2s²', 'Ligas aeroespaciais, reatores nucleares'),
            (5, 'B', 'Boro', 10.811, 'metalloid', 2, 13, 'Sólido', 2.34, 2077, 4000, 1808, '[He] 2s² 2p¹', 'Vidros, cerâmicas, detergentes'),
            (6, 'C', 'Carbono', 12.011, 'nonmetal', 2, 14, 'Sólido', 2.267, 3550, 4027, 'Pré-história', '[He] 2s² 2p²', 'Compostos orgânicos, aço, diamante'),
            (7, 'N', 'Nitrogênio', 14.007, 'nonmetal', 2, 15, 'Gás', 1.251, -210, -196, 1772, '[He] 2s² 2p³', 'Fertilizantes, explosivos, atmosfera inerte'),
            (8, 'O', 'Oxigênio', 15.999, 'nonmetal', 2, 16, 'Gás', 1.429, -219, -183, 1774, '[He] 2s² 2p⁴', 'Respiração, combustão, oxidação'),
            (9, 'F', 'Flúor', 18.998, 'halogen', 2, 17, 'Gás', 1.696, -220, -188, 1886, '[He] 2s² 2p⁵', 'Pasta de dente, teflon, refrigerantes'),
            (10, 'Ne', 'Neônio', 20.180, 'noble_gas', 2, 18, 'Gás', 0.900, -249, -246, 1898, '[He] 2s² 2p⁶', 'Letreiros luminosos, lasers'),
            
            # Período 3
            (11, 'Na', 'Sódio', 22.990, 'alkali_metal', 3, 1, 'Sólido', 0.971, 98, 883, 1807, '[Ne] 3s¹', 'Sal de cozinha, sabão, iluminação'),
            (12, 'Mg', 'Magnésio', 24.305, 'alkaline_earth', 3, 2, 'Sólido', 1.738, 650, 1090, 1755, '[Ne] 3s²', 'Ligas leves, fogos de artifício'),
            (13, 'Al', 'Alumínio', 26.982, 'post_transition', 3, 13, 'Sólido', 2.698, 660, 2519, 1825, '[Ne] 3s² 3p¹', 'Embalagens, aviação, construção'),
            (14, 'Si', 'Silício', 28.086, 'metalloid', 3, 14, 'Sólido', 2.329, 1414, 3265, 1824, '[Ne] 3s² 3p²', 'Chips, vidro, energia solar'),
            (15, 'P', 'Fósforo', 30.974, 'nonmetal', 3, 15, 'Sólido', 1.823, 44, 281, 1669, '[Ne] 3s² 3p³', 'Fertilizantes, fósforos, DNA'),
            (16, 'S', 'Enxofre', 32.065, 'nonmetal', 3, 16, 'Sólido', 2.067, 115, 445, 'Pré-história', '[Ne] 3s² 3p⁴', 'Ácido sulfúrico, vulcanização'),
            (17, 'Cl', 'Cloro', 35.453, 'halogen', 3, 17, 'Gás', 3.214, -102, -34, 1774, '[Ne] 3s² 3p⁵', 'Desinfetante, PVC, papel'),
            (18, 'Ar', 'Argônio', 39.948, 'noble_gas', 3, 18, 'Gás', 1.784, -189, -186, 1894, '[Ne] 3s² 3p⁶', 'Soldagem, lâmpadas, atmosfera inerte'),
            
            # Período 4
            (19, 'K', 'Potássio', 39.098, 'alkali_metal', 4, 1, 'Sólido', 0.862, 64, 759, 1807, '[Ar] 4s¹', 'Fertilizantes, sabão, vidro'),
            (20, 'Ca', 'Cálcio', 40.078, 'alkaline_earth', 4, 2, 'Sólido', 1.54, 842, 1484, 1808, '[Ar] 4s²', 'Cimento, ossos, leite'),
            (21, 'Sc', 'Escândio', 44.956, 'transition_metal', 4, 3, 'Sólido', 2.989, 1541, 2836, 1879, '[Ar] 3d¹ 4s²', 'Ligas de alumínio, lâmpadas'),
            (22, 'Ti', 'Titânio', 47.867, 'transition_metal', 4, 4, 'Sólido', 4.506, 1668, 3287, 1791, '[Ar] 3d² 4s²', 'Aviação, implantes, tinta'),
            (23, 'V', 'Vanádio', 50.942, 'transition_metal', 4, 5, 'Sólido', 6.11, 1910, 3407, 1801, '[Ar] 3d³ 4s²', 'Aço, catalisadores'),
            (24, 'Cr', 'Cromo', 51.996, 'transition_metal', 4, 6, 'Sólido', 7.15, 1907, 2671, 1797, '[Ar] 3d⁵ 4s¹', 'Aço inoxidável, cromagem'),
            (25, 'Mn', 'Manganês', 54.938, 'transition_metal', 4, 7, 'Sólido', 7.44, 1246, 2061, 1774, '[Ar] 3d⁵ 4s²', 'Aço, baterias, fertilizantes'),
            (26, 'Fe', 'Ferro', 55.845, 'transition_metal', 4, 8, 'Sólido', 7.874, 1538, 2862, 'Pré-história', '[Ar] 3d⁶ 4s²', 'Aço, construção, transporte'),
            (27, 'Co', 'Cobalto', 58.933, 'transition_metal', 4, 9, 'Sólido', 8.86, 1495, 2927, 1735, '[Ar] 3d⁷ 4s²', 'Baterias, ímãs, ligas'),
            (28, 'Ni', 'Níquel', 58.693, 'transition_metal', 4, 10, 'Sólido', 8.912, 1455, 2913, 1751, '[Ar] 3d⁸ 4s²', 'Moedas, aço inoxidável, baterias'),
            (29, 'Cu', 'Cobre', 63.546, 'transition_metal', 4, 11, 'Sólido', 8.96, 1085, 2562, 'Pré-história', '[Ar] 3d¹⁰ 4s¹', 'Fios elétricos, encanamento, moedas'),
            (30, 'Zn', 'Zinco', 65.38, 'transition_metal', 4, 12, 'Sólido', 7.134, 420, 907, 1746, '[Ar] 3d¹⁰ 4s²', 'Galvanização, baterias, ligas'),
            (31, 'Ga', 'Gálio', 69.723, 'post_transition', 4, 13, 'Sólido', 5.907, 30, 2204, 1875, '[Ar] 3d¹⁰ 4s² 4p¹', 'Eletrônicos, LEDs, semicondutores'),
            (32, 'Ge', 'Germânio', 72.64, 'metalloid', 4, 14, 'Sólido', 5.323, 938, 2833, 1886, '[Ar] 3d¹⁰ 4s² 4p²', 'Semicondutores, fibra óptica'),
            (33, 'As', 'Arsênio', 74.922, 'metalloid', 4, 15, 'Sólido', 5.776, 817, 614, 1250, '[Ar] 3d¹⁰ 4s² 4p³', 'Pesticidas, semicondutores'),
            (34, 'Se', 'Selênio', 78.96, 'nonmetal', 4, 16, 'Sólido', 4.809, 221, 685, 1817, '[Ar] 3d¹⁰ 4s² 4p⁴', 'Fotocópias, vidro, suplementos'),
            (35, 'Br', 'Bromo', 79.904, 'halogen', 4, 17, 'Líquido', 3.122, -7, 59, 1826, '[Ar] 3d¹⁰ 4s² 4p⁵', 'Retardantes de chama, medicamentos'),
            (36, 'Kr', 'Criptônio', 83.798, 'noble_gas', 4, 18, 'Gás', 3.733, -157, -153, 1898, '[Ar] 3d¹⁰ 4s² 4p⁶', 'Lâmpadas, lasers, isolamento'),
            
            # Período 5 (completo)
            (37, 'Rb', 'Rubídio', 85.468, 'alkali_metal', 5, 1, 'Sólido', 1.532, 39, 688, 1861, '[Kr] 5s¹', 'Pesquisa, células fotoelétricas'),
            (38, 'Sr', 'Estrôncio', 87.62, 'alkaline_earth', 5, 2, 'Sólido', 2.64, 777, 1377, 1790, '[Kr] 5s²', 'Fogos de artifício, ímãs'),
            (39, 'Y', 'Ítrio', 88.906, 'transition_metal', 5, 3, 'Sólido', 4.469, 1526, 3345, 1794, '[Kr] 4d¹ 5s²', 'Fósforos, lasers, supercondutores'),
            (40, 'Zr', 'Zircônio', 91.224, 'transition_metal', 5, 4, 'Sólido', 6.506, 1855, 4409, 1789, '[Kr] 4d² 5s²', 'Reatores nucleares, cerâmicas'),
            (41, 'Nb', 'Nióbio', 92.906, 'transition_metal', 5, 5, 'Sólido', 8.57, 2477, 4744, 1801, '[Kr] 4d⁴ 5s¹', 'Ligas de aço, supercondutores'),
            (42, 'Mo', 'Molibdênio', 95.94, 'transition_metal', 5, 6, 'Sólido', 10.22, 2623, 4639, 1778, '[Kr] 4d⁵ 5s¹', 'Ligas de aço, catalisadores'),
            (43, 'Tc', 'Tecnécio', 98, 'transition_metal', 5, 7, 'Sólido', 11.5, 2157, 4265, 1937, '[Kr] 4d⁵ 5s²', 'Medicina nuclear, pesquisa'),
            (44, 'Ru', 'Rutênio', 101.07, 'transition_metal', 5, 8, 'Sólido', 12.37, 2334, 4150, 1827, '[Kr] 4d⁷ 5s¹', 'Eletrônicos, catalisadores'),
            (45, 'Rh', 'Ródio', 102.906, 'transition_metal', 5, 9, 'Sólido', 12.41, 1964, 3695, 1803, '[Kr] 4d⁸ 5s¹', 'Catalisadores, joias'),
            (46, 'Pd', 'Paládio', 106.42, 'transition_metal', 5, 10, 'Sólido', 12.02, 1555, 2963, 1803, '[Kr] 4d¹⁰', 'Catalisadores, joias, odontologia'),
            (47, 'Ag', 'Prata', 107.868, 'transition_metal', 5, 11, 'Sólido', 10.501, 962, 2162, 'Pré-história', '[Kr] 4d¹⁰ 5s¹', 'Joias, eletrônicos, fotografia'),
            (48, 'Cd', 'Cádmio', 112.411, 'transition_metal', 5, 12, 'Sólido', 8.69, 321, 767, 1817, '[Kr] 4d¹⁰ 5s²', 'Baterias, pigmentos, revestimentos'),
            (49, 'In', 'Índio', 114.818, 'post_transition', 5, 13, 'Sólido', 7.31, 157, 2072, 1863, '[Kr] 4d¹⁰ 5s² 5p¹', 'Semicondutores, telas LCD'),
            (50, 'Sn', 'Estanho', 118.710, 'post_transition', 5, 14, 'Sólido', 7.287, 232, 2602, 'Pré-história', '[Kr] 4d¹⁰ 5s² 5p²', 'Soldas, latas, ligas'),
            (51, 'Sb', 'Antimônio', 121.760, 'metalloid', 5, 15, 'Sólido', 6.685, 631, 1587, 'Pré-história', '[Kr] 4d¹⁰ 5s² 5p³', 'Retardantes de chama, baterias'),
            (52, 'Te', 'Telúrio', 127.60, 'metalloid', 5, 16, 'Sólido', 6.232, 450, 988, 1783, '[Kr] 4d¹⁰ 5s² 5p⁴', 'Eletrônicos, ligas, vidros'),
            (53, 'I', 'Iodo', 126.904, 'halogen', 5, 17, 'Sólido', 4.93, 114, 184, 1811, '[Kr] 4d¹⁰ 5s² 5p⁵', 'Desinfetante, medicina, sal'),
            (54, 'Xe', 'Xenônio', 131.293, 'noble_gas', 5, 18, 'Gás', 5.887, -112, -108, 1898, '[Kr] 4d¹⁰ 5s² 5p⁶', 'Lâmpadas, anestesia, propulsão'),
            
            # Período 6 (completo)
            (55, 'Cs', 'Césio', 132.905, 'alkali_metal', 6, 1, 'Sólido', 1.873, 28, 671, 1860, '[Xe] 6s¹', 'Relógios atômicos, catalisadores'),
            (56, 'Ba', 'Bário', 137.327, 'alkaline_earth', 6, 2, 'Sólido', 3.594, 727, 1870, 1808, '[Xe] 6s²', 'Raio-X, fogos de artifício'),
            (72, 'Hf', 'Háfnio', 178.49, 'transition_metal', 6, 4, 'Sólido', 13.31, 2233, 4603, 1923, '[Xe] 4f¹⁴ 5d² 6s²', 'Reatores nucleares, ligas'),
            (73, 'Ta', 'Tântalo', 180.948, 'transition_metal', 6, 5, 'Sólido', 16.654, 3017, 5458, 1802, '[Xe] 4f¹⁴ 5d³ 6s²', 'Eletrônicos, implantes médicos'),
            (74, 'W', 'Tungstênio', 183.84, 'transition_metal', 6, 6, 'Sólido', 19.25, 3422, 5555, 1783, '[Xe] 4f¹⁴ 5d⁴ 6s²', 'Filamentos, ligas de alta temperatura'),
            (75, 'Re', 'Rênio', 186.207, 'transition_metal', 6, 7, 'Sólido', 21.02, 3186, 5596, 1925, '[Xe] 4f¹⁴ 5d⁵ 6s²', 'Catalisadores, ligas superresistentes'),
            (76, 'Os', 'Ósmio', 190.23, 'transition_metal', 6, 8, 'Sólido', 22.59, 3033, 5012, 1803, '[Xe] 4f¹⁴ 5d⁶ 6s²', 'Ligas duras, pontas de caneta'),
            (77, 'Ir', 'Irídio', 192.217, 'transition_metal', 6, 9, 'Sólido', 22.56, 2466, 4428, 1803, '[Xe] 4f¹⁴ 5d⁷ 6s²', 'Eletrodos, ligas anticorrosão'),
            (78, 'Pt', 'Platina', 195.084, 'transition_metal', 6, 10, 'Sólido', 21.46, 1768, 3825, 1735, '[Xe] 4f¹⁴ 5d⁹ 6s¹', 'Joias, catalisadores, medicina'),
            (79, 'Au', 'Ouro', 196.967, 'transition_metal', 6, 11, 'Sólido', 19.282, 1064, 2856, 'Pré-história', '[Xe] 4f¹⁴ 5d¹⁰ 6s¹', 'Joias, eletrônicos, reserva de valor'),
            (80, 'Hg', 'Mercúrio', 200.592, 'transition_metal', 6, 12, 'Líquido', 13.533, -39, 357, 'Pré-história', '[Xe] 4f¹⁴ 5d¹⁰ 6s²', 'Termômetros, lâmpadas, amalgamas'),
            (81, 'Tl', 'Tálio', 204.383, 'post_transition', 6, 13, 'Sólido', 11.85, 304, 1473, 1861, '[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p¹', 'Eletrônicos, vidros especiais'),
            (82, 'Pb', 'Chumbo', 207.2, 'post_transition', 6, 14, 'Sólido', 11.342, 327, 1749, 'Pré-história', '[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p²', 'Baterias, soldagem, proteção radiológica'),
            (83, 'Bi', 'Bismuto', 208.980, 'post_transition', 6, 15, 'Sólido', 9.807, 271, 1564, 1753, '[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p³', 'Medicamentos, cosméticos, ligas'),
            (84, 'Po', 'Polônio', 209, 'post_transition', 6, 16, 'Sólido', 9.32, 254, 962, 1898, '[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁴', 'Pesquisa nuclear, eliminação estática'),
            (85, 'At', 'Astato', 210, 'halogen', 6, 17, 'Sólido', 7, 302, 337, 1940, '[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁵', 'Pesquisa nuclear, medicina'),
            (86, 'Rn', 'Radônio', 222, 'noble_gas', 6, 18, 'Gás', 9.73, -71, -62, 1900, '[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁶', 'Pesquisa médica, detectores'),
            
            # Período 7 (completo)
            (87, 'Fr', 'Frâncio', 223, 'alkali_metal', 7, 1, 'Sólido', 1.87, 27, 677, 1939, '[Rn] 7s¹', 'Pesquisa científica'),
            (88, 'Ra', 'Rádio', 226, 'alkaline_earth', 7, 2, 'Sólido', 5.5, 700, 1737, 1898, '[Rn] 7s²', 'Pesquisa médica, tratamento de câncer'),
            (104, 'Rf', 'Rutherfórdio', 267, 'transition_metal', 7, 4, 'Sólido', 23, 2100, 5500, 1964, '[Rn] 5f¹⁴ 6d² 7s²', 'Pesquisa científica'),
            (105, 'Db', 'Dúbnio', 268, 'transition_metal', 7, 5, 'Sólido', 29, 2900, 6000, 1967, '[Rn] 5f¹⁴ 6d³ 7s²', 'Pesquisa científica'),
            (106, 'Sg', 'Seabórgio', 271, 'transition_metal', 7, 6, 'Sólido', 35, 3200, 6500, 1974, '[Rn] 5f¹⁴ 6d⁴ 7s²', 'Pesquisa científica'),
            (107, 'Bh', 'Bóhrio', 272, 'transition_metal', 7, 7, 'Sólido', 37, 3500, 7000, 1981, '[Rn] 5f¹⁴ 6d⁵ 7s²', 'Pesquisa científica'),
            (108, 'Hs', 'Hássio', 270, 'transition_metal', 7, 8, 'Sólido', 41, 3800, 7500, 1984, '[Rn] 5f¹⁴ 6d⁶ 7s²', 'Pesquisa científica'),
            (109, 'Mt', 'Meitnério', 276, 'transition_metal', 7, 9, 'Sólido', 35, 4100, 8000, 1982, '[Rn] 5f¹⁴ 6d⁷ 7s²', 'Pesquisa científica'),
            (110, 'Ds', 'Darmstácio', 281, 'transition_metal', 7, 10, 'Sólido', 34, 4400, 8500, 1994, '[Rn] 5f¹⁴ 6d⁸ 7s²', 'Pesquisa científica'),
            (111, 'Rg', 'Roentgênio', 280, 'transition_metal', 7, 11, 'Sólido', 28, 4700, 9000, 1994, '[Rn] 5f¹⁴ 6d⁹ 7s²', 'Pesquisa científica'),
            (112, 'Cn', 'Copernício', 285, 'transition_metal', 7, 12, 'Sólido', 23, 5000, 9500, 1996, '[Rn] 5f¹⁴ 6d¹⁰ 7s²', 'Pesquisa científica'),
            (113, 'Nh', 'Nihônio', 284, 'post_transition', 7, 13, 'Sólido', 16, 4300, 8800, 2004, '[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p¹', 'Pesquisa científica'),
            (114, 'Fl', 'Fleróvio', 289, 'post_transition', 7, 14, 'Sólido', 14, 3400, 6800, 1998, '[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p²', 'Pesquisa científica'),
            (115, 'Mc', 'Moscóvio', 288, 'post_transition', 7, 15, 'Sólido', 13, 3200, 6400, 2003, '[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p³', 'Pesquisa científica'),
            (116, 'Lv', 'Livermório', 293, 'post_transition', 7, 16, 'Sólido', 12, 3000, 6000, 2000, '[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p⁴', 'Pesquisa científica'),
            (117, 'Ts', 'Tenesso', 294, 'halogen', 7, 17, 'Sólido', 7, 2800, 5600, 2010, '[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p⁵', 'Pesquisa científica'),
            (118, 'Og', 'Oganessônio', 294, 'noble_gas', 7, 18, 'Sólido', 5, 2700, 5400, 2002, '[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p⁶', 'Pesquisa científica'),
            
            # Lantanídeos (elementos 57-71)
            (57, 'La', 'Lantânio', 138.91, 'lanthanide', 8, 4, 'Sólido', 6.145, 920, 3464, 1839, '[Xe] 5d¹ 6s²', 'Catalisadores, óptica, baterias'),
            (58, 'Ce', 'Cério', 140.12, 'lanthanide', 8, 5, 'Sólido', 6.77, 798, 3443, 1803, '[Xe] 4f¹ 5d¹ 6s²', 'Catalisadores, polimento, ligas'),
            (59, 'Pr', 'Praseodímio', 140.91, 'lanthanide', 8, 6, 'Sólido', 6.773, 931, 3520, 1885, '[Xe] 4f³ 6s²', 'Ímãs, ligas, vidros'),
            (60, 'Nd', 'Neodímio', 144.24, 'lanthanide', 8, 7, 'Sólido', 7.008, 1021, 3074, 1885, '[Xe] 4f⁴ 6s²', 'Ímãs permanentes, lasers'),
            (61, 'Pm', 'Promécio', 145, 'lanthanide', 8, 8, 'Sólido', 7.26, 1042, 3000, 1945, '[Xe] 4f⁵ 6s²', 'Pesquisa, baterias nucleares'),
            (62, 'Sm', 'Samário', 150.36, 'lanthanide', 8, 9, 'Sólido', 7.52, 1072, 1794, 1879, '[Xe] 4f⁶ 6s²', 'Ímãs, reatores nucleares'),
            (63, 'Eu', 'Európio', 151.96, 'lanthanide', 8, 10, 'Sólido', 5.243, 822, 1529, 1901, '[Xe] 4f⁷ 6s²', 'Fósforos, lasers, euros'),
            (64, 'Gd', 'Gadolínio', 157.25, 'lanthanide', 8, 11, 'Sólido', 7.895, 1313, 3273, 1880, '[Xe] 4f⁷ 5d¹ 6s²', 'MRI, reatores nucleares'),
            (65, 'Tb', 'Térbio', 158.93, 'lanthanide', 8, 12, 'Sólido', 8.229, 1356, 3230, 1843, '[Xe] 4f⁹ 6s²', 'Fósforos, ímãs, eletrônicos'),
            (66, 'Dy', 'Disprósio', 162.50, 'lanthanide', 8, 13, 'Sólido', 8.55, 1412, 2567, 1886, '[Xe] 4f¹⁰ 6s²', 'Ímãs, reatores nucleares'),
            (67, 'Ho', 'Hólmio', 164.93, 'lanthanide', 8, 14, 'Sólido', 8.795, 1474, 2700, 1878, '[Xe] 4f¹¹ 6s²', 'Ímãs, lasers, reatores'),
            (68, 'Er', 'Érbio', 167.26, 'lanthanide', 8, 15, 'Sólido', 9.066, 1529, 2868, 1843, '[Xe] 4f¹² 6s²', 'Fibra óptica, lasers'),
            (69, 'Tm', 'Túlio', 168.93, 'lanthanide', 8, 16, 'Sólido', 9.321, 1545, 1950, 1879, '[Xe] 4f¹³ 6s²', 'Raio-X portátil, pesquisa'),
            (70, 'Yb', 'Itérbio', 173.05, 'lanthanide', 8, 17, 'Sólido', 6.965, 824, 1196, 1878, '[Xe] 4f¹⁴ 6s²', 'Ligas, lasers, pesquisa'),
            (71, 'Lu', 'Lutécio', 174.97, 'lanthanide', 8, 18, 'Sólido', 9.84, 1663, 3402, 1907, '[Xe] 4f¹⁴ 5d¹ 6s²', 'Catalisadores, pesquisa médica'),
            
            # Actinídeos (elementos 89-103) - completos
            (89, 'Ac', 'Actínio', 227, 'actinide', 9, 4, 'Sólido', 10.07, 1051, 3198, 1899, '[Rn] 6d¹ 7s²', 'Pesquisa, fonte de nêutrons'),
            (90, 'Th', 'Tório', 232.04, 'actinide', 9, 5, 'Sólido', 11.72, 1750, 4788, 1828, '[Rn] 6d² 7s²', 'Combustível nuclear, ligas'),
            (91, 'Pa', 'Protactínio', 231.04, 'actinide', 9, 6, 'Sólido', 15.37, 1572, 4000, 1913, '[Rn] 5f² 6d¹ 7s²', 'Pesquisa nuclear'),
            (92, 'U', 'Urânio', 238.03, 'actinide', 9, 7, 'Sólido', 18.95, 1135, 4131, 1789, '[Rn] 5f³ 6d¹ 7s²', 'Energia nuclear, armas, datação'),
            (93, 'Np', 'Neptúnio', 237, 'actinide', 9, 8, 'Sólido', 20.45, 644, 4000, 1940, '[Rn] 5f⁴ 6d¹ 7s²', 'Pesquisa nuclear, plutônio'),
            (94, 'Pu', 'Plutônio', 244, 'actinide', 9, 9, 'Sólido', 19.84, 640, 3228, 1940, '[Rn] 5f⁶ 7s²', 'Armas nucleares, energia'),
            (95, 'Am', 'Amerício', 243, 'actinide', 9, 10, 'Sólido', 13.69, 1176, 2607, 1944, '[Rn] 5f⁷ 7s²', 'Detectores de fumaça, pesquisa'),
            (96, 'Cm', 'Cúrio', 247, 'actinide', 9, 11, 'Sólido', 13.51, 1345, 3110, 1944, '[Rn] 5f⁷ 6d¹ 7s²', 'Pesquisa nuclear, fontes de energia'),
            (97, 'Bk', 'Berquélio', 247, 'actinide', 9, 12, 'Sólido', 14.79, 1050, 2627, 1949, '[Rn] 5f⁹ 7s²', 'Pesquisa científica'),
            (98, 'Cf', 'Califórnio', 251, 'actinide', 9, 13, 'Sólido', 15.1, 900, 1743, 1950, '[Rn] 5f¹⁰ 7s²', 'Fonte de nêutrons, pesquisa'),
            (99, 'Es', 'Einstênio', 252, 'actinide', 9, 14, 'Sólido', 13.5, 860, 1130, 1952, '[Rn] 5f¹¹ 7s²', 'Pesquisa científica'),
            (100, 'Fm', 'Férmio', 257, 'actinide', 9, 15, 'Sólido', 9.7, 1527, 2000, 1952, '[Rn] 5f¹² 7s²', 'Pesquisa científica'),
            (101, 'Md', 'Mendelévio', 258, 'actinide', 9, 16, 'Sólido', 10.3, 827, 1100, 1955, '[Rn] 5f¹³ 7s²', 'Pesquisa científica'),
            (102, 'No', 'Nobélio', 259, 'actinide', 9, 17, 'Sólido', 9.9, 827, 1100, 1957, '[Rn] 5f¹⁴ 7s²', 'Pesquisa científica'),
            (103, 'Lr', 'Laurêncio', 262, 'actinide', 9, 18, 'Sólido', 15.6, 1627, 2000, 1961, '[Rn] 5f¹⁴ 7s² 7p¹', 'Pesquisa científica'),
        ]
        
        elements = {}
        for data in elements_data:
            num, symbol, name, mass, category, row, col = data[:7]
            state, density, melting, boiling, discovery, config, applications = data[7:] if len(data) > 7 else ('N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'Pesquisa científica')
            
            elements[num] = {
                'symbol': symbol,
                'name': name,
                'mass': mass,
                'category': category,
                'position': (row, col),
                'state': state,
                'density': density,
                'melting_point': melting,
                'boiling_point': boiling,
                'discovery_year': discovery,
                'electron_config': config,
                'applications': applications
            }
        
        return elements

    def resizeEvent(self, event):
        """Ajusta elementos quando a janela é redimensionada"""
        super().resizeEvent(event)
        
        # Calcular novo tamanho dos botões baseado no tamanho da janela
        if hasattr(self, 'element_buttons'):
            window_width = self.width()
            window_height = self.height()
            
            # Tamanho adaptativo dos botões (entre 30 e 60 pixels)
            button_size = max(30, min(60, int(window_width / 25)))
            
            for button in self.element_buttons.values():
                button.setFixedSize(button_size, button_size)
                # Ajustar tamanho da fonte também
                font_size = max(6, min(10, int(button_size / 6)))
                font = button.font()
                font.setPointSize(font_size)
                button.setFont(font)
