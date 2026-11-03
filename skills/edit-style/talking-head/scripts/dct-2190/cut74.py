#!/usr/bin/env python3
"""User 2026-11-03: drop the 7 f silent piece 74/75 (master 41.958-42.25 s, the breath after "you don't") and close
the gap. Insert 139 and caption 438 start on the cut (now the jump cut is under insert 139), "you don't" ends there,
everything after moves up 7 f, music trimmed 7 f. Usage: cut74.py hook-N.fcproj ..."""
import json, subprocess, sys
F = 10584000000
def seq(p):
    return json.loads(subprocess.run(["filmcraft-cli","--compact","--project",p,"inspect","sequence"],capture_output=True,text=True,check=True).stdout)
def run(p, cmds):
    f = p + ".cut.jsonl"; open(f,"w").write("".join(json.dumps(c)+"\n" for c in cmds+[{"id":"file.save","params":{}}]))
    o = subprocess.run(["filmcraft-cli","--compact","--project",p,"run",f],capture_output=True,text=True)
    rs = [json.loads(l) for l in o.stdout.splitlines() if l.startswith("{")]
    import os; os.unlink(f)
    if o.returncode or not all(r.get("ok") for r in rs): sys.exit(f"{p}: {[r for r in rs if not r.get('ok')] or o.stderr[-1500:]}")
def items(s):
    return {x["clip"]:(t["id"],x) for k in ("video","audio") for t in s[k] for x in t["items"]}
tr = lambda c,e,d: {"id":"timeline.trim","params":{"clip":c,"edge":e,"mode":"regular","deltaFrames":d}}
for p in sys.argv[1:]:
    it = items(seq(p)); a, b = it[74][1]["startFrame"], it[74][1]["endFrame"]; D = b - a
    assert D == 7 and it[139][1]["startFrame"] == it[438][1]["startFrame"] == it[436][1]["endFrame"] == a + 5, p
    mv = lambda c, to: {"id":"timeline.move","params":{"moves":[{"clip":c,"track":it[c][0],"time":to*F}],"insert":False,"linked":False}}
    run(p, [{"id":"timeline.delete","params":{"clips":[74,75],"ripple":False}}, tr(436,"out",-5),
            mv(139,a), mv(438,a), tr(139,"out",-2), tr(438,"out",-2)])
    s = seq(p)
    moves = sorted([{"clip":x["clip"],"track":t["id"],"time":(x["startFrame"]-D)*F} for k in ("video","audio") for t in s[k]
                    for x in t["items"] if x["startFrame"] >= b], key=lambda m: m["time"])
    run(p, [{"id":"timeline.move","params":{"moves":moves,"insert":False,"linked":False}}, tr(369,"out",-D)])
    print(p, f"cut {a}-{b}, {len(moves)} clips moved -{D} f")
