"""
Aba da Tabela Periódica Interativa
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QTextEdit, QGroupBox, QScrollArea, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor


class PeriodicTableTab(QWidget):
    """Aba da Tabela Periódica Interativa"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_element = None
        self.init_ui()
        
    def init_ui(self):
        """Inicializa a interface da tabela periódica"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Título
        title = QLabel("Tabela Periódica Interativa")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        main_layout.addWidget(title)
        
        # Layout principal horizontal
        content_layout = QHBoxLayout()
        
        # Painel esquerdo - Tabela Periódica
        table_widget = self.create_periodic_table()
        content_layout.addWidget(table_widget, 3)
        
        # Painel direito - Informações do elemento
        info_widget = self.create_element_info_panel()
        content_layout.addWidget(info_widget, 1)
        
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)
    
    def create_periodic_table(self) -> QWidget:
        """Cria a tabela periódica"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        table_widget = QWidget()
        self.table_layout = QGridLayout()
        self.table_layout.setSpacing(2)
        
        # Dados dos elementos (símbolo, nome, número atômico, massa atômica, categoria)
        self.elements_data = self.get_elements_data()
        
        # Cria os botões dos elementos
        self.element_buttons = {}
        
        for element in self.elements_data:
            button = self.create_element_button(element)
            self.element_buttons[element['symbol']] = button
            row, col = element['position']
            self.table_layout.addWidget(button, row, col)
        
        # Adiciona legendas dos grupos
        self.add_group_labels()
        
        table_widget.setLayout(self.table_layout)
        scroll_area.setWidget(table_widget)
        
        return scroll_area
    
    def create_element_button(self, element_data: dict) -> QPushButton:
        """Cria um botão para um elemento"""
        button = QPushButton()
        button.setMinimumSize(60, 60)
        button.setMaximumSize(60, 60)
        
        # Texto do botão: símbolo e número atômico
        text = f"{element_data['atomic_number']}\n{element_data['symbol']}\n{element_data['name'][:4]}"
        button.setText(text)
        button.setFont(QFont("Arial", 8))
        
        # Cor baseada na categoria
        self.set_element_color(button, element_data['category'])
        
        # Conecta o clique
        button.clicked.connect(lambda checked, elem=element_data: self.on_element_clicked(elem))
        
        return button
    
    def set_element_color(self, button: QPushButton, category: str):
        """Define a cor do elemento baseada na categoria"""
        colors = {
            'reactive_nonmetal': '#3498db',      # Azul
            'noble_gas': '#e74c3c',              # Vermelho
            'alkali_metal': '#f39c12',           # Laranja
            'alkaline_earth_metal': '#f1c40f',   # Amarelo
            'transition_metal': '#9b59b6',       # Roxo
            'post_transition_metal': '#2ecc71',  # Verde
            'metalloid': '#34495e',              # Cinza escuro
            'halogen': '#e67e22',                # Laranja escuro
            'lanthanide': '#1abc9c',             # Turquesa
            'actinide': '#95a5a6'                # Cinza
        }
        
        color = colors.get(category, '#bdc3c7')  # Cinza claro como padrão
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: 1px solid #34495e;
                border-radius: 3px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2c3e50;
                border: 2px solid #e74c3c;
            }}
            QPushButton:pressed {{
                background-color: #1a252f;
            }}
        """)
    
    def add_group_labels(self):
        """Adiciona rótulos dos grupos"""
        # Números dos grupos (1-18)
        for i in range(1, 19):
            label = QLabel(str(i))
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont("Arial", 10, QFont.Bold))
            label.setStyleSheet("color: #2c3e50; background-color: #ecf0f1; padding: 5px;")
            self.table_layout.addWidget(label, 0, i)
        
        # Números dos períodos (1-7)
        for i in range(1, 8):
            label = QLabel(str(i))
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont("Arial", 10, QFont.Bold))
            label.setStyleSheet("color: #2c3e50; background-color: #ecf0f1; padding: 5px;")
            self.table_layout.addWidget(label, i, 0)
    
    def create_element_info_panel(self) -> QWidget:
        """Cria o painel de informações do elemento"""
        group = QGroupBox("Informações do Elemento")
        layout = QVBoxLayout()
        
        # Nome e símbolo
        self.element_name_label = QLabel("Selecione um elemento")
        self.element_name_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.element_name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.element_name_label)
        
        # Informações detalhadas
        self.element_info = QTextEdit()
        self.element_info.setReadOnly(True)
        self.element_info.setMaximumHeight(300)
        self.element_info.setStyleSheet("font-family: monospace; font-size: 11px;")
        layout.addWidget(self.element_info)
        
        # Propriedades químicas
        properties_group = QGroupBox("Propriedades Químicas")
        properties_layout = QVBoxLayout()
        
        self.chemical_properties = QTextEdit()
        self.chemical_properties.setReadOnly(True)
        self.chemical_properties.setMaximumHeight(200)
        self.chemical_properties.setStyleSheet("font-family: monospace; font-size: 10px;")
        properties_layout.addWidget(self.chemical_properties)
        
        properties_group.setLayout(properties_layout)
        layout.addWidget(properties_group)
        
        # Configuração eletrônica
        electron_group = QGroupBox("Configuração Eletrônica")
        electron_layout = QVBoxLayout()
        
        self.electron_config = QLabel("")
        self.electron_config.setWordWrap(True)
        self.electron_config.setStyleSheet("font-family: monospace; font-size: 11px; padding: 10px;")
        electron_layout.addWidget(self.electron_config)
        
        electron_group.setLayout(electron_layout)
        layout.addWidget(electron_group)
        
        layout.addStretch()
        group.setLayout(layout)
        
        return group
    
    def on_element_clicked(self, element_data: dict):
        """Manipula o clique em um elemento"""
        self.selected_element = element_data
        self.update_element_info(element_data)
    
    def update_element_info(self, element_data: dict):
        """Atualiza as informações do elemento selecionado"""
        # Nome e símbolo
        name_text = f"{element_data['name']} ({element_data['symbol']})"
        self.element_name_label.setText(name_text)
        
        # Informações básicas
        info_text = f"""
Número Atômico: {element_data['atomic_number']}
Massa Atômica: {element_data['atomic_mass']} u
Categoria: {element_data['category_name']}
Período: {element_data['period']}
Grupo: {element_data['group']}
        
Estado: {element_data.get('state', 'N/A')}
Ponto de Fusão: {element_data.get('melting_point', 'N/A')}°C
Ponto de Ebulição: {element_data.get('boiling_point', 'N/A')}°C
Densidade: {element_data.get('density', 'N/A')} g/cm³
        """
        self.element_info.setText(info_text.strip())
        
        # Propriedades químicas
        chem_props = f"""
Raio Atômico: {element_data.get('atomic_radius', 'N/A')} pm
Eletronegatividade: {element_data.get('electronegativity', 'N/A')}
Energia de Ionização: {element_data.get('ionization_energy', 'N/A')} kJ/mol
        
Principais Compostos:
{element_data.get('compounds', 'Informação não disponível')}
        
Aplicações:
{element_data.get('applications', 'Informação não disponível')}
        """
        self.chemical_properties.setText(chem_props.strip())
        
        # Configuração eletrônica
        electron_config = element_data.get('electron_config', 'N/A')
        self.electron_config.setText(f"Configuração Eletrônica: {electron_config}")
    
    def get_elements_data(self) -> list:
        """Retorna os dados dos elementos químicos"""
        return [
            # Período 1
            {
                'symbol': 'H', 'name': 'Hidrogênio', 'atomic_number': 1, 'atomic_mass': 1.008,
                'position': (1, 1), 'period': 1, 'group': 1, 'category': 'reactive_nonmetal',
                'category_name': 'Não metal reativo', 'state': 'Gás', 'melting_point': -259.16,
                'boiling_point': -252.87, 'density': 0.0899, 'atomic_radius': 37,
                'electronegativity': 2.20, 'ionization_energy': 1312,
                'electron_config': '1s¹',
                'compounds': 'H₂O (água), HCl (ácido clorídrico), NH₃ (amônia)',
                'applications': 'Combustível, síntese de amônia, hidrogenação'
            },
            {
                'symbol': 'He', 'name': 'Hélio', 'atomic_number': 2, 'atomic_mass': 4.003,
                'position': (1, 18), 'period': 1, 'group': 18, 'category': 'noble_gas',
                'category_name': 'Gás nobre', 'state': 'Gás', 'melting_point': -272.20,
                'boiling_point': -268.93, 'density': 0.1786, 'atomic_radius': 32,
                'electronegativity': None, 'ionization_energy': 2372,
                'electron_config': '1s²',
                'compounds': 'Nenhum composto estável conhecido',
                'applications': 'Balões, criogenia, atmosfera inerte'
            },
            
            # Período 2
            {
                'symbol': 'Li', 'name': 'Lítio', 'atomic_number': 3, 'atomic_mass': 6.941,
                'position': (2, 1), 'period': 2, 'group': 1, 'category': 'alkali_metal',
                'category_name': 'Metal alcalino', 'state': 'Sólido', 'melting_point': 180.5,
                'boiling_point': 1342, 'density': 0.534, 'atomic_radius': 152,
                'electronegativity': 0.98, 'ionization_energy': 520,
                'electron_config': '1s² 2s¹',
                'compounds': 'LiCl (cloreto de lítio), Li₂CO₃ (carbonato de lítio)',
                'applications': 'Baterias, medicamentos, cerâmicas'
            },
            {
                'symbol': 'Be', 'name': 'Berílio', 'atomic_number': 4, 'atomic_mass': 9.012,
                'position': (2, 2), 'period': 2, 'group': 2, 'category': 'alkaline_earth_metal',
                'category_name': 'Metal alcalino-terroso', 'state': 'Sólido', 'melting_point': 1287,
                'boiling_point': 2470, 'density': 1.85, 'atomic_radius': 112,
                'electronegativity': 1.57, 'ionization_energy': 899,
                'electron_config': '1s² 2s²',
                'compounds': 'BeO (óxido de berílio), BeCl₂ (cloreto de berílio)',
                'applications': 'Ligas espaciais, reatores nucleares'
            },
            {
                'symbol': 'B', 'name': 'Boro', 'atomic_number': 5, 'atomic_mass': 10.811,
                'position': (2, 13), 'period': 2, 'group': 13, 'category': 'metalloid',
                'category_name': 'Metaloide', 'state': 'Sólido', 'melting_point': 2077,
                'boiling_point': 4000, 'density': 2.34, 'atomic_radius': 85,
                'electronegativity': 2.04, 'ionization_energy': 801,
                'electron_config': '1s² 2s² 2p¹',
                'compounds': 'H₃BO₃ (ácido bórico), B₂O₃ (óxido de boro)',
                'applications': 'Vidros, detergentes, materiais cerâmicos'
            },
            {
                'symbol': 'C', 'name': 'Carbono', 'atomic_number': 6, 'atomic_mass': 12.011,
                'position': (2, 14), 'period': 2, 'group': 14, 'category': 'reactive_nonmetal',
                'category_name': 'Não metal reativo', 'state': 'Sólido', 'melting_point': 3550,
                'boiling_point': 4027, 'density': 2.267, 'atomic_radius': 77,
                'electronegativity': 2.55, 'ionization_energy': 1086,
                'electron_config': '1s² 2s² 2p²',
                'compounds': 'CO₂ (dióxido de carbono), CO (monóxido de carbono)',
                'applications': 'Compostos orgânicos, aço, diamante, grafite'
            },
            {
                'symbol': 'N', 'name': 'Nitrogênio', 'atomic_number': 7, 'atomic_mass': 14.007,
                'position': (2, 15), 'period': 2, 'group': 15, 'category': 'reactive_nonmetal',
                'category_name': 'Não metal reativo', 'state': 'Gás', 'melting_point': -210.0,
                'boiling_point': -195.79, 'density': 1.251, 'atomic_radius': 75,
                'electronegativity': 3.04, 'ionization_energy': 1402,
                'electron_config': '1s² 2s² 2p³',
                'compounds': 'NH₃ (amônia), HNO₃ (ácido nítrico), N₂O (óxido nitroso)',
                'applications': 'Fertilizantes, explosivos, atmosfera inerte'
            },
            {
                'symbol': 'O', 'name': 'Oxigênio', 'atomic_number': 8, 'atomic_mass': 15.999,
                'position': (2, 16), 'period': 2, 'group': 16, 'category': 'reactive_nonmetal',
                'category_name': 'Não metal reativo', 'state': 'Gás', 'melting_point': -218.79,
                'boiling_point': -182.95, 'density': 1.429, 'atomic_radius': 73,
                'electronegativity': 3.44, 'ionization_energy': 1314,
                'electron_config': '1s² 2s² 2p⁴',
                'compounds': 'H₂O (água), O₂ (oxigênio), O₃ (ozônio)',
                'applications': 'Respiração, combustão, medicina, soldagem'
            },
            {
                'symbol': 'F', 'name': 'Flúor', 'atomic_number': 9, 'atomic_mass': 18.998,
                'position': (2, 17), 'period': 2, 'group': 17, 'category': 'halogen',
                'category_name': 'Halogênio', 'state': 'Gás', 'melting_point': -219.67,
                'boiling_point': -188.11, 'density': 1.696, 'atomic_radius': 72,
                'electronegativity': 3.98, 'ionization_energy': 1681,
                'electron_config': '1s² 2s² 2p⁵',
                'compounds': 'HF (ácido fluorídrico), NaF (fluoreto de sódio)',
                'applications': 'Pasta de dente, teflon, refrigerantes'
            },
            {
                'symbol': 'Ne', 'name': 'Neônio', 'atomic_number': 10, 'atomic_mass': 20.180,
                'position': (2, 18), 'period': 2, 'group': 18, 'category': 'noble_gas',
                'category_name': 'Gás nobre', 'state': 'Gás', 'melting_point': -248.59,
                'boiling_point': -246.08, 'density': 0.9002, 'atomic_radius': 69,
                'electronegativity': None, 'ionization_energy': 2081,
                'electron_config': '1s² 2s² 2p⁶',
                'compounds': 'Nenhum composto estável conhecido',
                'applications': 'Letreiros luminosos, lasers, indicadores'
            },
            
            # Período 3 (elementos principais)
            {
                'symbol': 'Na', 'name': 'Sódio', 'atomic_number': 11, 'atomic_mass': 22.990,
                'position': (3, 1), 'period': 3, 'group': 1, 'category': 'alkali_metal',
                'category_name': 'Metal alcalino', 'state': 'Sólido', 'melting_point': 97.79,
                'boiling_point': 883, 'density': 0.971, 'atomic_radius': 186,
                'electronegativity': 0.93, 'ionization_energy': 496,
                'electron_config': '1s² 2s² 2p⁶ 3s¹',
                'compounds': 'NaCl (sal de cozinha), NaOH (soda cáustica)',
                'applications': 'Sal de mesa, sabões, vidros'
            },
            {
                'symbol': 'Mg', 'name': 'Magnésio', 'atomic_number': 12, 'atomic_mass': 24.305,
                'position': (3, 2), 'period': 3, 'group': 2, 'category': 'alkaline_earth_metal',
                'category_name': 'Metal alcalino-terroso', 'state': 'Sólido', 'melting_point': 650,
                'boiling_point': 1090, 'density': 1.738, 'atomic_radius': 160,
                'electronegativity': 1.31, 'ionization_energy': 738,
                'electron_config': '1s² 2s² 2p⁶ 3s²',
                'compounds': 'MgO (óxido de magnésio), MgCl₂ (cloreto de magnésio)',
                'applications': 'Ligas leves, fogos de artifício, medicina'
            },
            {
                'symbol': 'Al', 'name': 'Alumínio', 'atomic_number': 13, 'atomic_mass': 26.982,
                'position': (3, 13), 'period': 3, 'group': 13, 'category': 'post_transition_metal',
                'category_name': 'Metal pós-transição', 'state': 'Sólido', 'melting_point': 660.32,
                'boiling_point': 2519, 'density': 2.70, 'atomic_radius': 143,
                'electronegativity': 1.61, 'ionization_energy': 578,
                'electron_config': '1s² 2s² 2p⁶ 3s² 3p¹',
                'compounds': 'Al₂O₃ (óxido de alumínio), AlCl₃ (cloreto de alumínio)',
                'applications': 'Embalagens, construção, transporte'
            },
            {
                'symbol': 'Si', 'name': 'Silício', 'atomic_number': 14, 'atomic_mass': 28.086,
                'position': (3, 14), 'period': 3, 'group': 14, 'category': 'metalloid',
                'category_name': 'Metaloide', 'state': 'Sólido', 'melting_point': 1414,
                'boiling_point': 3265, 'density': 2.33, 'atomic_radius': 118,
                'electronegativity': 1.90, 'ionization_energy': 787,
                'electron_config': '1s² 2s² 2p⁶ 3s² 3p²',
                'compounds': 'SiO₂ (sílica), SiC (carbeto de silício)',
                'applications': 'Semicondutores, vidros, cerâmicas'
            },
            {
                'symbol': 'P', 'name': 'Fósforo', 'atomic_number': 15, 'atomic_mass': 30.974,
                'position': (3, 15), 'period': 3, 'group': 15, 'category': 'reactive_nonmetal',
                'category_name': 'Não metal reativo', 'state': 'Sólido', 'melting_point': 44.15,
                'boiling_point': 280.5, 'density': 1.82, 'atomic_radius': 110,
                'electronegativity': 2.19, 'ionization_energy': 1012,
                'electron_config': '1s² 2s² 2p⁶ 3s² 3p³',
                'compounds': 'H₃PO₄ (ácido fosfórico), Ca₃(PO₄)₂ (fosfato de cálcio)',
                'applications': 'Fertilizantes, fósforos, DNA/RNA'
            },
            {
                'symbol': 'S', 'name': 'Enxofre', 'atomic_number': 16, 'atomic_mass': 32.065,
                'position': (3, 16), 'period': 3, 'group': 16, 'category': 'reactive_nonmetal',
                'category_name': 'Não metal reativo', 'state': 'Sólido', 'melting_point': 115.21,
                'boiling_point': 444.61, 'density': 2.067, 'atomic_radius': 105,
                'electronegativity': 2.58, 'ionization_energy': 1000,
                'electron_config': '1s² 2s² 2p⁶ 3s² 3p⁴',
                'compounds': 'H₂SO₄ (ácido sulfúrico), SO₂ (dióxido de enxofre)',
                'applications': 'Ácido sulfúrico, vulcanização da borracha'
            },
            {
                'symbol': 'Cl', 'name': 'Cloro', 'atomic_number': 17, 'atomic_mass': 35.453,
                'position': (3, 17), 'period': 3, 'group': 17, 'category': 'halogen',
                'category_name': 'Halogênio', 'state': 'Gás', 'melting_point': -101.5,
                'boiling_point': -34.04, 'density': 3.214, 'atomic_radius': 102,
                'electronegativity': 3.16, 'ionization_energy': 1251,
                'electron_config': '1s² 2s² 2p⁶ 3s² 3p⁵',
                'compounds': 'HCl (ácido clorídrico), NaClO (hipoclorito de sódio)',
                'applications': 'Desinfetante, PVC, água potável'
            },
            {
                'symbol': 'Ar', 'name': 'Argônio', 'atomic_number': 18, 'atomic_mass': 39.948,
                'position': (3, 18), 'period': 3, 'group': 18, 'category': 'noble_gas',
                'category_name': 'Gás nobre', 'state': 'Gás', 'melting_point': -189.35,
                'boiling_point': -185.85, 'density': 1.784, 'atomic_radius': 98,
                'electronegativity': None, 'ionization_energy': 1521,
                'electron_config': '1s² 2s² 2p⁶ 3s² 3p⁶',
                'compounds': 'Nenhum composto estável conhecido',
                'applications': 'Soldagem, lâmpadas, atmosfera inerte'
            },
            
            # Adicionar alguns elementos do período 4 para demonstração
            {
                'symbol': 'K', 'name': 'Potássio', 'atomic_number': 19, 'atomic_mass': 39.098,
                'position': (4, 1), 'period': 4, 'group': 1, 'category': 'alkali_metal',
                'category_name': 'Metal alcalino', 'state': 'Sólido', 'melting_point': 63.5,
                'boiling_point': 759, 'density': 0.862, 'atomic_radius': 227,
                'electronegativity': 0.82, 'ionization_energy': 419,
                'electron_config': '1s² 2s² 2p⁶ 3s² 3p⁶ 4s¹',
                'compounds': 'KCl (cloreto de potássio), KNO₃ (nitrato de potássio)',
                'applications': 'Fertilizantes, sabões, vidros'
            },
            {
                'symbol': 'Ca', 'name': 'Cálcio', 'atomic_number': 20, 'atomic_mass': 40.078,
                'position': (4, 2), 'period': 4, 'group': 2, 'category': 'alkaline_earth_metal',
                'category_name': 'Metal alcalino-terroso', 'state': 'Sólido', 'melting_point': 842,
                'boiling_point': 1484, 'density': 1.54, 'atomic_radius': 197,
                'electronegativity': 1.00, 'ionization_energy': 590,
                'electron_config': '1s² 2s² 2p⁶ 3s² 3p⁶ 4s²',
                'compounds': 'CaCO₃ (carbonato de cálcio), CaO (óxido de cálcio)',
                'applications': 'Cimento, ossos e dentes, suplementos'
            },
            {
                'symbol': 'Fe', 'name': 'Ferro', 'atomic_number': 26, 'atomic_mass': 55.845,
                'position': (4, 8), 'period': 4, 'group': 8, 'category': 'transition_metal',
                'category_name': 'Metal de transição', 'state': 'Sólido', 'melting_point': 1538,
                'boiling_point': 2861, 'density': 7.874, 'atomic_radius': 126,
                'electronegativity': 1.83, 'ionization_energy': 762,
                'electron_config': '1s² 2s² 2p⁶ 3s² 3p⁶ 4s² 3d⁶',
                'compounds': 'Fe₂O₃ (óxido de ferro), FeCl₃ (cloreto férrico)',
                'applications': 'Aço, construção, transporte, hemoglobina'
            }
        ]
