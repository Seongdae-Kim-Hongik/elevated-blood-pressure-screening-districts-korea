#  ★Spatial+·RSR·KH I–IV 표는 결과와 무관하게 전부 싣는다(UROP 교훈 2). 소실 변수에 '강건' 문구 금지.
import os, json, re
import pandas as pd
from build_iem_hbp import TX, put_table, OUT, N, to_pdf, TITLE, th
import content_hbp as C
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.abspath(os.path.join(HERE, "..", "..")); RS = os.path.join(B, "results_std3")
VARS = {"walking_rate": "ext__walking_rate", "moderate_pa_rate": "moderate_pa_rate", "public_sport_fac": "ext__public_sport_fac_per100k", "village_sport_fac": "ext__village_sport_fac_per100k",
        "obesity_rate": "obesity_rate", "high_risk_drinking": "ext__high_risk_drinking", "smoking_rate": "ext__smoking_rate", "screening_uptake": "ext__screening_uptake",
        "im_specialists": "im_specialists_per_100k", "basic_livelihood_rate": "basic_livelihood_rate", "urban_population_share": "urban_population_share", "physicians_per_1000": "physicians_per_1000",
        "sex_ratio": "sex_ratio", "fiscal_independence": "fiscal_independence", "pop80_share": "pop80_share"}
LAB = {"walking_rate": "Walking rate", "moderate_pa_rate": "Moderate-or-higher physical activity", "public_sport_fac": "Public sports facilities", "village_sport_fac": "Village sports facilities",
       "obesity_rate": "Obesity", "high_risk_drinking": "High-risk drinking", "smoking_rate": "Current smoking", "screening_uptake": "Screening uptake", "im_specialists": "Internal medicine specialists",
       "basic_livelihood_rate": "Public assistance recipients", "urban_population_share": "Urban population share", "physicians_per_1000": "Physicians", "sex_ratio": "Sex ratio",
       "fiscal_independence": "Fiscal autonomy", "pop80_share": "Aged 80 years or older"}
KEY4 = [("basic_livelihood_rate", "Public assistance"), ("obesity_rate", "Obesity"), ("public_sport_fac", "Sports facilities"), ("walking_rate", "Walking rate")]
f3 = lambda r: f"{r[0]:.3f} ({r[1]:.3f}-{r[2]:.3f})" if r else "\u2013"
def row(d, c):
    x = d[d["cov"].astype(str) == c]
    return f3([float(x.IRR.iloc[0]), float(x.lo.iloc[0]), float(x.hi.iloc[0])]) if len(x) and pd.notna(x.IRR.iloc[0]) else "fit failed"
D = lambda s: re.sub(r"(\d)-(\d)", "\\1\u2013\\2", s)
S1 = [("Walking rate", "Physical activity", "Adults walking at least 30 minutes on at least 5 days a week, age-standardized, %", "Community Health Survey", "\u2212"),
      ("Moderate-or-higher physical activity", "Physical activity", "Adults meeting moderate or vigorous physical activity criteria, age-standardized, %", "Community Health Survey", "\u2212"),
      ("Public sports facilities", "Physical activity", "Public sports facilities per 100,000 residents", "National public sports facility register", "\u2212"),
      ("Village sports facilities", "Physical activity", "Village (neighborhood) sports facilities per 100,000 residents", "National public sports facility register", "\u2212"),
      ("Obesity", "Blood pressure risk behavior", "Adults with self-reported body mass index of 25 kg/m² or more, age-standardized, %; not surveyed in 2019 (district mean of other years)", "Community Health Survey", "+"),
      ("High-risk drinking", "Blood pressure risk behavior", "Adults drinking 7 or more standard drinks (women 5) at least twice a week, age-standardized, %", "Community Health Survey", "+"),
      ("Current smoking", "Blood pressure risk behavior", "Adults currently smoking cigarettes, age-standardized, %", "Community Health Survey", "+"),
      ("Screening uptake", "Screening and care reach", "First-stage general health screening attendees as a share of those invited, %", "National Health Insurance Service via KOSIS", "\u2212"),
      ("Internal medicine specialists", "Screening and care reach", "Internal medicine specialists per 100,000 residents", "Health Insurance Review and Assessment Service", "+"),
      ("Public assistance recipients", "Screening and care reach", "Basic livelihood security recipients per 100 residents; implausible 2021-2023 values set to missing and interpolated", "Ministry of Health and Welfare via KOSIS", "+"),
      ("Urban population share", "Fixed adjustment", "Residents in urban zones, % of population", "Ministry of Land via KOSIS", "\u2013"),
      ("Physicians", "Fixed adjustment", "Physicians working in medical institutions per 1,000 residents", "KOSIS e-local indicators", "\u2013"),
      ("Sex ratio", "Fixed adjustment", "Men per 100 women", "Resident registration", "\u2013"),
      ("Fiscal autonomy", "Fixed adjustment", "Fiscal autonomy ratio of the local government, %", "Ministry of the Interior and Safety via KOSIS", "\u2013"),
      ("Aged 80 years or older", "Fixed adjustment", "Residents aged 80 years or older, % of population", "Resident registration", "\u2013"),
      ("Hit-and-run crashes", "Negative control", "Hit-and-run crashes per 100 traffic crashes", "KOSIS e-local indicators", "none"),
      ("Traffic culture index", "Negative control", "Traffic culture index score", "Korea Transportation Safety Authority via KOSIS", "none"),
      ("Fires", "Negative control", "Fires per 10,000 residents", "National Fire Agency via KOSIS", "none")]
def t1():
    return ("Table S1 District characteristics, definitions, sources, and expected direction", ["Characteristic", "Group", "Definition", "Source", "Expected"], [[a, b, D(c), d, e] for a, b, c, d, e in S1],
            "Expected direction for the elevated blood pressure criterion, set and hashed before modeling. All characteristics were standardized to 1 SD of district-years. KOSIS, Korean Statistical Information Service.")
def t2():
    G = N["gate"]
    rows = [["Panel", f"{th(N['n_rows'])} district-years = {N['n_districts']} districts \u00d7 6 years (2019-2024); unique keys; no missing outcome, expected count, or covariate; no year with all-zero values"],
            ["Outcome", "Examinees meeting the elevated blood pressure criterion of the metabolic syndrome (KOSIS DT_35007_N138): systolic \u2265130 mm Hg, diastolic \u226585 mm Hg, or antihypertensive treatment; cities with general districts summed from district rows"],
            ["Sejong", "Reported only at the province level; included from province-level rows (all years)"],
            ["Denominator", "Examinees in the same table by sex (DT_35007_N138); outcome is prevalence conditional on attending screening"],
            ["Expected counts", "2 sexes \u00d7 15 age groups (19 or younger, 13 five-year groups to 80-84, 85 or older); national rates from DT_35007_N139; district examinee age structure from resident population \u00d7 national age-specific screening rates, rescaled to observed examinees by sex; district totals equal national totals in every year"],
            ["Criterion check", f"Across provinces, share meeting the criterion vs share with systolic \u2265130 mm Hg (DT_35007_N062): r = {G['r_min']:.2f}-{G['r_max']:.2f} by year (2018 excluded); national ratio of the 2 shares {G['ratio2013']:.2f} (2013) to {G['ratio2024']:.2f} (2024); measured systolic \u2265130 mm Hg {G['sbp_min']:.1f}%-{G['sbp_max']:.1f}%"],
            ["2018", f"Table covered {G['exam2018_m']:.1f} million examinees ({100*G['share2018']:.0f}% of those with measured blood pressure); share meeting the criterion among women {G['f2018']:.1f}%; excluded from the main and 2013-2017 analyses, included in the 2013-2024 sensitivity analysis"],
            ["Population", "Resident registration by sex and 5-year age group; 2023 Changwon total corrected to 1,009,038; Gunwi linked as one district across its 2023 transfer to Daegu"],
            ["Cross-check", "Outcome, denominator, and 11 of the 15 modeled characteristics (walking, moderate activity, obesity, high-risk drinking, smoking, screening uptake, public sports facilities, urban population share, physicians, sex ratio, fiscal autonomy) matched a reference district database cell by cell; village sports facilities differed in 14 of 1,374 district-years; internal medicine specialists, public assistance, and the share aged 80 years or older were not compared cell by cell"],
            ["Imputation", "Obesity not surveyed in 2019: district mean of other years (229 district-years); public assistance 2021-2023 implausibly low in 10 cities with general districts (30 district-years): set to missing and interpolated"],
            ["Covariate sets", "Sets, directions, and model rules fixed and hashed (SHA-256) before any model with the characteristics was fitted"]]
    return ("Table S2 Data checks before modeling", ["Item", "Result"], [[a, D(b)] for a, b in rows], "")
def t3(part=1):
    rows = []
    specs = [("Principal model", "S3_main_IRR.csv", "std3"), ("Knorr-Held type I", "S9_typeI_IRR.csv", "std3"), ("Knorr-Held type II", "S43_part_KH_typeII.csv", "std3"),
             ("Knorr-Held type III", "S43_part_KH_typeIII.csv", "std3"), ("Knorr-Held type IV", "S43_part_KH_typeIV.csv", "std3"), ("Spatial+", "S41_part_D1_spatial_plus.csv", "std3"),
             ("Restricted spatial regression", "S43_part_RSR.csv", "std3"),
             ("Province-by-year effects", "S41_part_C4_sido_year_iid.csv", "std3"), ("Characteristics lagged 1 year", "S41_part_E1_lag1.csv", "std3"), ("Characteristics lagged 2 years", "S41_part_E2_lag2.csv", "std3"),
             ("Second-order random-walk year effect", "S41_part_C2_rw2_year.csv", "std3"), ("Poisson-lognormal likelihood", "S41_part_C1_poisson_lognormal.csv", "std3"),
             ("ICAR district effect", "S43_part_icar_besag.csv", "std3"), ("Independent district effect only", "S43_part_iid_only.csv", "std3"), ("No district effect", "S43_part_no_spatial.csv", "std3"),
             ("Queen contiguity graph (577 pairs)", "S3_main_IRR.csv", "s577"), ("Without the age-80 adjustment", "S3_main_IRR.csv", "s2"), ("Unstandardized expected counts", "S3_main_IRR.csv", "sc"),
             ("Population-based expected counts", "S3_main_IRR.csv", "sp"), ("2013-2017", "S3_main_IRR.csv", "aux"), ("2013-2024 including 2018", "S3_main_IRR.csv", "full")]
    specs = specs[:12] if part == 1 else specs[:1] + specs[12:]
    for lab, f, v in specs:
        p = os.path.join(B, f"results_{v}", f)
        if not os.path.exists(p): rows.append([lab, "not run"] + ["\u2013"] * len(KEY4)); continue
        d = pd.read_csv(p); w = d.WAIC.iloc[0] if "WAIC" in d else (N["waic_main"] if v == "std3" else N[v + "_fit"]["waic"])
        try: ws = f"{float(w):,.1f}"
        except Exception: ws = "\u2013"
        rows.append([lab, ws] + [row(d, VARS[k]) for k, _ in KEY4])
    ttl = "Table S3 Rate ratios per 1 SD (95% CrI) under alternative model structures" if part == 1 else "Table S4 Rate ratios per 1 SD (95% CrI) under alternative district effects, denominators, and periods"
    return (ttl, ["Specification", "WAIC"] + [l for _, l in KEY4], rows,
            "Each row changes one element of the principal model. All rows are shown regardless of result. WAICs are comparable only among models fitted to the same data (lagged models and other periods use different years). Knorr-Held type IV was refitted with the initial log precision set to 0 after the default fit failed. CrI, credible interval; ICAR, intrinsic conditional autoregressive; WAIC, widely applicable information criterion.")
def t4():
    rows = [["__H__", "Comparison outcomes (principal model refitted; comparison only)"]]
    for k, l in KEY4 + [("im_specialists", "Internal medicine specialists"), ("screening_uptake", "Screening uptake")]:
        rows.append([f"  {l}", f3(N["main"][k]), f3(N["nco"].get(f"HTNTC|{k}")), f3(N["nco"].get(f"UNDXHC|{k}"))])
    rows.append(["__H__", "Negative-control exposures (principal model)"])
    for k, l in (("hit_and_run_rate", "Hit-and-run crashes"), ("traffic_culture_index", "Traffic culture index"), ("fires_per_10000", "Fires")): rows.append([f"  {l}", f3(N["nc"][k]), "\u2013", "\u2013"])
    rows.append(["__H__", "Likelihoods (WAIC; estimates for public assistance)"])
    for fam, lab, eff in (("poisson", "Poisson", "RR"), ("nbinomial", "Negative binomial (principal)", "RR"), ("binomial", "Binomial", "OR"), ("betabinomial", "Beta-binomial", "OR"), ("binomial_olre", "Binomial with observation-level effect", "OR")):
        c = N["lik5c"].get(f"{fam}|basic_livelihood_rate")
        rows.append([f"  {lab}", f"{N['lik5'][fam]:,.1f}", f"{eff} {f3(c)}", f"Sports facilities {eff} {f3(N['lik5c'].get(fam + '|ext__public_sport_fac_per100k'))}"])
    rows.append(["__H__", "E-values (CrI limit)"])
    for k, l in KEY4[:3]: rows.append([f"  {l}", f"{N['evalue'][k][0]:.2f} ({N['evalue'][k][1]:.2f})", "\u2013", "\u2013"])
    return ("Table S5 Comparison outcomes, negative-control exposures, likelihoods, and E-values", ["Item", "Elevated blood pressure\n(or WAIC)", "Treated hypertension\n(or estimate)", "Suspected hypertension\n(or estimate)"], rows,
            "Comparison-outcome rows give rate ratios per 1 SD (95% CrI) for the elevated blood pressure criterion, examinees already treated for hypertension, and examinees newly suspected of hypertension (systolic \u2265140 or diastolic \u226590 mm Hg without treatment), each standardized for sex and age. OR, odds ratio; RR, rate (prevalence) ratio. E-value: minimum strength of association, on the risk ratio scale, that an unmeasured confounder would need with both the characteristic and the outcome to explain away the association.")
def t5():
    W = pd.read_csv(os.path.join(RS, "S4_window_IRR.csv")); M = pd.read_csv(os.path.join(RS, "S3_main_IRR.csv"))
    rows = [[LAB[k], row(M, c), row(W[W.window == "W1_2019-21"], c), row(W[W.window == "W2_2022-24"], c)] for k, c in VARS.items()]
    return ("Table S6 Principal model by period, rate ratios per 1 SD (95% CrI)", ["Characteristic", "2019-2024", "2019-2021", "2022-2024"], rows, "Periods were set before modeling. CrI, credible interval.")
def t6():
    G = pd.read_csv(os.path.join(B, "results_gate", "S0_judgement_national.csv")); G = G[G.year >= 2013]
    rows = []
    for y in sorted(G.year.unique()):
        g = G[G.year == y].set_index("sex")
        rows.append([str(y)] + [f"{g.loc[s, 'pct_flagged_hbp']:.1f}" for s in ("M", "F", "T")] + [f"{g.loc['T', 'pct_sbp130']:.1f}", f"{g.loc['T', 'pct_dbp90']:.1f}", f"{g.loc['T', 'ratio_flag_to_sbp130']:.2f}", f"{g.loc['T', 'metab_examinees']/1e6:.1f}"])
    return ("Table S7 Elevated blood pressure criterion and measured blood pressure, national, 2013-2024", ["Year", "Criterion, men %", "Criterion, women %", "Criterion, total %", "Systolic \u2265130, %", "Diastolic \u226590, %", "Ratio criterion / systolic \u2265130", "Examinees in table, million"], rows,
            "Criterion shares from DT_35007_N139; measured distributions from DT_35007_N063 and DT_35007_N061 (diastolic bands do not separate 85 mm Hg). In 2018 the metabolic syndrome table covered a partial sample of examinees.")
if __name__ == "__main__":
    J = TX(cite="bracket"); J.para("<b>Online Resource 1</b>"); J.para(TITLE); J.para("Internal and Emergency Medicine. Seongdae Kim, Hongik University, Seoul, Republic of Korea. kimsd@hongik.ac.kr")
    for t in (t1(), t2(), t3(1), t3(2), t4(), t5(), t6()):
        J.page_break(); put_table(J, t, fs=8)
    J.doc_title = "Online Resource 1"; p = os.path.join(OUT, "ESM_1.docx"); J.save(p); to_pdf(p); print("ESM ok")
