import requests

def test_url(url):
    print(f"Testing URL: {url}")
    try:
        response = requests.get(url, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
        else:
            print(f"Content: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

test_url("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/property/IUPACName/JSON")
