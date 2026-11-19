import json, os, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__)); AN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = {}
for f in ["HTNT/MS/build/refs_htnt.json", "HTND/MS/build/refs_htnd.json", "DXAW/MS/build/refs_dxaw.json", "LIPS/MS/build/refs_lips.json", "HCUV/MS/build/refs_hcuv.json"]:
    for k, v in json.load(open(os.path.join(AN, f))).items(): SRC.setdefault(k, dict(v, verified=v.get("verified", f.split("/")[0] + " 검증본")))
PM = {"grundy2005diagnosis": 16157765, "alberti2009harmonizing": 19805654, "jang2026age": 42772797, "kang2022current": 35610963, "sarkar2018neighbourhood": 29398408,
      "chiu2016moving": 26550779, "lai2023associations": 37580546, "park2020progress": 32404470, "choi2026degree": 42321737, "zou2004modified": 15033648, "hall2015obesity": 25767285, "barros2003alternatives": 14567763}
COPY = ["gbd2025global", "lewington2002age", "ncdrisc2021worldwide", "cheolseong2017data", "lee2017socioeconomic", "lee2019temporal", "kim2026korea", "cornelissen2013exercise", "roerecke2017effect",
        "leng2015socioeconomic", "inskip1983methods", "kang2015korea", "riebler2016intuitive", "simpson2017penalising", "rue2009approximate", "knorrheld2000bayesian", "steegen2016increasing",
        "dupont2022spatial", "lipsitch2010negative", "vanderweele2017sensitivity", "bell2015explaining", "morgenstern1995ecologic", "vonelm2007strengthening", "heidari2016sex",
        "besag1991bayesian", "gelman2014understanding", "ord1995local", "hodges2010adding", "harrison2015comparison", "lee2022hypertension", "kim2021ten", "lee2025regional", "mills2016global",
        "web:rcore2026", "web:mois2026population"]
R = {}
d = json.loads(urllib.request.urlopen("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urllib.parse.urlencode(dict(db="pubmed", id=",".join(map(str, PM.values())), retmode="json")), timeout=60).read())["result"]
for k, p in PM.items():
    x = d[str(p)]; doi = next((a["value"] for a in x.get("articleids", []) if a["idtype"] == "doi"), "")
    au = [a["name"] for a in x.get("authors", []) if a.get("authtype") == "Author"]
    R[k] = dict(type="journal", authors=au, title=x["title"].rstrip("."), journal=x["source"], year=int(x["pubdate"][:4]), vol=x.get("volume", ""), issue=x.get("issue", ""),
                pages=x.get("pages", ""), doi=doi, pmid=str(p), verified="PubMed esummary 2026-11-18")
for k in COPY: R[k] = dict(SRC[k])
for k, j in {"besag1991bayesian": "Ann Inst Stat Math", "gelman2014understanding": "Stat Comput", "ord1995local": "Geogr Anal"}.items(): R[k]["journal"] = j
R["web:rcore2026"]["accessed"] = R["web:mois2026population"]["accessed"] = "November 18, 2026"
R["web:kosis2026screening"] = dict(type="web", authors="National Health Insurance Service", title="National general health screening statistics: metabolic syndrome risk factors by district and sex (DT_35007_N138) and by sex and age (DT_35007_N139), distribution of systolic and diastolic blood pressure by province and age (DT_35007_N060-N063), existing hypertension and suspected hypertension (DT_35007_N105, DT_35007_N103), and screening targets and attendees (DT_35007_N001), 2013-2024. Korean Statistical Information Service", url="https://kosis.kr", year=2026, accessed="November 18, 2026")
for k, r in R.items():
    if r.get("type") == "journal": assert r.get("doi") or r.get("pmid") or r.get("journal"), k
json.dump(R, open(os.path.join(HERE, "refs_hbp.json"), "w"), ensure_ascii=False, indent=1)
for k, r in R.items(): print(k, "|", r.get("journal"), r.get("year"), r.get("vol"), r.get("pages"), r.get("doi"))
print(len(R))
