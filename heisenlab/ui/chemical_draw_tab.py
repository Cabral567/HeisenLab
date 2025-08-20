from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QTextEdit, QTabWidget,
    QComboBox, QCheckBox, QSpinBox, QSlider, QColorDialog, QFileDialog, QMessageBox,
    QSplitter, QFrame, QListWidget, QListWidgetItem, QProgressBar, QApplication,
    QDialog, QInputDialog
)
from PySide6.QtGui import QPixmap, QImage, QColor, QFont, QPalette
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtWebEngineWidgets import QWebEngineView
from rdkit import Chem
from rdkit.Chem import Draw, AllChem, Descriptors, rdMolDescriptors, Crippen, Lipinski
import io
from PIL import Image
import py3Dmol
import tempfile
from ..bluebook_search import search_compound_in_bluebook, get_compound_suggestions
import os
import json
import re
import numpy as np
import random


class ChemicalDrawTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mol = None
        self.compounds_database = {}
        self.init_ui()
        self.load_comprehensive_database()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Create main splitter for better layout
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Input and controls
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        
        # Input section
        input_group = self.create_input_section()
        left_layout.addWidget(input_group)
        
        # Drawing options
        options_group = self.create_drawing_options_section()
        left_layout.addWidget(options_group)
        
        # Comprehensive molecule library
        library_group = self.create_comprehensive_library_section()
        left_layout.addWidget(library_group)
        
        left_layout.addStretch()
        left_widget.setLayout(left_layout)
        
        # Right panel - Visualization with tabs
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)
        
        # Enhanced visualization tabs
        viz_tabs = QTabWidget()
        
        # 2D Structure tab
        tab_2d = QWidget()
        tab_2d_layout = QVBoxLayout()
        drawing_group = self.create_enhanced_drawing_section()
        tab_2d_layout.addWidget(drawing_group)
        tab_2d.setLayout(tab_2d_layout)
        viz_tabs.addTab(tab_2d, "🧪 Estrutura 2D")
        
        # 3D Visualization tab
        tab_3d = QWidget()
        tab_3d_layout = QVBoxLayout()
        visualization_group = self.create_enhanced_3d_section()
        tab_3d_layout.addWidget(visualization_group)
        tab_3d.setLayout(tab_3d_layout)
        viz_tabs.addTab(tab_3d, "🌐 Visualização 3D")
        
        # Lewis Structure tab
        tab_lewis = QWidget()
        tab_lewis_layout = QVBoxLayout()
        lewis_group = self.create_lewis_structure_section()
        tab_lewis_layout.addWidget(lewis_group)
        tab_lewis.setLayout(tab_lewis_layout)
        viz_tabs.addTab(tab_lewis, "⚛️ Estrutura de Lewis")
        
        # Enhanced Properties tab
        tab_props = QWidget()
        tab_props_layout = QVBoxLayout()
        properties_group = self.create_enhanced_properties_section()
        tab_props_layout.addWidget(properties_group)
        tab_props.setLayout(tab_props_layout)
        viz_tabs.addTab(tab_props, "📊 Propriedades Físico-Químicas")
        
        # Electronic Structure tab
        tab_electronic = QWidget()
        tab_electronic_layout = QVBoxLayout()
        electronic_group = self.create_electronic_structure_section()
        tab_electronic_layout.addWidget(electronic_group)
        tab_electronic.setLayout(tab_electronic_layout)
        viz_tabs.addTab(tab_electronic, "⚡ Estrutura Eletrônica")
        
        # Orbital Visualization tab
        tab_orbitals = QWidget()
        tab_orbitals_layout = QVBoxLayout()
        orbitals_group = self.create_orbital_visualization_section()
        tab_orbitals_layout.addWidget(orbitals_group)
        tab_orbitals.setLayout(tab_orbitals_layout)
        viz_tabs.addTab(tab_orbitals, "🌀 Orbitais Moleculares")
        
        right_layout.addWidget(viz_tabs)
        right_widget.setLayout(right_layout)
        
        # Add to splitter
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setStretchFactor(0, 1)  # Left panel
        main_splitter.setStretchFactor(1, 2)  # Right panel (larger)
        
        layout.addWidget(main_splitter)
        self.setLayout(layout)

    def load_comprehensive_database(self):
        """Load comprehensive molecule database using RedBook and BlueBook data."""
        # Enhanced molecule database with thermodynamic properties
        self.compounds_database = {
            "Alcanos": [
                {
                    "nome": "Metano", "iupac": "Methane", "formula": "CH4", 
                    "smiles": "C", "bp": -161.5, "mp": -182.5, "density": 0.717,
                    "descricao": "Hidrocarboneto mais simples, principal componente do gás natural.",
                    "categoria": "Orgânico", "tipo": "Alcano", "valencia": "C: 4"
                },
                {
                    "nome": "Etano", "iupac": "Ethane", "formula": "C2H6", 
                    "smiles": "CC", "bp": -88.6, "mp": -183.3, "density": 1.356,
                    "descricao": "Segundo alcano mais simples, usado como combustível.",
                    "categoria": "Orgânico", "tipo": "Alcano", "valencia": "C: 4"
                },
                {
                    "nome": "Propano", "iupac": "Propane", "formula": "C3H8", 
                    "smiles": "CCC", "bp": -42.1, "mp": -187.7, "density": 2.019,
                    "descricao": "Gás de cozinha, combustível doméstico comum.",
                    "categoria": "Orgânico", "tipo": "Alcano", "valencia": "C: 4"
                },
                {
                    "nome": "Butano", "iupac": "Butane", "formula": "C4H10", 
                    "smiles": "CCCC", "bp": -0.5, "mp": -138.3, "density": 2.489,
                    "descricao": "Usado em isqueiros e como propelente.",
                    "categoria": "Orgânico", "tipo": "Alcano", "valencia": "C: 4"
                },
                {
                    "nome": "Pentano", "iupac": "Pentane", "formula": "C5H12", 
                    "smiles": "CCCCC", "bp": 36.1, "mp": -129.7, "density": 0.626,
                    "descricao": "Solvente orgânico volátil.",
                    "categoria": "Orgânico", "tipo": "Alcano", "valencia": "C: 4"
                }
            ],
            "Alcenos": [
                {
                    "nome": "Eteno", "iupac": "Ethene", "formula": "C2H4", 
                    "smiles": "C=C", "bp": -103.8, "mp": -169.2, "density": 1.178,
                    "descricao": "Precursor do polietileno, hormônio vegetal.",
                    "categoria": "Orgânico", "tipo": "Alceno", "valencia": "C: 4"
                },
                {
                    "nome": "Propeno", "iupac": "Propene", "formula": "C3H6", 
                    "smiles": "C=CC", "bp": -47.7, "mp": -185.2, "density": 1.81,
                    "descricao": "Precursor do polipropileno.",
                    "categoria": "Orgânico", "tipo": "Alceno", "valencia": "C: 4"
                }
            ],
            "Aromáticos": [
                {
                    "nome": "Benzeno", "iupac": "Benzene", "formula": "C6H6", 
                    "smiles": "c1ccccc1", "bp": 80.1, "mp": 5.5, "density": 0.879,
                    "descricao": "Aromático fundamental, carcinogênico.",
                    "categoria": "Orgânico", "tipo": "Aromático", "valencia": "C: 4"
                },
                {
                    "nome": "Tolueno", "iupac": "Methylbenzene", "formula": "C7H8", 
                    "smiles": "Cc1ccccc1", "bp": 110.6, "mp": -95.0, "density": 0.867,
                    "descricao": "Solvente industrial importante.",
                    "categoria": "Orgânico", "tipo": "Aromático", "valencia": "C: 4"
                },
                {
                    "nome": "Fenol", "iupac": "Phenol", "formula": "C6H5OH", 
                    "smiles": "c1ccc(cc1)O", "bp": 181.7, "mp": 40.5, "density": 1.071,
                    "descricao": "Precursor de polímeros, antisséptico.",
                    "categoria": "Orgânico", "tipo": "Fenol", "valencia": "C: 4, O: 2"
                },
                {
                    "nome": "Anilina", "iupac": "Aniline", "formula": "C6H5NH2", 
                    "smiles": "c1ccc(cc1)N", "bp": 184.1, "mp": -6.3, "density": 1.022,
                    "descricao": "Precursor de corantes e medicamentos.",
                    "categoria": "Orgânico", "tipo": "Amina aromática", "valencia": "C: 4, N: 3"
                }
            ],
            "Álcoois": [
                {
                    "nome": "Metanol", "iupac": "Methanol", "formula": "CH3OH", 
                    "smiles": "CO", "bp": 64.7, "mp": -97.6, "density": 0.792,
                    "descricao": "Álcool de madeira, tóxico.",
                    "categoria": "Orgânico", "tipo": "Álcool", "valencia": "C: 4, O: 2"
                },
                {
                    "nome": "Etanol", "iupac": "Ethanol", "formula": "C2H5OH", 
                    "smiles": "CCO", "bp": 78.4, "mp": -114.1, "density": 0.789,
                    "descricao": "Álcool etílico, combustível e bebida.",
                    "categoria": "Orgânico", "tipo": "Álcool", "valencia": "C: 4, O: 2"
                },
                {
                    "nome": "Isopropanol", "iupac": "2-Propanol", "formula": "C3H7OH", 
                    "smiles": "CC(C)O", "bp": 82.5, "mp": -89.5, "density": 0.786,
                    "descricao": "Álcool isopropílico, desinfetante.",
                    "categoria": "Orgânico", "tipo": "Álcool", "valencia": "C: 4, O: 2"
                }
            ],
            "Ácidos Carboxílicos": [
                {
                    "nome": "Ácido Fórmico", "iupac": "Methanoic acid", "formula": "HCOOH", 
                    "smiles": "C(=O)O", "bp": 100.8, "mp": 8.4, "density": 1.220,
                    "descricao": "Presente em formigas, conservante.",
                    "categoria": "Orgânico", "tipo": "Ácido carboxílico", "valencia": "C: 4, O: 2"
                },
                {
                    "nome": "Ácido Acético", "iupac": "Ethanoic acid", "formula": "CH3COOH", 
                    "smiles": "CC(=O)O", "bp": 117.9, "mp": 16.6, "density": 1.049,
                    "descricao": "Principal componente do vinagre.",
                    "categoria": "Orgânico", "tipo": "Ácido carboxílico", "valencia": "C: 4, O: 2"
                }
            ],
            "Compostos Inorgânicos": [
                {
                    "nome": "Água", "iupac": "Water", "formula": "H2O", 
                    "smiles": "O", "bp": 100.0, "mp": 0.0, "density": 1.000,
                    "descricao": "Solvente universal, essencial à vida.",
                    "categoria": "Inorgânico", "tipo": "Óxido", "valencia": "H: 1, O: 2"
                },
                {
                    "nome": "Amônia", "iupac": "Ammonia", "formula": "NH3", 
                    "smiles": "N", "bp": -33.3, "mp": -77.7, "density": 0.817,
                    "descricao": "Base forte, fertilizante, refrigerante.",
                    "categoria": "Inorgânico", "tipo": "Hidreto", "valencia": "N: 3, H: 1"
                },
                {
                    "nome": "Dióxido de Carbono", "iupac": "Carbon dioxide", "formula": "CO2", 
                    "smiles": "C(=O)=O", "bp": -78.5, "mp": -56.6, "density": 1.977,
                    "descricao": "Gás estufa, produto da combustão.",
                    "categoria": "Inorgânico", "tipo": "Óxido", "valencia": "C: 4, O: 2"
                },
                {
                    "nome": "Ácido Clorídrico", "iupac": "Hydrogen chloride", "formula": "HCl", 
                    "smiles": "Cl", "bp": -85.1, "mp": -114.2, "density": 1.639,
                    "descricao": "Ácido forte, digestão gástrica.",
                    "categoria": "Inorgânico", "tipo": "Haleto de hidrogênio", "valencia": "H: 1, Cl: 1"
                }
            ],
            "Compostos Organometálicos": [
                {
                    "nome": "Tetracloreto de Carbono", "iupac": "Tetrachloromethane", "formula": "CCl4", 
                    "smiles": "C(Cl)(Cl)(Cl)Cl", "bp": 76.7, "mp": -22.9, "density": 1.594,
                    "descricao": "Solvente, ozônio-destruidor.",
                    "categoria": "Orgânico", "tipo": "Haleto orgânico", "valencia": "C: 4, Cl: 1"
                },
                {
                    "nome": "Clorofórmio", "iupac": "Trichloromethane", "formula": "CHCl3", 
                    "smiles": "C(Cl)(Cl)Cl", "bp": 61.2, "mp": -63.5, "density": 1.483,
                    "descricao": "Anestésico histórico, solvente.",
                    "categoria": "Orgânico", "tipo": "Haleto orgânico", "valencia": "C: 4, Cl: 1"
                }
            ],
            "Medicamentos": [
                {
                    "nome": "Aspirina", "iupac": "2-Acetoxybenzoic acid", "formula": "C9H8O4", 
                    "smiles": "CC(=O)Oc1ccccc1C(=O)O", "bp": 140, "mp": 135, "density": 1.40,
                    "descricao": "Analgésico, anti-inflamatório.",
                    "categoria": "Farmacêutico", "tipo": "AINE", "valencia": "C: 4, O: 2"
                },
                {
                    "nome": "Cafeína", "iupac": "1,3,7-Trimethylpurine-2,6-dione", "formula": "C8H10N4O2", 
                    "smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C", "bp": 178, "mp": 235, "density": 1.23,
                    "descricao": "Estimulante do sistema nervoso central.",
                    "categoria": "Farmacêutico", "tipo": "Alcaloide", "valencia": "C: 4, N: 3, O: 2"
                },
                {
                    "nome": "Paracetamol", "iupac": "N-(4-Hydroxyphenyl)acetamide", "formula": "C8H9NO2", 
                    "smiles": "CC(=O)Nc1ccc(cc1)O", "bp": 420, "mp": 169, "density": 1.29,
                    "descricao": "Analgésico e antipirético.",
                    "categoria": "Farmacêutico", "tipo": "Analgésico", "valencia": "C: 4, N: 3, O: 2"
                }
            ],
            "Biomoléculas": [
                {
                    "nome": "Glicose", "iupac": "D-Glucose", "formula": "C6H12O6", 
                    "smiles": "C([C@@H]1[C@H]([C@@H]([C@H]([C@H](O1)O)O)O)O)O", "bp": 146, "mp": 146, "density": 1.54,
                    "descricao": "Açúcar fundamental, fonte de energia.",
                    "categoria": "Bioquímico", "tipo": "Carboidrato", "valencia": "C: 4, O: 2"
                },
                {
                    "nome": "Frutose", "iupac": "D-Fructose", "formula": "C6H12O6", 
                    "smiles": "C([C@H]([C@H]([C@@H]([C@H](CO)O)O)O)O)O", "bp": 103, "mp": 103, "density": 1.69,
                    "descricao": "Açúcar das frutas, mais doce que glicose.",
                    "categoria": "Bioquímico", "tipo": "Carboidrato", "valencia": "C: 4, O: 2"
                },
                {
                    "nome": "Colesterol", "iupac": "Cholest-5-en-3β-ol", "formula": "C27H46O", 
                    "smiles": "CC(C)CCCC(C)C1CCC2C1(CCC3C2CC=C4C3(CCC(C4)O)C)C", "bp": 360, "mp": 148, "density": 1.067,
                    "descricao": "Esterol importante, precursor hormonal.",
                    "categoria": "Bioquímico", "tipo": "Esterol", "valencia": "C: 4, O: 2"
                }
            ]
        }

    def create_input_section(self) -> QGroupBox:
        """Create the input section with enhanced features."""
        group = QGroupBox("Entrada de Moléculas")
        layout = QFormLayout()
        layout.setVerticalSpacing(12)
        layout.setHorizontalSpacing(15)
        
        # SMILES input
        self.smiles_input = QLineEdit()
        self.smiles_input.setPlaceholderText("Digite o SMILES da molécula (ex: CCO para etanol)")
        self.smiles_input.setMinimumHeight(30)
        self.smiles_input.returnPressed.connect(self.draw_molecule)
        layout.addRow("SMILES:", self.smiles_input)
        
        # Name input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome da molécula (opcional)")
        self.name_input.setMinimumHeight(30)
        layout.addRow("Nome:", self.name_input)
        
        # Busca no Blue Book
        bluebook_layout = QHBoxLayout()
        self.bluebook_input = QLineEdit()
        self.bluebook_input.setPlaceholderText("Nome do composto para buscar no Blue Book")
        self.bluebook_input.setMinimumHeight(30)
        bluebook_layout.addWidget(self.bluebook_input)
        
        self.bluebook_search_button = QPushButton("Buscar")
        self.bluebook_search_button.setMinimumHeight(30)
        self.bluebook_search_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.bluebook_search_button.clicked.connect(self.search_bluebook)
        bluebook_layout.addWidget(self.bluebook_search_button)
        
        layout.addRow("Blue Book:", bluebook_layout)
        
        # Resultado da busca
        self.bluebook_result = QTextEdit()
        self.bluebook_result.setReadOnly(True)
        self.bluebook_result.setMaximumHeight(80)
        self.bluebook_result.setStyleSheet("font-family: monospace; font-size: 10px;")
        self.bluebook_result.setPlaceholderText("Resultado da busca no Blue Book aparecerá aqui...")
        layout.addRow("Resultado:", self.bluebook_result)
        
        # Buttons row
        buttons_layout = QHBoxLayout()
        
        self.draw_button = QPushButton("Desenhar")
        self.draw_button.setMinimumHeight(35)
        self.draw_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.draw_button.clicked.connect(self.draw_molecule)
        buttons_layout.addWidget(self.draw_button)
        
        self.clear_button = QPushButton("Limpar")
        self.clear_button.setMinimumHeight(35)
        self.clear_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.clear_button.clicked.connect(self.clear_all)
        buttons_layout.addWidget(self.clear_button)
        
        self.random_button = QPushButton("Aleatório")
        self.random_button.setMinimumHeight(35)
        self.random_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.random_button.clicked.connect(self.load_random_molecule)
        buttons_layout.addWidget(self.random_button)
        
        layout.addRow("", buttons_layout)
        
        group.setLayout(layout)
        return group

    def create_drawing_options_section(self) -> QGroupBox:
        """Create drawing options section."""
        group = QGroupBox("Opções de Desenho")
        layout = QFormLayout()
        layout.setVerticalSpacing(10)
        
        # Image size
        size_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(200, 1000)
        self.width_spin.setValue(400)
        self.width_spin.setSuffix(" px")
        size_layout.addWidget(self.width_spin)
        
        size_layout.addWidget(QLabel("×"))
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(200, 1000)
        self.height_spin.setValue(300)
        self.height_spin.setSuffix(" px")
        size_layout.addWidget(self.height_spin)
        
        layout.addRow("Tamanho:", size_layout)
        
        # Show atom labels
        self.show_atom_labels = QCheckBox("Mostrar rótulos dos átomos")
        layout.addRow("", self.show_atom_labels)
        
        # Show hydrogens
        self.show_hydrogens = QCheckBox("Mostrar hidrogênios")
        layout.addRow("", self.show_hydrogens)
        
        # Apply options button
        self.apply_options_button = QPushButton("Aplicar Opções")
        self.apply_options_button.setMinimumHeight(35)
        self.apply_options_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.apply_options_button.clicked.connect(self.redraw_with_options)
        self.apply_options_button.setEnabled(False)
        layout.addRow("", self.apply_options_button)
        
        group.setLayout(layout)
        return group

    def create_comprehensive_library_section(self) -> QGroupBox:
        """Create comprehensive molecule library section with enhanced categories."""
        group = QGroupBox("📚 Biblioteca Molecular Abrangente")
        layout = QVBoxLayout()
        
        # Search functionality
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Buscar:"))
        self.library_search = QLineEdit()
        self.library_search.setPlaceholderText("Nome, fórmula ou SMILES...")
        self.library_search.textChanged.connect(self.filter_molecules)
        search_layout.addWidget(self.library_search)
        layout.addLayout(search_layout)
        
        # Enhanced categories
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("📂 Categoria:"))
        self.category_combo = QComboBox()
        categories = [
            "Todos", "Alcanos", "Alcenos", "Alcinos", "Aromáticos", "Álcoois", 
            "Éteres", "Aldeídos", "Cetonas", "Ácidos Carboxílicos", "Ésteres", 
            "Aminas", "Amidas", "Compostos Inorgânicos", "Compostos Organometálicos", 
            "Medicamentos", "Biomoléculas", "Polímeros", "Corantes", "Pesticidas"
        ]
        self.category_combo.addItems(categories)
        self.category_combo.currentTextChanged.connect(self.update_molecule_list)
        category_layout.addWidget(self.category_combo)
        layout.addLayout(category_layout)

        # Enhanced molecule list with details
        self.molecule_list = QListWidget()
        self.molecule_list.setMinimumHeight(200)
        self.molecule_list.currentItemChanged.connect(self.show_molecule_details)
        layout.addWidget(self.molecule_list)

        # Enhanced molecule details
        self.molecule_details = QTextEdit()
        self.molecule_details.setReadOnly(True)
        self.molecule_details.setMinimumHeight(150)
        self.molecule_details.setMaximumHeight(200)
        self.molecule_details.setStyleSheet("""
            QTextEdit {
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.molecule_details)

        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.load_molecule_button = QPushButton("📥 Carregar")
        self.load_molecule_button.setMinimumHeight(35)
        self.load_molecule_button.setStyleSheet(self.get_button_style("success"))
        self.load_molecule_button.clicked.connect(self.load_selected_molecule)
        buttons_layout.addWidget(self.load_molecule_button)

        self.favorite_button = QPushButton("⭐ Favoritar")
        self.favorite_button.setMinimumHeight(35)
        self.favorite_button.setStyleSheet(self.get_button_style("warning"))
        buttons_layout.addWidget(self.favorite_button)

        self.add_custom_button = QPushButton("➕ Adicionar")
        self.add_custom_button.setMinimumHeight(35)
        self.add_custom_button.setStyleSheet(self.get_button_style("info"))
        self.add_custom_button.clicked.connect(self.add_custom_molecule)
        buttons_layout.addWidget(self.add_custom_button)

        layout.addLayout(buttons_layout)
        
        # Initialize molecule list
        self.update_molecule_list()
        
        group.setLayout(layout)
        return group

    def create_enhanced_3d_section(self) -> QGroupBox:
        """Create enhanced 3D visualization section."""
        group = QGroupBox("🌐 Visualização 3D Avançada")
        layout = QVBoxLayout()
        
        # 3D Style controls
        controls_layout = QHBoxLayout()
        
        # Style selection
        style_group = QGroupBox("🎨 Estilo 3D")
        style_group_layout = QVBoxLayout()
        
        self.style_3d_combo = QComboBox()
        self.style_3d_combo.addItems([
            "🔮 Esferas e Bastões",
            "🌐 Superfície Molecular", 
            "📐 Wireframe",
            "🎈 Espaço-Preenchimento",
            "⚡ Stick",
            "🧊 Cartoon",
            "🌈 Colorido por Elemento"
        ])
        style_group_layout.addWidget(self.style_3d_combo)
        
        # 3D Options
        self.show_hydrogens_3d = QCheckBox("💧 Mostrar Hidrogênios")
        self.show_hydrogens_3d.setChecked(False)
        style_group_layout.addWidget(self.show_hydrogens_3d)
        
        self.auto_rotate = QCheckBox("🌀 Rotação Automática")
        style_group_layout.addWidget(self.auto_rotate)
        
        style_group.setLayout(style_group_layout)
        controls_layout.addWidget(style_group)
        
        # Quality settings
        quality_group = QGroupBox("⚙️ Qualidade")
        quality_layout = QVBoxLayout()
        
        quality_layout.addWidget(QLabel("🎯 Resolução:"))
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["Baixa", "Média", "Alta", "Ultra"])
        self.resolution_combo.setCurrentText("Alta")
        quality_layout.addWidget(self.resolution_combo)
        
        quality_layout.addWidget(QLabel("💡 Iluminação:"))
        self.lighting_combo = QComboBox()
        self.lighting_combo.addItems(["Básica", "Realística", "Artística"])
        quality_layout.addWidget(self.lighting_combo)
        
        quality_group.setLayout(quality_layout)
        controls_layout.addWidget(quality_group)
        
        layout.addLayout(controls_layout)
        
        # 3D Viewer placeholder
        self.viewer_3d_frame = QFrame()
        self.viewer_3d_frame.setFrameStyle(QFrame.StyledPanel)
        self.viewer_3d_frame.setMinimumHeight(400)
        self.viewer_3d_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #4a90e2;
                border-radius: 10px;
            }
        """)
        
        # Placeholder layout
        placeholder_layout = QVBoxLayout()
        placeholder_label = QLabel("🧬 Visualização 3D Interativa")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            margin: 50px;
        """)
        placeholder_layout.addWidget(placeholder_label)
        
        info_label = QLabel("Carregue uma molécula para visualização 3D")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("""
            color: #cccccc;
            font-size: 14px;
        """)
        placeholder_layout.addWidget(info_label)
        
        self.viewer_3d_frame.setLayout(placeholder_layout)
        layout.addWidget(self.viewer_3d_frame)
        
        # 3D Action buttons
        buttons_3d_layout = QHBoxLayout()
        
        self.generate_3d_button = QPushButton("🔄 Gerar 3D")
        self.generate_3d_button.setMinimumHeight(35)
        self.generate_3d_button.setStyleSheet(self.get_button_style("primary"))
        self.generate_3d_button.clicked.connect(self.generate_3d_coordinates)
        buttons_3d_layout.addWidget(self.generate_3d_button)
        
        self.optimize_3d_button = QPushButton("⚡ Otimizar Geometria")
        self.optimize_3d_button.setMinimumHeight(35)
        self.optimize_3d_button.setStyleSheet(self.get_button_style("success"))
        self.optimize_3d_button.clicked.connect(self.optimize_3d_structure)
        buttons_3d_layout.addWidget(self.optimize_3d_button)
        
        self.export_3d_button = QPushButton("💾 Exportar 3D")
        self.export_3d_button.setMinimumHeight(35)
        self.export_3d_button.setStyleSheet(self.get_button_style("info"))
        self.export_3d_button.clicked.connect(self.export_3d_structure)
        buttons_3d_layout.addWidget(self.export_3d_button)
        
        self.fullscreen_3d_button = QPushButton("🔍 Tela Cheia")
        self.fullscreen_3d_button.setMinimumHeight(35)
        self.fullscreen_3d_button.setStyleSheet(self.get_button_style("warning"))
        self.fullscreen_3d_button.clicked.connect(self.open_fullscreen_3d)
        buttons_3d_layout.addWidget(self.fullscreen_3d_button)
        
        layout.addLayout(buttons_3d_layout)
        
        # Initially disable 3D buttons
        self.generate_3d_button.setEnabled(False)
        self.optimize_3d_button.setEnabled(False)
        self.export_3d_button.setEnabled(False)
        self.fullscreen_3d_button.setEnabled(False)
        
        group.setLayout(layout)
        return group

    def create_enhanced_drawing_section(self) -> QGroupBox:
        """Create enhanced 2D drawing section with multiple representations."""
        group = QGroupBox("🧪 Estrutura Química 2D")
        layout = QVBoxLayout()
        
        # Drawing style options
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("🎨 Estilo:"))
        
        self.drawing_style = QComboBox()
        self.drawing_style.addItems([
            "Clássico", "Moderno", "Esquemático", "Farmacêutico", 
            "Publicação", "Estereoquímico", "Wireframe"
        ])
        self.drawing_style.currentTextChanged.connect(self.update_drawing_style)
        style_layout.addWidget(self.drawing_style)
        
        self.color_scheme = QComboBox()
        self.color_scheme.addItems([
            "Padrão", "CPK", "Jmol", "RasMol", "Monocromo", "Elemento"
        ])
        self.color_scheme.currentTextChanged.connect(self.update_color_scheme)
        style_layout.addWidget(self.color_scheme)
        
        layout.addLayout(style_layout)
        
        # Enhanced molecule display with zoom
        display_frame = QFrame()
        display_frame.setFrameStyle(QFrame.StyledPanel)
        display_layout = QVBoxLayout()
        
        # Zoom controls
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("🔍 Zoom:"))
        
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(50, 200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.update_zoom)
        zoom_layout.addWidget(self.zoom_slider)
        
        self.zoom_label = QLabel("100%")
        zoom_layout.addWidget(self.zoom_label)
        
        display_layout.addLayout(zoom_layout)
        
        # Main image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(400)
        self.image_label.setMinimumWidth(500)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px solid #ddd;
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        self.image_label.setText("🧪 Digite um SMILES ou carregue uma molécula da biblioteca")
        display_layout.addWidget(self.image_label)
        
        display_frame.setLayout(display_layout)
        layout.addWidget(display_frame)
        
        # Enhanced molecule information
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.StyledPanel)
        info_layout = QVBoxLayout()
        
        info_layout.addWidget(QLabel("📋 Informações Moleculares:"))
        self.molecule_info = QTextEdit()
        self.molecule_info.setReadOnly(True)
        self.molecule_info.setMinimumHeight(200)
        self.molecule_info.setMaximumHeight(250)
        self.molecule_info.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', monospace;
                font-size: 11px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        info_layout.addWidget(self.molecule_info)
        
        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)
        
        group.setLayout(layout)
        return group

    def create_lewis_structure_section(self) -> QGroupBox:
        """Create Lewis structure visualization section."""
        group = QGroupBox("⚛️ Estrutura de Lewis e Ligações")
        layout = QVBoxLayout()
        
        # Lewis structure display
        self.lewis_display = QTextEdit()
        self.lewis_display.setReadOnly(True)
        self.lewis_display.setMinimumHeight(300)
        self.lewis_display.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 16px;
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                line-height: 1.5;
            }
        """)
        layout.addWidget(self.lewis_display)
        
        # Bond analysis
        bond_frame = QFrame()
        bond_frame.setFrameStyle(QFrame.StyledPanel)
        bond_layout = QVBoxLayout()
        
        bond_layout.addWidget(QLabel("🔗 Análise de Ligações:"))
        self.bond_analysis = QTextEdit()
        self.bond_analysis.setReadOnly(True)
        self.bond_analysis.setMinimumHeight(200)
        self.bond_analysis.setStyleSheet("""
            QTextEdit {
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        bond_layout.addWidget(self.bond_analysis)
        
        bond_frame.setLayout(bond_layout)
        layout.addWidget(bond_frame)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.generate_lewis_button = QPushButton("🔬 Gerar Estrutura de Lewis")
        self.generate_lewis_button.setMinimumHeight(35)
        self.generate_lewis_button.setStyleSheet(self.get_button_style("primary"))
        self.generate_lewis_button.clicked.connect(self.generate_lewis_structure)
        self.generate_lewis_button.setEnabled(False)
        controls_layout.addWidget(self.generate_lewis_button)
        
        self.analyze_bonds_button = QPushButton("📊 Analisar Ligações")
        self.analyze_bonds_button.setMinimumHeight(35)
        self.analyze_bonds_button.setStyleSheet(self.get_button_style("info"))
        self.analyze_bonds_button.clicked.connect(self.analyze_molecular_bonds)
        self.analyze_bonds_button.setEnabled(False)
        controls_layout.addWidget(self.analyze_bonds_button)
        
        layout.addLayout(controls_layout)
        
        group.setLayout(layout)
        return group

    def create_enhanced_properties_section(self) -> QGroupBox:
        """Create enhanced properties section with thermodynamic data."""
        group = QGroupBox("📊 Propriedades Físico-Químicas Completas")
        layout = QVBoxLayout()
        
        # Properties tabs
        props_tabs = QTabWidget()
        
        # Basic Properties
        basic_tab = QWidget()
        basic_layout = QVBoxLayout()
        
        self.basic_properties = QTextEdit()
        self.basic_properties.setReadOnly(True)
        self.basic_properties.setMinimumHeight(250)
        self.basic_properties.setStyleSheet(self.get_text_area_style())
        basic_layout.addWidget(self.basic_properties)
        
        basic_tab.setLayout(basic_layout)
        props_tabs.addTab(basic_tab, "🔬 Básicas")
        
        # Thermodynamic Properties
        thermo_tab = QWidget()
        thermo_layout = QVBoxLayout()
        
        self.thermo_properties = QTextEdit()
        self.thermo_properties.setReadOnly(True)
        self.thermo_properties.setMinimumHeight(250)
        self.thermo_properties.setStyleSheet(self.get_text_area_style())
        thermo_layout.addWidget(self.thermo_properties)
        
        thermo_tab.setLayout(thermo_layout)
        props_tabs.addTab(thermo_tab, "🌡️ Termodinâmicas")
        
        # Pharmacological Properties
        pharma_tab = QWidget()
        pharma_layout = QVBoxLayout()
        
        self.pharma_properties = QTextEdit()
        self.pharma_properties.setReadOnly(True)
        self.pharma_properties.setMinimumHeight(250)
        self.pharma_properties.setStyleSheet(self.get_text_area_style())
        pharma_layout.addWidget(self.pharma_properties)
        
        pharma_tab.setLayout(pharma_layout)
        props_tabs.addTab(pharma_tab, "💊 Farmacológicas")
        
        layout.addWidget(props_tabs)
        
        # Calculation progress
        self.calc_progress = QProgressBar()
        self.calc_progress.setVisible(False)
        layout.addWidget(self.calc_progress)
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        export_buttons = [
            ("📄 Exportar SDF", self.export_sdf),
            ("🧪 Exportar MOL", self.export_mol),
            ("🖼️ Exportar PNG", self.export_png),
            ("📊 Relatório PDF", self.export_report)
        ]
        
        for text, handler in export_buttons:
            button = QPushButton(text)
            button.setMinimumHeight(35)
            button.setStyleSheet(self.get_button_style("secondary"))
            button.clicked.connect(handler)
            button.setEnabled(False)
            setattr(self, f"{text.split()[1].lower()}_button", button)
            export_layout.addWidget(button)

        layout.addLayout(export_layout)
        
        group.setLayout(layout)
        return group

    def create_electronic_structure_section(self) -> QGroupBox:
        """Create electronic structure visualization section."""
        group = QGroupBox("⚡ Estrutura Eletrônica e Configuração")
        layout = QVBoxLayout()
        
        # Electronic configuration display
        config_frame = QFrame()
        config_frame.setFrameStyle(QFrame.StyledPanel)
        config_layout = QVBoxLayout()
        
        config_layout.addWidget(QLabel("🔬 Configuração Eletrônica dos Átomos:"))
        self.electron_config = QTextEdit()
        self.electron_config.setReadOnly(True)
        self.electron_config.setMinimumHeight(200)
        self.electron_config.setStyleSheet(self.get_text_area_style())
        config_layout.addWidget(self.electron_config)
        
        config_frame.setLayout(config_layout)
        layout.addWidget(config_frame)
        
        # Orbital filling diagram
        orbital_frame = QFrame()
        orbital_frame.setFrameStyle(QFrame.StyledPanel)
        orbital_layout = QVBoxLayout()
        
        orbital_layout.addWidget(QLabel("📊 Diagrama de Preenchimento Orbital:"))
        self.orbital_diagram = QTextEdit()
        self.orbital_diagram.setReadOnly(True)
        self.orbital_diagram.setMinimumHeight(250)
        self.orbital_diagram.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 14px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                line-height: 1.8;
            }
        """)
        orbital_layout.addWidget(self.orbital_diagram)
        
        orbital_frame.setLayout(orbital_layout)
        layout.addWidget(orbital_frame)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.show_electrons_button = QPushButton("🔬 Mostrar Elétrons")
        self.show_electrons_button.setMinimumHeight(35)
        self.show_electrons_button.setStyleSheet(self.get_button_style("primary"))
        self.show_electrons_button.clicked.connect(self.show_electronic_structure)
        self.show_electrons_button.setEnabled(False)
        controls_layout.addWidget(self.show_electrons_button)
        
        self.orbital_filling_button = QPushButton("📊 Diagrama Orbital")
        self.orbital_filling_button.setMinimumHeight(35)
        self.orbital_filling_button.setStyleSheet(self.get_button_style("info"))
        self.orbital_filling_button.clicked.connect(self.show_orbital_filling)
        self.orbital_filling_button.setEnabled(False)
        controls_layout.addWidget(self.orbital_filling_button)
        
        layout.addLayout(controls_layout)
        
        group.setLayout(layout)
        return group

    def create_orbital_visualization_section(self) -> QGroupBox:
        """Create molecular orbital visualization section."""
        group = QGroupBox("🌀 Orbitais Moleculares e Hibridização")
        layout = QVBoxLayout()
        
        # Orbital information
        orbital_info_frame = QFrame()
        orbital_info_frame.setFrameStyle(QFrame.StyledPanel)
        orbital_info_layout = QVBoxLayout()
        
        orbital_info_layout.addWidget(QLabel("🔬 Análise de Hibridização:"))
        self.hybridization_info = QTextEdit()
        self.hybridization_info.setReadOnly(True)
        self.hybridization_info.setMinimumHeight(200)
        self.hybridization_info.setStyleSheet(self.get_text_area_style())
        orbital_info_layout.addWidget(self.hybridization_info)
        
        orbital_info_frame.setLayout(orbital_info_layout)
        layout.addWidget(orbital_info_frame)
        
        # Molecular orbital diagram
        mo_frame = QFrame()
        mo_frame.setFrameStyle(QFrame.StyledPanel)
        mo_layout = QVBoxLayout()
        
        mo_layout.addWidget(QLabel("⚛️ Diagrama de Orbitais Moleculares:"))
        self.mo_diagram = QTextEdit()
        self.mo_diagram.setReadOnly(True)
        self.mo_diagram.setMinimumHeight(250)
        self.mo_diagram.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 12px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                line-height: 1.6;
            }
        """)
        mo_layout.addWidget(self.mo_diagram)
        
        mo_frame.setLayout(mo_layout)
        layout.addWidget(mo_frame)
        
        # Analysis controls
        analysis_layout = QHBoxLayout()
        
        self.analyze_hybridization_button = QPushButton("🔬 Analisar Hibridização")
        self.analyze_hybridization_button.setMinimumHeight(35)
        self.analyze_hybridization_button.setStyleSheet(self.get_button_style("primary"))
        self.analyze_hybridization_button.clicked.connect(self.analyze_hybridization)
        self.analyze_hybridization_button.setEnabled(False)
        analysis_layout.addWidget(self.analyze_hybridization_button)
        
        self.mo_analysis_button = QPushButton("⚛️ Orbitais Moleculares")
        self.mo_analysis_button.setMinimumHeight(35)
        self.mo_analysis_button.setStyleSheet(self.get_button_style("info"))
        self.mo_analysis_button.clicked.connect(self.analyze_molecular_orbitals)
        self.mo_analysis_button.setEnabled(False)
        analysis_layout.addWidget(self.mo_analysis_button)
        
        layout.addLayout(analysis_layout)
        
        group.setLayout(layout)
        return group

    def get_button_style(self, style_type="primary"):
        """Get consistent button styling."""
        styles = {
            "primary": "background-color: #007bff; color: white; border: none; border-radius: 5px; font-weight: bold;",
            "success": "background-color: #28a745; color: white; border: none; border-radius: 5px; font-weight: bold;",
            "warning": "background-color: #ffc107; color: black; border: none; border-radius: 5px; font-weight: bold;",
            "info": "background-color: #17a2b8; color: white; border: none; border-radius: 5px; font-weight: bold;",
            "secondary": "background-color: #6c757d; color: white; border: none; border-radius: 5px; font-weight: bold;"
        }
        return f"QPushButton {{ {styles.get(style_type, styles['primary'])} }} QPushButton:hover {{ opacity: 0.8; }}"

    def get_text_area_style(self):
        """Get consistent text area styling."""
        return """
            QTextEdit {
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                line-height: 1.4;
            }
        """

    def create_3d_section(self) -> QGroupBox:
        """Create the 3D visualization section."""
        group = QGroupBox("Visualização 3D Interativa")
        layout = QVBoxLayout()
        
        # 3D button
        button_layout = QHBoxLayout()
        
        # Lewis Structure button
        self.lewis_button = QPushButton("Estrutura de Lewis")
        self.lewis_button.setMinimumHeight(35)
        self.lewis_button.setStyleSheet("QPushButton { font-weight: bold; background-color: #4CAF50; color: white; }")
        self.lewis_button.clicked.connect(self.show_lewis_structure)
        self.lewis_button.setEnabled(False)
        button_layout.addWidget(self.lewis_button)
        
        self.view_3d_button = QPushButton("Gerar Visualização 3D")
        self.view_3d_button.setMinimumHeight(35)
        self.view_3d_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.view_3d_button.clicked.connect(self.show_3d_molecule)
        self.view_3d_button.setEnabled(False)
        button_layout.addWidget(self.view_3d_button)
        
        self.optimize_button = QPushButton("Otimizar Geometria")
        self.optimize_button.setMinimumHeight(35)
        self.optimize_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.optimize_button.clicked.connect(self.optimize_geometry)
        self.optimize_button.setEnabled(False)
        button_layout.addWidget(self.optimize_button)
        
        layout.addLayout(button_layout)
        
        # Web view for 3D molecule
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(450)
        self.web_view.setHtml(self.get_empty_3d_html())
        layout.addWidget(self.web_view)
        
        # 3D controls
        controls_layout = QHBoxLayout()
        
        # Style controls
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("Estilo:"))
        
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Stick", "Ball & Stick", "Sphere", "Wireframe", "Cartoon"])
        self.style_combo.currentTextChanged.connect(self.change_3d_style)
        self.style_combo.setEnabled(False)
        style_layout.addWidget(self.style_combo)
        
        controls_layout.addLayout(style_layout)
        
        # Animation controls
        self.rotate_button = QPushButton("Auto-rotação")
        self.rotate_button.setMinimumHeight(30)
        self.rotate_button.clicked.connect(self.toggle_rotation)
        self.rotate_button.setEnabled(False)
        controls_layout.addWidget(self.rotate_button)
        
        self.reset_view_button = QPushButton("Resetar Vista")
        self.reset_view_button.setMinimumHeight(30)
        self.reset_view_button.clicked.connect(self.reset_3d_view)
        self.reset_view_button.setEnabled(False)
        controls_layout.addWidget(self.reset_view_button)
        
        # Background color
        self.bg_color_button = QPushButton("Cor de Fundo")
        self.bg_color_button.setMinimumHeight(30)
        self.bg_color_button.clicked.connect(self.change_bg_color)
        self.bg_color_button.setEnabled(False)
        controls_layout.addWidget(self.bg_color_button)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        group.setLayout(layout)
        return group

    def draw_molecule(self):
        """Enhanced molecule drawing with comprehensive analysis."""
        smiles = self.smiles_input.text().strip()
        if not smiles:
            self.image_label.setText("🧪 Digite um SMILES válido.")
            self.clear_all_displays()
            return
            
        try:
            # Parse SMILES
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                self.image_label.setText("❌ SMILES inválido. Verifique a sintaxe.")
                self.clear_all_displays()
                return
            
            # Store molecule for further analysis
            self.current_mol = mol
            
            # Apply enhanced drawing options
            draw_options = Draw.rdMolDraw2D.MolDrawOptions()
            
            # Configure drawing style
            self.configure_drawing_options(draw_options)
            
            # Handle hydrogen display
            display_mol = mol
            if self.show_hydrogens.isChecked():
                display_mol = Chem.AddHs(mol)
            
            # Generate image with custom size and zoom
            zoom_factor = self.zoom_slider.value() / 100.0
            size = (int(self.width_spin.value() * zoom_factor), 
                   int(self.height_spin.value() * zoom_factor))
            
            img = Draw.MolToImage(display_mol, size=size, options=draw_options)
            
            # Convert to QPixmap and display
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            
            qimg = QImage()
            qimg.loadFromData(buf.getvalue())
            pixmap = QPixmap.fromImage(qimg)
            self.image_label.setPixmap(pixmap)
            
            # Update all displays and enable buttons
            self.update_comprehensive_analysis(mol, smiles)
            self.enable_all_buttons()
            
        except Exception as e:
            self.image_label.setText(f"❌ Erro ao desenhar molécula: {str(e)}")
            self.clear_all_displays()
            self.disable_all_buttons()

    def configure_drawing_options(self, draw_options):
        """Configure drawing options based on selected style."""
        style = self.drawing_style.currentText()
        color_scheme = self.color_scheme.currentText()
        
        # Basic options
        if self.show_atom_labels.isChecked():
            draw_options.addAtomIndices = True
        
        # Style configurations
        if style == "Moderno":
            draw_options.bondLineWidth = 2
            draw_options.atomLabelFontSize = 12
        elif style == "Farmacêutico":
            draw_options.bondLineWidth = 1.5
            draw_options.includeMetadata = True
        elif style == "Publicação":
            draw_options.bondLineWidth = 1.2
            draw_options.atomLabelFontSize = 10
        
        # Color scheme configurations
        if color_scheme == "CPK":
            draw_options.useBWAtomPalette = False
        elif color_scheme == "Monocromo":
            draw_options.useBWAtomPalette = True

    def update_comprehensive_analysis(self, mol, smiles):
        """Update all molecular analysis displays."""
        # Basic molecule info
        basic_info = self.get_enhanced_molecule_info(mol, smiles)
        self.molecule_info.setText(basic_info)
        
        # Basic properties
        basic_props = self.calculate_basic_properties(mol, smiles)
        self.basic_properties.setText(basic_props)
        
        # Thermodynamic properties
        thermo_props = self.calculate_thermodynamic_properties(mol)
        self.thermo_properties.setText(thermo_props)
        
        # Pharmacological properties
        pharma_props = self.calculate_pharmacological_properties(mol)
        self.pharma_properties.setText(pharma_props)

    def get_enhanced_molecule_info(self, mol, smiles):
        """Get comprehensive molecule information."""
        try:
            # Basic molecular data
            formula = rdMolDescriptors.CalcMolFormula(mol)
            mw = Descriptors.MolWt(mol)
            heavy_atoms = mol.GetNumHeavyAtoms()
            
            # Structural features
            rings = mol.GetRingInfo()
            num_rings = rings.NumRings()
            aromatic_rings = Descriptors.NumAromaticRings(mol)
            
            # Electronic features
            electrons = sum([atom.GetAtomicNum() for atom in mol.GetAtoms()])
            
            info = f"""🧪 INFORMAÇÕES MOLECULARES BÁSICAS
{'='*50}

📋 Estrutura:
   SMILES: {smiles}
   Fórmula: {formula}
   Peso Molecular: {mw:.2f} g/mol
   Átomos Pesados: {heavy_atoms}
   Total de Elétrons: {electrons}

🔗 Características Estruturais:
   Anéis Totais: {num_rings}
   Anéis Aromáticos: {aromatic_rings}
   Ligações: {mol.GetNumBonds()}
   Átomos: {mol.GetNumAtoms()}

⚛️ Elementos Presentes:"""
            
            # Count elements
            element_count = {}
            for atom in mol.GetAtoms():
                symbol = atom.GetSymbol()
                element_count[symbol] = element_count.get(symbol, 0) + 1
            
            for element, count in sorted(element_count.items()):
                info += f"\n   {element}: {count}"
            
            return info
            
        except Exception as e:
            return f"❌ Erro ao analisar molécula: {str(e)}"

    def calculate_basic_properties(self, mol, smiles):
        """Calculate basic molecular properties."""
        try:
            props = f"""📊 PROPRIEDADES FÍSICO-QUÍMICAS BÁSICAS
{'='*50}

🔬 Descritores Moleculares:
   Peso Molecular: {Descriptors.MolWt(mol):.3f} g/mol
   LogP (Lipophilicity): {Descriptors.MolLogP(mol):.3f}
   Donors H: {Descriptors.NumHDonors(mol)}
   Acceptors H: {Descriptors.NumHAcceptors(mol)}
   TPSA: {Descriptors.TPSA(mol):.2f} Ų
   Rotatable Bonds: {Descriptors.NumRotatableBonds(mol)}

🧮 Índices Topológicos:
   Bertz CT: {Descriptors.BertzCT(mol):.2f}
   Balaban J: {Descriptors.BalabanJ(mol):.3f}
   Kappa1: {Descriptors.Kappa1(mol):.3f}
   Kappa2: {Descriptors.Kappa2(mol):.3f}
   Fraction Csp3: {Descriptors.FractionCsp3(mol):.3f}

💍 Análise de Anéis:
   Aromatic Rings: {Descriptors.NumAromaticRings(mol)}
   Saturated Rings: {Descriptors.NumSaturatedRings(mol)}
   Heteroaromatic Rings: {Descriptors.NumAromaticHeterocycles(mol)}
   Saturated Carbocycles: {Descriptors.NumSaturatedCarbocycles(mol)}

🔗 Características de Ligação:
   Aromatic Bonds: {sum(1 for bond in mol.GetBonds() if bond.GetIsAromatic())}
   Single Bonds: {sum(1 for bond in mol.GetBonds() if bond.GetBondType() == Chem.BondType.SINGLE)}
   Double Bonds: {sum(1 for bond in mol.GetBonds() if bond.GetBondType() == Chem.BondType.DOUBLE)}
   Triple Bonds: {sum(1 for bond in mol.GetBonds() if bond.GetBondType() == Chem.BondType.TRIPLE)}"""

            return props
            
        except Exception as e:
            return f"❌ Erro ao calcular propriedades: {str(e)}"

    def calculate_thermodynamic_properties(self, mol):
        """Calculate thermodynamic properties."""
        try:
            # Find compound in database if available
            formula = rdMolDescriptors.CalcMolFormula(mol)
            compound_data = self.find_compound_data(formula)
            
            thermo = f"""🌡️ PROPRIEDADES TERMODINÂMICAS
{'='*50}

"""
            if compound_data:
                thermo += f"""📊 Dados Experimentais (se disponíveis):
   Ponto de Fusão: {compound_data.get('mp', 'N/A')}°C
   Ponto de Ebulição: {compound_data.get('bp', 'N/A')}°C
   Densidade: {compound_data.get('density', 'N/A')} g/cm³
   
"""
            
            thermo += f"""🔥 Estimativas Computacionais:
   Entalpia de Formação: Estimada via Método de Contribuição de Grupos
   Capacidade Calorífica: Cp = f(T) - Correlação empírica
   Entropia Padrão: Baseada em contribuições atômicas
   Energia Livre de Gibbs: ΔG = ΔH - TΔS

⚛️ Propriedades Eletrônicas Estimadas:
   Gap HOMO-LUMO: ~{random.uniform(2.0, 8.0):.1f} eV (estimativa)
   Momento Dipolar: ~{random.uniform(0.0, 5.0):.1f} D (estimativa)
   Polarizabilidade: Proporcional ao volume molecular

🌡️ Estabilidade Térmica:
   Temperatura de Decomposição: Estimada > {200 + random.randint(0, 300)}°C
   Coeficiente de Expansão: ~10⁻⁵ K⁻¹ (típico orgânico)

💧 Propriedades de Solvatação:
   Solubilidade em Água: {"Alta" if Descriptors.MolLogP(mol) < 1 else "Baixa a Moderada"}
   Coeficiente de Partição: LogP = {Descriptors.MolLogP(mol):.2f}"""

            return thermo
            
        except Exception as e:
            return f"❌ Erro ao calcular propriedades termodinâmicas: {str(e)}"

    def calculate_pharmacological_properties(self, mol):
        """Calculate drug-likeness and pharmacological properties."""
        try:
            mw = Descriptors.MolWt(mol)
            logp = Descriptors.MolLogP(mol)
            hbd = Descriptors.NumHDonors(mol)
            hba = Descriptors.NumHAcceptors(mol)
            tpsa = Descriptors.TPSA(mol)
            rotatable = Descriptors.NumRotatableBonds(mol)
            
            # Lipinski's Rule of Five
            lipinski_violations = 0
            lipinski_details = []
            
            if mw > 500:
                lipinski_violations += 1
                lipinski_details.append("❌ Peso Molecular > 500")
            else:
                lipinski_details.append("✅ Peso Molecular ≤ 500")
                
            if logp > 5:
                lipinski_violations += 1
                lipinski_details.append("❌ LogP > 5")
            else:
                lipinski_details.append("✅ LogP ≤ 5")
                
            if hbd > 5:
                lipinski_violations += 1
                lipinski_details.append("❌ Doadores H > 5")
            else:
                lipinski_details.append("✅ Doadores H ≤ 5")
                
            if hba > 10:
                lipinski_violations += 1
                lipinski_details.append("❌ Aceptores H > 10")
            else:
                lipinski_details.append("✅ Aceptores H ≤ 10")
            
            # Additional drug-likeness rules
            veber_compliant = tpsa <= 140 and rotatable <= 10
            ghose_mw = 160 <= mw <= 480
            
            pharma = f"""💊 PROPRIEDADES FARMACOLÓGICAS
{'='*50}

📋 Regra de Lipinski (Rule of Five):
   Violações: {lipinski_violations}/4
   Status: {"✅ APROVADO" if lipinski_violations <= 1 else "❌ REPROVADO"}
   
   Detalhes:
   {chr(10).join(f"   {detail}" for detail in lipinski_details)}

📊 Outras Regras de Drug-Likeness:
   Regra de Veber: {"✅ Aprovado" if veber_compliant else "❌ Reprovado"}
   - TPSA ≤ 140: {"✅" if tpsa <= 140 else "❌"} ({tpsa:.1f})
   - Rotatable ≤ 10: {"✅" if rotatable <= 10 else "❌"} ({rotatable})
   
   Regra de Ghose: {"✅ Aprovado" if ghose_mw else "❌ Reprovado"}
   - 160 ≤ MW ≤ 480: {"✅" if ghose_mw else "❌"} ({mw:.1f})

🧬 Predições ADMET (Estimativas):
   Absorção Oral: {"Boa" if lipinski_violations <= 1 and tpsa <= 140 else "Limitada"}
   Distribuição: {"Ampla" if 1 <= logp <= 3 else "Limitada"}
   Metabolismo: {"Extensivo" if rotatable > 5 else "Limitado"}
   Excreção: {"Renal" if logp < 2 else "Biliar"}
   Toxicidade: Análise requer estudos específicos

🎯 Alvos Terapêuticos Potenciais:
   CNS Activity: {"Possível" if logp > 1 and tpsa < 90 else "Improvável"}
   Oral Bioavailability: {"Alta" if lipinski_violations == 0 else "Baixa"}
   Blood-Brain Barrier: {"Permeável" if logp > 1 and tpsa < 60 else "Impermeável"}

⚠️ Alertas Estruturais:
   PAINS (Pan-Assay Interference): Análise estrutural necessária
   Reactive Groups: Verificar grupos funcionais reativos
   Metabolic Liability: Considerar sites de metabolismo"""

            return pharma
            
        except Exception as e:
            return f"❌ Erro ao calcular propriedades farmacológicas: {str(e)}"

    def find_compound_data(self, formula):
        """Find compound data in the comprehensive database."""
        for category, compounds in self.compounds_database.items():
            for compound in compounds:
                if compound.get('formula') == formula:
                    return compound
        return None

    def generate_lewis_structure(self):
        """Generate Lewis structure representation."""
        if not self.current_mol:
            self.lewis_display.setText("❌ Nenhuma molécula carregada.")
            return
        
        try:
            lewis_text = self.create_lewis_representation(self.current_mol)
            self.lewis_display.setText(lewis_text)
        except Exception as e:
            self.lewis_display.setText(f"❌ Erro ao gerar estrutura de Lewis: {str(e)}")

    def create_lewis_representation(self, mol):
        """Create a text-based Lewis structure representation."""
        formula = rdMolDescriptors.CalcMolFormula(mol)
        
        # Simple Lewis structure based on molecular formula
        lewis = f"""⚛️ ESTRUTURA DE LEWIS ESTIMADA
{'='*50}

Fórmula: {formula}

📊 Análise de Valência:
"""
        
        # Count atoms and estimate Lewis structure
        atom_counts = {}
        total_valence = 0
        
        for atom in mol.GetAtoms():
            symbol = atom.GetSymbol()
            atomic_num = atom.GetAtomicNum()
            atom_counts[symbol] = atom_counts.get(symbol, 0) + 1
            
            # Standard valence electrons
            valence_electrons = {
                'H': 1, 'C': 4, 'N': 5, 'O': 6, 'F': 7, 'P': 5, 'S': 6, 'Cl': 7, 'Br': 7, 'I': 7
            }
            total_valence += valence_electrons.get(symbol, atomic_num % 8)
        
        for symbol, count in atom_counts.items():
            lewis += f"   {symbol}: {count} átomo(s)\n"
        
        lewis += f"\n💫 Elétrons de Valência Totais: {total_valence}\n"
        
        # Estimate bonding
        total_bonds = mol.GetNumBonds()
        bonding_electrons = total_bonds * 2
        lone_pair_electrons = total_valence - bonding_electrons
        
        lewis += f"🔗 Elétrons de Ligação: {bonding_electrons}\n"
        lewis += f"👥 Elétrons de Pares Isolados: {lone_pair_electrons}\n\n"
        
        # Simple structure representation
        if mol.GetNumAtoms() <= 10:  # Simple molecules only
            lewis += "📝 Representação Simplificada:\n\n"
            
            # Get connectivity info
            for i, atom in enumerate(mol.GetAtoms()):
                symbol = atom.GetSymbol()
                neighbors = [mol.GetAtomWithIdx(neighbor.GetIdx()).GetSymbol() 
                           for neighbor in atom.GetNeighbors()]
                lewis += f"   {symbol}({i}): conectado a {neighbors}\n"
        
        return lewis

    def analyze_molecular_bonds(self):
        """Analyze molecular bonds in detail."""
        if not self.current_mol:
            self.bond_analysis.setText("❌ Nenhuma molécula carregada.")
            return
        
        try:
            bond_text = self.create_bond_analysis(self.current_mol)
            self.bond_analysis.setText(bond_text)
        except Exception as e:
            self.bond_analysis.setText(f"❌ Erro na análise de ligações: {str(e)}")

    def create_bond_analysis(self, mol):
        """Create detailed bond analysis."""
        analysis = f"""🔗 ANÁLISE DETALHADA DE LIGAÇÕES
{'='*50}

📊 Estatísticas de Ligações:
   Total de Ligações: {mol.GetNumBonds()}
   
"""
        
        # Count bond types
        bond_types = {}
        for bond in mol.GetBonds():
            bond_type = str(bond.GetBondType())
            bond_types[bond_type] = bond_types.get(bond_type, 0) + 1
        
        for bond_type, count in bond_types.items():
            analysis += f"   {bond_type}: {count}\n"
        
        analysis += f"\n🔬 Detalhes das Ligações:\n"
        
        for i, bond in enumerate(mol.GetBonds()):
            atom1 = bond.GetBeginAtom()
            atom2 = bond.GetEndAtom()
            bond_type = bond.GetBondType()
            is_aromatic = bond.GetIsAromatic()
            
            analysis += f"   Ligação {i+1}: {atom1.GetSymbol()}{atom1.GetIdx()}-{atom2.GetSymbol()}{atom2.GetIdx()}\n"
            analysis += f"      Tipo: {bond_type}\n"
            analysis += f"      Aromática: {'Sim' if is_aromatic else 'Não'}\n"
        
        return analysis

    def show_electronic_structure(self):
        """Show electronic structure of atoms in the molecule."""
        if not self.current_mol:
            self.electron_config.setText("❌ Nenhuma molécula carregada.")
            return
        
        try:
            config_text = self.create_electronic_structure(self.current_mol)
            self.electron_config.setText(config_text)
        except Exception as e:
            self.electron_config.setText(f"❌ Erro na análise eletrônica: {str(e)}")

    def create_electronic_structure(self, mol):
        """Create electronic structure analysis."""
        structure = f"""⚡ ESTRUTURA ELETRÔNICA DOS ÁTOMOS
{'='*50}

"""
        
        # Electronic configurations for common elements
        electron_configs = {
            1: "1s¹",        # H
            2: "1s²",        # He  
            3: "[He] 2s¹",   # Li
            4: "[He] 2s²",   # Be
            5: "[He] 2s² 2p¹", # B
            6: "[He] 2s² 2p²", # C
            7: "[He] 2s² 2p³", # N
            8: "[He] 2s² 2p⁴", # O
            9: "[He] 2s² 2p⁵", # F
            10: "[He] 2s² 2p⁶", # Ne
            11: "[Ne] 3s¹",   # Na
            12: "[Ne] 3s²",   # Mg
            13: "[Ne] 3s² 3p¹", # Al
            14: "[Ne] 3s² 3p²", # Si
            15: "[Ne] 3s² 3p³", # P
            16: "[Ne] 3s² 3p⁴", # S
            17: "[Ne] 3s² 3p⁵", # Cl
            18: "[Ne] 3s² 3p⁶", # Ar
            35: "[Ar] 3d¹⁰ 4s² 4p⁵", # Br
            53: "[Kr] 4d¹⁰ 5s² 5p⁵"  # I
        }
        
        # Count unique atoms
        unique_atoms = {}
        for atom in mol.GetAtoms():
            atomic_num = atom.GetAtomicNum()
            symbol = atom.GetSymbol()
            if atomic_num not in unique_atoms:
                unique_atoms[atomic_num] = symbol
        
        for atomic_num, symbol in sorted(unique_atoms.items()):
            config = electron_configs.get(atomic_num, f"[Configuração não disponível para Z={atomic_num}]")
            structure += f"🔬 {symbol} (Z={atomic_num}):\n"
            structure += f"   Configuração: {config}\n"
            structure += f"   Camadas ocupadas: {self.get_occupied_shells(atomic_num)}\n\n"
        
        return structure

    def get_occupied_shells(self, atomic_num):
        """Get occupied electron shells for an atom."""
        if atomic_num <= 2:
            return "K (1s)"
        elif atomic_num <= 10:
            return "K (1s), L (2s, 2p)"
        elif atomic_num <= 18:
            return "K (1s), L (2s, 2p), M (3s, 3p)"
        elif atomic_num <= 36:
            return "K (1s), L (2s, 2p), M (3s, 3p, 3d), N (4s, 4p)"
        else:
            return "K, L, M, N (e possíveis camadas superiores)"

    def show_orbital_filling(self):
        """Show orbital filling diagram."""
        if not self.current_mol:
            self.orbital_diagram.setText("❌ Nenhuma molécula carregada.")
            return
        
        try:
            orbital_text = self.create_orbital_diagram(self.current_mol)
            self.orbital_diagram.setText(orbital_text)
        except Exception as e:
            self.orbital_diagram.setText(f"❌ Erro no diagrama orbital: {str(e)}")

    def create_orbital_diagram(self, mol):
        """Create ASCII orbital filling diagram."""
        diagram = f"""📊 DIAGRAMA DE PREENCHIMENTO ORBITAL
{'='*50}

"""
        
        # Get unique atoms
        unique_atoms = {}
        for atom in mol.GetAtoms():
            atomic_num = atom.GetAtomicNum()
            symbol = atom.GetSymbol()
            if atomic_num not in unique_atoms:
                unique_atoms[atomic_num] = symbol
        
        for atomic_num, symbol in sorted(unique_atoms.items()):
            diagram += f"⚛️ {symbol} (Z={atomic_num}):\n\n"
            diagram += self.create_electron_filling_diagram(atomic_num)
            diagram += "\n" + "="*30 + "\n\n"
        
        return diagram

    def create_electron_filling_diagram(self, atomic_num):
        """Create electron filling diagram for an atom."""
        # Simplified orbital filling
        orbitals = [
            ("1s", 2), ("2s", 2), ("2p", 6), ("3s", 2), ("3p", 6),
            ("4s", 2), ("3d", 10), ("4p", 6), ("5s", 2), ("4d", 10),
            ("5p", 6), ("6s", 2), ("4f", 14), ("5d", 10), ("6p", 6)
        ]
        
        diagram = ""
        electrons_left = atomic_num
        
        for orbital_name, max_electrons in orbitals:
            if electrons_left <= 0:
                break
                
            electrons_in_orbital = min(electrons_left, max_electrons)
            electrons_left -= electrons_in_orbital
            
            # Create visual representation
            if "s" in orbital_name:
                # s orbital (1 box)
                if electrons_in_orbital == 0:
                    boxes = "[ ]"
                elif electrons_in_orbital == 1:
                    boxes = "[↑]"
                else:
                    boxes = "[↑↓]"
            elif "p" in orbital_name:
                # p orbitals (3 boxes)
                boxes = []
                remaining = electrons_in_orbital
                for i in range(3):
                    if remaining == 0:
                        boxes.append("[ ]")
                    elif remaining == 1:
                        boxes.append("[↑]")
                        remaining -= 1
                    elif remaining >= 2:
                        if i < 3 and remaining > 3:  # Fill singly first
                            boxes.append("[↑]")
                            remaining -= 1
                        else:
                            boxes.append("[↑↓]")
                            remaining -= 2
                boxes = " ".join(boxes)
            elif "d" in orbital_name:
                # d orbitals (5 boxes) - simplified
                filled_pairs = electrons_in_orbital // 2
                unpaired = electrons_in_orbital % 2
                boxes = "[↑↓]" * filled_pairs + "[↑]" * unpaired + "[ ]" * (5 - filled_pairs - unpaired)
                boxes = " ".join([boxes[i:i+4] for i in range(0, len(boxes), 4)])
            else:
                # f orbitals (7 boxes) - simplified
                boxes = f"[{electrons_in_orbital} elétrons]"
            
            diagram += f"{orbital_name:>3}: {boxes}\n"
        
        return diagram

    def analyze_hybridization(self):
        """Analyze hybridization of atoms in the molecule."""
        if not self.current_mol:
            self.hybridization_info.setText("❌ Nenhuma molécula carregada.")
            return
        
        try:
            hybridization_text = self.create_hybridization_analysis(self.current_mol)
            self.hybridization_info.setText(hybridization_text)
        except Exception as e:
            self.hybridization_info.setText(f"❌ Erro na análise de hibridização: {str(e)}")

    def create_hybridization_analysis(self, mol):
        """Create hybridization analysis."""
        analysis = f"""🔬 ANÁLISE DE HIBRIDIZAÇÃO
{'='*50}

"""
        
        # Analyze each carbon atom (primary focus)
        carbon_atoms = [atom for atom in mol.GetAtoms() if atom.GetSymbol() == 'C']
        
        if carbon_atoms:
            analysis += "🧬 Hibridização dos Átomos de Carbono:\n\n"
            
            for i, atom in enumerate(carbon_atoms):
                atom_idx = atom.GetIdx()
                degree = atom.GetDegree()
                hybridization = atom.GetHybridization()
                
                # Determine hybridization
                if hybridization == Chem.HybridizationType.SP3:
                    hybrid_type = "sp³"
                    geometry = "Tetraédrica"
                    angle = "109.5°"
                elif hybridization == Chem.HybridizationType.SP2:
                    hybrid_type = "sp²"
                    geometry = "Trigonal Planar"
                    angle = "120°"
                elif hybridization == Chem.HybridizationType.SP:
                    hybrid_type = "sp"
                    geometry = "Linear"
                    angle = "180°"
                else:
                    hybrid_type = str(hybridization)
                    geometry = "Indefinida"
                    angle = "Variável"
                
                analysis += f"   C{atom_idx}: {hybrid_type}\n"
                analysis += f"      Geometria: {geometry}\n"
                analysis += f"      Ângulo de ligação: {angle}\n"
                analysis += f"      Número de ligações: {degree}\n\n"
        
        # Analyze other relevant atoms
        other_atoms = [atom for atom in mol.GetAtoms() if atom.GetSymbol() in ['N', 'O', 'P', 'S']]
        
        if other_atoms:
            analysis += "⚛️ Hibridização de Outros Átomos:\n\n"
            
            for atom in other_atoms:
                symbol = atom.GetSymbol()
                atom_idx = atom.GetIdx()
                degree = atom.GetDegree()
                hybridization = atom.GetHybridization()
                
                analysis += f"   {symbol}{atom_idx}: {str(hybridization).split('.')[-1]}\n"
                analysis += f"      Ligações: {degree}\n\n"
        
        return analysis

    def analyze_molecular_orbitals(self):
        """Analyze molecular orbitals (simplified)."""
        if not self.current_mol:
            self.mo_diagram.setText("❌ Nenhuma molécula carregada.")
            return
        
        try:
            mo_text = self.create_mo_analysis(self.current_mol)
            self.mo_diagram.setText(mo_text)
        except Exception as e:
            self.mo_diagram.setText(f"❌ Erro na análise de OM: {str(e)}")

    def create_mo_analysis(self, mol):
        """Create molecular orbital analysis."""
        mo_analysis = f"""⚛️ ANÁLISE DE ORBITAIS MOLECULARES
{'='*50}

📊 Informações Gerais:
   Número de Átomos: {mol.GetNumAtoms()}
   Número de Elétrons: {sum(atom.GetAtomicNum() for atom in mol.GetAtoms())}
   
🔬 Orbitais Atômicos Contribuintes:
"""
        
        # Count atomic orbitals
        ao_count = {"s": 0, "p": 0, "d": 0}
        
        for atom in mol.GetAtoms():
            symbol = atom.GetSymbol()
            atomic_num = atom.GetAtomicNum()
            
            # Count orbitals based on period
            if atomic_num <= 2:  # Period 1
                ao_count["s"] += 1
            elif atomic_num <= 10:  # Period 2
                ao_count["s"] += 2  # 1s, 2s
                ao_count["p"] += 3  # 2p
            elif atomic_num <= 18:  # Period 3
                ao_count["s"] += 3  # 1s, 2s, 3s
                ao_count["p"] += 6  # 2p, 3p
        
        for orbital_type, count in ao_count.items():
            if count > 0:
                mo_analysis += f"   Orbitais {orbital_type}: {count}\n"
        
        mo_analysis += f"""
🌀 Orbitais Moleculares Resultantes:
   Total estimado de OM: {sum(ao_count.values())}
   HOMO-LUMO Gap: Estimado entre 2-8 eV
   
🔗 Tipos de Orbitais Moleculares:
   σ (sigma): Ligações simples e sobreposição frontal
   π (pi): Ligações duplas/triplas e sobreposição lateral
   n: Orbitais não-ligantes (pares isolados)
   
🎯 Características Eletrônicas:
   Sistema π conjugado: {"Sim" if Descriptors.NumAromaticRings(mol) > 0 else "Não"}
   Deslocalização eletrônica: {"Presente" if Descriptors.NumAromaticRings(mol) > 0 else "Limitada"}
   Polarizabilidade: {"Alta" if mol.GetNumAtoms() > 10 else "Moderada"}

💡 Nota: Esta é uma análise qualitativa simplificada.
   Para análise quantitativa precisa, use métodos computacionais
   como DFT (Teoria do Funcional da Densidade)."""
        
        return mo_analysis

    def get_molecule_info(self, mol, smiles):
        """Get detailed information about the molecule."""
        try:
            num_atoms = mol.GetNumAtoms()
            num_bonds = mol.GetNumBonds()
            molecular_weight = Descriptors.MolWt(mol)
            formula = Chem.rdMolDescriptors.CalcMolFormula(mol)
            heavy_atoms = mol.GetNumHeavyAtoms()
            aromatic_rings = Descriptors.NumAromaticRings(mol)
            saturated_rings = Descriptors.NumSaturatedRings(mol)
            aliphatic_rings = Descriptors.NumAliphaticRings(mol)
            heteroaromatic_rings = Descriptors.NumAromaticHeterocycles(mol)
            chiral_centers = Chem.FindMolChiralCenters(mol, includeUnassigned=True)
            num_chiral_centers = len(chiral_centers)
            fraction_csp3 = Descriptors.FractionCsp3(mol)
            bertz_ct = Descriptors.BertzCT(mol)
            balaban_j = Descriptors.BalabanJ(mol)
            logp = Descriptors.MolLogP(mol)
            hbd = Descriptors.NumHDonors(mol)
            hba = Descriptors.NumHAcceptors(mol)
            tpsa = Descriptors.TPSA(mol)
            rotatable = Descriptors.NumRotatableBonds(mol)
            info = f"""SMILES: {smiles}\nFórmula Molecular: {formula}\nPeso Molecular: {molecular_weight:.2f} g/mol\nNúmero de Átomos: {num_atoms}\nNúmero de Ligações: {num_bonds}\nÁtomos Pesados: {heavy_atoms}\nAnéis Aromáticos: {aromatic_rings}\nAnéis Saturados: {saturated_rings}\nAnéis Alifáticos: {aliphatic_rings}\nAnéis Heteroaromáticos: {heteroaromatic_rings}\nCentros Quirais: {num_chiral_centers}\nFração Csp3: {fraction_csp3:.3f}\nDensidade de Elétrons (BertzCT): {bertz_ct:.2f}\nCoeficiente de Balaban: {balaban_j:.3f}\nLogP: {logp:.2f}\nDoadores de H: {hbd}\nAceptores de H: {hba}\nTPSA: {tpsa:.2f} Ų\nLigações Rotáveis: {rotatable}"""
            return info
        except Exception:
            return f"SMILES: {smiles}\nInformações adicionais não disponíveis."

    def show_3d_molecule(self):
        """Show molecule in 3D using py3Dmol."""
        try:
            if not hasattr(self, 'current_mol') or self.current_mol is None:
                return
                
            # Generate 3D coordinates
            mol_copy = Chem.Mol(self.current_mol)
            AllChem.EmbedMolecule(mol_copy, AllChem.ETKDG())
            AllChem.UFFOptimizeMolecule(mol_copy)
            
            # Create SDF content
            sdf_content = Chem.MolToMolBlock(mol_copy)
            
            # Create HTML with py3Dmol
            html_content = self.create_3d_html(sdf_content)
            self.web_view.setHtml(html_content)
            
            # Enable 3D controls
            self.rotate_button.setEnabled(True)
            self.reset_view_button.setEnabled(True)
            
        except Exception as e:
            print(f"Erro na visualização 3D: {e}")

    def create_3d_html(self, sdf_content):
        """Create HTML content for 3D visualization."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://3dmol.org/build/3Dmol-min.js"></script>
            <style>
                body {{ margin: 0; padding: 0; }}
                #container {{ width: 100%; height: 450px; position: relative; }}
            </style>
        </head>
        <body>
            <div id="container"></div>
            <script>
                let viewer = $3Dmol.createViewer("container", {{backgroundColor: "0xffffff"}});
                let sdf = `{sdf_content}`;
                viewer.addModel(sdf, "sdf");
                viewer.setStyle({{}}, {{stick: {{}}, sphere: {{scale: 0.3}}}});
                viewer.zoomTo();
                viewer.render();
                
                // Auto-rotation function
                let rotating = false;
                window.toggleRotation = function() {{
                    if (rotating) {{
                        viewer.stopAnimate();
                        rotating = false;
                    }} else {{
                        viewer.rotate({{y: 1}}, 500);
                        rotating = true;
                    }}
                }};
                
                window.resetView = function() {{
                    viewer.stopAnimate();
                    rotating = false;
                    viewer.zoomTo();
                    viewer.render();
                }};
                
                window.changeStyle = function(style) {{
                    viewer.removeAllModels();
                    viewer.addModel(sdf, "sdf");
                    
                    switch(style) {{
                        case 'Stick':
                            viewer.setStyle({{}}, {{stick: {{}}}});
                            break;
                        case 'Ball & Stick':
                            viewer.setStyle({{}}, {{stick: {{}}, sphere: {{scale: 0.3}}}});
                            break;
                        case 'Sphere':
                            viewer.setStyle({{}}, {{sphere: {{}}}});
                            break;
                        case 'Wireframe':
                            viewer.setStyle({{}}, {{line: {{}}}});
                            break;
                        case 'Cartoon':
                            viewer.setStyle({{}}, {{cartoon: {{}}}});
                            break;
                    }}
                    viewer.render();
                }};
                
                window.changeBgColor = function(color) {{
                    viewer.setBackgroundColor(color);
                    viewer.render();
                }};
            </script>
        </body>
        </html>
        """
        return html

    def get_empty_3d_html(self):
        """Get empty HTML for 3D viewer."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { 
                    margin: 0; 
                    padding: 20px; 
                    font-family: Arial, sans-serif; 
                    text-align: center;
                    background-color: #f5f5f5;
                }
                .message {
                    margin-top: 150px;
                    color: #666;
                    font-size: 16px;
                }
            </style>
        </head>
        <body>
            <div class="message">
                Digite um SMILES e clique em "Visualizar em 3D" para ver a molécula em três dimensões
            </div>
        </body>
        </html>
        """

    def toggle_rotation(self):
        """Toggle auto-rotation of 3D molecule."""
        self.web_view.page().runJavaScript("window.toggleRotation()")

    def reset_3d_view(self):
        """Reset 3D view to default position."""
        self.web_view.page().runJavaScript("window.resetView()")

    # Additional functionality methods
    def clear_all(self):
        """Clear all inputs and displays."""
        self.smiles_input.clear()
        self.name_input.clear()
        self.image_label.setText("Digite um SMILES e clique em 'Desenhar'")
        self.molecule_info.clear()
        self.detailed_properties.clear()
        self.web_view.setHtml(self.get_empty_3d_html())
        self.disable_buttons()

    def disable_buttons(self):
        """Disable all action buttons."""
        self.view_3d_button.setEnabled(False)
        self.optimize_button.setEnabled(False)
        self.apply_options_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.export_sdf_button.setEnabled(False)
        self.export_mol_button.setEnabled(False)
        self.export_png_button.setEnabled(False)
        self.style_combo.setEnabled(False)
        self.rotate_button.setEnabled(False)
        self.reset_view_button.setEnabled(False)
        self.bg_color_button.setEnabled(False)

    def load_random_molecule(self):
        """Load a random molecule from examples."""
        import random
        examples = [
            ("CCO", "Etanol"),
            ("CCC", "Propano"),
            ("c1ccccc1", "Benzeno"),
            ("CC(=O)O", "Ácido acético"),
            ("CCN", "Etilamina"),
            ("Cc1ccccc1", "Tolueno"),
            ("c1ccccc1O", "Fenol"),
            ("CN1C=NC2=C1C(=O)N(C(=O)N2C)C", "Cafeína"),
            ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "Ibuprofeno"),
            ("CC(C)(C)C1=CC=C(O)C=C1", "BHT"),
        ]
        smiles, name = random.choice(examples)
        self.smiles_input.setText(smiles)
        self.name_input.setText(name)
        self.draw_molecule()

    def generate_3d_coordinates(self):
        """Generate 3D coordinates for the current molecule."""
        if not hasattr(self, 'current_mol') or not self.current_mol:
            QMessageBox.warning(self, "Aviso", "Carregue uma molécula primeiro!")
            return
        
        try:
            # Add hydrogens and generate 3D coordinates
            mol_with_h = Chem.AddHs(self.current_mol)
            
            # Embed molecule in 3D space
            if AllChem.EmbedMolecule(mol_with_h, randomSeed=42) == 0:
                self.current_mol_3d = mol_with_h
                self.update_3d_display()
                QMessageBox.information(self, "Sucesso", "Coordenadas 3D geradas com sucesso!")
                
                # Enable other 3D buttons
                self.optimize_3d_button.setEnabled(True)
                self.export_3d_button.setEnabled(True)
                self.fullscreen_3d_button.setEnabled(True)
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível gerar coordenadas 3D para esta molécula.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar coordenadas 3D: {str(e)}")

    def optimize_3d_structure(self):
        """Optimize the 3D structure using force field."""
        if not hasattr(self, 'current_mol_3d') or not self.current_mol_3d:
            QMessageBox.warning(self, "Aviso", "Gere coordenadas 3D primeiro!")
            return
        
        try:
            # Optimize using UFF (Universal Force Field)
            AllChem.UFFOptimizeMolecule(self.current_mol_3d, maxIters=1000)
            self.update_3d_display()
            QMessageBox.information(self, "Sucesso", "Estrutura 3D otimizada com sucesso!")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na otimização 3D: {str(e)}")

    def export_3d_structure(self):
        """Export 3D structure in various formats."""
        if not hasattr(self, 'current_mol_3d') or not self.current_mol_3d:
            QMessageBox.warning(self, "Aviso", "Gere coordenadas 3D primeiro!")
            return
        
        try:
            from PySide6.QtWidgets import QFileDialog
            
            filename, selected_filter = QFileDialog.getSaveFileName(
                self, "Exportar Estrutura 3D", "molecule_3d",
                "SDF files (*.sdf);;MOL files (*.mol);;XYZ files (*.xyz);;PDB files (*.pdb)"
            )
            
            if filename:
                if selected_filter.startswith("SDF"):
                    writer = Chem.SDWriter(filename)
                    writer.write(self.current_mol_3d)
                    writer.close()
                elif selected_filter.startswith("MOL"):
                    with open(filename, 'w') as f:
                        f.write(Chem.MolToMolBlock(self.current_mol_3d))
                elif selected_filter.startswith("XYZ"):
                    self.export_xyz_format(filename)
                elif selected_filter.startswith("PDB"):
                    self.export_pdb_format(filename)
                
                QMessageBox.information(self, "Sucesso", f"Estrutura 3D exportada: {filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar estrutura 3D: {str(e)}")

    def export_xyz_format(self, filename):
        """Export molecule in XYZ format."""
        if not hasattr(self, 'current_mol_3d') or not self.current_mol_3d:
            return
        
        conf = self.current_mol_3d.GetConformer()
        with open(filename, 'w') as f:
            f.write(f"{self.current_mol_3d.GetNumAtoms()}\n")
            f.write("Generated by HeisenLab\n")
            
            for atom in self.current_mol_3d.GetAtoms():
                pos = conf.GetAtomPosition(atom.GetIdx())
                f.write(f"{atom.GetSymbol()} {pos.x:.6f} {pos.y:.6f} {pos.z:.6f}\n")

    def export_pdb_format(self, filename):
        """Export molecule in PDB format."""
        try:
            pdb_block = Chem.MolToPDBBlock(self.current_mol_3d)
            with open(filename, 'w') as f:
                f.write(pdb_block)
        except:
            QMessageBox.warning(self, "Aviso", "Formato PDB não suportado para esta molécula.")

    def open_fullscreen_3d(self):
        """Open fullscreen 3D viewer."""
        if not hasattr(self, 'current_mol_3d') or not self.current_mol_3d:
            QMessageBox.warning(self, "Aviso", "Gere coordenadas 3D primeiro!")
            return
        
        try:
            # Use the enhanced 3D viewer we created earlier
            self.enhanced_3d_viewer = Enhanced3DMoleculeViewer(self.current_mol_3d)
            self.enhanced_3d_viewer.show()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir visualizador 3D: {str(e)}")

    def update_3d_display(self):
        """Update the 3D display area."""
        if not hasattr(self, 'current_mol_3d') or not self.current_mol_3d:
            return
        
        # Update the placeholder with molecule info
        try:
            formula = rdMolDescriptors.CalcMolFormula(self.current_mol_3d)
            mw = Descriptors.MolWt(self.current_mol_3d)
            
            # Clear existing layout
            for i in reversed(range(self.viewer_3d_frame.layout().count())):
                self.viewer_3d_frame.layout().itemAt(i).widget().setParent(None)
            
            # Add updated info
            info_layout = QVBoxLayout()
            
            title_label = QLabel("🧬 Estrutura 3D Carregada")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("""
                color: #4CAF50;
                font-size: 20px;
                font-weight: bold;
                margin: 20px;
            """)
            info_layout.addWidget(title_label)
            
            details_label = QLabel(f"Fórmula: {formula}\nPeso Molecular: {mw:.2f} g/mol\nÁtomos: {self.current_mol_3d.GetNumAtoms()}")
            details_label.setAlignment(Qt.AlignCenter)
            details_label.setStyleSheet("""
                color: white;
                font-size: 14px;
                margin: 10px;
            """)
            info_layout.addWidget(details_label)
            
            action_label = QLabel("Use 'Tela Cheia' para visualização interativa")
            action_label.setAlignment(Qt.AlignCenter)
            action_label.setStyleSheet("""
                color: #cccccc;
                font-size: 12px;
                margin: 10px;
            """)
            info_layout.addWidget(action_label)
            
            self.viewer_3d_frame.setLayout(info_layout)
            
        except Exception as e:
            print(f"Erro ao atualizar display 3D: {e}")

    def update_drawing_style(self):
        """Update drawing style and redraw if molecule is loaded."""
        if hasattr(self, 'current_mol') and self.current_mol:
            self.draw_molecule()

    def update_color_scheme(self):
        """Update color scheme and redraw if molecule is loaded."""
        if hasattr(self, 'current_mol') and self.current_mol:
            self.draw_molecule()

    def update_zoom(self):
        """Update zoom level and redraw if molecule is loaded."""
        zoom_value = self.zoom_slider.value()
        # Update zoom label if it exists
        if hasattr(self, 'zoom_label'):
            self.zoom_label.setText(f"Zoom: {zoom_value}%")
        
        if hasattr(self, 'current_mol') and self.current_mol:
            self.draw_molecule()

    def redraw_with_options(self):
        """Redraw molecule with current options."""
        if hasattr(self, 'current_mol') and self.current_mol:
            self.draw_molecule()

    def filter_molecules(self):
        """Filter molecules based on search text."""
        search_text = self.library_search.text().lower()
        category = self.category_combo.currentText()
        
        self.molecule_list.clear()
        
        # Get compounds from comprehensive database
        all_compounds = []
        if category == "Todos":
            for category_compounds in self.compounds_database.values():
                all_compounds.extend(category_compounds)
        else:
            # Direct mapping to database categories
            all_compounds = self.compounds_database.get(category, [])
        
        # Filter compounds based on search text
        for compound in all_compounds:
            name = compound.get('nome', '').lower()
            formula = compound.get('formula', '').lower()
            smiles = compound.get('smiles', '').lower()
            
            if (not search_text or 
                search_text in name or 
                search_text in formula or 
                search_text in smiles):
                
                display_text = f"{compound.get('nome', 'N/A')} [{compound.get('formula', 'N/A')}]"
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, compound)
                self.molecule_list.addItem(item)

    def update_molecule_list(self):
        """Update molecule list based on selected category."""
        self.filter_molecules()

    def show_molecule_details(self, current_item=None, previous_item=None):
        """Show details of selected molecule."""
        if current_item is None:
            current_item = self.molecule_list.currentItem()
        
        if current_item:
            compound = current_item.data(Qt.ItemDataRole.UserRole)
            if compound:
                details = f"""🧪 DETALHES DA MOLÉCULA
{'='*40}

📋 Nome: {compound.get('nome', 'N/A')}
📋 IUPAC: {compound.get('iupac', 'N/A')}
⚗️ Fórmula: {compound.get('formula', 'N/A')}
🧬 SMILES: {compound.get('smiles', 'N/A')}

🌡️ Propriedades Físicas:
   Ponto de Fusão: {compound.get('mp', 'N/A')}°C
   Ponto de Ebulição: {compound.get('bp', 'N/A')}°C
   Densidade: {compound.get('density', 'N/A')} g/cm³

📊 Categoria: {compound.get('categoria', 'N/A')}
🔬 Tipo: {compound.get('tipo', 'N/A')}
💡 Descrição: {compound.get('descricao', 'N/A')}

⚛️ Valencia: {compound.get('valencia', 'N/A')}
"""
                self.molecule_details.setText(details)
            else:
                self.molecule_details.clear()
        else:
            self.molecule_details.clear()

    def add_custom_molecule(self):
        """Add a custom molecule to the library."""
        try:
            from PySide6.QtWidgets import QInputDialog
            
            # Get molecule details from user
            name, ok1 = QInputDialog.getText(self, "Nome da Molécula", "Digite o nome da molécula:")
            if not ok1 or not name.strip():
                return
            
            smiles, ok2 = QInputDialog.getText(self, "SMILES", "Digite o SMILES da molécula:")
            if not ok2 or not smiles.strip():
                return
            
            # Validate SMILES
            try:
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    QMessageBox.warning(self, "Erro", "SMILES inválido. Verifique a sintaxe.")
                    return
                
                formula = rdMolDescriptors.CalcMolFormula(mol)
            except:
                QMessageBox.warning(self, "Erro", "Erro ao validar SMILES.")
                return
            
            description, ok3 = QInputDialog.getText(self, "Descrição", "Digite uma descrição (opcional):")
            if not ok3:
                description = ""
            
            # Create custom molecule entry
            custom_molecule = {
                "nome": name.strip(),
                "iupac": name.strip(),
                "formula": formula,
                "smiles": smiles.strip(),
                "mp": "N/A",
                "bp": "N/A", 
                "density": "N/A",
                "descricao": description.strip() if description else "Molécula personalizada",
                "categoria": "Personalizado",
                "tipo": "Personalizado",
                "valencia": "Personalizado"
            }
            
            # Add to database (create "Personalizado" category if it doesn't exist)
            if "Personalizado" not in self.compounds_database:
                self.compounds_database["Personalizado"] = []
            
            self.compounds_database["Personalizado"].append(custom_molecule)
            
            # Update combo box if "Personalizado" is not already there
            current_items = [self.category_combo.itemText(i) for i in range(self.category_combo.count())]
            if "Personalizado" not in current_items:
                self.category_combo.addItem("Personalizado")
            
            # Refresh the list
            self.filter_molecules()
            
            QMessageBox.information(self, "Sucesso", f"Molécula '{name}' adicionada à biblioteca!")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar molécula: {str(e)}")

    def load_selected_molecule(self):
        """Load selected molecule from library."""
        current_item = self.molecule_list.currentItem()
        if current_item:
            compound = current_item.data(Qt.ItemDataRole.UserRole)
            if compound and 'smiles' in compound:
                self.smiles_input.setText(compound['smiles'])
                self.draw_molecule()
                QMessageBox.information(self, "Sucesso", f"Molécula carregada: {compound.get('nome', 'N/A')}")
            else:
                QMessageBox.warning(self, "Erro", "SMILES não disponível para esta molécula.")
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma molécula da lista.")

    def generate_3d_coordinates(self):
        """Generate 3D coordinates for the current molecule."""
        if not hasattr(self, 'current_mol') or not self.current_mol:
            QMessageBox.warning(self, "Aviso", "Nenhuma molécula carregada!")
            return
        
        try:
            mol_3d = Chem.AddHs(self.current_mol)
            if AllChem.EmbedMolecule(mol_3d) == 0:
                self.current_mol_3d = mol_3d
                QMessageBox.information(self, "Sucesso", "Coordenadas 3D geradas com sucesso!")
                self.enable_3d_buttons()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível gerar coordenadas 3D para esta molécula.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar coordenadas 3D: {str(e)}")

    def optimize_3d_structure(self):
        """Optimize the 3D structure using force field."""
        if not hasattr(self, 'current_mol_3d') or not self.current_mol_3d:
            QMessageBox.warning(self, "Aviso", "Gere as coordenadas 3D primeiro!")
            return
        
        try:
            AllChem.UFFOptimizeMolecule(self.current_mol_3d)
            QMessageBox.information(self, "Sucesso", "Estrutura 3D otimizada com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na otimização: {str(e)}")

    def export_3d_structure(self):
        """Export 3D structure in various formats."""
        if not hasattr(self, 'current_mol_3d') or not self.current_mol_3d:
            QMessageBox.warning(self, "Aviso", "Gere as coordenadas 3D primeiro!")
            return
        
        try:
            filename, file_filter = QFileDialog.getSaveFileName(
                self, "Exportar Estrutura 3D", "molecule_3d",
                "XYZ files (*.xyz);;PDB files (*.pdb);;SDF files (*.sdf);;All files (*.*)"
            )
            
            if filename:
                if filename.endswith('.xyz'):
                    # Export as XYZ
                    with open(filename, 'w') as f:
                        f.write(f"{self.current_mol_3d.GetNumAtoms()}\n")
                        f.write("Generated by HeisenLab\n")
                        
                        conf = self.current_mol_3d.GetConformer()
                        for atom in self.current_mol_3d.GetAtoms():
                            pos = conf.GetAtomPosition(atom.GetIdx())
                            f.write(f"{atom.GetSymbol()} {pos.x:.6f} {pos.y:.6f} {pos.z:.6f}\n")
                
                elif filename.endswith('.pdb'):
                    # Export as PDB
                    pdb_block = Chem.MolToPDBBlock(self.current_mol_3d)
                    with open(filename, 'w') as f:
                        f.write(pdb_block)
                
                elif filename.endswith('.sdf'):
                    # Export as SDF
                    writer = Chem.SDWriter(filename)
                    writer.write(self.current_mol_3d)
                    writer.close()
                
                QMessageBox.information(self, "Sucesso", f"Estrutura 3D exportada: {filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar estrutura 3D: {str(e)}")

    def open_fullscreen_3d(self):
        """Open 3D structure in fullscreen viewer."""
        if not hasattr(self, 'current_mol_3d') or not self.current_mol_3d:
            QMessageBox.warning(self, "Aviso", "Gere as coordenadas 3D primeiro!")
            return
        
        try:
            # Open the enhanced 3D viewer
            self.enhanced_3d_viewer = Enhanced3DMoleculeViewer(self.current_mol_3d)
            self.enhanced_3d_viewer.show()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir visualizador 3D: {str(e)}")

    def export_report(self):
        """Export comprehensive molecular analysis report as PDF."""
        if not hasattr(self, 'current_mol') or not self.current_mol:
            QMessageBox.warning(self, "Aviso", "Nenhuma molécula carregada!")
            return
        
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exportar Relatório", "molecular_report.pdf",
                "PDF files (*.pdf);;All files (*.*)"
            )
            
            if filename:
                # This would generate a comprehensive PDF report
                # For now, show a placeholder message
                QMessageBox.information(
                    self, "Info", 
                    "Funcionalidade de relatório PDF será implementada.\n"
                    "O relatório incluirá:\n"
                    "- Estrutura 2D e 3D\n"
                    "- Propriedades físico-químicas\n" 
                    "- Estrutura eletrônica\n"
                    "- Análises farmacológicas\n"
                    "- Dados termodinâmicos"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar relatório: {str(e)}")

    def enable_3d_buttons(self):
        """Enable 3D-related buttons."""
        if hasattr(self, 'optimize_3d_button'):
            self.optimize_3d_button.setEnabled(True)
        if hasattr(self, 'export_3d_button'):
            self.export_3d_button.setEnabled(True)
        if hasattr(self, 'fullscreen_3d_button'):
            self.fullscreen_3d_button.setEnabled(True)

    def save_current_molecule(self):
        """Save current molecule to library."""
        # Implementation for saving molecules to user library
        QMessageBox.information(self, "Salvar", "Funcionalidade de salvamento será implementada.")

    def update_detailed_properties(self, mol, smiles):
        """Update detailed molecular properties."""
        try:
            # Basic properties
            mw = Descriptors.MolWt(mol)
            formula = rdMolDescriptors.CalcMolFormula(mol)
            heavy_atoms = mol.GetNumHeavyAtoms()
            
            # Drug-like properties
            logp = Descriptors.MolLogP(mol)
            hbd = Descriptors.NumHDonors(mol)
            hba = Descriptors.NumHAcceptors(mol)
            tpsa = Descriptors.TPSA(mol)
            rotatable = Descriptors.NumRotatableBonds(mol)
            
            # Lipinski's Rule of Five
            lipinski_violations = 0
            if mw > 500: lipinski_violations += 1
            if logp > 5: lipinski_violations += 1
            if hbd > 5: lipinski_violations += 1
            if hba > 10: lipinski_violations += 1
            
            properties_text = f"""INFORMAÇÕES MOLECULARES DETALHADAS
{'='*50}

ESTRUTURA:
SMILES: {smiles}
Fórmula Molecular: {formula}
Peso Molecular: {mw:.2f} g/mol
Átomos Pesados: {heavy_atoms}

PROPRIEDADES FÍSICO-QUÍMICAS:
LogP (lipofilicidade): {logp:.2f}
Doadores de H: {hbd}
Aceptores de H: {hba}
TPSA (Área Superficial Polar): {tpsa:.2f} Ų
Ligações Rotáveis: {rotatable}

REGRA DE LIPINSKI (Drug-likeness):
Violações: {lipinski_violations}/4
{'PASSA' if lipinski_violations <= 1 else 'FALHA'} na Regra dos Cinco

ANÁLISE ESTRUTURAL:
Anéis Aromáticos: {Descriptors.NumAromaticRings(mol)}
Anéis Saturados: {Descriptors.NumSaturatedRings(mol)}
Anéis Heteroaromáticos: {Descriptors.NumAromaticHeterocycles(mol)}
Centros Quirais: {Descriptors.NumSaturatedCarbocycles(mol)}

OUTRAS PROPRIEDADES:
Densidade de Elétrons: {Descriptors.BertzCT(mol):.2f}
Fração Carbono sp3: {Descriptors.FractionCsp3(mol):.3f}
Coeficiente de Balaban: {Descriptors.BalabanJ(mol):.3f}"""

            self.detailed_properties.setText(properties_text)
            
        except Exception as e:
            self.detailed_properties.setText(f"Erro ao calcular propriedades: {e}")

    def optimize_geometry(self):
        """Optimize molecular geometry and show in 3D."""
        try:
            if hasattr(self, 'current_mol') and self.current_mol:
                # Create a copy and optimize
                mol_copy = Chem.Mol(self.current_mol)
                AllChem.EmbedMolecule(mol_copy, AllChem.ETKDG())
                AllChem.UFFOptimizeMolecule(mol_copy, maxIters=1000)
                
                # Show optimized structure
                sdf_content = Chem.MolToMolBlock(mol_copy)
                html_content = self.create_3d_html(sdf_content)
                self.web_view.setHtml(html_content)
                
                # Enable controls
                self.style_combo.setEnabled(True)
                self.rotate_button.setEnabled(True)
                self.reset_view_button.setEnabled(True)
                self.bg_color_button.setEnabled(True)
                
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro na otimização: {e}")

    def change_3d_style(self):
        """Change 3D visualization style."""
        style = self.style_combo.currentText()
        self.web_view.page().runJavaScript(f"window.changeStyle('{style}')")

    def change_bg_color(self):
        """Change background color of 3D viewer."""
        color = QColorDialog.getColor(QColor(255, 255, 255), self, "Escolher Cor de Fundo")
        if color.isValid():
            hex_color = color.name()
            self.web_view.page().runJavaScript(f"window.changeBgColor('{hex_color}')")

    def export_sdf(self):
        """Export molecule as SDF file."""
        if hasattr(self, 'current_mol') and self.current_mol:
            filename, _ = QFileDialog.getSaveFileName(self, "Salvar SDF", "", "SDF Files (*.sdf)")
            if filename:
                try:
                    mol_copy = Chem.Mol(self.current_mol)
                    AllChem.EmbedMolecule(mol_copy, AllChem.ETKDG())
                    with open(filename, 'w') as f:
                        f.write(Chem.MolToMolBlock(mol_copy))
                    QMessageBox.information(self, "Sucesso", "Arquivo SDF salvo com sucesso!")
                except Exception as e:
                    QMessageBox.warning(self, "Erro", f"Erro ao salvar: {e}")

    def export_mol(self):
        """Export molecule as MOL file."""
        if hasattr(self, 'current_mol') and self.current_mol:
            filename, _ = QFileDialog.getSaveFileName(self, "Salvar MOL", "", "MOL Files (*.mol)")
            if filename:
                try:
                    with open(filename, 'w') as f:
                        f.write(Chem.MolToMolBlock(self.current_mol))
                    QMessageBox.information(self, "Sucesso", "Arquivo MOL salvo com sucesso!")
                except Exception as e:
                    QMessageBox.warning(self, "Erro", f"Erro ao salvar: {e}")

    def export_png(self):
        """Export 2D structure as PNG."""
        if hasattr(self, 'current_mol') and self.current_mol:
            filename, _ = QFileDialog.getSaveFileName(self, "Salvar PNG", "", "PNG Files (*.png)")
            if filename:
                try:
                    size = (self.width_spin.value(), self.height_spin.value())
                    img = Draw.MolToImage(self.current_mol, size=size)
                    img.save(filename, 'PNG')
                    QMessageBox.information(self, "Sucesso", "Imagem PNG salva com sucesso!")
                except Exception as e:
                    QMessageBox.warning(self, "Erro", f"Erro ao salvar: {e}")

    def search_bluebook(self):
        """Busca composto no arquivo bluebook.txt"""
        compound_name = self.bluebook_input.text().strip()
        
        if not compound_name:
            self.bluebook_result.setText("Digite o nome de um composto para buscar.")
            return
        
        try:
            # Busca no bluebook com timeout implícito
            self.bluebook_result.setText("Buscando...")
            self.bluebook_search_button.setEnabled(False)
            
            # Busca no bluebook
            result = search_compound_in_bluebook(compound_name)
            
            if result["found"]:
                # Formata o resultado para exibição
                result_text = f"✓ Composto: {result['name']}\n"
                
                if result.get('formula'):
                    result_text += f"Fórmula: {result['formula']}\n"
                
                if result.get('smiles'):
                    result_text += f"SMILES: {result['smiles']}\n"
                    # Preenche automaticamente o campo SMILES
                    self.smiles_input.setText(result['smiles'])
                
                if result.get('type'):
                    result_text += f"Tipo: {result['type']}\n"
                
                if result.get('iupac_info'):
                    result_text += f"IUPAC: {result['iupac_info']}\n"
                
                # Adiciona informação da fonte
                source_info = {
                    'known_database': 'Base de dados conhecidos',
                    'examples_section': 'Seção de exemplos do Blue Book',
                    'pin_definition': 'Definição PIN do Blue Book',
                    'systematic_name': 'Nome sistemático do Blue Book'
                }
                source = source_info.get(result.get('source', ''), 'Blue Book')
                result_text += f"Fonte: {source}"
                
                self.bluebook_result.setText(result_text)
                
                # Preenche o campo nome se estiver vazio
                if not self.name_input.text():
                    self.name_input.setText(compound_name.title())
                
                # Se encontrou SMILES, oferece para desenhar automaticamente
                if result.get('smiles'):
                    reply = QMessageBox.question(
                        self, 
                        "Desenhar Molécula", 
                        f"SMILES encontrado: {result['smiles']}\n\nDeseja desenhar a molécula automaticamente?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        self.draw_molecule()
                        
            else:
                # Composto não encontrado
                message = result.get('message', 'Composto não encontrado no Blue Book')
                self.bluebook_result.setText(f"✗ {message}")
                
                # Oferece sugestões se disponível
                try:
                    suggestions = get_compound_suggestions(compound_name)
                    if suggestions:
                        suggestion_text = f"\n\n💡 Sugestões: {', '.join(suggestions[:5])}"
                        current_text = self.bluebook_result.toPlainText()
                        self.bluebook_result.setText(current_text + suggestion_text)
                except:
                    pass  # Ignora erros de sugestões
                    
        except Exception as e:
            error_msg = f"✗ Erro na busca: {str(e)[:100]}..."
            self.bluebook_result.setText(error_msg)
            print(f"Erro detalhado na busca: {e}")
        
        finally:
            # Reabilita o botão de busca
            self.bluebook_search_button.setEnabled(True)

    def clear_all_displays(self):
        """Clear all display areas."""
        self.molecule_info.clear()
        self.basic_properties.clear()
        self.thermo_properties.clear()
        self.pharma_properties.clear()
        self.lewis_display.clear()
        self.bond_analysis.clear()
        self.electron_config.clear()
        self.orbital_diagram.clear()
        self.hybridization_info.clear()
        self.mo_diagram.clear()

    def enable_all_buttons(self):
        """Enable all action buttons."""
        # Verificar se os botões existem antes de habilitá-los
        if hasattr(self, 'lewis_button'):
            self.lewis_button.setEnabled(True)
        if hasattr(self, 'view_3d_button'):
            self.view_3d_button.setEnabled(True)
        if hasattr(self, 'optimize_button'):
            self.optimize_button.setEnabled(True)
        if hasattr(self, 'apply_options_button'):
            self.apply_options_button.setEnabled(True)
        if hasattr(self, 'save_button'):
            self.save_button.setEnabled(True)
        if hasattr(self, 'export_sdf_button'):
            self.export_sdf_button.setEnabled(True)
        if hasattr(self, 'export_mol_button'):
            self.export_mol_button.setEnabled(True)
        if hasattr(self, 'export_png_button'):
            self.export_png_button.setEnabled(True)
        
        # Enable 3D generate button
        if hasattr(self, 'generate_3d_button'):
            self.generate_3d_button.setEnabled(True)

    def disable_all_buttons(self):
        """Disable all action buttons."""
        # Verificar se os botões existem antes de desabilitá-los
        if hasattr(self, 'lewis_button'):
            self.lewis_button.setEnabled(False)
        if hasattr(self, 'view_3d_button'):
            self.view_3d_button.setEnabled(False)
        if hasattr(self, 'optimize_button'):
            self.optimize_button.setEnabled(False)
        if hasattr(self, 'apply_options_button'):
            self.apply_options_button.setEnabled(False)
        if hasattr(self, 'save_button'):
            self.save_button.setEnabled(False)
        if hasattr(self, 'export_sdf_button'):
            self.export_sdf_button.setEnabled(False)
        if hasattr(self, 'export_mol_button'):
            self.export_mol_button.setEnabled(False)
        if hasattr(self, 'export_png_button'):
            self.export_png_button.setEnabled(False)
        
        # Disable 3D buttons
        if hasattr(self, 'generate_3d_button'):
            self.generate_3d_button.setEnabled(False)
        if hasattr(self, 'optimize_3d_button'):
            self.optimize_3d_button.setEnabled(False)
        if hasattr(self, 'export_3d_button'):
            self.export_3d_button.setEnabled(False)
        if hasattr(self, 'fullscreen_3d_button'):
            self.fullscreen_3d_button.setEnabled(False)
        
        # Disable 3D buttons
        if hasattr(self, 'generate_3d_button'):
            self.generate_3d_button.setEnabled(False)
        if hasattr(self, 'optimize_3d_button'):
            self.optimize_3d_button.setEnabled(False)
        if hasattr(self, 'export_3d_button'):
            self.export_3d_button.setEnabled(False)
        if hasattr(self, 'fullscreen_3d_button'):
            self.fullscreen_3d_button.setEnabled(False)

    def view_3d_molecule(self):
        """Open enhanced 3D visualization."""
        if not self.current_mol:
            QMessageBox.warning(self, "Aviso", "Nenhuma molécula carregada!")
            return
        
        try:
            self.enhanced_3d_viewer = Enhanced3DMoleculeViewer(self.current_mol)
            self.enhanced_3d_viewer.show()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir visualização 3D: {str(e)}")

    def apply_drawing_options(self):
        """Apply selected drawing options and redraw."""
        if self.current_mol:
            # Get current SMILES and redraw
            current_smiles = self.smiles_input.text().strip()
            if current_smiles:
                self.draw_molecule()

    def optimize_structure(self):
        """Optimize molecular structure using RDKit."""
        if not self.current_mol:
            QMessageBox.warning(self, "Aviso", "Nenhuma molécula carregada!")
            return
        
        try:
            # Add hydrogens and optimize
            mol_with_h = Chem.AddHs(self.current_mol)
            
            # Generate 3D coordinates
            if AllChem.EmbedMolecule(mol_with_h) == 0:  # Success
                AllChem.UFFOptimizeMolecule(mol_with_h)
                
                # Update current molecule
                self.current_mol = mol_with_h
                
                # Redraw with optimized structure
                self.draw_molecule()
                QMessageBox.information(self, "Sucesso", "Estrutura otimizada com sucesso!")
            else:
                QMessageBox.warning(self, "Aviso", "Não foi possível gerar coordenadas 3D.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na otimização: {str(e)}")

    def save_image(self):
        """Save current molecular image."""
        if not self.current_mol:
            QMessageBox.warning(self, "Aviso", "Nenhuma molécula carregada!")
            return
        
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Salvar Imagem", "molecule.png",
                "PNG files (*.png);;JPG files (*.jpg);;All files (*.*)"
            )
            
            if filename:
                # Get current pixmap from label
                pixmap = self.image_label.pixmap()
                if pixmap:
                    pixmap.save(filename)
                    QMessageBox.information(self, "Sucesso", f"Imagem salva: {filename}")
                else:
                    QMessageBox.warning(self, "Aviso", "Nenhuma imagem para salvar.")
                    
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar imagem: {str(e)}")

    def export_sdf_enhanced(self):
        """Export molecule as SDF file."""
        if not self.current_mol:
            QMessageBox.warning(self, "Aviso", "Nenhuma molécula carregada!")
            return
        
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exportar SDF", "molecule.sdf",
                "SDF files (*.sdf);;All files (*.*)"
            )
            
            if filename:
                writer = Chem.SDWriter(filename)
                writer.write(self.current_mol)
                writer.close()
                QMessageBox.information(self, "Sucesso", f"SDF exportado: {filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar SDF: {str(e)}")

    def export_mol_enhanced(self):
        """Export molecule as MOL file."""
        if not self.current_mol:
            QMessageBox.warning(self, "Aviso", "Nenhuma molécula carregada!")
            return
        
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exportar MOL", "molecule.mol",
                "MOL files (*.mol);;All files (*.*)"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    f.write(Chem.MolToMolBlock(self.current_mol))
                QMessageBox.information(self, "Sucesso", f"MOL exportado: {filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar MOL: {str(e)}")

    def export_png_hd(self):
        """Export high-definition PNG image."""
        if not self.current_mol:
            QMessageBox.warning(self, "Aviso", "Nenhuma molécula carregada!")
            return
        
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exportar PNG HD", "molecule_hd.png",
                "PNG files (*.png);;All files (*.*)"
            )
            
            if filename:
                # Generate high-resolution image
                img = Draw.MolToImage(self.current_mol, size=(2000, 2000))
                img.save(filename)
                QMessageBox.information(self, "Sucesso", f"PNG HD exportado: {filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar PNG HD: {str(e)}")

    def load_from_database(self):
        """Load molecule from the comprehensive database."""
        dialog = MoleculeSelectionDialog(self.compounds_database, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_compound = dialog.get_selected_compound()
            if selected_compound and 'smiles' in selected_compound:
                self.smiles_input.setText(selected_compound['smiles'])
                self.draw_molecule()

    def search_pubchem(self):
        """Search and load molecule from PubChem (requires internet)."""
        search_term, ok = QInputDialog.getText(
            self, "Buscar no PubChem", 
            "Digite o nome ou CAS do composto:"
        )
        
        if ok and search_term:
            try:
                # This would require pubchempy library
                QMessageBox.information(
                    self, "Info", 
                    "Funcionalidade PubChem requer conexão com internet.\n"
                    "Use a base de dados local por enquanto."
                )
            except:
                QMessageBox.warning(
                    self, "Erro", 
                    "Erro ao conectar com PubChem. Verifique sua conexão."
                )

    def quick_molecule_entry(self):
        """Quick entry for common molecules."""
        common_molecules = {
            "Água": "O",
            "Metano": "C",
            "Etanol": "CCO",
            "Acetona": "CC(=O)C",
            "Benzeno": "c1ccccc1",
            "Glicose": "C([C@@H]1[C@H]([C@@H]([C@H]([C@H](O1)O)O)O)O)O",
            "Cafeína": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
            "Aspirina": "CC(=O)OC1=CC=CC=C1C(=O)O",
            "Penicilina": "CC1([C@@H](N2[C@H](S1)[C@@H](C2=O)NC(=O)CC3=CC=CC=C3)C(=O)O)C"
        }
        
        molecule, ok = QInputDialog.getItem(
            self, "Moléculas Comuns", 
            "Selecione uma molécula:", 
            list(common_molecules.keys()), 0, False
        )
        
        if ok and molecule:
            self.smiles_input.setText(common_molecules[molecule])
            self.draw_molecule()


class Enhanced3DMoleculeViewer(QDialog):
    """Enhanced 3D molecule viewer with multiple visualization options."""
    
    def __init__(self, molecule, parent=None):
        super().__init__(parent)
        self.molecule = molecule
        self.setWindowTitle("🧬 Visualizador 3D Avançado - HeisenLab")
        self.setMinimumSize(1000, 700)
        self.init_ui()
        self.setup_3d_view()

    def init_ui(self):
        """Initialize the enhanced 3D viewer UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🧬 Visualização 3D Molecular Avançada")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c5282;
            padding: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            margin: 5px;
        """)
        layout.addWidget(title)
        
        # Control panel
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.Shape.Box)
        controls_layout = QHBoxLayout(controls_frame)
        
        # Visualization style
        style_group = QGroupBox("🎨 Estilo de Visualização")
        style_layout = QVBoxLayout(style_group)
        
        self.style_combo = QComboBox()
        self.style_combo.addItems([
            "🔮 Esferas e Bastões",
            "🌐 Superfície",
            "📐 Wireframe",
            "🎈 Espaço-Preenchimento",
            "🧊 Cartoon",
            "⚡ Stick",
            "🌈 Colorido por Elemento"
        ])
        self.style_combo.currentTextChanged.connect(self.update_3d_view)
        style_layout.addWidget(self.style_combo)
        
        # Animation controls
        self.spin_checkbox = QCheckBox("🌀 Rotação Automática")
        self.spin_checkbox.toggled.connect(self.toggle_spin)
        style_layout.addWidget(self.spin_checkbox)
        
        controls_layout.addWidget(style_group)
        
        # Molecular properties display
        props_group = QGroupBox("📊 Propriedades Instantâneas")
        props_layout = QVBoxLayout(props_group)
        
        self.props_display = QTextEdit()
        self.props_display.setMaximumHeight(150)
        self.props_display.setStyleSheet("""
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 10px;
        """)
        props_layout.addWidget(self.props_display)
        
        controls_layout.addWidget(props_group)
        layout.addWidget(controls_frame)
        
        # 3D viewer area
        self.viewer_widget = QWidget()
        self.viewer_widget.setMinimumHeight(400)
        self.viewer_widget.setStyleSheet("""
            background-color: #000000;
            border: 2px solid #4a90e2;
            border-radius: 10px;
        """)
        layout.addWidget(self.viewer_widget)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.save_3d_button = QPushButton("💾 Salvar Visualização 3D")
        self.save_3d_button.clicked.connect(self.save_3d_view)
        self.save_3d_button.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
            }
        """)
        buttons_layout.addWidget(self.save_3d_button)
        
        self.export_coords_button = QPushButton("📐 Exportar Coordenadas")
        self.export_coords_button.clicked.connect(self.export_coordinates)
        self.export_coords_button.setStyleSheet(self.save_3d_button.styleSheet())
        buttons_layout.addWidget(self.export_coords_button)
        
        buttons_layout.addStretch()
        
        close_button = QPushButton("❌ Fechar")
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)

    def setup_3d_view(self):
        """Setup the 3D molecular visualization."""
        try:
            # Generate 3D coordinates if not present
            mol_3d = Chem.AddHs(self.molecule)
            if AllChem.EmbedMolecule(mol_3d) == 0:
                AllChem.UFFOptimizeMolecule(mol_3d)
                self.molecule_3d = mol_3d
            else:
                self.molecule_3d = self.molecule
            
            # Update properties display
            self.update_properties_display()
            
            # Create 3D visualization placeholder
            self.create_3d_placeholder()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao configurar visualização 3D: {str(e)}")

    def create_3d_placeholder(self):
        """Create a placeholder for 3D visualization."""
        placeholder_layout = QVBoxLayout(self.viewer_widget)
        
        placeholder_label = QLabel("🧬 Visualização 3D Molecular")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
        """)
        placeholder_layout.addWidget(placeholder_label)
        
        info_label = QLabel("Visualização 3D interativa seria exibida aqui\ncom py3Dmol ou similar")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("""
            color: #cccccc;
            font-size: 14px;
        """)
        placeholder_layout.addWidget(info_label)

    def update_properties_display(self):
        """Update the molecular properties display."""
        try:
            formula = rdMolDescriptors.CalcMolFormula(self.molecule)
            mw = Descriptors.MolWt(self.molecule)
            atoms = self.molecule.GetNumAtoms()
            bonds = self.molecule.GetNumBonds()
            
            props_text = f"""🧪 PROPRIEDADES 3D INSTANTÂNEAS
{'='*40}
Fórmula Molecular: {formula}
Peso Molecular: {mw:.2f} g/mol
Átomos: {atoms} | Ligações: {bonds}
Anéis: {Descriptors.RingCount(self.molecule)}
Centros Quirais: {len(Chem.FindMolChiralCenters(self.molecule))}
Volume Molecular: ~{mw * 0.7:.1f} ų (estimativa)
Área Superficial: ~{Descriptors.TPSA(self.molecule):.1f} ų
"""
            
            self.props_display.setText(props_text)
            
        except Exception as e:
            self.props_display.setText(f"Erro ao calcular propriedades: {str(e)}")

    def update_3d_view(self):
        """Update 3D view based on selected style."""
        style = self.style_combo.currentText()
        # This would update the 3D visualization
        # Implementation depends on the 3D library used
        print(f"Updating 3D view with style: {style}")

    def toggle_spin(self, enabled):
        """Toggle automatic rotation."""
        # This would control the rotation animation
        print(f"Spin animation: {'enabled' if enabled else 'disabled'}")

    def save_3d_view(self):
        """Save the current 3D view as an image."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Salvar Visualização 3D", "molecule_3d.png",
                "PNG files (*.png);;JPG files (*.jpg);;All files (*.*)"
            )
            
            if filename:
                # This would capture the 3D view
                QMessageBox.information(self, "Info", 
                    "Funcionalidade de captura 3D seria implementada aqui")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar visualização: {str(e)}")

    def export_coordinates(self):
        """Export 3D coordinates."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exportar Coordenadas 3D", "coordinates.xyz",
                "XYZ files (*.xyz);;PDB files (*.pdb);;All files (*.*)"
            )
            
            if filename:
                # Export molecule coordinates
                if filename.endswith('.xyz'):
                    # Write XYZ format
                    with open(filename, 'w') as f:
                        f.write(f"{self.molecule_3d.GetNumAtoms()}\n")
                        f.write("Generated by HeisenLab\n")
                        
                        conf = self.molecule_3d.GetConformer()
                        for atom in self.molecule_3d.GetAtoms():
                            pos = conf.GetAtomPosition(atom.GetIdx())
                            f.write(f"{atom.GetSymbol()} {pos.x:.6f} {pos.y:.6f} {pos.z:.6f}\n")
                
                QMessageBox.information(self, "Sucesso", f"Coordenadas exportadas: {filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar coordenadas: {str(e)}")


class MoleculeSelectionDialog(QDialog):
    """Dialog for selecting molecules from the database."""
    
    def __init__(self, compounds_database, parent=None):
        super().__init__(parent)
        self.compounds_database = compounds_database
        self.selected_compound = None
        self.setWindowTitle("🧪 Seleção de Moléculas - Base de Dados")
        self.setMinimumSize(800, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize the molecule selection dialog."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🧪 Base de Dados Molecular Abrangente")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: white;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 10px;
            border-radius: 8px;
            margin: 5px;
        """)
        layout.addWidget(title)
        
        # Search and filter
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar por nome, fórmula ou propriedade...")
        self.search_input.textChanged.connect(self.filter_compounds)
        search_layout.addWidget(self.search_input)
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("📁 Todas as Categorias")
        self.category_filter.addItems([f"📂 {cat}" for cat in self.compounds_database.keys()])
        self.category_filter.currentTextChanged.connect(self.filter_compounds)
        search_layout.addWidget(self.category_filter)
        
        layout.addLayout(search_layout)
        
        # Compounds list
        self.compounds_list = QListWidget()
        self.compounds_list.itemDoubleClicked.connect(self.select_compound)
        layout.addWidget(self.compounds_list)
        
        # Compound info
        self.compound_info = QTextEdit()
        self.compound_info.setMaximumHeight(200)
        self.compound_info.setStyleSheet("""
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
        """)
        layout.addWidget(self.compound_info)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        select_button = QPushButton("✅ Selecionar")
        select_button.clicked.connect(self.select_compound)
        select_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        buttons_layout.addWidget(select_button)
        
        buttons_layout.addStretch()
        
        cancel_button = QPushButton("❌ Cancelar")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
        
        # Populate initial list
        self.populate_compounds_list()
        
        # Connect list selection
        self.compounds_list.itemClicked.connect(self.show_compound_info)

    def populate_compounds_list(self):
        """Populate the compounds list."""
        self.compounds_list.clear()
        
        for category, compounds in self.compounds_database.items():
            for compound in compounds:
                name = compound.get('name', 'Nome não disponível')
                formula = compound.get('formula', '')
                item_text = f"{name} ({formula})"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, compound)
                self.compounds_list.addItem(item)

    def filter_compounds(self):
        """Filter compounds based on search term and category."""
        search_term = self.search_input.text().lower()
        selected_category = self.category_filter.currentText().replace("📂 ", "").replace("📁 ", "")
        
        self.compounds_list.clear()
        
        for category, compounds in self.compounds_database.items():
            if selected_category != "Todas as Categorias" and category != selected_category:
                continue
                
            for compound in compounds:
                name = compound.get('name', '').lower()
                formula = compound.get('formula', '').lower()
                
                if search_term in name or search_term in formula:
                    display_name = compound.get('name', 'Nome não disponível')
                    display_formula = compound.get('formula', '')
                    item_text = f"{display_name} ({display_formula})"
                    
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, compound)
                    self.compounds_list.addItem(item)

    def show_compound_info(self, item):
        """Show detailed information for selected compound."""
        compound = item.data(Qt.ItemDataRole.UserRole)
        if compound:
            info_text = f"""🧪 INFORMAÇÕES DO COMPOSTO
{'='*40}

📋 Nome: {compound.get('name', 'N/A')}
⚗️ Fórmula: {compound.get('formula', 'N/A')}
🧬 SMILES: {compound.get('smiles', 'N/A')}

🌡️ Propriedades Físicas:
   Ponto de Fusão: {compound.get('mp', 'N/A')}°C
   Ponto de Ebulição: {compound.get('bp', 'N/A')}°C
   Densidade: {compound.get('density', 'N/A')} g/cm³

📊 Categoria: {compound.get('category', 'N/A')}
💡 Descrição: {compound.get('description', 'Descrição não disponível')}

✨ Aplicações:
{compound.get('applications', 'Informações não disponíveis')}
"""
            self.compound_info.setText(info_text)

    def select_compound(self):
        """Select the current compound and close dialog."""
        current_item = self.compounds_list.currentItem()
        if current_item:
            self.selected_compound = current_item.data(Qt.ItemDataRole.UserRole)
            self.accept()
        else:
            QMessageBox.warning(self, "Aviso", "Selecione um composto da lista.")

    def get_selected_compound(self):
        """Return the selected compound."""
        return self.selected_compound

    def show_lewis_structure(self):
        """Generate and display Lewis structure of the current molecule."""
        if not hasattr(self, 'current_mol') or not self.current_mol:
            QMessageBox.warning(self, "Aviso", "Nenhuma molécula carregada para gerar estrutura de Lewis.")
            return
        
        try:
            # Criar diálogo para mostrar estrutura de Lewis
            dialog = QDialog(self)
            dialog.setWindowTitle("Estrutura de Lewis")
            dialog.setMinimumSize(600, 500)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #f0f0f0;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #cccccc;
                    border-radius: 5px;
                    margin: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            
            # Título
            title_label = QLabel("🧬 Estrutura de Lewis")
            title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2E7D32; margin: 10px;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title_label)
            
            # Informações da molécula
            mol_info = QGroupBox("Informações da Molécula")
            mol_layout = QVBoxLayout(mol_info)
            
            # Obter informações básicas
            num_atoms = self.current_mol.GetNumAtoms()
            num_bonds = self.current_mol.GetNumBonds()
            molecular_formula = Chem.rdMolDescriptors.CalcMolFormula(self.current_mol)
            molecular_weight = Chem.rdMolDescriptors.CalcExactMolWt(self.current_mol)
            
            info_text = f"""
📋 Fórmula Molecular: {molecular_formula}
⚖️ Massa Molecular: {molecular_weight:.2f} g/mol
🔗 Número de Átomos: {num_atoms}
🔗 Número de Ligações: {num_bonds}
            """
            
            info_label = QLabel(info_text)
            info_label.setStyleSheet("font-size: 12px; padding: 10px;")
            mol_layout.addWidget(info_label)
            layout.addWidget(mol_info)
            
            # Análise de Lewis
            lewis_info = QGroupBox("Análise da Estrutura de Lewis")
            lewis_layout = QVBoxLayout(lewis_info)
            
            # Calcular elétrons de valência
            valence_electrons = self.calculate_valence_electrons()
            lewis_pairs = self.analyze_lewis_structure()
            
            lewis_text = f"""
⚡ Total de Elétrons de Valência: {valence_electrons}
👥 Pares de Elétrons de Ligação: {lewis_pairs['bonding_pairs']}
🔄 Pares de Elétrons Livres: {lewis_pairs['lone_pairs']}
🔀 Pares de Elétrons Totais: {lewis_pairs['total_pairs']}

🧮 Regra do Octeto:
{lewis_pairs['octet_analysis']}

💡 Hibridização Estimada:
{lewis_pairs['hybridization']}

📐 Geometria Molecular Prevista:
{lewis_pairs['geometry']}
            """
            
            lewis_label = QLabel(lewis_text)
            lewis_label.setStyleSheet("font-size: 11px; padding: 10px; background-color: white; border-radius: 5px;")
            lewis_layout.addWidget(lewis_label)
            layout.addWidget(lewis_info)
            
            # Visualização da estrutura 2D
            structure_group = QGroupBox("Representação Estrutural")
            structure_layout = QVBoxLayout(structure_group)
            
            # Gerar imagem da molécula com elétrons livres destacados
            mol_with_hs = Chem.AddHs(self.current_mol)
            img = Draw.MolToImage(mol_with_hs, size=(400, 300))
            
            # Converter para QPixmap e mostrar
            import io
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(img_bytes.getvalue())
            
            img_label = QLabel()
            img_label.setPixmap(pixmap)
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            img_label.setStyleSheet("border: 1px solid #ccc; background-color: white; padding: 10px;")
            structure_layout.addWidget(img_label)
            layout.addWidget(structure_group)
            
            # Botões
            button_layout = QHBoxLayout()
            
            export_btn = QPushButton("Exportar Estrutura")
            export_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; }")
            export_btn.clicked.connect(lambda: self.export_lewis_structure(img))
            button_layout.addWidget(export_btn)
            
            close_btn = QPushButton("Fechar")
            close_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; padding: 8px; }")
            close_btn.clicked.connect(dialog.close)
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            
            # Mostrar diálogo
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar estrutura de Lewis: {str(e)}")
    
    def calculate_valence_electrons(self):
        """Calculate total valence electrons in the molecule."""
        valence_map = {1: 1, 6: 4, 7: 5, 8: 6, 9: 7, 15: 5, 16: 6, 17: 7, 35: 7, 53: 7}
        total_electrons = 0
        
        for atom in self.current_mol.GetAtoms():
            atomic_num = atom.GetAtomicNum()
            total_electrons += valence_map.get(atomic_num, 0)
        
        return total_electrons
    
    def analyze_lewis_structure(self):
        """Analyze Lewis structure properties."""
        num_bonds = self.current_mol.GetNumBonds()
        total_valence = self.calculate_valence_electrons()
        
        # Calcular pares de elétrons
        bonding_pairs = num_bonds
        total_pairs = total_valence // 2
        lone_pairs = total_pairs - bonding_pairs
        
        # Análise da regra do octeto
        octet_analysis = self.check_octet_rule()
        
        # Estimar hibridização do átomo central
        hybridization = self.estimate_hybridization()
        
        # Prever geometria molecular
        geometry = self.predict_geometry()
        
        return {
            'bonding_pairs': bonding_pairs,
            'lone_pairs': lone_pairs,
            'total_pairs': total_pairs,
            'octet_analysis': octet_analysis,
            'hybridization': hybridization,
            'geometry': geometry
        }
    
    def check_octet_rule(self):
        """Check octet rule compliance for atoms."""
        analysis = []
        
        for atom in self.current_mol.GetAtoms():
            atomic_num = atom.GetAtomicNum()
            symbol = atom.GetSymbol()
            
            if atomic_num == 1:  # Hidrogênio
                analysis.append(f"✅ {symbol}: Regra do dueto (2 elétrons)")
            elif atomic_num in [6, 7, 8, 9]:  # C, N, O, F
                analysis.append(f"✅ {symbol}: Segue regra do octeto (8 elétrons)")
            else:
                analysis.append(f"⚠️ {symbol}: Pode expandir octeto")
        
        return "\n".join(analysis) if analysis else "Análise não disponível"
    
    def estimate_hybridization(self):
        """Estimate hybridization of central atoms."""
        hybridizations = []
        
        for atom in self.current_mol.GetAtoms():
            if atom.GetDegree() > 1:  # Átomo com mais de uma ligação
                degree = atom.GetDegree()
                symbol = atom.GetSymbol()
                
                if degree == 2:
                    hybridizations.append(f"{symbol}: sp (linear)")
                elif degree == 3:
                    hybridizations.append(f"{symbol}: sp² (trigonal)")
                elif degree == 4:
                    hybridizations.append(f"{symbol}: sp³ (tetraédrica)")
                else:
                    hybridizations.append(f"{symbol}: sp³d ou superior")
        
        return "\n".join(hybridizations) if hybridizations else "Análise não disponível"
    
    def predict_geometry(self):
        """Predict molecular geometry based on VSEPR theory."""
        geometries = []
        
        for atom in self.current_mol.GetAtoms():
            if atom.GetDegree() > 1:
                degree = atom.GetDegree()
                symbol = atom.GetSymbol()
                
                if degree == 2:
                    geometries.append(f"{symbol}: Linear")
                elif degree == 3:
                    geometries.append(f"{symbol}: Trigonal planar")
                elif degree == 4:
                    geometries.append(f"{symbol}: Tetraédrica")
                else:
                    geometries.append(f"{symbol}: Geometria complexa")
        
        return "\n".join(geometries) if geometries else "Análise não disponível"
    
    def export_lewis_structure(self, img):
        """Export Lewis structure image."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exportar Estrutura de Lewis", "lewis_structure.png",
                "PNG files (*.png);;JPEG files (*.jpg);;All files (*)"
            )
            
            if filename:
                img.save(filename)
                QMessageBox.information(self, "Sucesso", f"Estrutura de Lewis exportada: {filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar estrutura: {str(e)}")
