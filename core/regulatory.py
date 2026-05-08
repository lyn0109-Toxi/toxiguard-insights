import requests
import urllib.parse

# --- ICH M7 Expert Knowledge Base (Expanded) ---
ASHBY_ALERTS = {
    "Aromatic Amine": {
        "smarts": "[NX3;H2,H1;!$(NC=O)]-c1ccccc1",
        "likelihood": "Certain",
        "mechanism": "Metabolic activation to nitrenium ions, causing DNA adducts.",
        "reference": "ICH M7(R2); Ashby & Tennant (1991)",
        "priority": "Critical",
        "expert_comment": "Primary aromatic amines (Anilines) are key structural alerts for mutagenicity."
    },
    "Fused-Ring Aromatic Amine": {
        "smarts": "[NX3;H2,H1;!$(NC=O)]-c1ccc2ccccc2c1",
        "likelihood": "Certain",
        "mechanism": "Planar fused rings intercalate into DNA; amine group forms covalent bonds.",
        "reference": "IARC Monograph Vol 77",
        "priority": "Critical",
        "expert_comment": "Naphthylamines and similar fused systems are potent carcinogens."
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
    },
    "Brivaracetam": {
        "impurities": [
            {"id": "Impurity 1", "name": "4-Propyl-pyrrolidin-2-one", "origin": "Synthesis", "alert": "None", "class": 5},
            {"id": "Impurity 2", "name": "Brivaracetam Acid", "origin": "Hydrolysis", "alert": "None", "class": 5},
            {"id": "PGI-1", "name": "2-Bromobutyryl chloride", "origin": "Process Reagent", "alert": "Alkyl Halide", "class": 3}
        ],
        "monograph_ref": "FDA Approval 2016; EP 10.0",
        "dmf_summary": "Mutagenicity assessment performed for process-related intermediates. PGI-1 controlled via purge study (ICH M7 Option 4)."
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

# --- Statistical-based QSAR Simulation (Mock) ---
# In a real scenario, this would use a machine learning model or fragment-based stats.
STATISTICAL_ALERTS = {
    "Aromatic amine fragment count": {"weight": 0.85, "alert": "Aromatic Amine"},
    "Nitro group density": {"weight": 0.78, "alert": "Nitro Group"},
    "Halogenated alkyl": {"weight": 0.65, "alert": "Alkyl Halide"}
}

def get_statistical_assessment(smiles):
    """Simulate a statistical-based QSAR methodology (Method 2)"""
    # Simple fragment-based probability simulation
    results = []
    if "N" in smiles and "c1ccccc1" in smiles:
        results.append({"method": "Statistical (SAR)", "alert": "Aromatic Amine", "probability": 0.82})
    if "N(=O)=O" in smiles or "[N+](=O)[O-]" in smiles:
        results.append({"method": "Statistical (SAR)", "alert": "Nitro Group", "probability": 0.75})
    return results

def calculate_ttc_limit(daily_dose_mg, duration_days=3650):
    """Calculate TTC (Threshold of Toxicological Concern) based on ICH M7"""
    # Basic TTC rule: 1.5 ug/day for lifetime exposure
    # Temporary threshold for shorter durations:
    if duration_days <= 30: limit_ug = 120
    elif duration_days <= 365: limit_ug = 20
    elif duration_days <= 3650: limit_ug = 10
    else: limit_ug = 1.5
    
    if daily_dose_mg > 0:
        limit_ppm = (limit_ug / daily_dose_mg)
        return {"limit_ug_day": limit_ug, "limit_ppm": round(limit_ppm, 2)}
    return {"limit_ug_day": limit_ug, "limit_ppm": "N/A"}

def assess_genotoxicity(smiles, drug_substance_smiles=None, daily_dose_mg=10):
    """
    Enhanced ICH M7 Categorization Logic with Dual Methodology:
    """
    try:
        from rdkit import Chem
    except ImportError:
        return {"status": "error", "message": "RDKit not installed"}

    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return {"status": "error", "message": "Invalid SMILES"}

    can_smiles = Chem.MolToSmiles(mol, isomericSmiles=True)

    # 0. Pre-calculate TTC info
    ttc_info = calculate_ttc_limit(daily_dose_mg)

    # 1. Check Known Database (Class 1 & 2)
    if can_smiles in KNOWN_MUTAGENS:
        m_info = KNOWN_MUTAGENS[can_smiles]
        return {
            "status": "alert",
            "class": f"ICH M7 Class {m_info['class']}",
            "alerts": [{
                "method": "Historical Evidence",
                "alert": "Known Mutagen/Carcinogen", 
                "evidence": m_info['evidence'],
                "mechanism": "Confirmed in historical toxicology studies.",
                "reference": m_info['evidence']
            }],
            "ttc_info": ttc_info
        }

    # 2. Methodology 1: Expert Rule-based (Ashby)
    expert_alerts = []
    for name, data in ASHBY_ALERTS.items():
        pat = Chem.MolFromSmarts(data["smarts"])
        if mol.HasSubstructMatch(pat):
            expert_alerts.append({
                "method": "Expert Rule-based",
                "alert": name,
                "likelihood": data["likelihood"],
                "mechanism": data["mechanism"],
                "reference": data["reference"]
            })

    # 3. Methodology 2: Statistical-based (Mock)
    stat_alerts = get_statistical_assessment(smiles)

    all_alerts = expert_alerts + stat_alerts
    ttc_info = calculate_ttc_limit(daily_dose_mg)

    if not all_alerts:
        return {
            "status": "safe",
            "class": "ICH M7 Class 5",
            "alerts": [],
            "ttc_info": ttc_info
        }

    # 4. Final Classification Logic
    # Class 3: Alerting structure (unrelated to drug)
    # Class 4: Alerting structure (shared with drug)
    final_class = "ICH M7 Class 3"
    if drug_substance_smiles:
        ds_mol = Chem.MolFromSmiles(drug_substance_smiles)
        if ds_mol:
            for alert in expert_alerts:
                pat = Chem.MolFromSmarts(ASHBY_ALERTS[alert['alert']]["smarts"])
                if ds_mol.HasSubstructMatch(pat):
                    final_class = "ICH M7 Class 4"
                    break

    return {
        "status": "alert" if final_class == "ICH M7 Class 3" else "controlled",
        "class": final_class,
        "alerts": all_alerts,
        "ttc_info": ttc_info
    }

# --- Professional Degradation & Forced Degradation Library (Expanded) ---
DEGRADATION_RULES = {
    "Acid Hydrolysis (Ester)": {
        "smarts": "[CX3:1](=[OX1:2])[OX2:3][CX4:4]>>[CX3:1](=[OX1:2])[OX2:3].[OX2][CX4:4]",
        "condition": "Acidic stress (pH < 2), Heat",
        "rationale": "Acid-catalyzed nucleophilic substitution at the carbonyl center. High risk for prodrugs and polyesters.",
        "reg_significance": "Commonly requires qualification if >0.15% (ICH Q3A).",
        "risk_level": "Critical"
    },
    "Base Hydrolysis (Amide)": {
        "smarts": "[CX3:1](=[OX1:2])[NX3:3][CX4:4]>>[CX3:1](=[OX1:2])[OX2].[NX3:3][CX4:4]",
        "condition": "Basic stress (pH > 10), Prolonged Heat",
        "rationale": "Base-promoted hydrolysis of stable amide bonds. Often seen in penicillin/cephalosporin class drugs.",
        "reg_significance": "Often considered a 'Process-Related Impurity' if formed during synthesis.",
        "risk_level": "Medium"
    },
    "Oxidative N-Dealkylation": {
        "smarts": "[NX3:1]([CX4:2])[H:3]>>[NX3:1]([H])[H].[CX4:2]=[OX1]",
        "condition": "Peroxides, Metal ions (Fe/Cu), Air exposure",
        "rationale": "Alpha-carbon oxidation followed by C-N bond cleavage. Common in secondary/tertiary amines.",
        "reg_significance": "Reaction with excipient peroxides is a major stability concern for tablets.",
        "risk_level": "High"
    },
    "Photolytic Ether Cleavage": {
        "smarts": "[OX2:1][CX4:2]>>[OX2:1].[CX4:2][OH]",
        "condition": "UV/Visible Light (ICH Q1B)",
        "rationale": "Photon-induced homolytic cleavage of C-O bonds. Common in methoxy/ethoxy substituted aromatics.",
        "reg_significance": "Requires light-resistant packaging (amber vials/alu-alu blisters).",
        "risk_level": "High"
    },
    "Aromatic Nitro Reduction": {
        "smarts": "[N+:1](=[O:2])[O-:3]>>[NX3:1]([H])[H]",
        "condition": "Reducing agents, Anaerobic conditions",
        "rationale": "Step-wise reduction of nitro to hydroxylamine and then to amine. Intermediates are often mutagenic.",
        "reg_significance": "Class 2/3 Alert formation potential. Critical for genotoxicity assessment.",
        "risk_level": "Critical"
    },
    "Decarboxylation": {
        "smarts": "[CX3:1](=[OX1:2])[OX2:3][H:4]>>[CX4:1].[OX1]=[CX3]=[OX1]",
        "condition": "Thermal stress, Acid catalysis",
        "rationale": "Loss of CO2 from carboxylic acids, especially those with alpha-electron withdrawing groups.",
        "reg_significance": "Leads to loss of potency; often a major degradation pathway for NSAIDs.",
        "risk_level": "Medium"
    }
}

def predict_degradation_products(smiles):
    """Predict potential impurities with professional regulatory backing"""
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
    
    for name, data in DEGRADATION_RULES.items():
        rxn = AllChem.ReactionFromSmarts(data["smarts"])
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
                            "condition": data["condition"],
                            "rationale": data["rationale"],
                            "significance": data["reg_significance"],
                            "risk": data["risk_level"],
                            "smiles": psmiles,
                            "class": toxicity["class"],
                            "status": toxicity["status"]
                        })
                        seen_smiles.add(psmiles)
                except:
                    continue
    return products
