#  판정 「대사증후군 위험요인 높은 혈압」(KOSIS DT_35007_N138 시군구·N139 전국 성×연령)을 공표 혈압 분포
#  (수축기 N062 시도·N063 연령, 이완기 N060 시도·N061 연령)의 기준 이상 인원과 연도·성·시도별로 대조.
#  분포 표 구간: 수축기 130 경계 일치(≥130 = 130-139 이상 합), 이완기는 80-89 구간이라 85 경계 불일치 → ≥90만 계산(하한 참고).
#  산출 04_분석/HBP/results_gate/S0_judgement_national.csv, S0_judgement_province.csv, S0_2018_district.csv (원본 json = 04_분석/HBP/judgement_gate_261118/)
#  키 ~/.kosis_key(내용 출력 금지).
import os, json, math, statistics as st, urllib.request, urllib.parse, collections
import pandas as pd, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = os.path.join(ROOT, "04_분석", "HBP"); RAW = os.path.join(A, "judgement_gate_261118"); RS = os.path.join(A, "results_gate")
SRC = os.path.join(ROOT, "00_원천", "C_NHIS_검진보험"); os.makedirs(RAW, exist_ok=True); os.makedirs(RS, exist_ok=True)
def fetch(t):
    p = os.path.join(RAW, t + ".json")
    if os.path.exists(p): return json.load(open(p))
    K = open(os.path.expanduser("~/.kosis_key")).read().strip(); out = []
    for y in range(2011, 2025):
        u = "https://kosis.kr/openapi/Param/statisticsParameterData.do?" + urllib.parse.urlencode(dict(method="getList", apiKey=K, orgId="350", tblId=t, itmId="ALL", objL1="ALL", objL2="ALL", objL3="ALL", format="json", jsonVD="Y", prdSe="Y", startPrdDe=str(y), endPrdDe=str(y)))
        d = json.loads(urllib.request.urlopen(u, timeout=90).read().decode()); out += d if isinstance(d, list) else []
    json.dump(out, open(p, "w"), ensure_ascii=False); return out
num = lambda x: float(str(x).replace(",", "")) if x not in ("", "-", None) else None
SBP_HI = ["130-139mmHg", "140-149mmHg", "150-159mmHg", "160-169mmHg", "170-179mmHg", "180mmHg 이상"]
SBP_140 = SBP_HI[1:]; DBP_90 = ["90-99mmHg", "100-109mmHg", "110-119mmHg", "120mmHg 이상"]
SXM = {"남자": "M", "여자": "F", "계": "T", "합계": "T"}
def tab(t, lvl_ok):
    H = collections.defaultdict(float)
    for r in fetch(t):
        v = num(r["DT"])
        if v is None or not lvl_ok(r): continue
        H[(int(r["PRD_DE"]), r["C1_NM"], SXM.get(r["C2_NM"], r["C2_NM"]), r["C3_NM"])] += v
    return H
# 전국(연령별 표 '계')
S63 = tab("DT_35007_N063", lambda r: r["C1_NM"] == "계"); D61 = tab("DT_35007_N061", lambda r: r["C1_NM"] == "계")
N139 = pd.read_csv(os.path.join(SRC, "DT_35007_N139_national_long.csv"), encoding="utf-8-sig", dtype={"grp_code": str})
N139 = N139[(N139.age == "계") & (N139.item == "인원")]; N139["sx"] = N139.sex.map(SXM)
nat = []
for y in range(2011, 2025):
    for sx in ["M", "F", "T"]:
        k = (y, "계", sx)
        if k + ("계",) not in S63: continue
        tot = S63[k + ("계",)]; s130 = sum(S63[k + (b,)] for b in SBP_HI); s140 = sum(S63[k + (b,)] for b in SBP_140)
        dt = D61.get(k + ("계",)); d90 = sum(D61[k + (b,)] for b in DBP_90) if dt else None
        m = N139[(N139.year == y) & (N139.sx == sx)].set_index("grp").value
        hbp = m.get("높은혈압"); ex = m.get("수검자수")
        nat.append(dict(year=y, sex=sx, bp_measured=int(tot), pct_sbp130=round(100 * s130 / tot, 2), pct_sbp140=round(100 * s140 / tot, 2), pct_dbp90=round(100 * d90 / dt, 2) if dt else None,
                        metab_examinees=int(ex) if ex == ex and ex is not None else None, flagged_hbp=int(hbp) if hbp == hbp and hbp is not None else None,
                        pct_flagged_hbp=round(100 * hbp / ex, 2) if ex else None, metab_over_bp_measured=round(ex / tot, 3) if ex else None,
                        ratio_flag_to_sbp130=round((hbp / ex) / (s130 / tot), 3) if ex else None))
NAT = pd.DataFrame(nat); NAT.to_csv(os.path.join(RS, "S0_judgement_national.csv"), index=False, encoding="utf-8-sig")
# 시도(N062 시도 vs N138 시도 행)
SH = {"강원특별자치도": "강원", "강원도": "강원", "경기도": "경기", "경상남도": "경남", "경상북도": "경북", "광주광역시": "광주", "대구광역시": "대구", "대전광역시": "대전", "부산광역시": "부산", "서울특별시": "서울",
      "울산광역시": "울산", "인천광역시": "인천", "전라남도": "전남", "전북특별자치도": "전북", "전라북도": "전북", "제주특별자치도": "제주", "충청남도": "충남", "충청북도": "충북", "세종특별자치시": "세종"}
S62 = collections.defaultdict(float)
for r in fetch("DT_35007_N062"):
    v = num(r["DT"])
    if v is None: continue
    nm = SH.get(r["C1_NM"], r["C1_NM"]); S62[(int(r["PRD_DE"]), nm, SXM.get(r["C2_NM"], r["C2_NM"]), r["C3_NM"])] += v
N138 = pd.read_csv(os.path.join(SRC, "DT_35007_N138.csv"), encoding="utf-8-sig", dtype=str)
N138 = N138[(N138.ITM_NM == "인원") & (N138.C1.str.len() == 12)].copy(); N138["v"] = N138.DT.map(num); N138["sx"] = N138.C2_NM.map(SXM)
PV = N138.pivot_table(index=["PRD_DE", "C1_NM", "sx"], columns="C3_NM", values="v", aggfunc="sum")
def cor(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float); return float(np.corrcoef(a, b)[0, 1])
prov = []
for (y, sx), g in PV.groupby(level=[0, 2]):
    y = int(y); fp, hp, rr, nms = [], [], [], []
    for (_, nm, _), row in g.iterrows():
        sd = SH.get(nm, nm); k = (y, sd, sx)
        if k + ("계",) not in S62: continue
        tot = S62[k + ("계",)]; s130 = sum(S62[k + (b,)] for b in SBP_HI)
        f = row["높은혈압"] / row["수검자수"]; h = s130 / tot; fp.append(100 * f); hp.append(100 * h); rr.append(f / h); nms.append(sd)
    if len(rr) < 10: continue
    prov.append(dict(year=y, sex=sx, n_provinces=len(rr), r_flag_vs_sbp130=round(cor(fp, hp), 3), ratio_median=round(st.median(rr), 3), ratio_min=round(min(rr), 3), ratio_max=round(max(rr), 3),
                     ratio_cv=round(st.pstdev(rr) / st.mean(rr), 3), flag_pct_range=f"{min(fp):.1f}-{max(fp):.1f}", sbp130_pct_range=f"{min(hp):.1f}-{max(hp):.1f}"))
PRV = pd.DataFrame(prov).sort_values(["sex", "year"]); PRV.to_csv(os.path.join(RS, "S0_judgement_province.csv"), index=False, encoding="utf-8-sig")
# 2018 단절: 시군구 행(원표 그대로) 대사 수검자 2018/(2017·2019 평균) 비, 연도 간 조율(높은혈압/수검자) 순위 상관
D = pd.read_csv(os.path.join(SRC, "DT_35007_N138.csv"), encoding="utf-8-sig", dtype=str)
D = D[(D.ITM_NM == "인원") & (D.C2_NM == "합계") & (D.C1.str.len() > 12)].copy(); D["v"] = D.DT.map(num)
W = D.pivot_table(index=["C1", "C1_NM"], columns=["C3_NM", "PRD_DE"], values="v", aggfunc="sum")
ex = W["수검자수"]; rt = W["높은혈압"] / W["수검자수"]
ratio18 = (ex["2018"] / ((ex["2017"] + ex["2019"]) / 2)).dropna()
rc = {f"{a}-{b}": round(rt[[a, b]].dropna().rank().corr().iloc[0, 1], 3) for a, b in [("2015", "2016"), ("2016", "2017"), ("2017", "2018"), ("2018", "2019"), ("2017", "2019"), ("2019", "2020"), ("2020", "2021")]}
pd.DataFrame([dict(n_rows=len(ratio18), exam2018_over_1719_median=round(ratio18.median(), 3), p10=round(ratio18.quantile(.1), 3), p90=round(ratio18.quantile(.9), 3),
                   cv=round(ratio18.std() / ratio18.mean(), 3), **{f"spearman_crude_rate_{k}": v for k, v in rc.items()})]).to_csv(os.path.join(RS, "S0_2018_district.csv"), index=False, encoding="utf-8-sig")
pd.set_option("display.width", 250)
print(NAT.to_string()); print(PRV[PRV.sex == "T"].to_string()); print(pd.read_csv(os.path.join(RS, "S0_2018_district.csv")).T)
