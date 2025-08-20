from mendeleev import element

def info_mendeleev(symbol):
    try:
        el = element(symbol)
        return {
            'name': el.name, 
            'atomic_number': el.atomic_number,
            'atomic_weight': el.atomic_weight if hasattr(el, 'atomic_weight') else el.atomic_mass,
            'valence': el.valence if hasattr(el, 'valence') else 'N/A'
        }
    except:
        return {'error': 'Element not found'}

# Todos os elementos da tabela periódica (1-118)
elements = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 
            'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca',
            'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
            'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr',
            'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn',
            'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd',
            'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
            'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
            'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th',
            'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm',
            'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds',
            'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og']

if __name__ == "__main__":
    print('Tabela Periódica Completa:')
    print('=' * 80)
    for symbol in elements:
        info = info_mendeleev(symbol)
        if 'error' not in info:
            print(f'{symbol:3} | {info["name"]:15} | Z={info["atomic_number"]:3} | Massa={info["atomic_weight"]:8.3f} | Valência={info["valence"]}')
        else:
            print(f'{symbol:3} | Erro ao obter informações')
