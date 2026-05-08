import requests
import urllib.parse

def test_lookup(name):
    clean_name = urllib.parse.quote(name.strip())
    # Request multiple properties to see what's available
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_name}/property/CanonicalSMILES,IsomericSMILES,MolecularFormula/JSON"
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        data = response.json()
        props = data["PropertyTable"]["Properties"][0]
        print(f"Name: {name}")
        for key, val in props.items():
            print(f"  {key}: {val}")
        return props
    else:
        print(f"Failed for {name}: {response.status_code}")
        return None

test_lookup("rosuvastatin")
test_lookup("atorvastatin")
