#!/usr/bin/env python3
"""dominance.py -- evolution-dominance check for Gen 1, from the pret/pokered disassembly.

A chain-free instrument (same role as heroclix's tools/dominance.py). Within an evolution line the
growth rate -- so the tournament level -- is shared, so an evolved form with >= every base stat, the
same types and a superset of moves cannot do worse under OPTIMAL play. Any ranking that puts a
dominated pre-evolution above its evolution is flagging its AI or movesets, not the Pokemon.

Usage: py -3.14 tools/dominance.py [cache_dir]      (default: data/pokered, gitignored)

Fetches base_stats/*.asm + evos_moves.asm from pret/pokered master (cached), then for every
evolution edge pre -> post reports: stats where post < pre, type change, level-up moves pre learns
that post never learns (by level-up, level-1 set or TM), and TM/HM moves pre has that post lacks.

SCOPE: pokered = Red/Blue. Yellow-only learnsets (pret/pokeyellow) are NOT merged yet, so an edge
flagged only for lost level-up moves is provisional. In-game, moves learned before evolving carry
over -- under that reading the move-loss flags do not break dominance (see the summary line).
"""
import os, re, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

W = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "pokered")
RAW = "https://raw.githubusercontent.com/pret/pokered/master/data/pokemon/"

def get(rel, local):
    p = os.path.join(W, local)
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with urllib.request.urlopen(RAW + rel, timeout=30) as r:
            open(p, "wb").write(r.read())
    return open(p, encoding="utf-8").read()

index = get("base_stats.asm", "bs.asm")
names = re.findall(r"base_stats/([a-z_]+)\.asm", index)
with ThreadPoolExecutor(8) as ex:
    texts = dict(zip(names, ex.map(lambda n: get(f"base_stats/{n}.asm", f"bs/{n}.asm"), names)))

mon = {}
for n, t in texts.items():
    dex = re.search(r"db DEX_(\w+)", t).group(1)
    stats = list(map(int, re.search(r"db\s+(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)", t).groups()))
    types = tuple(re.search(r"db (\w+), (\w+) ; type", t).groups())
    l1 = [m for m in re.search(r"db (.+?) ; level 1 learnset", t).group(1).replace(" ", "").split(",") if m != "NO_MOVE"]
    growth = re.search(r"db (GROWTH_\w+)", t).group(1)
    tm = set(re.findall(r"[A-Z_]+[A-Z0-9_]*", re.search(r"tmhm(.*?); end", t, re.S).group(1)))
    mon[dex] = dict(stats=stats, types=types, l1=set(l1), growth=growth, tm=tm)

evos = get("evos_moves.asm", "evos.asm")
learn, edges = {}, []
for blk in re.split(r"\n(?=\w+EvosMoves:)", evos):
    m = re.match(r"(\w+)EvosMoves:", blk)
    if not m or "MissingNo" in m.group(1):
        continue
    ev, ls = blk.split("; Learnset")
    key = m.group(1).upper()
    learn[key] = {mv for _, mv in re.findall(r"db (\d+), (\w+)", ls)}
    for line in re.findall(r"db EVOLVE_\w+, ([^\n]+)", ev):
        edges.append((key, line.split(",")[-1].strip()))

def norm(k):  # evos labels vs DEX_ names
    return {"NIDORANM": "NIDORAN_M", "NIDORANF": "NIDORAN_F", "MRMIME": "MR_MIME", "FARFETCHD": "FARFETCHD"}.get(k, k)

S = ["hp", "atk", "def", "spd", "spc"]
clean = carry = 0
for pre, post in sorted(set(edges)):
    a, b = mon[norm(pre)], mon[norm(post)]
    worse = [f"{S[i]} {a['stats'][i]}->{b['stats'][i]}" for i in range(5) if b["stats"][i] < a["stats"][i]]
    typ = "" if a["types"] == b["types"] else f"type {'/'.join(a['types'])}->{'/'.join(b['types'])}"
    lost_lvl = sorted((learn[pre] | a["l1"]) - (learn[post.upper()] | b["l1"]) - b["tm"])
    lost_tm = sorted(a["tm"] - b["tm"])
    flags = [x for x in [", ".join(worse), typ, ("loses lvl moves: " + ",".join(lost_lvl)) if lost_lvl else "",
                         ("loses TM: " + ",".join(lost_tm)) if lost_tm else "",
                         "" if a["growth"] == b["growth"] else "growth differs"] if x]
    if not worse and not typ:
        carry += 1
    if flags:
        print(f"{pre:>11} -> {post:<11} " + " | ".join(flags))
    else:
        clean += 1
print(f"\n{len(set(edges))} evolution edges; {clean} strictly clean (stats>=, same type, no move lost); "
      f"{carry} dominated if pre-evolution moves carry over (stats>=, same type)")
