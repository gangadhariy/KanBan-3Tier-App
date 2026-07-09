#!/usr/bin/env python3
"""
Enterprise Trivy HTML Report Generator
Reads:
  - trivy-report.json (required)
  - build-info.json (optional)

Generates:
  - trivy-report.html
"""
import json, os
from datetime import datetime

INPUT="trivy-report.json"
BUILD="build-info.json"
OUT="trivy-report.html"

sev_order=["CRITICAL","HIGH","MEDIUM","LOW","UNKNOWN"]
colors={"CRITICAL":"#dc2626","HIGH":"#ea580c","MEDIUM":"#ca8a04","LOW":"#2563eb","UNKNOWN":"#6b7280"}

with open(INPUT) as f:
    data=json.load(f)

build={}
if os.path.exists(BUILD):
    with open(BUILD) as f:
        build=json.load(f)

counts={k:0 for k in sev_order}
rows=[]
for r in data.get("Results",[]):
    target=r.get("Target","")
    for v in r.get("Vulnerabilities",[]):
        sev=v.get("Severity","UNKNOWN")
        if sev not in counts: sev="UNKNOWN"
        counts[sev]+=1
        rows.append({
            "sev":sev,
            "id":v.get("VulnerabilityID",""),
            "pkg":v.get("PkgName",""),
            "inst":v.get("InstalledVersion",""),
            "fix":v.get("FixedVersion",""),
            "target":target,
            "title":v.get("Title") or v.get("Description","")
        })

rows.sort(key=lambda x: sev_order.index(x["sev"]) if x["sev"] in sev_order else 99)

cards=""
for s in sev_order:
    cards+=f'<div class="card" style="background:{colors[s]}"><h3>{s}</h3><div class="num">{counts[s]}</div></div>'

trs=""
for r in rows:
    desc=r["title"].replace("\n"," ")
    badge=f'<span class="badge" style="background:{colors[r["sev"]]}">{r["sev"]}</span>'
    fix="❌ No Fix" if not r["fix"] else "✅ "+r["fix"]
    trs+=f"""<tr>
<td>{badge}</td>
<td><a target="_blank" href="https://nvd.nist.gov/vuln/detail/{r['id']}">{r['id']}</a></td>
<td>{r['pkg']}</td><td>{r['inst']}</td><td>{fix}</td><td>{r['target']}</td>
<td><details><summary>View</summary>{desc}</details></td></tr>"""

html=f"""<!doctype html><html><head><meta charset=utf-8>
<title>Enterprise Trivy Report</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body{{font-family:Arial;background:#f4f6f9;margin:0}}
header{{background:#111827;color:#fff;padding:25px}}
.wrap{{padding:25px}}
.cards{{display:flex;gap:15px;flex-wrap:wrap}}
.card{{flex:1;color:#fff;border-radius:10px;padding:15px;min-width:120px;text-align:center}}
.num{{font-size:42px;font-weight:bold}}
table{{width:100%;border-collapse:collapse;background:#fff}}
th{{background:#1f2937;color:#fff;position:sticky;top:0}}
th,td{{padding:10px;border:1px solid #ddd}}
.badge{{padding:5px 10px;border-radius:5px;color:#fff;font-weight:bold}}
input{{padding:10px;width:300px;margin:20px 0}}
.grid{{display:grid;grid-template-columns:2fr 1fr;gap:25px}}
.box{{background:#fff;padding:20px;border-radius:10px}}
</style>
<script>
function search(){{
let f=document.getElementById('s').value.toUpperCase();
let tr=document.querySelectorAll('#t tbody tr');
tr.forEach(x=>x.style.display=x.innerText.toUpperCase().includes(f)?'':'none');
}}
</script></head><body>
<header>
<h1>🛡 Enterprise Trivy Security Report</h1>
<p>Generated: {datetime.now()}</p>
</header>
<div class="wrap">
<div class="cards">{cards}</div>
<div class="grid">
<div class="box">
<h2>Build Information</h2>
<table>
<tr><td>Job</td><td>{build.get("jobName",os.getenv("JOB_NAME","N/A"))}</td></tr>
<tr><td>Build</td><td>{build.get("buildNumber",os.getenv("BUILD_NUMBER","N/A"))}</td></tr>
<tr><td>Branch</td><td>{build.get("branch",os.getenv("GIT_BRANCH","N/A"))}</td></tr>
<tr><td>Commit</td><td>{build.get("commit",os.getenv("GIT_COMMIT","N/A"))}</td></tr>
<tr><td>Image</td><td>{build.get("image",os.getenv("DOCKER_IMAGE","N/A"))}</td></tr>
</table>
</div>
<div class="box"><canvas id="pie"></canvas></div>
</div>
<input id="s" onkeyup="search()" placeholder="Search...">
<table id="t"><thead><tr><th>Severity</th><th>CVE</th><th>Package</th><th>Installed</th><th>Fixed</th><th>Target</th><th>Description</th></tr></thead>
<tbody>{trs}</tbody></table>
<h2>Recommendations</h2>
<ul>
<li>Upgrade packages where fixes are available.</li>
<li>Rebuild and rescan the image.</li>
<li>Fail pipeline on Critical vulnerabilities.</li>
<li>Review SonarQube Quality Gate before deployment.</li>
</ul>
</div>
<script>
new Chart(document.getElementById('pie'),{{
type:'pie',
data:{{labels:{sev_order},
datasets:[{{data:[{",".join(str(counts[s]) for s in sev_order)}],
backgroundColor:['#dc2626','#ea580c','#ca8a04','#2563eb','#6b7280']}}]}}
}});
</script></body></html>"""
with open(OUT,"w") as f:f.write(html)
print("Generated",OUT)
