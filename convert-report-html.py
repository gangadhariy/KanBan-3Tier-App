#!/usr/bin/env python3

import json
from datetime import datetime

INPUT_FILE = "trivy-report.json"
OUTPUT_FILE = "trivy-report.html"

severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]

colors = {
    "CRITICAL": "#dc2626",
    "HIGH": "#ea580c",
    "MEDIUM": "#ca8a04",
    "LOW": "#2563eb",
    "UNKNOWN": "#6b7280"
}

try:
    with open(INPUT_FILE) as f:
        data = json.load(f)
except Exception as e:
    print(e)
    exit(1)

counts = {s: 0 for s in severity_order}
rows = []

for result in data.get("Results", []):
    target = result.get("Target", "")
    rtype = result.get("Type", "")

    for vuln in result.get("Vulnerabilities", []):

        sev = vuln.get("Severity", "UNKNOWN")

        if sev not in counts:
            counts["UNKNOWN"] += 1
        else:
            counts[sev] += 1

        rows.append({
            "target": target,
            "type": rtype,
            "pkg": vuln.get("PkgName", ""),
            "installed": vuln.get("InstalledVersion", ""),
            "fixed": vuln.get("FixedVersion", "-"),
            "severity": sev,
            "id": vuln.get("VulnerabilityID", ""),
            "title": vuln.get("Title", ""),
            "description": vuln.get("Description", "")
        })

rows.sort(key=lambda x: severity_order.index(x["severity"]) if x["severity"] in severity_order else 99)

html = f"""
<!DOCTYPE html>
<html>
<head>

<meta charset="UTF-8">

<title>Trivy Security Report</title>

<style>

body {{
font-family: Arial;
background:#f4f6f9;
margin:0;
padding:40px;
}}

.header {{
background:#111827;
color:white;
padding:25px;
border-radius:10px;
}}

.summary {{
display:flex;
gap:20px;
margin-top:30px;
margin-bottom:30px;
flex-wrap:wrap;
}}

.card {{
flex:1;
min-width:150px;
color:white;
padding:20px;
border-radius:10px;
text-align:center;
font-size:20px;
font-weight:bold;
}}

table {{
width:100%;
border-collapse:collapse;
background:white;
}}

th {{
background:#1f2937;
color:white;
padding:12px;
}}

td {{
padding:10px;
border-bottom:1px solid #ddd;
vertical-align:top;
}}

tr:hover {{
background:#f3f4f6;
}}

.badge {{
padding:5px 10px;
border-radius:5px;
color:white;
font-weight:bold;
}}

.search {{
margin-bottom:20px;
padding:12px;
width:350px;
font-size:16px;
}}

.footer {{
margin-top:30px;
text-align:center;
color:#777;
}}

</style>

<script>

function searchTable() {{

let input=document.getElementById("search").value.toUpperCase();

let table=document.getElementById("tbl");

let tr=table.getElementsByTagName("tr");

for(let i=1;i<tr.length;i++){{

let txt=tr[i].innerText.toUpperCase();

tr[i].style.display=txt.indexOf(input)>-1?"":"none";

}}

}}

</script>

</head>

<body>

<div class="header">

<h1>🛡 Trivy Security Scan Report</h1>

<p><b>Generated:</b> {datetime.now()}</p>

<p><b>Total Vulnerabilities:</b> {len(rows)}</p>

</div>

<div class="summary">

"""

for sev in severity_order:
    html += f"""
<div class="card" style="background:{colors[sev]}">
<div>{sev}</div>
<div style="font-size:45px">{counts[sev]}</div>
</div>
"""

html += """
</div>

<input id="search" class="search" onkeyup="searchTable()" placeholder="Search vulnerability...">

<table id="tbl">

<tr>
<th>Severity</th>
<th>CVE</th>
<th>Package</th>
<th>Installed</th>
<th>Fixed</th>
<th>Target</th>
<th>Description</th>
</tr>

"""

for r in rows:

    desc = r["title"] if r["title"] else r["description"]

    desc = desc.replace("\n"," ")

    if len(desc) > 120:
        desc = desc[:120] + "..."

    html += f"""

<tr>

<td>

<span class="badge" style="background:{colors.get(r['severity'],'gray')}">

{r['severity']}

</span>

</td>

<td>

<a href="https://nvd.nist.gov/vuln/detail/{r['id']}" target="_blank">

{r['id']}

</a>

</td>

<td>{r['pkg']}</td>

<td>{r['installed']}</td>

<td>{r['fixed']}</td>

<td>{r['target']}</td>

<td>{desc}</td>

</tr>

"""

html += """

</table>

<div class="footer">

Generated using Trivy + Python

</div>

</body>

</html>

"""

with open(OUTPUT_FILE, "w") as f:
    f.write(html)

print("HTML report generated:", OUTPUT_FILE)