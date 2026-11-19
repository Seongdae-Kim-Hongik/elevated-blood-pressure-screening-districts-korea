#!/usr/bin/env python3
#  판정 정의(99G_hbp 게이트): 높은 혈압 = 수축기 ≥130 또는 이완기 ≥85 mmHg 또는 고혈압 약물 치료(측정값+투약 복합 판정). 분모 = 대사증후군 위험요인 표 수검자(N138).
#  기간: 주 2019-2024(6년), 보조 2013-2017(aux), 민감도 2013-2024 전 기간(full, 2018 부분 표본 포함). 2018은 표 수검자가 혈압 측정자의 33%뿐인 부분 표본이라 주·보조에서 뺀다.
import os, json, sqlite3, unicodedata, hashlib
import numpy as np, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); PAN = os.path.join(ROOT, "02_패널"); AN = os.path.join(ROOT, "04_분석")
DB = os.path.expandvars("$ST_GPT_DATASET") + "/02_체육건강_시공간_GPT버전/02_체육건강_시공간_GPT버전.sqlite"
POOL = "EXT_canonical_pool_HBP_261118.csv"
D = pd.read_csv(os.path.join(PAN, "EXT_canonical_pool_DIGX_261114.csv")); D = D[D.year.between(2011, 2024)].drop(columns=["digx_deaths"])
D["fbd_region"] = D.fbd_region.map(NFC)
T = pd.read_csv(os.path.join(PAN, "EXT_canonical_pool_LIPT_261111.csv"))[["year", "fbd_region", "im_specialists_per100k", "unmet_need_rate"]]; T["fbd_region"] = T.fbd_region.map(NFC)
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
RY = pd.read_sql('select year, fbd_region, "chk__수검률" as screening_uptake, "chk__질환의심_고혈압당뇨_고혈압" as undxh_cases from region_year where year between 2011 and 2024', con); RY["fbd_region"] = RY.fbd_region.map(NFC)
E = pd.read_csv(os.path.join(PAN, "HBPF_Estd3h.csv"))
Y = E[["year", "fbd_region", "cases", "offset"]].rename(columns={"cases": "hbp_cases", "offset": "hbp_examinees"}); Y["fbd_region"] = Y.fbd_region.map(NFC)
P = D.merge(T, on=["year", "fbd_region"], how="left", validate="one_to_one").merge(RY.drop(columns="undxh_cases"), on=["year", "fbd_region"], how="left", validate="one_to_one").merge(Y, on=["year", "fbd_region"], how="left", validate="one_to_one")
assert len(P) == 229 * 14, len(P)
r = P.fbd_region.map(P[P.year.isin([2020, 2024])].groupby("fbd_region").basic_livelihood_rate.mean())
bad = P.year.isin([2021, 2022, 2023]) & ((P.basic_livelihood_rate < 0.2 * r) | (P.basic_livelihood_rate > 5 * r)); print("수급률 규칙 위반 칸(정정본이면 0):", int(bad.sum()))
SRCN = os.path.join(ROOT, "00_원천", "C_NHIS_검진보험")
U = pd.concat([pd.read_csv(os.path.join(SRCN, f), encoding="utf-8-sig", low_memory=False) for f in ["DT_35007_N001.csv", "DT_35007_N001_1.csv"]])
U = U[U.C1_NM.astype(str).str.contains("세종") & (U.C2_NM == "합계")].drop_duplicates(["PRD_DE", "ITM_NM"]).pivot(index="PRD_DE", columns="ITM_NM", values="DT").astype(float)
sju = (U["수검인원"] / U["대상인원"] * 100); print("세종 수검률(원표 시도 머리행):", sju.round(2).to_dict())
m = (P.fbd_region == NFC("세종시세종시")) & P.screening_uptake.isna(); P.loc[m, "screening_uptake"] = P.loc[m, "year"].map(sju).values
n0 = int(P.screening_uptake.isna().sum()); miss = P.loc[P.screening_uptake.isna(), ["fbd_region", "year"]].values.tolist()
P = P.sort_values(["fbd_region", "year"]); P["screening_uptake"] = P.groupby("fbd_region").screening_uptake.transform(lambda s: s.interpolate(limit_area="inside").bfill().ffill())
print(f"수검률 보간·이월 {n0}칸:", miss); P = P.sort_values(["year", "fbd_region"]).reset_index(drop=True)
print("결측 칸(hbp는 2011-12 표 없음이 정상):", P.isna().sum()[P.isna().sum() > 0].to_dict())
P.to_csv(os.path.join(PAN, POOL), index=False, encoding="utf-8-sig")
# 비교 결과 패널(2019-24, 비교 결과로만)
H = pd.read_csv(os.path.join(PAN, "HTNT_Estd3q.csv")); H = H[H.year.between(2019, 2024)]
UE = pd.read_csv(os.path.join(PAN, "UNDXH_Estd.csv")); UE["fbd_region"] = UE.fbd_region.map(NFC)
UC = RY[["year", "fbd_region", "undxh_cases"]].rename(columns={"undxh_cases": "cases"})
UX = UE.merge(UC, on=["year", "fbd_region"], how="left", validate="one_to_one"); UX = UX[UX.year.between(2019, 2024) & UX.cases.notna()]
for t2, S, src in [("HTNTC", H, "35호 HTNT 02_패널/HTNT_Estd3q.csv cases·E_std"), ("UNDXHC", UX, "25호 UNDXH cases = SQLite chk__질환의심_고혈압당뇨_고혈압, E = 02_패널/UNDXH_Estd.csv")]:
    os.makedirs(os.path.join(AN, t2), exist_ok=True); S[["year", "fbd_region", "cases"]].to_csv(os.path.join(AN, t2, f"panel_{t2}.csv"), index=False)
    S[["year", "fbd_region", "E_std"]].to_csv(os.path.join(PAN, f"{t2}_Estd.csv"), index=False)
    open(os.path.join(AN, t2, "README.md"), "w").write(f"# {t2}: comparison-outcome copy for HBP(2026-11-18). 원본 = {src}(2019-24). 분석 대상 아님.\n")
    print(t2, len(S), S.year.min(), S.year.max(), S.fbd_region.nunique(), "O/E", round(S.cases.sum() / S.E_std.sum(), 4))

FORCED = ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"]
NEG = ["hit_and_run_rate", "traffic_culture_index", "fires_per_10000"]
SENS = ["tertiary_educated_share", "unmet_need_rate", "living_alone_elderly"]
HYP = ["walking_rate", "moderate_pa_rate", "public_sport_fac_per100k", "village_sport_fac_per100k",
       "obesity_rate", "high_risk_drinking", "smoking_rate", "screening_uptake", "im_specialists_per100k", "basic_livelihood_rate"]
OBES = "kchs__DT_H_OBE_OBE__SR"
X = lambda L: [OBES if v == "obesity_rate" else "ext__" + v for v in L]
XK = lambda v: OBES if v == "obesity_rate" else "ext__" + v
EXPECT = {
 "walking_rate": "- (walking rate)", "moderate_pa_rate": "- (moderate-or-higher physical activity)", "public_sport_fac_per100k": "- (public sports facilities)",
 "village_sport_fac_per100k": "- (village sports facilities)", "obesity_rate": "+ (self-reported obesity)", "high_risk_drinking": "+ (high-risk drinking)", "smoking_rate": "+ (current smoking)",
 "screening_uptake": "- (screening uptake)", "im_specialists_per100k": "+ (internal medicine specialists)", "basic_livelihood_rate": "+ (public assistance recipients)",
}
SETS = {"S1_narrative_full": X(HYP),
        "S2_core": X(["walking_rate", "public_sport_fac_per100k", "obesity_rate", "screening_uptake", "im_specialists_per100k", "basic_livelihood_rate"]),
        "S3_physical_activity": X(["walking_rate", "moderate_pa_rate", "public_sport_fac_per100k", "village_sport_fac_per100k"]),
        "S4_bp_risk_behaviour": X(["obesity_rate", "high_risk_drinking", "smoking_rate"]),
        "S5_detection_care": X(["screening_uptake", "im_specialists_per100k", "basic_livelihood_rate"]),
        "S6_risk_detection": X(["obesity_rate", "high_risk_drinking", "smoking_rate", "screening_uptake", "im_specialists_per100k", "basic_livelihood_rate"])}
pov = [{"year": 2023, "fbd_region": "경상남도창원시", "population": 1009038, "source": "KOSIS DT_1YL20651E 2023 통합창원시 계(유방암 11/4 population_final_audit)"}]
allv = ["hbp_cases", "hbp_examinees"] + FORCED + NEG + SENS + [v for v in HYP if v != "obesity_rate"]
LAB_M = "sex-and-age-standardised expected high-blood-pressure (metabolic risk factor) cases, 2 sexes x 15 age bands (<=19, 20-24 to 80-84, 85+) (national rates DT_35007_N139; district examinee age structure approximated from resident population x national uptake, sex totals observed from DT_35007_N138), YEARS"
def make(efile, years, windows, post, note_extra, excl=None):
    return {
     "tag": "HBP", "outcome_column": "ext__hbp_cases",
     "outcome_label_en": "Examinees meeting the 'high blood pressure' metabolic-syndrome risk-factor criterion at the National General Health Screening (systolic >=130 or diastolic >=85 mmHg, or on antihypertensive medication; NHIS health screening statistics DT_35007_N138, annual)",
     "disease_en": "High blood pressure as a metabolic risk factor at health screening (measured elevation or treated hypertension)",
     "disease_ko": "검진 대사증후군 위험요인 높은 혈압(측정 130/85 이상 또는 고혈압 약물 치료)",
     "offset": "ext__hbp_examinees", "exclude_years": excl or [],
     "forced": X(FORCED), "negative_controls": X(NEG),
     "offset_E_column": "E_std", "offset_E_file": efile, "offset_E_label": LAB_M.replace("YEARS", f"{years[0]}-{years[1]}"),
     "graph": "593-edge contact graph, ST_GRAPH=04_분석/HBP/graph_593.graph",
     "population_override": pov, "sensitivity_only_extra": X(SENS),
     "version": f"std3 physical-activity pathway (screen-detected high blood pressure: physical activity and sport facilities, blood-pressure risk behaviours, detection and care reach, deprivation), {years[0]}-{years[1]}" + note_extra,
     "sets": SETS, "transform": {XK(v): "none" for v in FORCED + NEG + SENS + HYP},
     "expected_direction": {XK(k): v for k, v in EXPECT.items()},
     "rules": {"likelihood": "forced-only 모형 WAIC 낮은 쪽(Poisson/NB)", "set_choice": "WAIC 최소, 4 이내면 변수 적은 세트", "credible": "95% CrI 1 제외", "vif_drop": 10, "multiverse_specs": 200,
               "main_model_note": "주모형 = S1_narrative_full(가설 10 + 강제통제 5). 세트를 다시 바꾸지 않음. VIF>10 유지·보고.",
               "years": list(years), "windows": windows, "covid_post_from": post,
               "windows_note": "결과 전 고정."},
     "note": "Outcome: elevated blood pressure criterion of the metabolic syndrome at the general health screening (NHIS), 229 districts; expected counts standardised for sex and 15 age groups.",
     "extra_columns": {"ext__" + v: [POOL, v] for v in allv}}
w_main = {"W1_2019-21": [2019, 2021], "W2_2022-24": [2022, 2024]}
OUT = {}
for ver in ["std3", "s577", "s2", "sc", "sp"]:
    j = make("HBP_Estd3h.csv", (2019, 2024), w_main, 2020, "")
    j["rules"]["windows_note"] = "6년 패널(2019-24): 시간 효과 rw1 6점, 창 = 2019-21·2022-24 2개(결과 전 고정). 2018 부분 표본을 가로지르지 않는다."
    if ver == "s577": j["sens_note"] = "민감도: 그래프만 queen 577"
    if ver == "s2": j["sens_note"] = "민감도: 80세 이상 비율 강제통제 없음"; j["forced"] = X(FORCED[:4])
    if ver == "sp": j["sens_note"] = "민감도: 주민 인구 분모 성·연령 표준화 E(수검 선택 민감도, 무조건부 유병)"; j["offset_E_column"] = "E_pop"; j["offset_E_label"] = "population-based sex-age standardised E (resident population x national high-blood-pressure per resident rate)"
    if ver == "sc": j["sens_note"] = "민감도: 비표준화(조) E(수검자 × 전국 연도 판정 율)"; j["offset_E_column"] = "E_crude"; j["offset_E_label"] = "crude E (examinees x national annual high-blood-pressure rate)"
    OUT[ver] = j
j = make("HBPA_Estd3h.csv", (2013, 2017), {"W1_2013-15": [2013, 2015], "W2_2016-17": [2016, 2017]}, 2016, " [aux: 2013-2017, before the 2018 partial-sample year]")
j["rules"]["windows_note"] = "보조 기간 2013-17(2018 부분 표본 이전). 창 2013-15·2016-17. S5 COVID 단계는 해당 없음."; OUT["aux"] = j
j = make("HBPF_Estd3h.csv", (2013, 2024), {"W1_2013-17": [2013, 2017], "W2_2018-24": [2018, 2024]}, 2020, " [full: 2013-2024 including the 2018 partial sample]")
j["rules"]["windows_note"] = "민감도 전 기간 2013-24(2018 부분 표본 포함, 연도별 E가 전국 수준을 흡수)."; OUT["full"] = j
H = []
for ver, j in OUT.items():
    fp = os.path.join(HERE, f"sets_HBP_{ver}.json"); json.dump(j, open(fp, "w"), ensure_ascii=False, indent=1)
    H.append(f"sets_HBP_{ver}.json sha256={hashlib.sha256(open(fp, 'rb').read()).hexdigest()}")
open(os.path.join(HERE, "00_HBP_sets_해시_적합전_261118.txt"), "w").write("# 63호 HBP sets json 해시(적합 전 고정, 2026-11-18)\n" + "\n".join(H) + "\n(11/18 23:2x 재생성: E 파일에 E_pop 열 추가·sp 세트 추가, 적합 전. std3 내용은 이전 해시와 같음)\n")
print("\n".join(H))
