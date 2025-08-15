from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QTextEdit
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
from rdkit import Chem
from rdkit.Chem import Draw
import io
from PIL import Image


class ChemicalDrawTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)  # Espaçamento entre seções
        layout.setContentsMargins(15, 15, 15, 15)  # Margens da janela
        
        # Create a scroll area for better navigation
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Main content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        
        # Chemical Drawing Section
        drawing_group = self.create_drawing_section()
        content_layout.addWidget(drawing_group)
        
        # Examples Section
        examples_group = self.create_examples_section()
        content_layout.addWidget(examples_group)
        
        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)
        
        layout.addWidget(scroll)
        self.setLayout(layout)

    def create_drawing_section(self) -> QGroupBox:
        """Create the chemical drawing section."""
        group = QGroupBox("Desenho de Moléculas Orgânicas")
        layout = QFormLayout()
        layout.setVerticalSpacing(12)
        layout.setHorizontalSpacing(15)
        
        # SMILES input
        self.smiles_input = QLineEdit()
        self.smiles_input.setPlaceholderText("Digite o SMILES da molécula (ex: CCO para etanol)")
        self.smiles_input.setMinimumHeight(30)
        self.smiles_input.returnPressed.connect(self.draw_molecule)
        layout.addRow("SMILES:", self.smiles_input)
        
        # Draw button
        self.draw_button = QPushButton("Desenhar Molécula")
        self.draw_button.setMinimumHeight(35)
        self.draw_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.draw_button.clicked.connect(self.draw_molecule)
        layout.addRow("", self.draw_button)
        
        # Molecule display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(300)
        self.image_label.setMinimumWidth(300)
        self.image_label.setStyleSheet("border: 1px solid gray; background-color: white;")
        self.image_label.setText("Digite um SMILES e clique em 'Desenhar Molécula'")
        layout.addRow("Estrutura:", self.image_label)
        
        # Molecule info
        self.molecule_info = QTextEdit()
        self.molecule_info.setReadOnly(True)
        self.molecule_info.setMinimumHeight(100)
        self.molecule_info.setMaximumHeight(120)
        self.molecule_info.setStyleSheet("font-family: monospace; font-size: 11px;")
        layout.addRow("Informações:", self.molecule_info)
        
        group.setLayout(layout)
        return group

    def create_examples_section(self) -> QGroupBox:
        """Create the examples section."""
        group = QGroupBox("Exemplos de SMILES")
        layout = QVBoxLayout()
        
        examples_text = QTextEdit()
        examples_text.setReadOnly(True)
        examples_text.setMaximumHeight(150)
        examples_text.setStyleSheet("font-family: monospace; font-size: 11px;")
        
        examples = """Exemplos de SMILES para testar:

• Moléculas simples:
  CCO           - Etanol
  CCC           - Propano
  CC(C)C        - Isobutano
  
• Moléculas com grupos funcionais:
  CC(=O)O       - Ácido acético
  CC(=O)N       - Acetamida
  CCN           - Etilamina
  
• Compostos aromáticos:
  c1ccccc1      - Benzeno
  Cc1ccccc1     - Tolueno
  c1ccccc1O     - Fenol
  
• Moléculas complexas:
  CN1C=NC2=C1C(=O)N(C(=O)N2C)C  - Cafeína
  CC(C)CC1=CC=C(C=C1)C(C)C(=O)O - Ibuprofeno"""
        
        examples_text.setText(examples)
        layout.addWidget(examples_text)
        
        group.setLayout(layout)
        return group

    def draw_molecule(self):
        """Draw molecule from SMILES input."""
        smiles = self.smiles_input.text().strip()
        if not smiles:
            self.image_label.setText("Digite um SMILES válido.")
            self.molecule_info.clear()
            return
            
        try:
            # Parse SMILES
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                self.image_label.setText("SMILES inválido. Verifique a sintaxe.")
                self.molecule_info.clear()
                return
            
            # Generate image
            img = Draw.MolToImage(mol, size=(400, 300))
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            
            # Display image
            qimg = QImage()
            qimg.loadFromData(buf.getvalue())
            pixmap = QPixmap.fromImage(qimg)
            self.image_label.setPixmap(pixmap)
            
            # Display molecule info
            info = self.get_molecule_info(mol, smiles)
            self.molecule_info.setText(info)
            
        except Exception as e:
            self.image_label.setText(f"Erro ao desenhar molécula: {str(e)}")
            self.molecule_info.clear()

    def get_molecule_info(self, mol, smiles):
        """Get basic information about the molecule."""
        try:
            num_atoms = mol.GetNumAtoms()
            num_bonds = mol.GetNumBonds()
            molecular_weight = Chem.Descriptors.MolWt(mol)
            formula = Chem.rdMolDescriptors.CalcMolFormula(mol)
            
            info = f"""SMILES: {smiles}
Fórmula Molecular: {formula}
Peso Molecular: {molecular_weight:.2f} g/mol
Número de Átomos: {num_atoms}
Número de Ligações: {num_bonds}"""
            
            return info
        except Exception:
            return f"SMILES: {smiles}\nInformações adicionais não disponíveis."
