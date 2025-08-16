"""
Módulo para busca de compostos químicos no arquivo bluebook.txt
Baseado na análise da estrutura do IUPAC Blue Book v3
"""
import os
import re
from typing import Dict, List, Optional, Tuple


class BluebookSearch:
    """Classe para buscar compostos químicos no arquivo bluebook.txt"""
    
    def __init__(self, bluebook_path: str = None):
        """
        Inicializa o buscador do bluebook
        
        Args:
            bluebook_path: Caminho para o arquivo bluebook.txt
        """
        if bluebook_path is None:
            # Caminho padrão relativo ao projeto
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            bluebook_path = os.path.join(project_root, "assets", "bluebook.txt")
        
        self.bluebook_path = bluebook_path
        self._content_cache = None
        
        # Base de dados expandida com compostos conhecidos do bluebook
        self.known_compounds = {
            # Hidrocarbonetos básicos
            "methane": {"formula": "CH4", "smiles": "C", "type": "alkane"},
            "ethane": {"formula": "C2H6", "smiles": "CC", "type": "alkane"},
            "propane": {"formula": "C3H8", "smiles": "CCC", "type": "alkane"},
            "butane": {"formula": "C4H10", "smiles": "CCCC", "type": "alkane"},
            "pentane": {"formula": "C5H12", "smiles": "CCCCC", "type": "alkane"},
            "hexane": {"formula": "C6H14", "smiles": "CCCCCC", "type": "alkane"},
            
            # Compostos aromáticos
            "benzene": {"formula": "C6H6", "smiles": "c1ccccc1", "type": "aromatic"},
            "toluene": {"formula": "C7H8", "smiles": "Cc1ccccc1", "type": "aromatic"},
            "phenol": {"formula": "C6H5OH", "smiles": "Oc1ccccc1", "type": "phenol"},
            "styrene": {"formula": "C8H8", "smiles": "C=Cc1ccccc1", "type": "aromatic"},
            "vinylbenzene": {"formula": "C8H8", "smiles": "C=Cc1ccccc1", "type": "aromatic"},
            "ethenylbenzene": {"formula": "C8H8", "smiles": "C=Cc1ccccc1", "type": "aromatic"},
            "quinoline": {"formula": "C9H7N", "smiles": "c1ccc2ncccc2c1", "type": "heterocyclic"},
            "biphenyl": {"formula": "C12H10", "smiles": "c1ccc(cc1)c2ccccc2", "type": "aromatic"},
            
            # Álcoois
            "ethanol": {"formula": "C2H5OH", "smiles": "CCO", "type": "alcohol"},
            "methanol": {"formula": "CH3OH", "smiles": "CO", "type": "alcohol"},
            "propanol": {"formula": "C3H7OH", "smiles": "CCCO", "type": "alcohol"},
            "butanol": {"formula": "C4H9OH", "smiles": "CCCCO", "type": "alcohol"},
            
            # Ácidos carboxílicos
            "acetic acid": {"formula": "CH3COOH", "smiles": "CC(=O)O", "type": "carboxylic acid"},
            "ethanoic acid": {"formula": "CH3COOH", "smiles": "CC(=O)O", "type": "carboxylic acid"},
            "formic acid": {"formula": "HCOOH", "smiles": "C(=O)O", "type": "carboxylic acid"},
            "propanoic acid": {"formula": "C2H5COOH", "smiles": "CCC(=O)O", "type": "carboxylic acid"},
            
            # Cetonas
            "acetone": {"formula": "C3H6O", "smiles": "CC(=O)C", "type": "ketone"},
            "propan-2-one": {"formula": "C3H6O", "smiles": "CC(=O)C", "type": "ketone"},
            "butan-2-one": {"formula": "C4H8O", "smiles": "CCC(=O)C", "type": "ketone"},
            
            # Aldeídos
            "formaldehyde": {"formula": "CH2O", "smiles": "C=O", "type": "aldehyde"},
            "methanal": {"formula": "CH2O", "smiles": "C=O", "type": "aldehyde"},
            "acetaldehyde": {"formula": "C2H4O", "smiles": "CC=O", "type": "aldehyde"},
            "ethanal": {"formula": "C2H4O", "smiles": "CC=O", "type": "aldehyde"},
            
            # Cíclicos
            "cyclohexane": {"formula": "C6H12", "smiles": "C1CCCCC1", "type": "cycloalkane"},
            "cyclopentane": {"formula": "C5H10", "smiles": "C1CCCC1", "type": "cycloalkane"},
            "cyclohexene": {"formula": "C6H10", "smiles": "C1CCC=CC1", "type": "cycloalkene"},
            
            # Heterocíclicos
            "pyridine": {"formula": "C5H5N", "smiles": "c1ccncc1", "type": "heterocyclic"},
            "thiazole": {"formula": "C3H3NS", "smiles": "c1cscn1", "type": "heterocyclic"},
            "oxazole": {"formula": "C3H3NO", "smiles": "c1cocn1", "type": "heterocyclic"},
            
            # Ésteres
            "ethyl acetate": {"formula": "C4H8O2", "smiles": "CCOC(=O)C", "type": "ester"},
            "methyl acetate": {"formula": "C3H6O2", "smiles": "COC(=O)C", "type": "ester"},
            
            # Aminas
            "methylamine": {"formula": "CH3NH2", "smiles": "CN", "type": "amine"},
            "ethylamine": {"formula": "C2H5NH2", "smiles": "CCN", "type": "amine"},
            "aniline": {"formula": "C6H5NH2", "smiles": "Nc1ccccc1", "type": "aromatic amine"},
            
            # Éteres
            "diethyl ether": {"formula": "C4H10O", "smiles": "CCOCC", "type": "ether"},
            "dimethyl ether": {"formula": "C2H6O", "smiles": "COC", "type": "ether"},
        }
        
    def _load_content(self) -> str:
        """Carrega o conteúdo do arquivo bluebook.txt"""
        if self._content_cache is None:
            try:
                # Verifica se o arquivo existe
                if not os.path.exists(self.bluebook_path):
                    print(f"Arquivo bluebook.txt não encontrado em: {self.bluebook_path}")
                    self._content_cache = ""
                    return self._content_cache
                
                # Carrega apenas uma parte do arquivo para evitar travamentos
                with open(self.bluebook_path, 'r', encoding='utf-8') as f:
                    # Lê apenas os primeiros 500KB para evitar travamentos
                    self._content_cache = f.read(500000)
            except Exception as e:
                print(f"Erro ao carregar bluebook.txt: {e}")
                self._content_cache = ""
        return self._content_cache
    
    def search_compound(self, compound_name: str) -> Dict[str, any]:
        """
        Busca um composto no bluebook.txt com análise estrutural melhorada
        
        Args:
            compound_name: Nome do composto a ser buscado
            
        Returns:
            Dicionário com informações do composto encontrado
        """
        if not compound_name.strip():
            return {"found": False, "message": "Nome do composto não pode estar vazio"}
        
        # Normaliza o nome para busca
        search_name = compound_name.strip().lower()
        
        # Primeiro, verifica na base de dados conhecidos
        if search_name in self.known_compounds:
            compound_data = self.known_compounds[search_name]
            return {
                "found": True,
                "name": compound_name,
                "formula": compound_data["formula"],
                "smiles": compound_data["smiles"],
                "type": compound_data["type"],
                "context": f"Composto encontrado na base de dados: {compound_data['type']}",
                "iupac_info": "Composto conhecido do IUPAC Blue Book",
                "source": "known_database"
            }
        
        # Se não encontrado, busca no arquivo bluebook.txt
        content = self._load_content()
        if not content:
            return {"found": False, "message": "Erro ao carregar arquivo bluebook.txt"}
        
        # Busca padrões específicos do bluebook
        result = self._search_bluebook_patterns(content, search_name, compound_name)
        
        if result["found"]:
            return result
        else:
            # Busca parcial e sugestões
            suggestions = self._find_similar_compounds(search_name)
            message = f"Composto '{compound_name}' não encontrado no Blue Book"
            if suggestions:
                message += f"\n\nSugestões: {', '.join(suggestions[:5])}"
            
            return {"found": False, "message": message}
    
    def _search_bluebook_patterns(self, content: str, search_name: str, original_name: str) -> Dict[str, any]:
        """
        Busca padrões específicos baseados na estrutura do bluebook
        """
        # Limita o conteúdo para busca mais rápida
        if len(content) > 100000:
            content = content[:100000]
        
        patterns = [
            self._search_examples_section,
            self._search_pin_definitions,
            self._search_systematic_names,
        ]
        
        for pattern_func in patterns:
            try:
                result = pattern_func(content, search_name, original_name)
                if result["found"]:
                    return result
            except Exception as e:
                print(f"Erro na busca por padrão: {e}")
                continue
        
        return {"found": False}
    
    def _search_examples_section(self, content: str, search_name: str, original_name: str) -> Dict[str, any]:
        """Busca na seção de exemplos do bluebook"""
        # Padrão: Examples: seguido de estruturas e nomes
        example_pattern = r'Examples?:\s*\n(.*?)(?=\n\n|\nP-|\n[A-Z]|\Z)'
        
        for match in re.finditer(example_pattern, content, re.IGNORECASE | re.DOTALL):
            section_text = match.group(1)
            
            # Busca o nome no contexto
            if search_name in section_text.lower():
                lines = section_text.split('\n')
                for i, line in enumerate(lines):
                    if search_name in line.lower():
                        # Extrai contexto ao redor
                        context_start = max(0, i-3)
                        context_end = min(len(lines), i+5)
                        context_lines = lines[context_start:context_end]
                        context = '\n'.join(context_lines)
                        
                        # Busca fórmula molecular nas linhas próximas
                        formula = self._extract_formula_from_context(context_lines, i - context_start)
                        
                        # Determina tipo IUPAC
                        iupac_info = self._determine_iupac_type(line, context)
                        
                        # Busca SMILES conhecido
                        smiles = self._get_known_smiles(search_name, formula)
                        
                        return {
                            "found": True,
                            "name": original_name,
                            "formula": formula,
                            "smiles": smiles,
                            "context": context,
                            "iupac_info": iupac_info,
                            "source": "examples_section"
                        }
        
        return {"found": False}
    
    def _search_pin_definitions(self, content: str, search_name: str, original_name: str) -> Dict[str, any]:
        """Busca definições de PIN (Preferred IUPAC Names)"""
        # Padrão para PINs
        pin_patterns = [
            rf'{re.escape(search_name)}\s*\([^)]*PIN[^)]*\)',
            rf'{re.escape(search_name)}\s*\([^)]*preferred\s+IUPAC\s+name[^)]*\)',
        ]
        
        for pattern in pin_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                context = self._get_context_around_match(content, match.start(), match.end(), 200)
                formula = self._extract_formula_from_text(context)
                smiles = self._get_known_smiles(search_name, formula)
                
                return {
                    "found": True,
                    "name": original_name,
                    "formula": formula,
                    "smiles": smiles,
                    "context": context,
                    "iupac_info": "Preferred IUPAC Name (PIN)",
                    "source": "pin_definition"
                }
        
        return {"found": False}
    
    def _search_systematic_names(self, content: str, search_name: str, original_name: str) -> Dict[str, any]:
        """Busca nomes sistemáticos"""
        # Padrão para nomes sistemáticos
        systematic_pattern = rf'{re.escape(search_name)}.*?systematic.*?name'
        
        for match in re.finditer(systematic_pattern, content, re.IGNORECASE | re.DOTALL):
            if match.end() - match.start() < 300:  # Limita tamanho da correspondência
                context = self._get_context_around_match(content, match.start(), match.end(), 150)
                formula = self._extract_formula_from_text(context)
                smiles = self._get_known_smiles(search_name, formula)
                
                return {
                    "found": True,
                    "name": original_name,
                    "formula": formula,
                    "smiles": smiles,
                    "context": context,
                    "iupac_info": "Systematic Name",
                    "source": "systematic_name"
                }
        
        return {"found": False}
    
    def _search_retained_names(self, content: str, search_name: str, original_name: str) -> Dict[str, any]:
        """Busca nomes retidos (retained names)"""
        retained_pattern = rf'{re.escape(search_name)}.*?retained.*?name'
        
        for match in re.finditer(retained_pattern, content, re.IGNORECASE | re.DOTALL):
            if match.end() - match.start() < 300:
                context = self._get_context_around_match(content, match.start(), match.end(), 150)
                formula = self._extract_formula_from_text(context)
                smiles = self._get_known_smiles(search_name, formula)
                
                return {
                    "found": True,
                    "name": original_name,
                    "formula": formula,
                    "smiles": smiles,
                    "context": context,
                    "iupac_info": "Retained Name",
                    "source": "retained_name"
                }
        
        return {"found": False}
    
    def _search_formula_contexts(self, content: str, search_name: str, original_name: str) -> Dict[str, any]:
        """Busca contextos que contenham fórmulas moleculares"""
        # Padrão para linhas com fórmulas seguidas de nomes
        formula_name_pattern = r'([A-Z][a-z]?[0-9]*(?:[A-Z][a-z]?[0-9]*)*)\s*\n.*?' + re.escape(search_name)
        
        for match in re.finditer(formula_name_pattern, content, re.IGNORECASE | re.DOTALL):
            if match.end() - match.start() < 200:
                formula = match.group(1)
                context = self._get_context_around_match(content, match.start(), match.end(), 100)
                smiles = self._get_known_smiles(search_name, formula)
                
                return {
                    "found": True,
                    "name": original_name,
                    "formula": formula,
                    "smiles": smiles,
                    "context": context,
                    "iupac_info": "Encontrado com fórmula molecular",
                    "source": "formula_context"
                }
        
        return {"found": False}
    
    def _extract_formula_from_context(self, lines: List[str], target_line_idx: int) -> Optional[str]:
        """Extrai fórmula molecular do contexto de linhas"""
        # Busca nas linhas próximas à linha alvo
        search_range = range(max(0, target_line_idx - 2), min(len(lines), target_line_idx + 3))
        
        for i in search_range:
            formula = self._extract_formula_from_text(lines[i])
            if formula and self._is_valid_molecular_formula(formula):
                return formula
        
        return None
    
    def _extract_formula_from_text(self, text: str) -> Optional[str]:
        """Extrai fórmula molecular de um texto"""
        # Padrões para fórmulas moleculares
        formula_patterns = [
            r'\bC[0-9]*H[0-9]*[A-Z]*[0-9]*\b',  # CH4, C2H6, etc.
            r'\b[A-Z][a-z]?[0-9]*(?:[A-Z][a-z]?[0-9]*)*\b'  # Fórmula geral
        ]
        
        for pattern in formula_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if self._is_valid_molecular_formula(match):
                    return match
        
        return None
    
    def _is_valid_molecular_formula(self, formula: str) -> bool:
        """Verifica se uma string é uma fórmula molecular válida"""
        if len(formula) < 2:
            return False
        
        # Deve começar com elemento químico
        if not formula[0].isupper():
            return False
        
        # Deve conter pelo menos um número ou H
        if not any(c.isdigit() or c == 'H' for c in formula):
            return False
        
        # Não deve ser apenas um elemento
        if formula in ['C', 'H', 'N', 'O', 'S', 'P', 'F', 'Cl', 'Br', 'I']:
            return False
        
        return True
    
    def _determine_iupac_type(self, line: str, context: str) -> str:
        """Determina o tipo de nome IUPAC baseado no contexto"""
        line_lower = line.lower()
        context_lower = context.lower()
        
        if 'pin' in line_lower or 'preferred iupac name' in line_lower:
            return "Preferred IUPAC Name (PIN)"
        elif 'retained name' in context_lower:
            return "Retained Name"
        elif 'systematic' in context_lower:
            return "Systematic Name"
        elif 'preselected' in context_lower:
            return "Preselected Name"
        else:
            return "IUPAC Name"
    
    def _get_context_around_match(self, content: str, start: int, end: int, window: int = 200) -> str:
        """Obtém contexto ao redor de uma correspondência"""
        context_start = max(0, start - window)
        context_end = min(len(content), end + window)
        return content[context_start:context_end]
    
    def _get_known_smiles(self, name: str, formula: str = None) -> Optional[str]:
        """Obtém SMILES conhecido para um composto"""
        if name in self.known_compounds:
            return self.known_compounds[name]["smiles"]
        
        # Busca por sinônimos
        for compound, data in self.known_compounds.items():
            if name in compound or compound in name:
                return data["smiles"]
        
        return None
    
    def _find_similar_compounds(self, search_name: str) -> List[str]:
        """Encontra compostos similares para sugestões"""
        suggestions = []
        
        # Busca em compostos conhecidos
        for compound in self.known_compounds.keys():
            if (compound.startswith(search_name) or 
                search_name in compound or 
                self._similar_strings(search_name, compound)):
                suggestions.append(compound)
        
        return sorted(suggestions)[:10]
    
    def _similar_strings(self, s1: str, s2: str, threshold: float = 0.6) -> bool:
        """Verifica se duas strings são similares"""
        if len(s1) < 3 or len(s2) < 3:
            return False
        
        # Cálculo simples de similaridade baseado em caracteres comuns
        common_chars = set(s1.lower()) & set(s2.lower())
        similarity = len(common_chars) / max(len(set(s1.lower())), len(set(s2.lower())))
        
        return similarity >= threshold
    
    def get_suggestions(self, partial_name: str, limit: int = 10) -> List[str]:
        """
        Retorna sugestões baseadas em nome parcial
        
        Args:
            partial_name: Nome parcial para buscar sugestões
            limit: Número máximo de sugestões
            
        Returns:
            Lista de sugestões de nomes
        """
        if len(partial_name) < 2:
            return []
        
        partial_lower = partial_name.lower()
        suggestions = []
        
        # Busca em compostos conhecidos
        for compound in self.known_compounds.keys():
            if compound.startswith(partial_lower):
                suggestions.append(compound)
        
        return sorted(suggestions)[:limit]


# Funções utilitárias para usar na interface
def search_compound_in_bluebook(compound_name: str) -> Dict[str, any]:
    """
    Função utilitária para buscar composto no bluebook
    
    Args:
        compound_name: Nome do composto a ser buscado
        
    Returns:
        Dicionário com informações do composto
    """
    searcher = BluebookSearch()
    return searcher.search_compound(compound_name)


def get_compound_suggestions(partial_name: str) -> List[str]:
    """
    Função utilitária para obter sugestões de compostos
    
    Args:
        partial_name: Nome parcial do composto
        
    Returns:
        Lista de sugestões
    """
    searcher = BluebookSearch()
    return searcher.get_suggestions(partial_name)
