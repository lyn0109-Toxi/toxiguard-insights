from __future__ import annotations

from urllib.parse import quote_plus
from typing import Any


GUIDELINE_SOURCES = [
    {
        "name": "FDA ICH M7(R2) Guidance / Q&A",
        "url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/questions-and-answers-m7r2-assessment-and-control-dna-reactive-mutagenic-impurities-pharmaceuticals",
        "scope": "Assessment and control of DNA-reactive mutagenic impurities",
    },
    {
        "name": "EMA ICH M7(R2) Scientific Guideline",
        "url": "https://www.ema.europa.eu/en/ich-m7-assessment-control-dna-reactive-mutagenic-impurities-pharmaceuticals-limit-potential-carcinogenic-risk-scientific-guideline",
        "scope": "ICH M7(R2), addendum, and Q&A documents",
    },
    {
        "name": "USP Organic Impurities FAQ",
        "url": "https://www.usp.org/frequently-asked-questions/organic-impurities",
        "scope": "Terminology and treatment of organic impurities and degradation products",
    },
    {
        "name": "FDA ANDAs: Impurities in Drug Products",
        "url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/andas-impurities-drug-products",
        "scope": "CMC information for reporting, identifying, and qualifying degradation products in ANDA drug products",
    },
]


PUBLIC_EVIDENCE_SOURCE_LIBRARY = [
    {
        "Agency": "FDA",
        "Source": "Orange Book Data Files",
        "URL": "https://www.fda.gov/drugs/drug-approvals-and-databases/orange-book-data-files",
        "Evidence use": "RLD/RS, active ingredient, dosage form, route, strength, applicant, application number, therapeutic equivalence context",
        "Access": "Free public structured files",
        "Platform role": "Reference product and ANDA strategy anchor",
    },
    {
        "Agency": "FDA",
        "Source": "Drugs@FDA / openFDA Drugs@FDA",
        "URL": "https://open.fda.gov/apis/drug/drugsfda/",
        "Evidence use": "Approval history, submissions, application metadata, labels, reviews, and supplement context where available",
        "Access": "Free public API",
        "Platform role": "Approval and regulatory history source",
    },
    {
        "Agency": "FDA",
        "Source": "DailyMed / openFDA Drug Label",
        "URL": "https://open.fda.gov/apis/drug/label/",
        "Evidence use": "Dosage form, route, strength, excipients, storage, handling, administration, warnings, and labeling claims",
        "Access": "Free public API",
        "Platform role": "Product identity, formulation, and CMC context",
    },
    {
        "Agency": "FDA",
        "Source": "NDC Directory / openFDA NDC",
        "URL": "https://open.fda.gov/apis/drug/ndc/",
        "Evidence use": "Marketed product, labeler, package, route, dosage form, strength, and marketing category",
        "Access": "Free public API",
        "Platform role": "Marketed product cross-check",
    },
    {
        "Agency": "FDA",
        "Source": "Inactive Ingredient Database",
        "URL": "https://www.fda.gov/drugs/drug-approvals-and-databases/inactive-ingredients-database-download",
        "Evidence use": "Inactive ingredient, route, dosage form, maximum potency / MDE context",
        "Access": "Free public download",
        "Platform role": "Excipient and formulation precedent",
    },
    {
        "Agency": "FDA",
        "Source": "Product-Specific Guidances",
        "URL": "https://www.accessdata.fda.gov/scripts/cder/psg/index.cfm",
        "Evidence use": "Product-specific BE expectations, study type, analyte, fasting/fed, in vitro and in vivo requirements",
        "Access": "Free public search",
        "Platform role": "BE strategy anchor",
    },
    {
        "Agency": "FDA",
        "Source": "Dissolution Methods Database",
        "URL": "https://www.accessdata.fda.gov/scripts/cder/dissolution/",
        "Evidence use": "Apparatus, medium, rpm, sampling time, and dissolution method conditions",
        "Access": "Free public search; direct automated access may be blocked",
        "Platform role": "Dissolution method planning",
    },
    {
        "Agency": "FDA",
        "Source": "GSRS / UNII",
        "URL": "https://precision.fda.gov/uniisearch/",
        "Evidence use": "Substance identity, synonyms, salts, UNII, and regulatory substance mapping",
        "Access": "Free public search",
        "Platform role": "Chemical identity confirmation",
    },
    {
        "Agency": "FDA",
        "Source": "ICH M7(R2) FDA Guidance / Q&A",
        "URL": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/questions-and-answers-m7r2-assessment-and-control-dna-reactive-mutagenic-impurities-pharmaceuticals",
        "Evidence use": "DNA-reactive mutagenic impurity assessment, two complementary QSAR methods, class assignment, and control strategy",
        "Access": "Free public guidance",
        "Platform role": "Genotoxic impurity and QSAR decision basis",
    },
    {
        "Agency": "FDA",
        "Source": "Nitrosamine Impurity Guidance",
        "URL": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/control-nitrosamine-impurities-human-drugs",
        "Evidence use": "Nitrosamine risk assessment, confirmatory testing, acceptable intake, and control strategy",
        "Access": "Free public guidance",
        "Platform role": "Nitrosamine-specific impurity workflow",
    },
    {
        "Agency": "EMA",
        "Source": "EMA Medicines / EPAR",
        "URL": "https://www.ema.europa.eu/en/medicines",
        "Evidence use": "EU product assessment reports, public assessment summaries, product information, and lifecycle context",
        "Access": "Free public search",
        "Platform role": "EU product and regulatory precedent",
    },
    {
        "Agency": "EMA",
        "Source": "EMA ICH M7(R2) scientific guideline",
        "URL": "https://www.ema.europa.eu/en/ich-m7-assessment-control-dna-reactive-mutagenic-impurities-pharmaceuticals-limit-potential-carcinogenic-risk-scientific-guideline",
        "Evidence use": "EU/ICH interpretation of mutagenic impurity assessment and control",
        "Access": "Free public guideline page",
        "Platform role": "EMA/ICH alignment for QSAR narrative",
    },
    {
        "Agency": "EMA",
        "Source": "Nitrosamine impurities in human medicines",
        "URL": "https://www.ema.europa.eu/en/human-regulatory-overview/post-authorisation/referral-procedures-human-medicines/nitrosamine-impurities",
        "Evidence use": "EU nitrosamine risk review, Q&A, acceptable intakes, and regulatory expectations",
        "Access": "Free public guidance page",
        "Platform role": "EU nitrosamine risk workflow",
    },
    {
        "Agency": "ICH",
        "Source": "ICH Guidelines Database",
        "URL": "https://www.ich.org/page/quality-guidelines",
        "Evidence use": "Official ICH quality guideline access point",
        "Access": "Free public guideline database",
        "Platform role": "Primary guideline source index",
    },
    {
        "Agency": "ICH",
        "Source": "ICH Q3A(R2)",
        "URL": "https://database.ich.org/sites/default/files/Q3A_R2__Guideline.pdf",
        "Evidence use": "Impurities in new drug substances",
        "Access": "Free public PDF",
        "Platform role": "Drug substance impurity threshold and qualification basis",
    },
    {
        "Agency": "ICH",
        "Source": "ICH Q3B(R2)",
        "URL": "https://database.ich.org/sites/default/files/Q3B_R2__Guideline.pdf",
        "Evidence use": "Impurities / degradation products in new drug products",
        "Access": "Free public PDF",
        "Platform role": "Drug product degradation product threshold and qualification basis",
    },
    {
        "Agency": "ICH",
        "Source": "ICH Q1A(R2)",
        "URL": "https://database.ich.org/sites/default/files/Q1A%28R2%29%20Guideline.pdf",
        "Evidence use": "Stability testing of new drug substances and products",
        "Access": "Free public PDF",
        "Platform role": "Stability and degradation study basis",
    },
    {
        "Agency": "ICH",
        "Source": "ICH M13A",
        "URL": "https://www.ich.org/page/multidisciplinary-guidelines",
        "Evidence use": "Bioequivalence for immediate-release solid oral dosage forms",
        "Access": "Free public guideline page",
        "Platform role": "BE and comparative dissolution framework",
    },
]


EVIDENCE_ACQUISITION_PLAN = [
    {
        "Evidence layer": "Public FDA source",
        "Best source": "Orange Book, Drugs@FDA/openFDA, DailyMed/openFDA Label, NDC, IID, PSG, Dissolution Methods, GSRS",
        "What it confirms": "Approved product identity, RLD/RS, route, dosage form, strength, formulation context, BE method and regulatory precedent",
        "Availability": "Free public; some web pages may block direct automated scraping",
        "Platform action": "Auto-link and extract when APIs/files are available; provide manual source link when access is blocked",
    },
    {
        "Evidence layer": "Public EMA source",
        "Best source": "EMA medicines database, EPAR, EMA ICH M7 page, EMA nitrosamine guidance",
        "What it confirms": "EU product precedent, quality/safety assessment context, CHMP/EMA interpretation of ICH and nitrosamine expectations",
        "Availability": "Free public",
        "Platform action": "Provide EMA regulatory source map and EU precedent review queue",
    },
    {
        "Evidence layer": "Official ICH guideline basis",
        "Best source": "ICH M7, Q3A, Q3B, Q1A, Q3C, Q3D, M13A",
        "What it confirms": "Guideline logic for mutagenic impurities, degradation products, stability, residual solvents, elemental impurities, and BE",
        "Availability": "Free public",
        "Platform action": "Map each module output to the controlling ICH guideline",
    },
    {
        "Evidence layer": "Impurity identity and structure",
        "Best source": "FDA/EMA public assessment reports, PubMed, PubChem, supplier public pages, qualified internal LC-MS/NMR",
        "What it confirms": "Impurity name, origin, structure, CAS, and whether QSAR can be run",
        "Availability": "Mixed; many details require licensed pharmacopeia/reference-standard or internal analytical data",
        "Platform action": "Mark as structure pending when public sources do not provide qualified SMILES/InChI",
    },
    {
        "Evidence layer": "Licensed / internal verification",
        "Best source": "USP-NF, Ph. Eur., BP, JP, supplier COA, DMF, forced degradation, stability batches",
        "What it confirms": "Official limits, methods, reference standards, confirmed degradation pathways and batch-specific controls",
        "Availability": "Licensed, confidential, or sponsor-controlled",
        "Platform action": "Show as verification-needed, not as absent evidence",
    },
]


PHARMACOPEIA_DB: dict[str, dict[str, Any]] = {
    "Atorvastatin": {
        "smiles": "CC(C)c1c(C(=O)Nc2ccccc2)c(c(s1)c3ccc(F)cc3)C(O)CC(O)CC(=O)O",
        "monograph_ref": "USP / EP related substances framework; verify against current licensed monograph.",
        "dmf_summary": "Control strategy should connect oxidative degradation, lactonization, esterification-related impurities, and validated stability-indicating methods.",
        "impurities": [
            {
                "id": "EP Impurity D / USP Related Compound D",
                "name": "Atorvastatin epoxide / atorvastatin epoxydione impurity",
                "origin": "Oxidative degradation or low-level synthesis by-product",
                "alert": "Epoxide / Aziridine",
                "class": 3,
                "smiles": "CC(C)C(=O)C1(C(O1)(C2=CC=CC=C2)C(=O)C3=CC=C(C=C3)F)C(=O)NC4=CC=CC=C4",
                "cas": "148146-51-4",
                "source_name": "EP/USP reference-standard supplier listings; verify against USP/EP monograph",
                "source_url": "https://veeprho.com/impurities/atorvastatin-ep-impurity-d/",
                "issue": "Epoxide ring is an electrophilic structural alert; bacterial mutagenicity evidence or expert review is needed before downgrading.",
            },
            {
                "id": "Atorvastatin Pyrrolidone Lactone",
                "name": "Atorvastatin pyrrolidone lactone",
                "origin": "Lactonization / degradation product",
                "alert": "None",
                "class": 5,
                "smiles": None,
                "cas": "906552-19-0",
                "source_name": "USP Pharmaceutical Analytical Impurity listing",
                "source_url": "https://www.sigmaaldrich.cn/CN/en/product/usp/1a00820",
                "issue": "Known analytical impurity; assess under Q3A/Q3B and stability context unless a mutagenic alert is identified.",
            },
            {
                "id": "Atorvastatin Methyl Ester",
                "name": "Atorvastatin methyl ester",
                "origin": "Esterification process impurity",
                "alert": "None",
                "class": 5,
                "smiles": None,
                "cas": "345891-62-5",
                "source_name": "USP Pharmaceutical Analytical Impurity listing",
                "source_url": "https://www.sigmaaldrich.cn/CN/en/product/usp/1a00020",
                "issue": "Process impurity; specification justification should rely on purge, method validation, and Q3A/Q3B thresholds.",
            },
        ],
    },
    "Rosuvastatin": {
        "smiles": None,
        "monograph_ref": "USP / EP related substances framework; verify against current licensed monograph.",
        "dmf_summary": "Diastereomeric and lactone-related impurities are typically managed by stereochemical control and stability monitoring.",
        "impurities": [
            {
                "id": "USP Related Compound A",
                "name": "Rosuvastatin diastereomer",
                "origin": "Synthesis / stereochemical impurity",
                "alert": "None",
                "class": 5,
                "smiles": None,
                "cas": None,
                "source_name": "USP/EP related substance listing; verify exact standard",
                "source_url": None,
                "issue": "Usually a quality/stereochemical control issue rather than an ICH M7 alert unless structure-specific alert is present.",
            },
            {
                "id": "USP Related Compound B",
                "name": "Rosuvastatin lactone",
                "origin": "Degradation / lactonization",
                "alert": "None",
                "class": 5,
                "smiles": None,
                "cas": None,
                "source_name": "USP/EP related substance listing; verify exact standard",
                "source_url": None,
                "issue": "Assess as known degradation product under Q3B/stability controls.",
            },
        ],
    },
    "Brivaracetam": {
        "smiles": "CCCC1CN(C(=O)C1)C(C(N)=O)CC",
        "monograph_ref": "FDA approval and EP reference context; verify against current licensed monograph.",
        "dmf_summary": "Process-related intermediates and alkylating reagents should be controlled by purge justification under ICH M7 Option 4 where applicable.",
        "impurities": [
            {
                "id": "Impurity 1",
                "name": "4-Propyl-pyrrolidin-2-one",
                "origin": "Synthesis",
                "alert": "None",
                "class": 5,
                "smiles": None,
                "cas": None,
                "source_name": "Development/DMF-style process impurity library",
                "source_url": None,
                "issue": "Non-alerting process impurity in current demo library.",
            },
            {
                "id": "PGI-1",
                "name": "2-Bromobutyryl chloride",
                "origin": "Process reagent",
                "alert": "Alkyl Halide",
                "class": 3,
                "smiles": "CCCC(=O)Cl",
                "cas": None,
                "source_name": "Process impurity risk library",
                "source_url": None,
                "issue": "Potentially alerting electrophile; control by purge, specification, or confirmatory testing.",
            },
        ],
    },
    "Telmisartan": {
        "smiles": "CCCc1nc2c(C)cc(cc2n1Cc3ccc(cc3)c4ccccc4C(O)=O)c5nc6ccccc6n5C",
        "monograph_ref": "USP-NF Telmisartan Tablets monograph identifies USP Telmisartan RS and USP Telmisartan Related Compound A RS; verify current licensed monograph before submission.",
        "dmf_summary": "For FDA submissions, degradation products should be reported, identified, and qualified under FDA ANDA impurity guidance and ICH Q3B/ICH M7 as applicable.",
        "regulatory_sources": [
            {
                "name": "USP-NF Telmisartan Tablets monograph DOI",
                "url": "https://doi.usp.org/USPNF/USPNF_M80815_07_01.html",
                "scope": "USP identity, assay, impurity, and reference-standard context for Telmisartan Tablets.",
            },
            {
                "name": "FDA ANDAs: Impurities in Drug Products",
                "url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/andas-impurities-drug-products",
                "scope": "FDA expectations for degradation product reporting, identification, and qualification in ANDA submissions.",
            },
            {
                "name": "FDA GSRS / UNII Telmisartan",
                "url": "https://precision.fda.gov/uniisearch/srs/unii/u5syw473rq",
                "scope": "FDA substance identity record and regulatory synonyms/mappings.",
            },
        ],
        "impurities": [
            {
                "id": "USP Related Compound A / EP Impurity A",
                "name": "4-Methyl-6-(1-methyl-1H-1,3-benzodiazol-2-yl)-2-propyl-1H-1,3-benzodiazole",
                "origin": "Compendial related substance / process-related impurity",
                "alert": "None loaded",
                "class": 5,
                "smiles": None,
                "cas": "152628-02-9",
                "source_name": "USP-NF Telmisartan Tablets monograph; supplier identity listing for EP/USP impurity A",
                "source_url": "https://doi.usp.org/USPNF/USPNF_M80815_07_01.html",
                "issue": "USP identifies Related Compound A reference standard. Structure should be loaded from a qualified reference-standard COA or licensed monograph before final QSAR conclusion.",
                "evidence_source_category": "pharmacopeia",
            },
            {
                "id": "EP Impurity B / USP Related Compound B",
                "name": "Telmisartan Related Compound B",
                "origin": "Compendial related substance / commercial reference impurity",
                "alert": "None loaded",
                "class": 5,
                "smiles": "O=C(C1=C(C2=CC=C(CN3C(CCC)=NC4=C3C(C)=CC(C5=NC6=C(N5C)C=CC=C6)=C4)C=C2)C=CC=C1)O",
                "cas": "1026353-20-7",
                "source_name": "Reference standard supplier listing aligned to EP/USP related compound naming",
                "source_url": "https://clearsynth.com/product/Telmisartan-EP-Impurity-B",
                "issue": "Related compound identity can support targeted related-substance monitoring; final limits should be justified from licensed monograph/specification and batch/stability data.",
                "evidence_source_category": "pharmacopeia-style reference standard",
            },
            {
                "id": "Photo-acidic degradation product",
                "name": "Telmisartan photolytic degradation product",
                "origin": "Photolytic degradation under acidic stress",
                "alert": "Structure pending",
                "class": "review",
                "smiles": None,
                "cas": None,
                "source_name": "Journal of Pharmaceutical and Biomedical Analysis stability study",
                "source_url": "https://www.sciencedirect.com/science/article/pii/S0731708510002815",
                "issue": "Published stress study reports telmisartan lability under photo-acidic condition with a single degradation product characterized by LC-MS/TOF and related techniques. Load the assigned structure before final ICH M7 QSAR classification.",
                "evidence_source_category": "stability literature",
            },
        ],
    },
    "Naltrexone": {
        "smiles": "C1CC1CN2CC[C@]34[C@@H]5C(=O)CC[C@]3([C@H]2CC6=C4C(=C(C=C6)O)O5)O",
        "monograph_ref": "USP-NF Naltrexone Hydrochloride and Naltrexone Hydrochloride Tablets monographs identify USP Naltrexone RS and USP Naltrexone Related Compound A RS; verify current licensed USP/EP monograph before submission.",
        "dmf_summary": "For oral naltrexone hydrochloride, manage Related Compound A and other organic impurities through validated related-substances and stability-indicating methods. For Vivitrol, connect API impurity control with PLG microsphere release/degradation, storage, diluent, and injectable product-specific CMC strategy.",
        "regulatory_sources": [
            {
                "name": "USP-NF Naltrexone Hydrochloride monograph DOI",
                "url": "https://doi.usp.org/USPNF/USPNF_M55530_05_01.html",
                "scope": "USP identity and reference-standard context for Naltrexone Hydrochloride, including Naltrexone Related Compound A RS.",
            },
            {
                "name": "USP-NF Naltrexone Hydrochloride Tablets monograph DOI",
                "url": "https://doi.usp.org/USPNF/USPNF_M55538_02_01.html",
                "scope": "USP tablet monograph and reference-standard context for naltrexone hydrochloride tablets.",
            },
            {
                "name": "DailyMed Vivitrol label",
                "url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=cd11c435-b0f0-4bb9-ae78-60f101f3703f",
                "scope": "Vivitrol dosage form, strength, PLG microsphere matrix, diluent composition, storage, and administration details.",
            },
            {
                "name": "FDA Vivitrol postmarket information",
                "url": "https://www.fda.gov/drugs/postmarket-drug-safety-information-patients-and-providers/naltrexone-extended-release-injectable-suspension-marketed-vivitrol-information",
                "scope": "FDA regulatory information and label access for naltrexone extended-release injectable suspension marketed as Vivitrol.",
            },
            {
                "name": "Accelerated in vitro release testing method for naltrexone loaded PLGA microspheres",
                "url": "https://www.sciencedirect.com/science/article/pii/S0378517317300595",
                "scope": "Published in vitro release and naltrexone stability/degradation considerations for Vivitrol-like PLGA microspheres.",
            },
            {
                "name": "Reverse engineering of Vivitrol PLGA microspheres",
                "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7975983/",
                "scope": "Open-access discussion of Vivitrol PLGA microsphere critical attributes, in vitro release, PLGA molecular-weight change, and degradation behavior.",
            },
        ],
        "impurities": [
            {
                "id": "USP Related Compound A",
                "name": "Naltrexone Related Compound A / N-(3-butenyl)noroxymorphone hydrochloride",
                "origin": "USP compendial related substance / process-related impurity reference standard",
                "alert": "None identified by current local screen",
                "class": 5,
                "smiles": "Cl.N1([C@H]2[C@]3([C@@]4([C@@H](Oc5c4c(ccc5O)C2)C(=O)CC3)CC1)O)CCC=C",
                "cas": "131670-05-8",
                "source_name": "USP reference standard supplier listing; USP-NF monograph reference-standard context",
                "source_url": "https://www.sigmaaldrich.com/US/en/product/usp/1453526",
                "issue": "USP identifies Naltrexone Related Compound A RS for Naltrexone Hydrochloride and Naltrexone Hydrochloride Tablets. Treat as a qualified related-substance target; final limits require current licensed monograph/specification and batch/stability data.",
                "evidence_source_category": "pharmacopeia",
            },
            {
                "id": "Vivitrol PLG microsphere matrix",
                "name": "75:25 polylactide-co-glycolide microsphere matrix",
                "origin": "Vivitrol formulation / long-acting injectable release-controlling excipient",
                "alert": "Not an API genotoxicity alert",
                "class": "formulation review",
                "smiles": None,
                "cas": None,
                "source_name": "DailyMed Vivitrol label",
                "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=cd11c435-b0f0-4bb9-ae78-60f101f3703f",
                "issue": "Vivitrol microspheres contain naltrexone in a biodegradable 75:25 PLG matrix. CMC review should focus on release kinetics, PLG molecular weight/dispersity, residual solvents, particle-size distribution, injection-site performance, and storage controls rather than oral IR dissolution f2.",
                "evidence_source_category": "formulation / CMC",
            },
            {
                "id": "Vivitrol in vitro release/degradation behavior",
                "name": "Naltrexone PLGA microsphere in vitro release and degradation profile",
                "origin": "Stability literature / Vivitrol-like microsphere in vitro release testing",
                "alert": "Not an API genotoxicity alert",
                "class": "product-specific review",
                "smiles": None,
                "cas": None,
                "source_name": "International Journal of Pharmaceutics; open-access Vivitrol reverse-engineering study",
                "source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7975983/",
                "issue": "Published Vivitrol microsphere studies report multi-week release and PLGA molecular-weight/pH changes during release. For generic or development strategy, use product-specific in vitro release and PK bridging logic, not oral immediate-release dissolution f2 as the primary basis.",
                "evidence_source_category": "stability literature",
            },
            {
                "id": "Vivitrol diluent system",
                "name": "Vivitrol diluent excipients",
                "origin": "Product-specific injectable diluent / reconstitution system",
                "alert": "Not an API genotoxicity alert",
                "class": "formulation review",
                "smiles": None,
                "cas": None,
                "source_name": "DailyMed Vivitrol label",
                "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=cd11c435-b0f0-4bb9-ae78-60f101f3703f",
                "issue": "The diluent contains carboxymethylcellulose sodium, polysorbate 20, sodium chloride, pH adjusters, and water for injection. Review compatibility, reconstitution, syringeability/injectability, microbial quality, and product handling as CMC risk factors.",
                "evidence_source_category": "formulation / CMC",
            },
        ],
    },
}


def get_pharmacopeia_info(name: str | None) -> dict[str, Any] | None:
    if not name:
        return None
    query = name.strip().lower()
    for drug, data in PHARMACOPEIA_DB.items():
        if query in drug.lower() or drug.lower() in query:
            return data
    return None


def build_regulatory_source_map(name: str | None, smiles: str | None = None) -> list[dict[str, Any]]:
    query = (name or smiles or "submitted compound").strip()
    encoded = quote_plus(query)
    rows = []
    for source in PUBLIC_EVIDENCE_SOURCE_LIBRARY:
        item = {
            "name": f"{source['Agency']} - {source['Source']}",
            "url": source["URL"],
            "scope": source["Evidence use"],
            "use_in_app": source["Platform role"],
            "agency": source["Agency"],
            "access": source["Access"],
        }
        rows.append(item)

    rows.extend([
        {
            "name": "FDA GSRS / UNII compound search",
            "url": f"https://precision.fda.gov/uniisearch/srs/unii/search?search={encoded}",
            "scope": "Compound-specific FDA substance identity search.",
            "use_in_app": "Confirm identity, salt, synonyms, and regulatory mappings for the submitted compound.",
            "agency": "FDA",
            "access": "Free public search",
        },
        {
            "name": "EMA medicines compound search",
            "url": f"https://www.ema.europa.eu/en/medicines?search_api_fulltext={encoded}",
            "scope": "Compound-specific EMA product / EPAR search.",
            "use_in_app": "Check EU product precedent and public assessment context.",
            "agency": "EMA",
            "access": "Free public search",
        },
        {
            "name": "PubMed impurity / degradation literature search",
            "url": f"https://pubmed.ncbi.nlm.nih.gov/?term={encoded}+impurity+degradation+stability",
            "scope": "Open literature discovery for degradation products, impurities, stability and analytical methods.",
            "use_in_app": "Find public literature before marking a structure as licensed/internal verification needed.",
            "agency": "NCBI / literature",
            "access": "Free public search",
        },
        {
            "name": "PubChem compound record",
            "url": f"https://pubchem.ncbi.nlm.nih.gov/#query={encoded}",
            "scope": "Open chemical identity, identifiers, calculated properties, and linked safety resources.",
            "use_in_app": "Use as supporting identity evidence, not final regulatory impurity qualification.",
            "agency": "NIH",
            "access": "Free public search",
        },
    ])
    return rows


def build_evidence_acquisition_plan() -> list[dict[str, str]]:
    return [dict(row) for row in EVIDENCE_ACQUISITION_PLAN]


def get_regulatory_profile(name: str | None, smiles: str | None = None) -> dict[str, Any]:
    curated = get_pharmacopeia_info(name)
    if curated:
        profile = dict(curated)
        profile["profile_type"] = "curated"
        profile["regulatory_sources"] = curated.get("regulatory_sources") or build_regulatory_source_map(name, smiles)
        return profile

    return {
        "profile_type": "source-discovery",
        "smiles": smiles,
        "monograph_ref": "A submission-grade impurity profile has not been curated from public FDA/EMA/ICH sources yet. This does not mean no impurities exist; many structures and limits require licensed pharmacopeial, reference-standard, DMF, supplier COA, or internal analytical data.",
        "dmf_summary": "Use the FDA/EMA/ICH source map and evidence acquisition plan below to convert public-source gaps into a development workplan: confirm official guidance, search public product/literature sources, obtain qualified impurity structures, and reserve final limits for licensed or internal verification.",
        "regulatory_sources": build_regulatory_source_map(name, smiles),
        "evidence_acquisition_plan": build_evidence_acquisition_plan(),
        "impurities": [],
    }


def get_local_smiles(name: str | None) -> dict[str, str] | None:
    info = get_pharmacopeia_info(name)
    if info and info.get("smiles"):
        return {"smiles": info["smiles"], "source": "Local compendial/DMF library"}
    return None


def match_known_impurities(parent_name: str | None = None, smiles: str | None = None) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    info = get_pharmacopeia_info(parent_name)
    if info:
        for impurity in info.get("impurities", []):
            item = dict(impurity)
            item["parent"] = parent_name
            matches.append(item)

    if smiles:
        normalized = smiles.strip()
        for parent, data in PHARMACOPEIA_DB.items():
            for impurity in data.get("impurities", []):
                if impurity.get("smiles") and impurity["smiles"] == normalized:
                    item = dict(impurity)
                    item["parent"] = parent
                    item["match_type"] = "Exact SMILES"
                    matches.append(item)
    return matches
