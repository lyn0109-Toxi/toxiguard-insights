import sys
# Validation Script for ToxiScope QSAR Engine
try:
    from rdkit import Chem
    from rdkit.Chem import Draw
    print("RDKit Version:", Chem.rdBase.rdkitVersion)
except ImportError:
    print("ERROR: RDKit not found.")
    sys.exit(1)

ASHBY_ALERTS = {
    "Aromatic Amine": "[c,C;!$(C=O)]-N",
    "Nitro Group": "[N+](=O)[O-]",
    "Epoxide / Aziridine": "C1[O,N]C1",
    "Alkyl Halide": "[C;!$(C=O)][Cl,Br,I]",
}

test_molecules = [
    {"name": "Telmisartan", "smiles": "CCCC1=NC2=C(N1CC3=CC=C(C=C3)C4=CC=CC=C4C(=O)O)C=C(C=C2C)C5=NC6=CC=CC=C6N5C", "expected": "Clean"},
    {"name": "Aniline", "smiles": "c1ccc(N)cc1", "expected": "Aromatic Amine"},
    {"name": "Nitrobenzene", "smiles": "c1ccc(cc1)[N+](=O)[O-]", "expected": "Nitro Group"},
    {"name": "Ethylene Oxide", "smiles": "C1OC1", "expected": "Epoxide / Aziridine"},
]

print("\n--- Starting Engine Validation ---")
for test in test_molecules:
    mol = Chem.MolFromSmiles(test["smiles"])
    if not mol:
        print(f"FAILED: Could not parse {test['name']}")
        continue
    
    found = []
    for name, smarts in ASHBY_ALERTS.items():
        pat = Chem.MolFromSmarts(smarts)
        if mol.HasSubstructMatch(pat):
            found.append(name)
    
    result_status = "ALERT" if found else "CLEAN"
    print(f"[{test['name']}] Status: {result_status} | Found: {found} | Expected: {test['expected']}")
