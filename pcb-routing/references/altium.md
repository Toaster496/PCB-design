# Altium routing mechanics

TOC: §1 Interactive routing · §2 Diff pairs · §3 Length tuning · §4 Planes/pours ·
§5 Rules enforcement while routing

## §1 Interactive routing

- Route mode: Place → Interactive Routing (Ctrl+W start); click-drag to place;
  Shift+R cycles routing conflict resolution modes (Stop / Ignore Obstacles /
  Push-and-Shove / Hug-and-Push — use Push-and-Shove for density, never Ignore
  except for deliberate violation-planning).
- Via while routing: press 2 (toggle layer + via) — the via drops when the layer
  switches; number row = layer selection.
- Widths: come from rules (per-net-class) automatically; override with Tab during
  routing (single-segment).
- Lock: lock a routed track (right-click → Lock) so later passes don't shove
  finished critical nets. Selection filter (Shift+S single-layer mode / selection
  masks) for bulk moves.
- DRC live: online DRC on (violation overlays as you route); full DRC:
  Reports → Design Rule Check.

## §2 Diff pairs

- Define pairs in schematic (differential pair directive on the wire pair) or
  Objects → Differential Pairs; net naming `_P/_N` or `+/-` conventions pair
  automatically.
- Route with Place → Interactive Differential Pair Routing — coupled geometry
  enforced; width/gap from the diff pair rules (impedance-profile driven: Design
  → Impedance Calculation / layer stack manager's impedance tab in recent versions).

## §3 Length tuning

- Place → Interactive Length Tuning / Interactive Delay Tuning (serpentine on the
  fly; Tab adjusts amplitude/pitch/target).
- Net-length rules (Matched Lengths / Max-Min length classes) drive the target;
  derive the tolerance from the timing budget (SKILL.md §6).
- The PCB panel → Nets view shows live length vs target while tuning.

## §4 Planes/pours

- Internal planes: dedicated power planes assigned by net (Layer Stack Manager);
  split planes drawn as regions with isolation gaps.
- Polygon pours: Place → Solid Region (polygon), net-assigned, with per-polygon
  thermal-relief/direct connect and pour priority; repour (Tools → Polygon Pours →
  Repour) after edits, or enable repour-on-modification.
- Pad/pin-level connection override: the thermal relay direct-connect rules or
  per-pad properties (use for EPs — see SKILL.md §2 & `../../pcb-design-rules`).

## §5 Rules enforcement

Rules (Design → Rules) are enforced DURING interactive routing — set them before
routing (net classes, widths, via styles, clearances per `../../pcb-design-rules`).
Blind/buried vias: enable in Layer Stack Manager (drill pair manager); they
participate in rules like any via. Final gate: DRC report clean + visual passes per
SKILL.md §8.
