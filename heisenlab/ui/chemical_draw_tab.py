from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QTextEdit, QTabWidget,
    QComboBox, QCheckBox, QSpinBox, QSlider, QColorDialog, QFileDialog, QMessageBox,
    QSplitter, QFrame, QApplication  # adicionada QApplication
)
from PySide6.QtGui import QPixmap, QImage, QColor, QFont
from PySide6.QtCore import Qt, QTimer, QEvent
from PySide6.QtWebEngineWidgets import QWebEngineView
from rdkit import Chem
from rdkit.Chem import Draw, AllChem, Descriptors, rdMolDescriptors, Crippen, Lipinski
import io
from PIL import Image
import py3Dmol
import tempfile
import pubchempy as pcp
import os
import json
import requests  # <-- adicionado


# --- Novas classes utilitárias de zoom (melhor prática) ---
class ZoomableTextEdit(QTextEdit):
    """QTextEdit com zoom via Ctrl + Scroll (Shift acelera)."""
    def __init__(self, base_point_size=11, min_factor=0.5, max_factor=3.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._base_size = base_point_size
        self._zoom_factor = 1.0
        self._min_factor = min_factor
        self._max_factor = max_factor
        self._apply_zoom()
        self.setContextMenuPolicy(Qt.DefaultContextMenu)

    def _apply_zoom(self):
        # Usa stylesheet para sobrescrever qualquer font-size prévio
        pt = self._base_size * self._zoom_factor
        self.setStyleSheet(f"font-family: monospace; font-size: {pt:.2f}pt;")

    def wheelEvent(self, event):
        if QApplication.keyboardModifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            step_mul = 1.2 if (QApplication.keyboardModifiers() & Qt.ShiftModifier) else 1.1
            if delta > 0:
                self._zoom_factor = min(self._zoom_factor * step_mul, self._max_factor)
            else:
                self._zoom_factor = max(self._zoom_factor / step_mul, self._min_factor)
            self._apply_zoom()
            event.accept()
        else:
            super().wheelEvent(event)

    def resetZoom(self):
        self._zoom_factor = 1.0
        self._apply_zoom()


class ChemicalDrawTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_smiles = ""
        self.zoom_factor = 1.0  # agora usado apenas para escala visual (como equations)
        self.base_size = 600     # tamanho base fixo da imagem RDKit
        self.text_zoom_factor = 1.0
        self._text_widgets = []
        self.image_label = None
        self._base_mol_pixmap = None  # pixmap original (não escalado) para zoom tipo equations
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        main_splitter = QSplitter(Qt.Horizontal)
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        input_group = self.create_input_section()
        left_layout.addWidget(input_group)
        options_group = self.create_drawing_options_section()
        left_layout.addWidget(options_group)
        # Removido: biblioteca de moléculas
        left_layout.addStretch()
        left_widget.setLayout(left_layout)
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)
        viz_tabs = QTabWidget()
        tab_2d = QWidget()
        tab_2d_layout = QVBoxLayout()
        drawing_group = self.create_drawing_section()
        tab_2d_layout.addWidget(drawing_group)
        tab_2d.setLayout(tab_2d_layout)
        viz_tabs.addTab(tab_2d, "Visualização 2D")
        tab_3d = QWidget()
        tab_3d_layout = QVBoxLayout()
        visualization_group = self.create_3d_section()
        tab_3d_layout.addWidget(visualization_group)
        tab_3d.setLayout(tab_3d_layout)
        viz_tabs.addTab(tab_3d, "Visualização 3D")
        tab_props = QWidget()
        tab_props_layout = QVBoxLayout()
        properties_group = self.create_properties_section()
        tab_props_layout.addWidget(properties_group)
        tab_props.setLayout(tab_props_layout)
        viz_tabs.addTab(tab_props, "Propriedades")
        right_layout.addWidget(viz_tabs)
        right_widget.setLayout(right_layout)
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 2)
        layout.addWidget(main_splitter)
        self.setLayout(layout)
        # Registrar detailed_properties se já existir
        if hasattr(self, 'detailed_properties'):
            self.register_text_widget(self.detailed_properties, 11)
        self.apply_text_zoom()

    def create_input_section(self) -> QGroupBox:
        """Create the input section with PubChem search only."""
        group = QGroupBox("Entrada de Moléculas")
        layout = QFormLayout()
        layout.setVerticalSpacing(12)
        layout.setHorizontalSpacing(15)

        # Busca no PubChem
        pubchem_layout = QHBoxLayout()
        self.pubchem_input = QLineEdit()
        self.pubchem_input.setPlaceholderText("Nome do composto para buscar no PubChem")
        self.pubchem_input.setMinimumHeight(30)
        pubchem_layout.addWidget(self.pubchem_input)

        self.pubchem_search_button = QPushButton("Buscar")
        self.pubchem_search_button.setMinimumHeight(30)
        self.pubchem_search_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.pubchem_search_button.clicked.connect(self.search_pubchem)
        pubchem_layout.addWidget(self.pubchem_search_button)

        layout.addRow("PubChem:", pubchem_layout)

        # Resultado da busca
        self.pubchem_result = ZoomableTextEdit(base_point_size=10)
        self.pubchem_result.setReadOnly(True)
        self.pubchem_result.setMaximumHeight(80)
        # Removido font-size fixo para permitir zoom
        self.pubchem_result.setPlaceholderText("Resultado da busca no PubChem aparecerá aqui...")
        self.pubchem_result.installEventFilter(self)  # habilita zoom
        layout.addRow("Resultado:", self.pubchem_result)
        
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
        """Opções de desenho (sem tamanho, zoom via scroll)."""
        group = QGroupBox("Opções de Desenho")
        v = QVBoxLayout()
        self.show_atom_labels = QCheckBox("Mostrar rótulos dos átomos")
        v.addWidget(self.show_atom_labels)
        self.show_hydrogens = QCheckBox("Mostrar hidrogênios")
        v.addWidget(self.show_hydrogens)
        self.apply_options_button = QPushButton("Redesenhar")
        self.apply_options_button.setMinimumHeight(35)
        self.apply_options_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.apply_options_button.clicked.connect(self.redraw_with_options)
        self.apply_options_button.setEnabled(False)
        v.addWidget(self.apply_options_button)
        group.setLayout(v)
        return group

    def create_molecule_library_section(self) -> QGroupBox:
        """Removido."""
        group = QGroupBox("(Desativado)")
        v = QVBoxLayout(); v.addWidget(QLabel("Biblioteca removida")); group.setLayout(v)
        return group

    def create_properties_section(self) -> QGroupBox:
        """Create detailed properties section."""
        group = QGroupBox("Propriedades Moleculares Detalhadas")
        layout = QVBoxLayout()
        
        # Properties text area
        self.detailed_properties = ZoomableTextEdit(base_point_size=11)
        self.detailed_properties.setReadOnly(True)
        self.detailed_properties.setMinimumHeight(300)
        # Removido font-size fixo
        self.detailed_properties.installEventFilter(self)
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
        group = QGroupBox("Estrutura 2D")
        layout = QVBoxLayout()
        # Scroll area para permitir ampliar além do tamanho do label
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(True)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(400)
        self.image_label.setMinimumWidth(500)
        self.image_label.setStyleSheet("border: 1px solid gray; background-color: white;")
        self.image_label.setText("Digite o nome do composto e clique em 'Buscar' ou 'Desenhar'\nScroll: Zoom | Duplo-clique: Reset")
        self.image_label.installEventFilter(self)
        self.image_scroll.setWidget(self.image_label)
        layout.addWidget(self.image_scroll)
        self.molecule_info = ZoomableTextEdit(base_point_size=11)
        self.molecule_info.setReadOnly(True)
        self.molecule_info.setMinimumHeight(200)
        self.molecule_info.setMaximumHeight(250)
        # Removido font-size fixo
        self.molecule_info.installEventFilter(self)
        self.register_text_widget(self.pubchem_result, 10)
        self.register_text_widget(self.molecule_info, 11)
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
        smiles = getattr(self, 'current_smiles', '').strip()
        print(f"[DEBUG] draw_molecule: smiles='{smiles}' (gera imagem base única)")
        if not smiles:
            name = self.pubchem_input.text().strip()
            if name:
                s, _ = self.fetch_smiles_from_pubchem(name)
                if s:
                    self.current_smiles = s
                    smiles = s
                else:
                    self.image_label.setText("Não foi possível obter SMILES.")
                    self.molecule_info.clear(); self.detailed_properties.clear(); return
            else:
                self.image_label.setText("Digite o nome do composto e clique em 'Buscar'")
                self.molecule_info.clear(); self.detailed_properties.clear(); return
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                mol = Chem.MolFromSmiles(smiles, sanitize=False)
                if mol: Chem.SanitizeMol(mol)
            if mol is None:
                self.image_label.setText("SMILES inválido."); return
            opts = Draw.rdMolDraw2D.MolDrawOptions()
            if self.show_atom_labels.isChecked():
                opts.addAtomIndices = True
            if self.show_hydrogens.isChecked():
                mol = Chem.AddHs(mol)
            # Gera imagem base FIXA (não depende do zoom) — zoom apenas escala este pixmap (como equations)
            img = Draw.MolToImage(mol, size=(self.base_size, self.base_size), options=opts)
            buf = io.BytesIO(); img.save(buf, format='PNG')
            qimg = QImage.fromData(buf.getvalue())
            self._base_mol_pixmap = QPixmap.fromImage(qimg)
            self.apply_image_zoom()  # aplica escala atual
            self.current_mol = mol
            self.molecule_info.setText(self.get_molecule_info(mol, smiles))
            self.view_3d_button.setEnabled(True)
            self.optimize_button.setEnabled(True)
            self.apply_options_button.setEnabled(True)
            self.export_sdf_button.setEnabled(True)
            self.export_mol_button.setEnabled(True)
            self.export_png_button.setEnabled(True)
            self.update_detailed_properties(mol, smiles)
        except Exception as e:
            self.image_label.setText(f"Erro ao desenhar: {e}")
            self.molecule_info.clear(); self.detailed_properties.clear(); self.disable_buttons()

    def search_pubchem(self):
        """Busca nome no PubChem, obtém SMILES (com fallbacks) e desenha automaticamente."""
        name = self.pubchem_input.text().strip()
        if not name:
            self.pubchem_result.setText("Digite um nome para buscar.")
            return
        self.pubchem_result.setText("Buscando no PubChem...")
        try:
            smiles, comp = self.fetch_smiles_from_pubchem(name)
            if smiles:
                self.current_smiles = smiles
                formula = ''
                iupac = ''
                cid = ''
                if comp:
                    formula = getattr(comp, 'molecular_formula', '') or getattr(comp, 'MolecularFormula', '')
                    iupac = getattr(comp, 'iupac_name', '') or getattr(comp, 'IUPACName', '')
                    cid = getattr(comp, 'cid', '')
                txt = f"✓ Composto: {iupac or name}\n"
                if formula:
                    txt += f"Fórmula: {formula}\n"
                txt += f"SMILES: {smiles}\n"
                if cid:
                    txt += f"PubChem CID: {cid}\n"
                txt += "Fonte: PubChem" if comp else "Fonte: Fallback"
                self.pubchem_result.setText(txt)
                self.draw_molecule()
            else:
                self.pubchem_result.setText("✗ Não encontrado ou sem SMILES.")
        except Exception as e:
            self.pubchem_result.setText(f"Erro: {e}")

    def fetch_smiles_from_pubchem(self, name: str):
        """Retorna (smiles, compound) com múltiplos fallbacks e logs detalhados.
        Passos:
          1. Normaliza nome (strip, lower, remove acentos simples)
          2. Tenta PubChem via get_compounds
          3. Tenta via CIDs + get_properties
          4. Tenta API REST direta (requests)
          5. Fallback local (dicionário de nomes comuns)
        """
        def _normalize(s: str):
            import unicodedata
            s2 = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
            return s2.strip()
        name_in = name
        name = _normalize(name)
        print(f"[DEBUG] fetch_smiles_from_pubchem: nome_original='{name_in}' normalizado='{name}'")

        COMMON_NAME_SMILES = {
            'glucose': 'OC[C@H]1O[C@@H](O)[C@H](O)[C@@H](O)[C@H]1O',
            'benzene': 'c1ccccc1',
            'toluene': 'Cc1ccccc1',
            'phenol': 'c1ccccc1O',
            'acetic acid': 'CC(=O)O',
            'ethanol': 'CCO',
            'caffeine': 'CN1C=NC2=C1C(=O)N(C(=O)N2C)C',
            'ibuprofen': 'CC(C)CC1=CC=C(C=C1)C(C)C(=O)O'
        }

        try:
            # 1) get_compounds
            try:
                compounds = pcp.get_compounds(name, 'name')
                print(f"[DEBUG] fetch_smiles_from_pubchem: get_compounds len={len(compounds)}")
            except Exception as e:
                print(f"[DEBUG] fetch_smiles_from_pubchem: exceção get_compounds: {e}")
                compounds = []
            if compounds:
                c = compounds[0]
                smiles = (getattr(c, 'isomeric_smiles', None) or getattr(c, 'canonical_smiles', None) or getattr(c, 'smiles', None))
                print(f"[DEBUG] fetch_smiles_from_pubchem: smiles primário='{smiles}'")
                if smiles:
                    return smiles.strip(), c
            # 2) CIDs + properties
            try:
                cids = pcp.get_cids(name, 'name')
                print(f"[DEBUG] fetch_smiles_from_pubchem: cids={cids}")
            except Exception as e:
                print(f"[DEBUG] fetch_smiles_from_pubchem: exceção get_cids: {e}")
                cids = []
            if cids:
                cid = cids[0]
                try:
                    props = pcp.get_properties(['IsomericSMILES','CanonicalSMILES','SMILES','MolecularFormula','IUPACName'], cid, 'cid')
                    print(f"[DEBUG] fetch_smiles_from_pubchem: props={props}")
                except Exception as e:
                    print(f"[DEBUG] fetch_smiles_from_pubchem: exceção get_properties: {e}")
                    props = []
                if props:
                    p = props[0]
                    smiles = p.get('IsomericSMILES') or p.get('CanonicalSMILES') or p.get('SMILES')
                    if smiles:
                        try:
                            comp = pcp.Compound.from_cid(cid)
                        except Exception:
                            comp = None
                        print(f"[DEBUG] fetch_smiles_from_pubchem: smiles via props='{smiles}'")
                        return smiles.strip(), comp
            # 3) API REST direta
            try:
                url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/IsomericSMILES,CanonicalSMILES,SMILES,Title/JSON"
                r = requests.get(url, timeout=8)
                print(f"[DEBUG] fetch_smiles_from_pubchem: REST status={r.status_code}")
                if r.ok:
                    data = r.json()
                    props = data.get('PropertyTable', {}).get('Properties', [])
                    if props:
                        first = props[0]
                        smiles = first.get('IsomericSMILES') or first.get('CanonicalSMILES') or first.get('SMILES')
                        if smiles:
                            print(f"[DEBUG] fetch_smiles_from_pubchem: REST smiles='{smiles}'")
                            return smiles.strip(), None
            except Exception as e:
                print(f"[DEBUG] fetch_smiles_from_pubchem: exceção REST: {e}")
            # 4) Fallback local
            key = name.lower()
            if key in COMMON_NAME_SMILES:
                smiles = COMMON_NAME_SMILES[key]
                print(f"[DEBUG] fetch_smiles_from_pubchem: fallback local para '{key}' -> '{smiles}'")
                return smiles, None
            print("[DEBUG] fetch_smiles_from_pubchem: nenhum SMILES encontrado")
            return None, None
        except Exception as e:
            print(f"[DEBUG] fetch_smiles_from_pubchem erro geral: {e}")
            return None, None

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

    def update_detailed_properties(self, mol, smiles):
        """Calcula e mostra propriedades detalhadas."""
        try:
            mw = Descriptors.MolWt(mol)
            formula = rdMolDescriptors.CalcMolFormula(mol)
            logp = Descriptors.MolLogP(mol)
            hbd = Descriptors.NumHDonors(mol)
            hba = Descriptors.NumHAcceptors(mol)
            tpsa = Descriptors.TPSA(mol)
            rot = Descriptors.NumRotatableBonds(mol)
            lip_v = sum([
                1 if mw>500 else 0,
                1 if logp>5 else 0,
                1 if hbd>5 else 0,
                1 if hba>10 else 0
            ])
            txt = (f"INFORMAÇÕES MOLECULARES\n" + "="*40 +
                   f"\nSMILES: {smiles}\nFórmula: {formula}\nPeso Molecular: {mw:.2f}\nLogP: {logp:.2f}\nHBA: {hba}  HBD: {hbd}" \
                   f"\nTPSA: {tpsa:.2f}\nRotáveis: {rot}\nLipinski Violações: {lip_v}/4")
            self.detailed_properties.setText(txt)
        except Exception as e:
            self.detailed_properties.setText(f"Erro propriedades: {e}")

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
                Busque um composto no PubChem ou gere um aleatório para visualizar em 3D
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
        self.pubchem_input.clear()
        self.current_smiles = ""
        self.image_label.setText("Digite o nome do composto e clique em 'Buscar' ou 'Desenhar'")
        self.molecule_info.clear()
        self.detailed_properties.clear()
        self.web_view.setHtml(self.get_empty_3d_html())
        self.disable_buttons()

    def disable_buttons(self):
        self.view_3d_button.setEnabled(False)
        self.optimize_button.setEnabled(False)
        self.apply_options_button.setEnabled(False)
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
        self.pubchem_input.setText(name)
        self.current_smiles = smiles
        self.draw_molecule()

    def redraw_with_options(self):
        if hasattr(self, 'current_mol') and self.current_mol:
            self.draw_molecule()

    def register_text_widget(self, widget, base_pt):
        """Mantido por compatibilidade; não usado para ZoomableTextEdit."""
        if isinstance(widget, ZoomableTextEdit):
            return
        for w, _ in self._text_widgets:
            if w is widget:
                return
        self._text_widgets.append((widget, base_pt))
        # Garantir captura de eventos do viewport (QTextEdit usa viewport interno para rolagem)
        widget.installEventFilter(self)
        if hasattr(widget, 'viewport'):
            widget.viewport().installEventFilter(self)

    def apply_text_zoom(self):
        for w, base in self._text_widgets:
            f = w.font()
            f.setPointSizeF(base * self.text_zoom_factor)
            w.setFont(f)

    def adjust_text_zoom(self, delta_steps):
        # delta_steps positivo aumenta
        self.text_zoom_factor *= (1.1 ** delta_steps)
        self.text_zoom_factor = max(0.5, min(self.text_zoom_factor, 3.0))
        self.apply_text_zoom()

    def eventFilter(self, obj, event):
        # Apenas tratamento de zoom da imagem agora
        img_label = getattr(self, 'image_label', None)
        if img_label is not None and obj == img_label:
            if event.type() == QEvent.MouseButtonDblClick:
                self.zoom_factor = 1.0
                self.apply_image_zoom()
                return True
            if event.type() == QEvent.Wheel:
                delta = event.angleDelta().y()
                step = 1.15 if (QApplication.keyboardModifiers() & Qt.ShiftModifier) else 1.10
                if delta > 0:
                    self.zoom_factor *= step
                else:
                    self.zoom_factor /= step
                self.zoom_factor = max(0.2, min(self.zoom_factor, 8.0))
                self.apply_image_zoom()
                return True
        return super().eventFilter(obj, event)

    def export_sdf(self):
        if not hasattr(self, 'current_mol') or self.current_mol is None:
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Salvar SDF", "", "SDF (*.sdf)")
        if filename:
            try:
                mol = Chem.Mol(self.current_mol)
                AllChem.EmbedMolecule(mol, AllChem.ETKDG())
                with open(filename, 'w') as f:
                    f.write(Chem.MolToMolBlock(mol))
                QMessageBox.information(self, "OK", "SDF salvo.")
            except Exception as e:
                QMessageBox.warning(self, "Erro", str(e))

    def export_mol(self):
        if not hasattr(self, 'current_mol') or self.current_mol is None:
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Salvar MOL", "", "MOL (*.mol)")
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(Chem.MolToMolBlock(self.current_mol))
                QMessageBox.information(self, "OK", "MOL salvo.")
            except Exception as e:
                QMessageBox.warning(self, "Erro", str(e))

    def export_png(self):
        if not hasattr(self, 'current_mol') or self.current_mol is None:
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Salvar PNG", "", "PNG (*.png)")
        if filename:
            try:
                # Regera imagem em alta resolução proporcional ao zoom (para qualidade melhor que simples upscale)
                size = int(self.base_size * self.zoom_factor)
                size = max(200, min(size, 3000))
                opts = Draw.rdMolDraw2D.MolDrawOptions()
                if self.show_atom_labels.isChecked():
                    opts.addAtomIndices = True
                mol = self.current_mol
                if self.show_hydrogens.isChecked():
                    mol = Chem.AddHs(mol)
                img = Draw.MolToImage(mol, size=(size, size), options=opts)
                img.save(filename, 'PNG')
                QMessageBox.information(self, "OK", "PNG salvo.")
            except Exception as e:
                QMessageBox.warning(self, "Erro", str(e))

    def optimize_geometry(self):
        if not hasattr(self, 'current_mol') or self.current_mol is None:
            return
        try:
            mol = Chem.Mol(self.current_mol)
            AllChem.EmbedMolecule(mol, AllChem.ETKDG())
            AllChem.UFFOptimizeMolecule(mol)
            sdf = Chem.MolToMolBlock(mol)
            self.web_view.setHtml(self.create_3d_html(sdf))
            self.style_combo.setEnabled(True)
            self.rotate_button.setEnabled(True)
            self.reset_view_button.setEnabled(True)
            self.bg_color_button.setEnabled(True)
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Otimização: {e}")

    def change_3d_style(self):
        style = self.style_combo.currentText()
        self.web_view.page().runJavaScript(f"window.changeStyle('{style}')")

    def change_bg_color(self):
        color = QColorDialog.getColor(QColor(255,255,255), self, "Cor de Fundo")
        if color.isValid():
            self.web_view.page().runJavaScript(f"window.changeBgColor('{color.name()}')")

    def apply_image_zoom(self):
        """Escala o pixmap base conforme zoom_factor usando tamanho original e permite rolagem."""
        if not self._base_mol_pixmap or not self.image_label:
            return
        target_w = max(50, int(self._base_mol_pixmap.width() * self.zoom_factor))
        target_h = max(50, int(self._base_mol_pixmap.height() * self.zoom_factor))
        scaled = self._base_mol_pixmap.scaled(target_w, target_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled)
        self.image_label.resize(scaled.size())

    def resizeEvent(self, event):
        # Ao redimensionar a janela, reescala a imagem mantendo o zoom atual
        self.apply_image_zoom()
        super().resizeEvent(event)
