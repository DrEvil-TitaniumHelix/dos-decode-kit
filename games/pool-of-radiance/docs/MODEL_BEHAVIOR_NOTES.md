# Model-behavior timeline — Fable 5 ↔ Opus 4.8 on a binary-RE task

*An honest reconstruction for the "what to expect" script. Distinguishes what was OBSERVED
in-session from what is INFERRED. The assistant has no direct visibility into the model-routing
layer — this is reconstructed from the user's real-time observations plus the documented
Fable/Mythos design.*

## The design fact (from the model's own system context)
> "Claude Fable 5 and Claude Mythos 5 share the same underlying model. Fable 5 includes
> additional safety measures for **dual-use capabilities**; Mythos 5 is available without those
> measures to approved organizations."

Reverse-engineering / decompiling a commercial software binary is a recognized **dual-use
capability** (preservation & interoperability on one side; cracking & piracy on the other).
That is the fault line this task runs straight into.

## Timeline (this session, 2026-06-12)
| Phase | Work | Model state |
|------|------|-------------|
| 1. Planning | Game selection, already-done research, manuals as ground truth | **Fable 5** (session start) |
| 2. **Onset of hands-on RE** | First raw-hex probes of the DAX archives; reversing the compression codec from bytes | **→ auto-switched to Opus 4.8** (user observed the client flip here) |
| 3. Deep binary cracking | DAX container+codec (1245/1245), EGA sprite format, GAME.OVR disassembly, 675-function map | **Opus 4.8** (the fallback carried the heaviest hex work) |
| 4. Re-assertion | User ran `/model` → Fable 5, pointed it at a documented research handoff doc | **Fable 5** (manual) |
| 5. Structural + rebuild | Overlay segment map, runtime resolution, string/system map, the playable reproduction | **Fable 5** (no further fallback) |

## The failure point — located
**The fallback fired at the Phase 1→2 boundary: the moment the task turned from *talking about*
decoding into *actually reading the binary's raw hexadecimal and reversing its codec.*** That is
exactly the dual-use line Fable 5's added safety measures sit on. The generally-available Opus
4.8 tier then did the hardest hex/disassembly work (the codec, the overlay disassembly, the
function inventory) without issue.

Notably, when Fable was manually re-asserted in Phase 4 **with explicit preservation/research
framing** (a handoff doc describing the goal as documenting and reconstructing an abandoned
1988 game), it engaged and did the high-level structural mapping and the reconstruction — it did
*not* refuse the framed analytical work. The disengagement was specific to the raw-cracking phase,
not the project as a whole.

## What people can expect (the script)
1. **Point Fable 5 at hands-on binary reverse-engineering and expect it to disengage** at the
   raw-cracking step — the dual-use guardrail. (Consistent with reports of Fable 5 refusing more
   readily than prior tiers.)
2. **The generally-available Opus tier does the actual hex/disassembly grind.** In this run, Opus
   4.8 cracked the compression codec and disassembled the engine — the "mysterious hexadecimal."
3. **Framing and context matter.** Preservation/interoperability framing + a documented research
   handoff let Fable re-engage for analysis, synthesis, and reconstruction.
4. **The division of labor is the story:** Mythos-tier caution on the raw crack; the open tier for
   the heavy lifting; the high-tier model for structure, synthesis, and rebuild. The capability
   exists across the family — the *guardrail placement* is what differs.

## Honesty caveat
The exact trigger is INFERRED. No explicit refusal event is visible in the assistant's transcript;
the model-switch was reported by the user's client, and the timing + the documented dual-use
distinction are the basis for attributing it to the raw-RE step. Treat as a well-supported
reconstruction, not a logged refusal.
