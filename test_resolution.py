import requests
import urllib.parse

def test_resolve(name):
    print(f"Testing resolution for: {name}")
    clean_name = urllib.parse.quote(name.strip())
    
    # Method 1: Direct Property by Name
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/property/IsomericSMILES,IUPACName/JSON"
    try:
        r = requests.get(url, timeout=5)
        print(f"Method 1 (Direct) Status: {r.status_code}")
    except Exception as e:
        print(f"Method 1 Error: {e}")

    # Method 2: CID Search then Property
    url_cid = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/cids/JSON"
    try:
        r = requests.get(url_cid, timeout=5)
        print(f"Method 2 (CID Search) Status: {r.status_code}")
        if r.status_code == 200:
            cid = r.json()["IdentifierList"]["CID"][0]
            print(f"Found CID: {cid}")
            url_prop = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/IsomericSMILES,IUPACName,MolecularFormula/JSON"
            r_prop = requests.get(url_prop, timeout=5)
            print(f"Method 2 (Prop by CID) Status: {r_prop.status_code}")
    except Exception as e:
        print(f"Method 2 Error: {e}")

    # Method 3: NIH CIR Fallback
    url_nih = f"https://cactus.nci.nih.gov/chemical/structure/{clean_name}/smiles"
    try:
        r = requests.get(url_nih, timeout=5)
        print(f"Method 3 (NIH CIR) Status: {r.status_code}")
    except Exception as e:
        print(f"Method 3 Error: {e}")

if __name__ == "__main__":
    test_resolve("telmisartan")
    test_resolve("atorvastatin")
    test_resolve("rosuvastatin")
