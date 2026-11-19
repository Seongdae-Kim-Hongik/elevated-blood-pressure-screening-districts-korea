#   제목면(저자·소속·교신·ORCID), "Statements and Declarations" 절, 그림 캡션은 원고 안("Fig. 1" 굵게, 끝 마침표 없음), 그림 파일 Fig1.tif, 보충은 "Online Resource 1".
import os, re, json, subprocess
from docx.shared import Pt
from jkms_engine import JKMS
import content_hbp as C
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_hbp.json"), encoding="utf-8")); th = C.th
_zf = os.path.join(OUT, "zenodo_doi.txt"); ZENODO = open(_zf).read().strip() if os.path.exists(_zf) else "[ZENODO DOI]"
REPO = "elevated-blood-pressure-screening-districts-korea"; GITHUB = f"https://github.com/Seongdae-Kim-Hongik/{REPO}"
TITLE = C.TITLE; ORCID = "0000-0002-1525-0091"
ADDRESS = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
EMAIL = "kimsd@hongik.ac.kr"
FUNDING = "No funding was received for conducting this study."
COI = "The author has no relevant financial or non-financial interests to disclose."
ETHICS = "The Institutional Review Board of Hongik University approved the study (7002340-202511-HR-012; continuing review 7002340-202611-HR-040). The study used only published aggregate statistics and was performed in accordance with the 1964 Declaration of Helsinki and its later amendments."
CONSENT = "Not applicable. Only published aggregate statistics were used, and the Institutional Review Board waived informed consent."
AI_STATEMENT = "The author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing of the manuscript and takes full responsibility for its content."
CONTRIB = "Seongdae Kim: Conceptualization, Data curation, Formal analysis, Methodology, Software, Visualization, Writing - original draft, Writing - review and editing."
def data_statement(): return ("All source data are publicly available aggregate statistics cited in the Methods. The processed district-year data are available from the author on reasonable request.")
def code_statement(): return f"The analysis code and the scripts that generate every number, table, and figure are openly available on Zenodo (https://doi.org/{ZENODO}) and GitHub ({GITHUB}) under the MIT License."

def cites(t): return re.sub(r"\s*\[(@[^\]]+)\]", lambda m: " {{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
def all_keys():
    src = open(os.path.join(HERE, "content_hbp.py"), encoding="utf-8").read() + open(os.path.join(HERE, "content_hbp_intro_methods.py"), encoding="utf-8").read()
    src = re.sub(r"(?m)^\s*#.*$", "", src)
    return sorted({k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")})
KEYS = all_keys(); _miss = [k for k in KEYS if k not in REFS]; assert not _miss, _miss
def ref(k):   # Springer 기본형: Author AB, Author CD (2019) Title. J Abbrev 144:49–58. https://doi.org/… ; 6인 초과 = 6인 et al
    r = REFS[k]
    if r["type"] == "web":
        return f"{r['authors']} ({r['year']}) {r['title']}. {r['url']}. Accessed {r['accessed']}"
    au = r["authors"]; a = ", ".join(au[:6]) + (" et al" if len(au) > 6 else "")
    s = f"{a} ({r['year']}) {r['title'].rstrip('.')}. {r['journal']}"
    if r.get("vol"): s += f" {r['vol']}"
    if r.get("pages"): s += f":{str(r['pages']).replace('-', '–')}"
    return s + (f". https://doi.org/{r['doi']}" if r.get("doi") else "")

class TX(JKMS):
    raw = False; table_bold = True
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw: text = re.sub(r"(^|[\s(])-(?=\d)", "\\1\u2212", text)
        return super()._emit(p, text, sz, bold, italic)

COVLAB = [("Physical activity", [("walking_rate", "Walking rate, %"), ("moderate_pa_rate", "Moderate-or-higher physical activity, %"), ("public_sport_fac", "Public sports facilities per 100,000"), ("village_sport_fac", "Village sports facilities per 100,000")]),
          ("Blood pressure risk behaviors", [("obesity_rate", "Obesity (self-reported), %"), ("high_risk_drinking", "High-risk drinking, %"), ("smoking_rate", "Current smoking, %")]),
          ("Screening and care reach", [("screening_uptake", "Screening uptake, %"), ("im_specialists", "Internal medicine specialists per 100,000"), ("basic_livelihood_rate", "Public assistance recipients, %")]),
          ("Fixed adjustments", [("urban_population_share", "Urban population share, %"), ("physicians_per_1000", "Physicians per 1,000"), ("sex_ratio", "Sex ratio, men per 100 women"), ("fiscal_independence", "Fiscal autonomy, %"), ("pop80_share", "Aged 80 years or older, %")])]
def table1():
    T = N["T1"]; cols = ["2019-2021", "2022-2024", "2019-2024"]
    rows = [["__H__", "Elevated blood pressure criterion"], ["  District-years, n"] + [th(T[c]["n"]) for c in cols], ["  Examinees, million"] + [f"{T[c]['exam']/1e6:.1f}" for c in cols],
            ["  Meeting the criterion, million"] + [f"{T[c]['cases']/1e6:.1f}" for c in cols], ["  Meeting the criterion, % of examinees"] + [f"{100*T[c]['rate']:.1f}" for c in cols],
            ["  District ratio, median<sup>a</sup>"] + [f"{T[c]['sir_med']:.2f}" for c in cols], ["  District ratio, 10th-90th percentile<sup>a</sup>"] + [f"{T[c]['sir_p10']:.2f}-{T[c]['sir_p90']:.2f}" for c in cols]]
    for g, vs in COVLAB:
        rows.append(["__H__", f"{g}, mean (SD)"])
        for v, lab in vs:
            mx = max(abs(T[c]["cov"][v][0]) for c in cols); dp = 0 if mx >= 100 else (2 if mx < 5 else 1)
            rows.append([f"  {lab}"] + [f"{T[c]['cov'][v][0]:,.{dp}f} ({T[c]['cov'][v][1]:,.{dp}f})" for c in cols])
    foot = ("<sup>a</sup>Observed over expected examinees meeting the criterion (indirect standardization for sex and 15 age groups), summed over the period. Means and SDs are over district-years. "
            "Survey-based rates are age-standardized rates from the Community Health Survey. Criterion: systolic blood pressure of 130 mm Hg or higher, diastolic blood pressure of 85 mm Hg or higher, or antihypertensive treatment.")
    return ("Table 1 Elevated blood pressure at screening and district characteristics by period, Korea, 2019-2024", ["Characteristic"] + cols, rows, foot)
def table2():
    rows = []; f = lambda x: f"{x[0]:.3f} ({x[1]:.3f}-{x[2]:.3f})" if x else "\u2013"
    for g, vs in COVLAB:
        rows.append(["__H__", g])
        for v, lab in vs:
            lab = re.sub(r", %$|, men per 100 women$", "", lab)
            mv = N["mv"].get(v)
            rows.append([f"  {lab}", f(N["main"][v]), f"{100*mv[0]:.0f}" if mv else "\u2013", f(N[C.kh_best].get(v)), f(N["nco"].get("HTNTC|" + v)), f(N["nco"].get("UNDXHC|" + v))])
    foot = ("Rate ratios per 1 SD with 95% credible intervals (CrIs). Principal model: negative binomial with a Besag-York-Molli\u00e9 2 district effect and random-walk and independent year effects, "
            f"10 characteristics and 5 fixed adjustments ({th(N['n_rows'])} district-years). \u2013, forced into every model (no subset share). "
            "<sup>a</sup>Share of the 200 covariate-subset models containing the characteristic in which the CrI excluded 1. "
            f"<sup>b</sup>Principal model plus the Knorr-Held type {C.KHB} space-time interaction, the space-time model with the lowest WAIC. "
            "<sup>c</sup>Principal model refitted with examinees already treated for hypertension, standardized in the same way (comparison only). "
            "<sup>d</sup>Principal model refitted with examinees newly suspected of hypertension (comparison only).")
    return ("Table 2 District characteristics and elevated blood pressure at screening, Korea, 2019-2024",
            ["Characteristic", "Principal model\nRR (95% CrI)", "Subsets\ncredible, %<sup>a</sup>", f"Knorr-Held type {C.KHB}\nRR (95% CrI)<sup>b</sup>", "Treated hypertension\nRR (95% CrI)<sup>c</sup>", "Suspected hypertension\nRR (95% CrI)<sup>d</sup>"], rows, foot)

FIGCAP = {
 1: "Elevated blood pressure at health screening across Korean districts. (A) Ratio of observed to expected examinees meeting the criterion (indirect standardization for sex and 15 age groups) summed over 2019-2024; solid outlines, Getis-Ord Gi* hot spots, and dashed outlines, cold spots (P < .05). "
    "(B) National share of examinees meeting the criterion, 2013-2017 and 2019-2024; the shaded band marks 2018, when the table counted about one-third of examinees and was excluded. "
    "(C) Median self-reported obesity, public assistance recipients, public sports facilities per 100,000 residents, and population density in hot-spot, other, and cold-spot districts, each relative to the highest group",
 2: "Rate ratios per 1 SD of 4 district characteristics across model specifications. Points and lines show rate ratios and 95% credible intervals from the principal model; models with Knorr-Held type II, III, and IV space-time interactions (type I in Online Resource 1, Table S3); a model with province-by-year effects; Spatial+; "
    "and the principal model refitted with examinees already treated for hypertension and with examinees newly suspected of hypertension (comparison outcomes from other screening tables)",
}
def foot_row(J, text, sz=8, ls=12):
    from docx.enum.text import WD_LINE_SPACING
    t = J.doc.tables[-1]; r = t.add_row(); m = r.cells[0].merge(r.cells[-1]); m.text = ""; p = m.paragraphs[0]
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(ls); p.paragraph_format.space_before = Pt(4)
    c = J.counting; J.counting = False; J._emit(p, text, sz); J.counting = c
def put_table(J, t, fs=9):
    c = J.counting; J.counting = False; J.table_fit(t[0], t[1], t[2], "", fs_max=fs, title_bold=True); foot_row(J, t[3]); J.counting = c

def build(nc=0, aw=0):
    J = TX(cite="bracket")
    J.para(f"<b>{TITLE}</b>")
    J.para("Seongdae Kim", before=12); J.para(ADDRESS)
    J.para(f"<b>Corresponding author:</b> Seongdae Kim, {ADDRESS}. Email: {EMAIL}. ORCID: {ORCID}", before=6)
    J.para(f"<b>Running title:</b> {C.RUNNING}", before=6)
    J.para(f"<b>Article type:</b> Original Article. <b>Length:</b> main text {th(nc)} characters with spaces; abstract {aw} words; 2 tables and 2 figures; {len(KEYS)} references.", before=6)
    J.para("<b>Acknowledgements:</b> None.", before=6)
    J.page_break(); J.head("Abstract", 1)
    for h, t in C.ABSTRACT: J.para(f"<b>{h}</b> {t}")
    J.para(f"<b>Keywords</b> {C.KEYWORDS}", before=6)
    J.page_break(); J.counting = True
    J.head("Introduction", 1)
    for p in C.INTRO: J.para(cites(p), indent=True)
    J.head("Methods", 1)
    for x in C.METHODS:
        J.head(x[0], 2)
        for p in x[1:]: J.para(cites(p), indent=True)
    J.head("Results", 1)
    for x in C.RESULTS:
        J.head(x[0], 2)
        for p in x[1:]: J.para(cites(p), indent=True)
    J.head("Discussion", 1)
    for p in C.DISCUSSION:
        if p.startswith("### "): J.head(p[4:].strip(), 2); continue
        J.para(cites(p), indent=True)
    J.head("Conclusions", 2)
    for p in C.CONCLUSION: J.para(cites(p), indent=True)
    J.counting = False
    J.head("Statements and Declarations", 1)
    for h, t in (("Funding", FUNDING), ("Competing interests", COI), ("Ethics approval", ETHICS), ("Consent to participate", CONSENT), ("Consent for publication", "Not applicable."),
                 ("Data availability", data_statement()), ("Code availability", code_statement()), ("Use of artificial intelligence tools", AI_STATEMENT), ("Author contributions", CONTRIB)):
        J.head(h, 2); J.para(t)
    assert sorted(J.cites) == KEYS, (set(J.cites) ^ set(KEYS))
    J.page_break(); J.head("References", 1); J.raw = True; rl = []
    for n, k in enumerate(J.cites, 1): s = f"{n}. {ref(k)}"; rl.append(s); J.para(s)
    J.raw = False
    J.page_break(); put_table(J, table1()); J.page_break(); put_table(J, table2(), fs=8)
    J.page_break(); J.head("Figure captions", 1)
    for k in sorted(FIGCAP): J.para(f"<b>Fig. {k}</b> {FIGCAP[k]}")
    return J, rl

def body_chars(path):
    from docx import Document
    t = "\n".join(x.text for x in Document(path).paragraphs)
    return len(t[t.find("\nIntroduction\n"):t.find("\nStatements and Declarations\n")].replace("\n", " "))
def to_pdf(p): subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_hbp_iem", "--convert-to", "pdf", "--outdir", os.path.dirname(p), p], check=True, capture_output=True)

if __name__ == "__main__":
    p = os.path.join(OUT, "Manuscript.docx")
    aw = sum(len(t.split()) for _, t in C.ABSTRACT) + len(C.ABSTRACT); assert 150 <= aw <= 250, aw
    assert 4 <= len(C.KEYWORDS.split(";")) <= 6
    J, rl = build(); J.doc_title = "Manuscript"; J.save(p); nc = body_chars(p)
    J, rl = build(nc, aw); J.doc_title = "Manuscript"; J.save(p); assert body_chars(p) == nc
    to_pdf(p)
    open(os.path.join(OUT, "wordcount_iem.txt"), "w").write(f"body_chars={nc}\nabstract_words={aw}\nrefs={len(KEYS)}\ntables=2\nfigures=2\ntitle_words={len(TITLE.split())}\n")
    open(os.path.join(OUT, "references.txt"), "w").write("\n".join(rl))
    print(f"body chars {nc} (limit 25,000) | abstract {aw} | refs {len(KEYS)} (limit 50)")
