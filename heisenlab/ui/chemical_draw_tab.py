from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QTextEdit, QTabWidget,
    QComboBox, QCheckBox, QSpinBox, QSlider, QColorDialog, QFileDialog, QMessageBox,
    QSplitter, QFrame
)
from PySide6.QtGui import QPixmap, QImage, QColor, QFont
from PySide6.QtCore import Qt, QTimer
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


class ChemicalDrawTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

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
        
        # Molecule library
        library_group = self.create_molecule_library_section()
        left_layout.addWidget(library_group)
        
        left_layout.addStretch()
        left_widget.setLayout(left_layout)
        
        # Right panel - Visualization
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)
        
        # Visualization tabs
        viz_tabs = QTabWidget()
        
        # 2D tab
        tab_2d = QWidget()
        tab_2d_layout = QVBoxLayout()
        drawing_group = self.create_drawing_section()
        tab_2d_layout.addWidget(drawing_group)
        tab_2d.setLayout(tab_2d_layout)
        viz_tabs.addTab(tab_2d, "Visualização 2D")
        
        # 3D tab
        tab_3d = QWidget()
        tab_3d_layout = QVBoxLayout()
        visualization_group = self.create_3d_section()
        tab_3d_layout.addWidget(visualization_group)
        tab_3d.setLayout(tab_3d_layout)
        viz_tabs.addTab(tab_3d, "Visualização 3D")
        
        # Properties tab
        tab_props = QWidget()
        tab_props_layout = QVBoxLayout()
        properties_group = self.create_properties_section()
        tab_props_layout.addWidget(properties_group)
        tab_props.setLayout(tab_props_layout)
        viz_tabs.addTab(tab_props, "Propriedades")
        
        right_layout.addWidget(viz_tabs)
        right_widget.setLayout(right_layout)
        
        # Add to splitter
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setStretchFactor(0, 1)  # Left panel
        main_splitter.setStretchFactor(1, 2)  # Right panel (larger)
        
        layout.addWidget(main_splitter)
        self.setLayout(layout)

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

    def create_molecule_library_section(self) -> QGroupBox:
        """Create molecule library section."""
        group = QGroupBox("Biblioteca de Moléculas")
        layout = QVBoxLayout()
        
        # Categorias expandidas
        categorias = [
            "Alcanos", "Alcenos", "Alcinos", "Aromáticos", "Álcoois", "Éteres", "Aldeídos", "Cetonas", "Ácidos Carboxílicos", "Ésteres", "Aminas", "Amidas", "Haletos Orgânicos", "Compostos Nitrogenados", "Compostos Sulfurados", "Compostos Fosforados", "Compostos Organometálicos", "Naturais", "Medicamentos", "Outros"
        ]
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Categoria:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(categorias)
        self.category_combo.currentTextChanged.connect(self.update_molecule_list)
        category_layout.addWidget(self.category_combo)
        layout.addLayout(category_layout)

        # Base de dados expandida (exemplo, pode ser enriquecida com parsing do bluebook.txt)
        self.molecule_db = {
            "Alcanos": [
                {"nome": "Metano", "iupac": "Methane", "formula": "CH4", "descricao": "Hidrocarboneto mais simples."},
                {"nome": "Etano", "iupac": "Ethane", "formula": "C2H6", "descricao": "Segundo alcano da série."},
                {"nome": "Propano", "iupac": "Propane", "formula": "C3H8", "descricao": "Gás de cozinha."},
                {"nome": "Butano", "iupac": "Butane", "formula": "C4H10", "descricao": "Usado em isqueiros."}
            ],
            "Aromáticos": [
                {"nome": "Benzeno", "iupac": "Benzene", "formula": "C6H6", "descricao": "Aromático clássico."},
                {"nome": "Tolueno", "iupac": "Toluene", "formula": "C7H8", "descricao": "Derivado do benzeno."},
                {"nome": "Fenol", "iupac": "Phenol", "formula": "C6H5OH", "descricao": "Benzeno com grupo hidroxila."}
            ],
            "Ácidos Carboxílicos": [
                {"nome": "Ácido Acético", "iupac": "Acetic acid", "formula": "CH3COOH", "descricao": "Principal componente do vinagre."},
                {"nome": "Ácido Fórmico", "iupac": "Formic acid", "formula": "HCOOH", "descricao": "Presente em formigas."}
            ],
            "Aldeídos": [
                {"nome": "Formaldeído", "iupac": "Methanal", "formula": "HCHO", "descricao": "Conservante e desinfetante."},
                {"nome": "Acetaldeído", "iupac": "Ethanal", "formula": "CH3CHO", "descricao": "Intermediário industrial."}
            ],
            "Outros": [
                {"nome": "Cafeína", "iupac": "1,3,7-Trimethylpurine-2,6-dione", "formula": "C8H10N4O2", "descricao": "Alcaloide estimulante."}
            ]
        }

        # Combo de moléculas
        self.molecule_combo = QComboBox()
        layout.addWidget(self.molecule_combo)

        # Detalhes da molécula
        self.molecule_details = QTextEdit()
        self.molecule_details.setReadOnly(True)
        self.molecule_details.setMinimumHeight(80)
        self.molecule_details.setMaximumHeight(120)
        self.molecule_details.setStyleSheet("font-family: monospace; font-size: 11px;")
        layout.addWidget(self.molecule_details)

        self.update_molecule_list()
        # Load button
        self.load_molecule_button = QPushButton("Carregar Molécula")
        self.load_molecule_button.setMinimumHeight(35)
        self.load_molecule_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.load_molecule_button.clicked.connect(self.load_selected_molecule)
        layout.addWidget(self.load_molecule_button)

        # Save current molecule
        self.save_button = QPushButton("Salvar Molécula Atual")
        self.save_button.setMinimumHeight(35)
        self.save_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.save_button.setEnabled(False)
        layout.addWidget(self.save_button)

        group.setLayout(layout)
        return group

    def create_properties_section(self) -> QGroupBox:
        """Create detailed properties section."""
        group = QGroupBox("Propriedades Moleculares Detalhadas")
        layout = QVBoxLayout()
        
        # Properties text area
        self.detailed_properties = QTextEdit()
        self.detailed_properties.setReadOnly(True)
        self.detailed_properties.setMinimumHeight(300)
        self.detailed_properties.setStyleSheet("font-family: monospace; font-size: 11px;")
        layout.addWidget(self.detailed_properties)
        
        # Export buttons
        export_layout = QHBoxLayout()
        self.export_sdf_button = QPushButton("Exportar SDF")
        self.export_sdf_button.setMinimumHeight(35)
        self.export_sdf_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.export_sdf_button.clicked.connect(self.export_sdf)
        self.export_sdf_button.setEnabled(False)
        export_layout.addWidget(self.export_sdf_button)

        self.export_mol_button = QPushButton("Exportar MOL")
        self.export_mol_button.setMinimumHeight(35)
        self.export_mol_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.export_mol_button.clicked.connect(self.export_mol)
        self.export_mol_button.setEnabled(False)
        export_layout.addWidget(self.export_mol_button)

        self.export_png_button = QPushButton("Exportar PNG")
        self.export_png_button.setMinimumHeight(35)
        self.export_png_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.export_png_button.clicked.connect(self.export_png)
        self.export_png_button.setEnabled(False)
        export_layout.addWidget(self.export_png_button)

        layout.addLayout(export_layout)

        group.setLayout(layout)
        return group
    def create_drawing_section(self) -> QGroupBox:
        """Create the chemical drawing section."""
        group = QGroupBox("Estrutura 2D")
        layout = QVBoxLayout()
        
        # Molecule display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(400)
        self.image_label.setMinimumWidth(500)
        self.image_label.setStyleSheet("border: 1px solid gray; background-color: white;")
        self.image_label.setText("Digite um SMILES e clique em 'Desenhar'")
        layout.addWidget(self.image_label)
        
        # Enhanced molecule info
        self.molecule_info = QTextEdit()
        self.molecule_info.setReadOnly(True)
        self.molecule_info.setMinimumHeight(200)
        self.molecule_info.setMaximumHeight(250)
        self.molecule_info.setStyleSheet("font-family: monospace; font-size: 11px;")
        layout.addWidget(self.molecule_info)
        
        group.setLayout(layout)
        return group

    def create_3d_section(self) -> QGroupBox:
        """Create the 3D visualization section."""
        group = QGroupBox("Visualização 3D Interativa")
        layout = QVBoxLayout()
        
        # 3D button
        button_layout = QHBoxLayout()
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
        """Draw molecule from SMILES input."""
        smiles = self.smiles_input.text().strip()
        if not smiles:
            self.image_label.setText("Digite um SMILES válido.")
            self.molecule_info.clear()
            self.detailed_properties.clear()
            return
            
        try:
            # Parse SMILES
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                self.image_label.setText("SMILES inválido. Verifique a sintaxe.")
                self.molecule_info.clear()
                self.detailed_properties.clear()
                return
            
            # Apply drawing options
            draw_options = Draw.rdMolDraw2D.MolDrawOptions()
            if self.show_atom_labels.isChecked():
                draw_options.addAtomIndices = True
            
            # Handle hydrogen display
            if self.show_hydrogens.isChecked():
                mol = Chem.AddHs(mol)
            
            # Generate image with custom size
            size = (self.width_spin.value(), self.height_spin.value())
            img = Draw.MolToImage(mol, size=size, options=draw_options)
            
            # Convert to QPixmap and display
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            
            qimg = QImage()
            qimg.loadFromData(buf.getvalue())
            pixmap = QPixmap.fromImage(qimg)
            self.image_label.setPixmap(pixmap)
            
            # Display basic molecule info
            info = self.get_molecule_info(mol, smiles)
            self.molecule_info.setText(info)
            
            # Enable buttons
            self.view_3d_button.setEnabled(True)
            self.optimize_button.setEnabled(True)
            self.apply_options_button.setEnabled(True)
            self.save_button.setEnabled(True)
            self.export_sdf_button.setEnabled(True)
            self.export_mol_button.setEnabled(True)
            self.export_png_button.setEnabled(True)
            self.current_mol = mol  # Store molecule for 3D visualization
            
            # Update detailed properties
            self.update_detailed_properties(mol, smiles)
            
        except Exception as e:
            self.image_label.setText(f"Erro ao desenhar molécula: {str(e)}")
            self.molecule_info.clear()
            self.detailed_properties.clear()
            self.disable_buttons()

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

    def redraw_with_options(self):
        """Redraw molecule with current options."""
        if hasattr(self, 'current_mol') and self.current_mol:
            self.draw_molecule()

    def update_molecule_list(self):
        """Update molecule list based on selected category."""
        category = self.category_combo.currentText()
        self.molecule_combo.clear()
        for mol in self.molecule_db.get(category, []):
            display = f"{mol['nome']} [{mol['formula']}]"
            self.molecule_combo.addItem(display, mol)
        self.show_molecule_details()
        self.molecule_combo.currentIndexChanged.connect(self.show_molecule_details)

    def show_molecule_details(self):
        mol = self.molecule_combo.currentData()
        if mol:
            details = f"Nome: {mol['nome']}\nIUPAC: {mol['iupac']}\nFórmula: {mol['formula']}\nDescrição: {mol['descricao']}"
            self.molecule_details.setText(details)
        else:
            self.molecule_details.clear()

    def load_selected_molecule(self):
        """Load selected molecule from library."""
        mol = self.molecule_combo.currentData()
        if mol:
            self.smiles_input.setText("")  # Sem SMILES
            self.name_input.setText(mol['nome'])
            self.molecule_info.setText(f"Nome: {mol['nome']}\nIUPAC: {mol['iupac']}\nFórmula: {mol['formula']}\nDescrição: {mol['descricao']}")

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
