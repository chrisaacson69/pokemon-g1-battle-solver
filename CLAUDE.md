# pokemon-g1-battle-solver — app-local rules

Scope ladder: user-global `~/.claude/CLAUDE.md` (kernel: grounding, how-Chris-works) → the
vault's `projects/CLAUDE.md` (the project SDK) → **this file** (app-local). The thesis this
project tests lives in the vault: `research/gaming/pokemon-gen1-1v1-tournament.md`.

## What this project is

Exact solutions for Gen 1 (Red/Blue/Yellow) 1v1 battles. Gym Leader Matt ranked all 151
Pokémon from ~170k *sampled* battles driven by a **fixed priority-list AI**. A fixed policy turns
each matchup into an absorbing Markov chain, so every matchup has an exact win/draw/loss
probability. Goals, in order:

1. **Chain-free checks first:** evolution dominance (`tools/dominance.py`), which needs no battle model.
2. **The exact duel:** one matchup as an absorbing chain under a stated fixed policy.
3. **Cross-check:** Monte Carlo of the *same* policy must converge to the exact answer.
4. Only then a full 151×151 table, and a comparison against Matt's published ranking.

## Hard rules

- **pokered is the oracle.** Mechanics and data come from the
  [pret/pokered](https://github.com/pret/pokered) disassembly (and
  [pret/pokeyellow](https://github.com/pret/pokeyellow) for Yellow), never from wikis or from
  memory. When a wiki and the disassembly disagree, the disassembly wins, and the disagreement
  is a finding to record in `docs/`.
- **`data/` is gitignored and never committed.** The game data is Nintendo/Game Freak's. Tools
  fetch from pret into `data/` and cache it there. Commit tools and derived analysis only, the
  same posture as ROMs in the sibling decompiler repos and as `heroclix`'s `data/`.
- **Empty/failed fetch ≠ data.** Never cache a partial or empty file. `get()` re-fetches on a
  zero-byte cache entry. Keep that behavior.
- **State the policy, and count what it excludes.** A ranking is of (Pokémon × moveset ×
  policy), not of the Pokémon. Every result names the policy it was solved under. Moves the model
  can't represent yet are excluded **and counted**, never treated as a no-op. This is the heroclix
  Hercules lesson: *the metric crowns whatever best fits the model's blind spot.*
- **Dominance holds under optimal play only.** Under a heuristic policy an extra move can hurt.
  A dominance inversion flags the *policy*. It doesn't prove the policy wrong.

## Reuse before build

`heroclix` (sibling repo, `../heroclix`) already has `tools/duel.py`, an exact 1v1 absorbing-chain
solver (`N = (I-Q)^-1`, `B = N R`), and a dominance scan with the same role as ours. **Read
it before writing the duel.** If the chain machinery turns out game-agnostic, factoring it into a
shared lib is the SDK's rule ("factor out the moment a second app needs it"). Make that a
deliberate decision when the duel is written, not an accidental copy.

## Findings flow back to the vault

Results that hold beyond Gen 1 (fixed-policy ⇒ exact chain, dominance as a check on the AI,
sampling versus solving) go to the vault's `research/` with this repo as a dated specimen.
Pokémon-specific details (move effects, quirks, data layouts) stay here in `docs/`.
