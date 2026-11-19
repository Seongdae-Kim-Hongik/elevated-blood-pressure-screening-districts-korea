import os, re, subprocess
from docx import Document
from docx.shared import Pt, Cm
import content_hbp as C
import build_iem_hbp as BC
OUT = BC.OUT; N = C.N; W = dict(l.split("=") for l in open(os.path.join(OUT, "wordcount_iem.txt")).read().split())
SIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "signature_kim.png")
DATE = "19 November 2026"
cl = [DATE, "The Editors-in-Chief", "Internal and Emergency Medicine", "",
      "Dear Editors,",
      f"Please find enclosed the manuscript entitled \"{BC.TITLE}\" by Seongdae Kim, for consideration as an Original Article in the Internal Medicine section of Internal and Emergency Medicine.",
      f"The elevated blood pressure criterion of the metabolic syndrome counts both measured elevation and antihypertensive treatment, and internists and health planners use metabolic syndrome components to compare cardiometabolic risk between populations. Using national health screening statistics for all {N['n_districts']} Korean districts from 2019 to 2024, this study checked the published criterion against the measured blood pressure distribution and found that its national rise was consistent with a growing treated component. District differences in the criterion were modest and stable; associations with public assistance, obesity, and public sports facilities were small, depended on model specification, and explained little of the geography, and walking and moderate physical activity showed no consistent association.",
      "For clinicians and services that rely on metabolic syndrome components to describe populations, the study indicates that treated and untreated blood pressure should be distinguished before areas are compared.",
      f"The main text contains {int(W['body_chars']):,} characters with spaces, with an abstract of {int(W['abstract_words'])} words, two tables, two figures, and {W['refs']} references. Online Resource 1 contains the data checks and all sensitivity analyses.",
      f"The analysis code is openly available on Zenodo (https://doi.org/{BC.ZENODO}) and GitHub ({BC.GITHUB}). The processed analytic data are available from the author on reasonable request.",
      f"This manuscript has not been published previously and is not under consideration for publication elsewhere. The author has read and approved the manuscript. The Institutional Review Board of Hongik University approved the study (7002340-202511-HR-012; continuing review 7002340-202611-HR-040) and waived informed consent because only aggregated public statistics were used. The author has no competing interests and received no specific funding. {BC.AI_STATEMENT}",
      "Thank you for considering this manuscript.", "", "Yours sincerely,", "[[SIG]]",
      "Seongdae Kim, PhD (corresponding author)", BC.ADDRESS, f"Email: {BC.EMAIL}"]
d = Document(); st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(10.5); st.paragraph_format.space_after = Pt(3); st.paragraph_format.line_spacing = 1.0
for s in d.sections: s.page_width, s.page_height = Cm(21), Cm(29.7); s.left_margin = s.right_margin = Cm(2.3); s.top_margin = s.bottom_margin = Cm(2.0)
gap = False
for t in cl:
    if t == "": gap = True; continue
    if t == "[[SIG]]": p = d.add_paragraph(); p.add_run().add_picture(SIG, width=Cm(3.2)); continue
    p = d.add_paragraph(t)
    if gap: p.paragraph_format.space_before = Pt(8); gap = False
d.core_properties.author = "Seongdae Kim"; d.core_properties.last_modified_by = "Seongdae Kim"; d.core_properties.title = "Cover Letter"; d.core_properties.comments = ""
fp = os.path.join(OUT, "Cover_Letter.docx"); d.save(fp)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_hbp_cl", "--convert-to", "pdf", "--outdir", OUT, fp], capture_output=True)
txt = subprocess.run(["pdftotext", fp.replace(".docx", ".pdf"), "-"], capture_output=True, text=True).stdout
assert not re.search(r"\b(we|our|us|I)\b", txt) and "—" not in txt and "7002340-202611-HR-040" in txt, "문체·IRB"
assert not re.search(r"(?i)overlap|same data(set)?|previously submitted|Chun|reviewer", txt), "중복 고지·심사자"
pages = subprocess.run(["pdfinfo", fp.replace(".docx", ".pdf")], capture_output=True, text=True).stdout.split("Pages:")[1].split()[0]
assert pages == "1", pages; print("cover pages", pages)
