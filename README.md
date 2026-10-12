# pokemon-g1-battle-solver

Exact (not sampled) solutions for Generation 1 Pokémon 1v1 battles, grounded in the
[pret/pokered](https://github.com/pret/pokered) disassembly.

**Why:** Gym Leader Matt's ["I Simulated 170,000 Battles to Rank All Generation 1 Pokémon"](https://www.youtube.com/watch?v=PvMYjcQg75M)
(2026-10-09) ranks the field with 15 Monte Carlo battles per pair under a *fixed* priority-list
AI. A fixed policy makes every matchup an absorbing Markov chain with an exact answer. This repo
computes that answer, along with the checks the video skipped.

## Status

| Step | Tool | State |
|---|---|---|
| Evolution dominance from pokered | `tools/dominance.py` | **done**: 72 edges; 48 strictly dominated; 56 if pre-evolution moves carry over |
| Merge Yellow learnsets (pokeyellow) | — | next |
| Find Matt's full ranking table; run the dominance-inversion check | — | open |
| Exact duel (one matchup, stated fixed policy) | — | open; read `../heroclix/tools/duel.py` first |
| Monte Carlo of the same policy (cross-check) | — | open |
| 151×151 exact table; bracket odds | — | open |

## Run

```
py -3.14 tools/dominance.py          # fetches pokered data into data/ (gitignored), prints non-dominated edges
```

Game data is fetched at runtime and never committed. See `CLAUDE.md`.
