#!/bin/bash
# HBP 체인 재개(2026-11-19 09:05): 원 체인 셸이 81a 완료(01:00) 뒤 종료됨. 81a·81R·88k kh·struct·s577 완료분은 그대로 쓰고 나머지만 실행.
set -x
export SK_RSLOTS=7
S="${ST_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"; cd "$S"; RS="$S/01_스크립트/rslot.sh"
T=HBP; GR="$S/04_분석/$T/graph_593.graph"; D=261118
q(){ while [ "$(jobs -rp | wc -l)" -ge 3 ]; do sleep 10; done; }
lw(){ while [ "$(sysctl -n vm.loadavg | awk '{print int($3)}')" -ge 14 ]; do sleep 300; done; }
( for V in s2 sc sp aux full; do lw; ST_VER=$V python3 01_스크립트/80_build_disease_panel_v.py $T && (cd 01_스크립트 && ST_VER=$V ST_THREADS=1 ST_MV_N=2 ST_GRAPH="$GR" $RS Rscript 81_fit_inla.R $T); done > 04_분석/$T/run_sens3b.log 2>&1 ) &
export ST_VER=std3 ST_THREADS=1 ST_GRAPH="$GR"
(cd 01_스크립트 && $RS Rscript 81_fit_inla.R $T) > 04_분석/$T/run_std3_81b.log 2>&1 || exit 1
python3 01_스크립트/82L_core_report_nwin.py $T $D > 04_분석/$T/run_std3_82.log 2>&1
python3 01_스크립트/83_check_report.py $T $D >> 04_분석/$T/run_std3_82.log 2>&1
echo "CHAIN done"
python3 01_스크립트/87_window_grid.py $T std3; (cd 01_스크립트 && TAG=$T ST_VER=std3 $RS Rscript 85_window_maps.R $T std3); python3 01_스크립트/86_yearly_maps_ehsa_hbp.py $T std3
python3 01_스크립트/88g_sens_prep.py $T std3 HTNTC,UNDXHC || exit 1
cd 01_스크립트; export TAG=$T NCO=HTNTC,UNDXHC
L=../04_분석/$T
for G in 1 2 3 4 5 6; do q; lw; GROUP=$G $RS Rscript 88g_sens_suite_hbp.R > $L/run_std3_88g_$G.log 2>&1 & sleep 5; done
q; lw; $RS Rscript 88h_ppc_varpart.R > $L/run_std3_88h.log 2>&1 &
for G in nb review; do q; lw; $RS Rscript 88k_struct_kh_hbp.R $G > $L/run_std3_88k_$G.log 2>&1 & sleep 5; done
wait
cd ..; TAG=$T ST_VER=std3 python3 01_스크립트/89g_sens_combine.py $T std3 > 04_분석/$T/run_std3_89g.log 2>&1
echo "ALL rc=$?"; grep -l "FAILED" 04_분석/$T/run_std3_88*.log; true
