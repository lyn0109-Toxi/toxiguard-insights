import requests
import urllib.parse
from rdkit import Chem

def verify_compound(name):
    print(f"\n--- Verifying: {name} ---")
    clean_name = urllib.parse.quote(name.strip())
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/property/CID,IsomericSMILES,MolecularFormula,IUPACName/JSON"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            props = data["PropertyTable"]["Properties"][0]
            smiles = props.get("IsomericSMILES") or props.get("CanonicalSMILES")
            cid = props.get("CID")
            formula = props.get("MolecularFormula")
            iupac = props.get("IUPACName")
            
            print(f"✅ CID: {cid}")
            print(f"✅ Formula: {formula}")
            print(f"✅ IUPAC: {iupac}")
            print(f"✅ SMILES: {smiles}")
            
            # Check for corrupted patterns like '@@HCC' or missing brackets
            if "@@" in smiles and "[" not in smiles:
                print("❌ ERROR: SMILES appears corrupted (missing brackets)!")
            elif Chem.MolFromSmiles(smiles):
                print("✅ RDKit: SMILES is Chemically Valid.")
            else:
                print("❌ RDKit: SMILES is INVALID.")
        else:
            print(f"❌ Failed to fetch data: {response.status_code}")
    except Exception as e:
        print(f"❌ Technical Exception: {str(e)}")

verify_compound("rosuvastatin")
verify_compound("atorvastatin")
verify_compound("aspirin")
