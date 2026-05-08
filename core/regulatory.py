import requests
import urllib.parse

# --- ICH M7 Expert Knowledge Base (Expanded) ---
ASHBY_ALERTS = {
    "Aromatic Amine": {
        "smarts": "[NX3;H2,H1;!$(NC=O)]-c1ccc2ccccc2c1",
        "likelihood": "Certain",
        "mechanism": "Metabolic activation (N-hydroxylation) leads to nitrenium ions, which form DNA adducts at guanine residues.",
        "reference": "ICH M7(R2); Ashby & Tennant (1991)",
        "priority": "Critical",
        "expert_comment": "Primary aromatic amines on fused ring systems (e.g., naphthylamine) are classic DNA intercalators and covalent binders."
    },
    "Nitro Group": {
        "smarts": "[N+](=O)[O-]",
        "likelihood": "Plausible",
        "mechanism": "Reductive metabolism by bacterial nitroreductases to reactive hydroxylamines.",
        "reference": "ICH M7(R2); Kazius et al. (2005)",
        "priority": "High",
        "expert_comment": "Aromatic nitro groups undergo step-wise reduction; intermediates are potent electrophiles."
    },
    "Epoxide / Aziridine": {
        "smarts": "C1[O,N]C1",
        "likelihood": "Certain",
        "mechanism": "Direct alkylation of DNA bases via SN2 ring-opening mechanism.",
        "reference": "ICH M7(R2); Miller & Miller (1981)",
        "priority": "Critical",
        "expert_comment": "Highly strained 3-membered rings are inherently electrophilic and do not require metabolic activation."
    }
}

# --- Pharmacopeial & DMF Reference Database (USP/EP/DMF) ---
PHARMACOPEIA_DB = {
    "Atorvastatin": {
        "impurities": [
            {"id": "EP Impurity A", "name": "Desfluoro atorvastatin", "origin": "Synthesis By-product", "alert": "None", "class": 5},
            {"id": "EP Impurity D", "name": "Atorvastatin epoxide", "origin": "Oxidative Degradation", "alert": "Epoxide", "class": 3},
            {"id": "EP Impurity H", "name": "Atorvastatin lactone", "origin": "Cyclization / Synthesis", "alert": "None", "class": 5},
            {"id": "DMF Process 1", "name": "Methyl ester analog", "origin": "Esterification (DMF Step 4)", "alert": "None", "class": 5}
        ],
        "monograph_ref": "USP 43-NF 38; EP 10.0",
        "dmf_summary": "Controlled via Paal-Knorr synthesis; purge studies confirm removal of genotoxic Stage-1 intermediates."
    },
    "Rosuvastatin": {
        "impurities": [
            {"id": "USP RC A", "name": "Rosuvastatin Diastereomer", "origin": "Synthesis", "alert": "None", "class": 5},
            {"id": "USP RC B", "name": "Rosuvastatin Lactone", "origin": "Degradation", "alert": "None", "class": 5}
        ],
        "monograph_ref": "USP 42; EP 9.0",
        "dmf_summary": "Managed through selective reduction stages; diastereomers controlled at <0.15%."
    }
}

# --- Detailed Experimental Evidence Dossier (Experimental-based) ---
EXPERIMENTAL_DB = {
    "c1ccc(N)cc1": {
        "name": "Aniline",
        "assay_data": [
            {"test": "Ames (TA98)", "result": "Positive", "condition": "+S9 Activation", "source": "NTP TR-211"},
            {"test": "Ames (TA100)", "result": "Positive", "condition": "+S9 Activation", "source": "NTP TR-211"},
            {"test": "In Vitro MN", "result": "Positive", "condition": "Human Lymphocytes", "source": "IARC Vol 77"}
        ],
        "overall_conclusion": "Mutagenic under metabolic activation."
    },
    "Nc1ccccc1": { # Canonical
        "name": "Aniline",
        "assay_data": [
            {"test": "Ames (TA98)", "result": "Positive", "condition": "+S9 Activation", "source": "NTP TR-211"},
            {"test": "In Vitro MN", "result": "Positive", "condition": "Human Lymphocytes", "source": "IARC Vol 77"}
        ],
        "overall_conclusion": "Mutagenic under metabolic activation."
    }
}

def get_smiles_from_name(name):
    """Triple-Engine SMILES Resolver (PubChem Direct -> CID Search -> NIH CIR)"""
    clean_name = urllib.parse.quote(name.strip())
    
    # Engine 1: PubChem Direct Property
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/property/IsomericSMILES,CanonicalSMILES,MolecularFormula,IUPACName/JSON"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            props = data["PropertyTable"]["Properties"][0]
            smiles = props.get("IsomericSMILES") or props.get("CanonicalSMILES")
            if smiles:
                return {
                    "smiles": smiles,
                    "cid": props.get("CID"),
                    "formula": props.get("MolecularFormula"),
                    "iupac": props.get("IUPACName", "N/A"),
                    "source": "PubChem (Direct)"
                }
    except:
        pass

    # Engine 2: PubChem CID Search Fallback
    try:
        url_cid = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/cids/JSON"
        r_cid = requests.get(url_cid, timeout=5)
        if r_cid.status_code == 200:
            cid = r_cid.json()["IdentifierList"]["CID"][0]
            url_prop = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/IsomericSMILES,CanonicalSMILES,MolecularFormula,IUPACName/JSON"
            r_prop = requests.get(url_prop, timeout=5)
            if r_prop.status_code == 200:
                props = r_prop.json()["PropertyTable"]["Properties"][0]
                smiles = props.get("IsomericSMILES") or props.get("CanonicalSMILES")
                if smiles:
                    return {
                        "smiles": smiles,
                        "cid": props.get("CID"),
                        "formula": props.get("MolecularFormula"),
                        "iupac": props.get("IUPACName", "N/A"),
                        "source": "PubChem (CID Search)"
                    }
    except:
        pass

    # Engine 3: NIH CIR Fallback
    try:
        url_nih = f"https://cactus.nci.nih.gov/chemical/structure/{clean_name}/smiles"
        r_nih = requests.get(url_nih, timeout=5)
        if r_nih.status_code == 200:
            smiles = r_nih.text.strip()
            if smiles:
                return {
                    "smiles": smiles,
                    "cid": "N/A",
                    "formula": "N/A",
                    "iupac": "N/A",
                    "source": "NIH CIR"
                }
    except:
        pass
        
    return None

def get_pharmacopeia_info(name):
    """Retrieve USP/EP/DMF related substance information"""
    for drug, data in PHARMACOPEIA_DB.items():
        if name.lower() in drug.lower():
            return data
    return None

def get_experimental_detail(smiles):
    """Retrieve detailed assay evidence for a SMILES"""
    try:
        from rdkit import Chem
        mol = Chem.MolFromSmiles(smiles)
        can_smiles = Chem.MolToSmiles(mol, isomericSmiles=True)
        return EXPERIMENTAL_DB.get(can_smiles)
    except:
        return EXPERIMENTAL_DB.get(smiles)

# --- Known Carcinogens & Mutagens Database (Mock for Class 1 & 2) ---
KNOWN_MUTAGENS = {
    "Nc1ccccc1": {"class": 2, "name": "Aniline", "evidence": "Positive Ames (NTP TR-211)"},
    "c1ccc2c(c1)ccc3c2ccc4c3ccc5c4cccc5": {"class": 1, "name": "Benzo[a]pyrene", "evidence": "Known Carcinogen (IARC Group 1)"}
}

def assess_genotoxicity(smiles, drug_substance_smiles=None):
    """
    Full ICH M7 Categorization Logic:
    - Class 1: Known mutagenic carcinogens
    - Class 2: Known mutagens (unknown carcinogenicity)
    - Class 3: Alerting structure (unrelated to drug)
    - Class 4: Alerting structure (related to drug substance)
    - Class 5: No alerts
    """
    try:
        from rdkit import Chem
    except ImportError:
        return {"status": "error", "message": "RDKit not installed"}

    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return {"status": "error", "message": "Invalid SMILES"}

    can_smiles = Chem.MolToSmiles(mol, isomericSmiles=True)

    # 1. Check Known Database (Class 1 & 2)
    if can_smiles in KNOWN_MUTAGENS:
        m_info = KNOWN_MUTAGENS[can_smiles]
        return {
            "status": "alert",
            "class": f"ICH M7 Class {m_info['class']}",
            "alerts": [{"alert": "Known Mutagen/Carcinogen", "evidence": m_info['evidence']}]
        }

    # 2. Check Structural Alerts (Class 3, 4, 5)
    found_alerts = []
    for name, data in ASHBY_ALERTS.items():
        pat = Chem.MolFromSmarts(data["smarts"])
        if mol.HasSubstructMatch(pat):
            found_alerts.append({
                "alert": name,
                "likelihood": data["likelihood"],
                "mechanism": data["mechanism"],
                "reference": data["reference"],
                "expert_comment": data.get("expert_comment", "")
            })

    if not found_alerts:
        return {
            "status": "safe",
            "class": "ICH M7 Class 5",
            "alerts": []
        }

    # 3. Differentiate Class 3 vs Class 4
    if drug_substance_smiles:
        ds_mol = Chem.MolFromSmiles(drug_substance_smiles)
        if ds_mol:
            for alert in found_alerts:
                pat = Chem.MolFromSmarts(ASHBY_ALERTS[alert['alert']]["smarts"])
                if ds_mol.HasSubstructMatch(pat):
                    return {
                        "status": "controlled",
                        "class": "ICH M7 Class 4",
                        "alerts": found_alerts,
                        "note": "Alert shared with drug substance (Class 4)."
                    }

    return {
        "status": "alert",
        "class": "ICH M7 Class 3",
        "alerts": found_alerts
    }

# --- Degradation & Impurity Prediction Engine ---
DEGRADATION_RULES = {
    "Ester Hydrolysis": "[CX3:1](=[OX1:2])[OX2:3][CX4:4]>>[CX3:1](=[OX1:2])[OX2:3].[OX2][CX4:4]",
    "Amide Hydrolysis": "[CX3:1](=[OX1:2])[NX3:3][CX4:4]>>[CX3:1](=[OX1:2])[OX2].[NX3:3][CX4:4]",
    "N-Oxidation": "[NX3:1]([CX4:2])([CX4:3])[CX4:4]>>[NX3+:1]([CX4:2])([CX4:3])([CX4:4])[O-]",
    "O-Dealkylation": "[OX2:1][CX4:2]>>[OX2:1].[CX4:2][OH]",
    "Nitro Reduction": "[N+:1](=[O:2])([O-:3])>>[NX3:1]([H])[H]"
}

def predict_degradation_products(smiles):
    """Predict potential impurities via common degradation pathways"""
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
    except ImportError:
        return []
    
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return []
        
    products = []
    seen_smiles = {Chem.MolToSmiles(mol)}
    
    for name, smarts in DEGRADATION_RULES.items():
        rxn = AllChem.ReactionFromSmarts(smarts)
        outcomes = rxn.RunReactants((mol,))
        for outcome in outcomes:
            for prod_mol in outcome:
                try:
                    Chem.SanitizeMol(prod_mol)
                    psmiles = Chem.MolToSmiles(prod_mol)
                    if psmiles not in seen_smiles:
                        toxicity = assess_genotoxicity(psmiles)
                        products.append({
                            "pathway": name,
                            "smiles": psmiles,
                            "class": toxicity["class"],
                            "status": toxicity["status"]
                        })
                        seen_smiles.add(psmiles)
                except:
                    continue
    return products
