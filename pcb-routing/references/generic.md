# Generic & headless routing (EasyEDA, no-tool, scripted)

TOC: §1 EasyEDA notes · §2 Advising without a tool · §3 Headless/scripted routing
pattern (field-tested) · §4 Netlist as the connectivity source of truth

## §1 EasyEDA notes

- Route mode: the routing tool follows Design Manager rules; set track/via/clearance
  in Design → Design Rules BEFORE routing (defaults are looser than quick-turn fabs).
- Copper areas (pours): draw the area, assign net, set clearance + connection style
  per area; refill/rebuild after edits (not always automatic in Std).
- Diff pair: EasyEDA Pro has the pair router; Std requires manual symmetric routing
  (route one member, then mirror its geometry) — verify lengths with the measure
  tool.
- Length tuning: Pro has a length-matching serpentine tool; Std is manual +
  measure. Keep the SKILL.md §6 rules (amplitude ≥3× width etc.).
- Export gerbers per fab guide; run their online analyzer before ordering.

## §2 Advising without a tool (plain-text consulting)

When the human uses any tool or paper: apply the SKILL.md strategy — order of
operations, ground physics, hot loops — and check THEIR geometry from exports
(gerbers) or descriptions. Concretely:

- Ask for: the layer count + stackup, which layer each critical net runs on, where
  the planes are broken, and the converter part (datasheet hot-loop figure).
- Red flags to call out: SW-node copper spread wide; sense trace parallel to the
  inductor; crystal nets taking the long way around; diff pair members on
  different layers; single return via for a layer-transitioning 8-bit bus;
  any "we'll add the ground later".
- Numbers: from `../../pcb-design-rules/SKILL.md` tables with the method attached.

## §3 Headless/scripted routing pattern (field-tested on a completed 2-layer board)

When no GUI is usable (agent/CI environments), a scripted router converges — IF the
clearance model is exact. Pattern (generalizes to any grid router):

1. **Netlist-first**: export the netlist from the schematic; drive ALL connectivity
   from it (pad-net assignments), never from memory or labels — the netlist is the
   single source of truth (§4).
2. **Grid + classes**: 0.1 mm-class grid; per-class track width and clearance
   (own-net vs other-net handled separately — DRC exempt same-net, so must the
   router).
3. **Occupancy model matching DRC exactly**: other-net obstacles block at
   (clearance + half-their-width + half-my-width) via centerline marking; own-net
   unblocked; board edge + margin blocked; via placement pads block neighbors.
   Mismatched models = a router that "succeeds" and a DRC that disagrees — the
   classic failure of naive scripted routers.
4. **Cost search**: maze/A* with via cost (via ≈ 0.4–0.6 of a long detour — vias
   cost reliability and inductance), crossing penalty, route order by priority
   (critical/power first per SKILL.md §1).
5. **DRC-in-the-loop**: export → `kicad-cli pcb drc` (or equivalent) → parse JSON →
   fix-violation passes (delete-loc-and-retry, targeted gap-fill) → re-run. Dozens
   of iterations are normal; the DRC report is the only truth.
6. **Pours last**, then refill, then final DRC + unconnected triage (zone-island
   artifacts vs real gaps), then the visual/3D passes.

Caveats: scripted routing is a fallback, not a preference — interactive push-and-shove
solves local conflicts a maze router solves by detours. Use scripted when headless is
the only option; always end with the same acceptance gates.

## §4 Netlist as the connectivity source of truth

Field-tested rule for ANY scripted board manipulation: derive pad→net maps from the
exported netlist; verify placements/edits against it; after edits, re-export and
diff. When schematic and board disagree, the netlist + re-import is the reconciliation
mechanism — don't hand-patch one side. (This also catches the "component replaced but
orphaned tracks still reference the old net" class of bugs — purge the old net's
tracks when you replace a part.)
