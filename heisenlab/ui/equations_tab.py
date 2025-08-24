from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QGroupBox, QGridLayout, QMessageBox,
    QSplitter, QFrame, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use backend sem interface gráfica
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import tempfile
import os

try:
    from chempy import balance_stoichiometry, Reaction
    CHEMPY_AVAILABLE = True
except ImportError:
    CHEMPY_AVAILABLE = False


class EquationsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Splitter para dividir entrada e resultado
        splitter = QSplitter(Qt.Vertical)
        
        # Grupo de entrada
        input_group = QGroupBox("Entrada da Equação")
        input_layout = QVBoxLayout()
        
        # Instruções
        instructions = QLabel(
            "Digite a equação química completa usando → ou = para separar reagentes dos produtos.\n\n"
            "REGRAS IMPORTANTES:\n"
            "• Use a notação correta dos elementos: H2, O2, Cl2 (não CL2)\n"
            "• Primeira letra maiúscula, segunda minúscula: Cl, Br, Na\n"
            "• Separe compostos com + (exemplo: H2 + Cl2 → HCl)\n\n"
            "Exemplos válidos:\n"
            "• H2 + O2 → H2O\n"
            "• C2H6 + O2 → CO2 + H2O\n"
            "• H2 + Cl2 → HCl"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #cccccc; font-size: 14px; padding: 8px;")
        input_layout.addWidget(instructions)
        
        # Campo para equação completa
        equation_label = QLabel("Equação:")
        input_layout.addWidget(equation_label)
        
        self.equation_input = QLineEdit()
        self.equation_input.setPlaceholderText("Ex: H2 + Cl2 → HCl (use Cl, não CL)")
        input_layout.addWidget(self.equation_input)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        self.balance_button = QPushButton("Balancear Equação")
        self.balance_button.clicked.connect(self.balance_equation)
        buttons_layout.addWidget(self.balance_button)
        
        clear_button = QPushButton("Limpar")
        clear_button.clicked.connect(self.clear_inputs)
        buttons_layout.addWidget(clear_button)
        
        input_layout.addLayout(buttons_layout)
        
        input_group.setLayout(input_layout)
        splitter.addWidget(input_group)
        
        # Grupo de resultado
        result_group = QGroupBox("Resultado")
        result_layout = QVBoxLayout()
        
        # Área para exibir a equação renderizada
        self.equation_display = QLabel()
        self.equation_display.setAlignment(Qt.AlignCenter)
        self.equation_display.setMinimumHeight(120)
        self.equation_display.setMaximumHeight(180)
        self.equation_display.setStyleSheet("""
            border: 1px solid #555; 
            background-color: transparent; 
            margin: 5px; 
            border-radius: 5px;
            padding: 15px;
        """)
        result_layout.addWidget(self.equation_display)
        
        # Área de resultado textual
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(200)
        result_layout.addWidget(self.result_text)
        
        result_group.setLayout(result_layout)
        splitter.addWidget(result_group)
        
        # Exemplos
        examples_group = QGroupBox("Exemplos")
        examples_layout = QVBoxLayout()
        
        example_buttons_layout = QHBoxLayout()
        
        # Botões de exemplo
        example1_btn = QPushButton("Combustão do Metano")
        example1_btn.clicked.connect(lambda: self.load_example("CH4 + O2 → CO2 + H2O"))
        
        example2_btn = QPushButton("Combustão do Etanol")
        example2_btn.clicked.connect(lambda: self.load_example("C2H5OH + O2 → CO2 + H2O"))
        
        example3_btn = QPushButton("Síntese da Amônia")
        example3_btn.clicked.connect(lambda: self.load_example("N2 + H2 → NH3"))
        
        example4_btn = QPushButton("Fotossíntese")
        example4_btn.clicked.connect(lambda: self.load_example("CO2 + H2O → C6H12O6 + O2"))
        
        example_buttons_layout.addWidget(example1_btn)
        example_buttons_layout.addWidget(example2_btn)
        example_buttons_layout.addWidget(example3_btn)
        example_buttons_layout.addWidget(example4_btn)
        
        examples_layout.addLayout(example_buttons_layout)
        examples_group.setLayout(examples_layout)
        
        # Adicionar tudo ao layout principal
        main_layout.addWidget(splitter)
        main_layout.addWidget(examples_group)
        
        self.setLayout(main_layout)
        
        # Verificar se ChemPy está disponível
        if not CHEMPY_AVAILABLE:
            self.show_chempy_warning()

    def load_example(self, equation):
        """Carrega um exemplo no campo de entrada"""
        self.equation_input.setText(equation)

    def show_chempy_warning(self):
        """Mostra aviso se ChemPy não estiver disponível"""
        warning = QMessageBox()
        warning.setIcon(QMessageBox.Warning)
        warning.setWindowTitle("ChemPy não encontrado")
        warning.setText("A biblioteca ChemPy não foi encontrada.\n\nPara usar esta funcionalidade, instale com:\npip install chempy")
        warning.exec()
        
        self.balance_button.setEnabled(False)
        self.result_text.setPlainText("ChemPy não está instalado. Execute 'pip install chempy' para usar esta funcionalidade.")

    def parse_equation(self, equation_text):
        """Parse da equação química completa"""
        # Remove espaços extras
        equation_text = equation_text.strip()
        
        # Separadores possíveis
        separators = ['→', '->', '=', '⟶']
        separator_used = None
        
        for sep in separators:
            if sep in equation_text:
                separator_used = sep
                break
        
        if not separator_used:
            raise ValueError("Equação deve conter um separador (→, ->, = ou ⟶) entre reagentes e produtos")
        
        # Dividir em reagentes e produtos
        parts = equation_text.split(separator_used)
        if len(parts) != 2:
            raise ValueError("Equação deve ter exatamente um separador entre reagentes e produtos")
        
        reagents_text, products_text = parts
        
        # Parse dos compostos
        reagents = self.parse_compounds(reagents_text)
        products = self.parse_compounds(products_text)
        
        return reagents, products

    def parse_compounds(self, text):
        """Parse dos compostos a partir do texto"""
        if not text.strip():
            return set()
        
        # Remove espaços e divide por + ou vírgula
        import re
        compounds = re.split(r'[+,]', text)
        compounds = [compound.strip() for compound in compounds if compound.strip()]
        
        return set(compounds)

    def format_compound_for_latex(self, compound):
        """Formata um composto químico para LaTeX"""
        import re
        
        # Tratar grupos entre parênteses primeiro
        # Ex: Ca(OH)2 -> Ca(OH)_2
        paren_pattern = r'\)(\d+)'
        compound = re.sub(paren_pattern, r')_{\1}', compound)
        
        # Padrão para encontrar números após letras (mas não após parênteses)
        pattern = r'([A-Z][a-z]?)(\d+)(?!\})'
        
        def replace_subscript(match):
            element = match.group(1)
            number = match.group(2)
            return f"{element}_{{{number}}}"
        
        latex_compound = re.sub(pattern, replace_subscript, compound)
        
        # Tratar cargas iônicas
        charge_pattern = r'(\d*)([+-])$'
        def replace_charge(match):
            number = match.group(1)
            sign = match.group(2)
            if number:
                return f'^{{{number}{sign}}}'
            else:
                return f'^{{{sign}}}'
        
        latex_compound = re.sub(charge_pattern, replace_charge, latex_compound)
            
        return latex_compound

    def create_latex_equation(self, balanced_reagents, balanced_products):
        """Cria uma string LaTeX da equação balanceada"""
        # Formatar reagentes
        reagent_parts = []
        for compound, coeff in balanced_reagents.items():
            latex_compound = self.format_compound_for_latex(compound)
            if coeff == 1:
                reagent_parts.append(latex_compound)
            else:
                reagent_parts.append(f"{coeff}\\,{latex_compound}")
        
        # Formatar produtos
        product_parts = []
        for compound, coeff in balanced_products.items():
            latex_compound = self.format_compound_for_latex(compound)
            if coeff == 1:
                product_parts.append(latex_compound)
            else:
                product_parts.append(f"{coeff}\\,{latex_compound}")
        
        # Juntar com + e →
        reagents_str = " + ".join(reagent_parts)
        products_str = " + ".join(product_parts)
        
        return f"${reagents_str} \\rightarrow {products_str}$"

    def render_latex_equation(self, latex_equation):
        """Renderiza uma equação LaTeX e retorna como QPixmap"""
        try:
            # Configurar matplotlib para LaTeX
            plt.rcParams.update({
                'font.size': 140,
                'text.usetex': False,  # Usar mathtext ao invés de LaTeX completo
                'font.family': 'serif',
                'mathtext.fontset': 'cm'  # Computer Modern font
            })
            
            # Criar figura com fundo transparente
            fig, ax = plt.subplots(figsize=(14, 3))
            ax.text(0.5, 0.5, latex_equation, transform=ax.transAxes, 
                   fontsize=50, ha='center', va='center', color='white')
            ax.axis('off')
            
            # Fundo transparente
            fig.patch.set_facecolor('none')
            ax.set_facecolor('none')
            
            # Remover margens
            fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
            
            # Salvar em buffer com alta resolução
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', 
                       dpi=200, facecolor='none', edgecolor='none',
                       pad_inches=0.1, transparent=True)
            buf.seek(0)
            
            # Criar QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(buf.getvalue())
            
            plt.close(fig)
            buf.close()
            
            return pixmap
            
        except Exception as e:
            print(f"Erro ao renderizar LaTeX: {e}")
            return None

    def balance_equation(self):
        """Balanceia a equação química"""
        if not CHEMPY_AVAILABLE:
            self.show_chempy_warning()
            return
        
        try:
            # Obter equação
            equation_text = self.equation_input.text().strip()
            
            if not equation_text:
                self.result_text.setPlainText("Por favor, digite a equação química.")
                return
            
            # Parse da equação
            reagents, products = self.parse_equation(equation_text)
            
            if not reagents or not products:
                self.result_text.setPlainText("Por favor, verifique a entrada da equação.")
                return
            
            # Balancear usando ChemPy
            balanced_reagents, balanced_products = balance_stoichiometry(reagents, products)
            
            # Criar objeto Reaction para exibição
            reaction = Reaction(balanced_reagents, balanced_products)
            
            # Renderizar equação em LaTeX
            latex_equation = self.create_latex_equation(balanced_reagents, balanced_products)
            pixmap = self.render_latex_equation(latex_equation)
            
            if pixmap:
                # Escalar mantendo proporção
                scaled_pixmap = pixmap.scaled(
                    self.equation_display.size(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.equation_display.setPixmap(scaled_pixmap)
            else:
                # Fallback para texto simples
                self.equation_display.setText(str(reaction))
                self.equation_display.setStyleSheet(self.equation_display.styleSheet() + "font-size: 20px; font-weight: bold; color: white;")
            
            # Formatação do resultado textual
            result_text = "EQUAÇÃO BALANCEADA:\n"
            result_text += "=" * 50 + "\n\n"
            result_text += str(reaction) + "\n\n"
            
            result_text += "COEFICIENTES ESTEQUIOMÉTRICOS:\n"
            result_text += "=" * 50 + "\n\n"
            
            result_text += "Reagentes:\n"
            for compound, coeff in balanced_reagents.items():
                result_text += f"  {compound}: {coeff}\n"
            
            result_text += "\nProdutos:\n"
            for compound, coeff in balanced_products.items():
                result_text += f"  {compound}: {coeff}\n"
            
            # Adicionar informações adicionais
            result_text += "\n\nINFORMAÇÕES ADICIONAIS:\n"
            result_text += "=" * 50 + "\n\n"
            
            total_reagents = sum(balanced_reagents.values())
            total_products = sum(balanced_products.values())
            
            result_text += f"Total de moléculas reagentes: {total_reagents}\n"
            result_text += f"Total de moléculas produtos: {total_products}\n"
            result_text += f"Número de tipos de reagentes: {len(balanced_reagents)}\n"
            result_text += f"Número de tipos de produtos: {len(balanced_products)}\n"
            
            self.result_text.setPlainText(result_text)
            
        except Exception as e:
            error_message = f"ERRO AO BALANCEAR A EQUAÇÃO:\n\n{str(e)}\n\n"
            error_message += "VERIFICAÇÕES NECESSÁRIAS:\n"
            error_message += "• Notação dos elementos: use Cl (não CL), Br (não BR)\n"
            error_message += "• Primeira letra maiúscula, segunda minúscula\n"
            error_message += "• Separação com + entre compostos\n"
            error_message += "• Use → ou = para separar reagentes dos produtos\n\n"
            error_message += "EXEMPLOS CORRETOS:\n"
            error_message += "• H2 + Cl2 → HCl (não H2 + CL2 → HCL)\n"
            error_message += "• CH4 + O2 → CO2 + H2O\n"
            error_message += "• N2 + H2 → NH3\n"
            error_message += "• Ca + O2 → CaO\n\n"
            error_message += "NOTA: Utilize um dos exemplos abaixo para testar a funcionalidade."
            
            self.result_text.setPlainText(error_message)

    def clear_inputs(self):
        """Limpa os campos de entrada"""
        self.equation_input.clear()
        self.result_text.clear()
        self.equation_display.clear()
