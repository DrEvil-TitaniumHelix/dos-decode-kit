# The Decode Kit — methodology for reverse-engineering & reconstructing DOS games

A repeatable process, proven on Midwinter (1989) and Pool of Radiance (1988). The kit is the
*method* (+ reusable scaffolding), not a magic one-click tool — formats differ per game.

## The pipeline (per game)
1. **Unwrap** — identify & undo the executable packer (EXEPACK/LZEXE/overlay), get clean code/data.
2. **Container & codec** — crack the archive format (directory + compression). One codec usually
   unlocks every asset file (and often the whole engine family — e.g. all 12 SSI Gold Box games).
3. **Assets** — decode image/sprite/map formats; validate by rendering (the eye is the oracle).
4. **Data structures** — characters, items, maps, tables — validate against the shipped manuals.
5. **Engine code** — disassemble; map the function inventory; resolve the call graph & runtime.
6. **The content VM** — many games compile their content (events/dialog/quests) to a bytecode
   interpreter. Decode the VM (dispatch + opcodes + text codec) to recover the actual game.
7. **Reconstruct** — feed the decoded data into a new front-end (web / Unreal / Godot).

Ground truth at every step: the bytes themselves (hard validation oracles) + the original manuals.
Never accept a plausible-but-unverified decode.

## ⭐ Model-aware task routing (a core part of the toolset)
Reverse-engineering rewards switching between Claude models by capability tier — this is
*model switching*, distinct from *agent switching* (parallelism). The pattern that emerged on a
real decode:

- **Opus 4.8 carries most of the load.** Planning, scaffolding, a lot of the decode grind,
  reconstruction, and synthesis. It's the workhorse and gets you most of the way there.
- **When Opus hits a wall, switch to Fable 5 — it does the hard decode, then continues.** On the
  toughest cracks (where Opus stalls and keeps circling the same spot), the higher-capability
  Mythos-class model breaks through and carries the thread forward. Don't bang Opus's head against
  the wall — switch the model at the wall, then let it run on.
- **The multi-agent workflow is the vehicle.** Scope and orchestrate the job, route each chunk to
  the tier that fits, and escalate to Fable exactly at the walls.

Observed live on 2026-06-12 (Pool of Radiance): Opus did a lot of the decode, hit walls on the
hardest parts, and Fable broke through and continued — including a cleaner re-decode of the source
art after Opus's first graphics pass came out wrong.

> ⚠️ Note (2026-06-12): **Fable 5 was withdrawn from public availability the day after this run**
> (a US export-control directive; see press). The "escalate to Fable at the wall" step is therefore
> not reproducible as written today — Opus 4.8 and the open tier remain available. Whether the method
> still completes *without* the Fable escalation is an open test (next subject: Curse of the Azure
> Bonds). Be honest about this in any write-up: this run used a model that is no longer accessible.

## Reusable scaffolding (game-agnostic starting line)
- packer-unwrap helpers, capstone 16-bit disassembly harness, overlay/segment-map parser,
  function-inventory + call-graph tooling, the DAX-style archive reader pattern, render-to-validate
  harness, and the multi-agent workflow templates (function-ledger sweep; bytecode-VM decode).
