# KiCad routing mechanics (7/9)

TOC: §1 Interactive router · §2 Diff pairs · §3 Length tuning · §4 Zones/pours ·
§5 Headless kicad-cli flow

## §1 Interactive router

- Route mode: **Interactive Router** (X key toggles); keep "Highlight net" ( ` key)
  on the net being routed — seeing the whole net beats pad-hopping.
- **Push-and-shove** mode (default in 7+): shoves neighbors within rules — prefer it
  over walkaround for density; walkaround (W) for deliberate detours.
- Via placement while routing: press V (through via), Shift+V cycles via styles
  (blind/buried if enabled in setup).
- Track width live-change: W?? no — width follows the net class; manual override =
  properties dialog or the "track width" dropdown while routing.
- Router settings: Options → Drag (45° mode) keeps corners legal when dragging;
  "Fix all vias/segments" via lock (L) once a segment is final.
- DRC hotkey (Ctrl+Shift+D / Inspect → DRC), results panel with click-to-zoom per
  violation.

## §2 Diff pairs

- Define pairs in **Schematic/Board Setup → Net Classes** (diff pair column) or by
  net-name suffix conventions (e.g. `USB_D+`/`USB_D-` auto-pairs with +/− suffix).
- Route both with **Route Differential Pair** (6 key): single action, coupled
  geometry enforced; gap follows class rules; obstacle squeeze works within limits.
- Tuning happens after: Length Tuning tools (§3). Don't hand-serpentine in the pair
  router.

## §3 Length tuning

- **Length Tuning** toolbar (toolbar icon / hotkey: single-net serpentine); start on
  the trace, drag — amplitude/pitch adjustable live; constraints from
  "Custom Rules… → length constraints" or set target interactively.
- **Tune Diff Pair Skew**: automatically adds serpentines to the shorter member.
- Set target lengths from the timing budget derivation (SKILL.md §6), not from
  "make them equal".

## §4 Zones/pours

- Draw zone (Add Filled Zone), assign net, set priority (higher = wins overlap),
  clearance + min width on the zone, connection style per zone: thermal relief /
  solid / none. Per-pad overrides: pad properties → zone connection (the override
  list for EPs/shells is the standard trick).
- **Fill/Refill zones** (B key) after EVERY routing change; "zone fill" is not live —
  stale fills cause phantom DRC and unconnected-item artifacts. Refill before any
  export (DRC includes fills only when current).
- Zone islands: zone properties → remove islands (always/never); keep DRC reporting
  them until the strategy is deliberate.

## §5 Headless kicad-cli flow

For scripted/agent-driven boards (no GUI available):

1. Edit the .kicad_pcb as s-expression text (or via pcbnew python bindings if the
   environment ships them) — preserve unedited file regions verbatim when scripting
   (re-serialization round-trips have historically broken parsers; edit surgically).
2. Run DRC headless: `kicad-cli pcb drc --output report.json --format json board.kicad_pcb`
   — parse the JSON, fix, re-run: DRC-in-the-loop beats self-assurance.
3. Export per artifact: `kicad-cli pcb export gerbers/drills/pos/step/svg...`.
4. Scripted routing pattern (field-tested on a 2-layer board): grid-based maze
   router with per-class track widths and exact DRC-matched clearance model —
   own-net exempt, other-net blocked at clearance + half-widths, board-edge margin,
   via cost in the search — then DRC, then targeted gap-fill passes, then pours.
   Convergence is iterative (dozens of passes); budget for it, and let DRC output
   drive each iteration.
