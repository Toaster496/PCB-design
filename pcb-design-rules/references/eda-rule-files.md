# EDA rule files — encoding the rule set per tool

TOC: §1 KiCad · §2 Altium · §3 EasyEDA · §4 Generic (no tool / scripted)

Read only your tool's section. The numbers to enter come from
`../../SKILL.md` + your fab's capability page; this reference is the "where do I type
it" map.

## §1 KiCad (7/9)

Net classes: **Board Setup → Design Rules → Net Classes** (per-class track width,
via size, clearance; assign nets by pattern or individually in Schematic Setup →
Net Classes in v8+ or the board's nets panel).

Custom DRC rules (custom.rules, KiCad syntax):
```
(rule "HV-zone"
  (constraint clearance (min 3mm))
  (condition "A.NetClass == 'HV_IN'"))
(rule "power-width"
  (constraint track_width (min 0.8mm))
  (condition "A.NetClass == 'PWR_2A'"))
```
Zone-level overrides (clearance, connect style solid/thermal, priority) live on the
zone properties dialog; per-net via/width by class; board-level defaults in Board
Setup. The DRC engine enforces net-class + rules file; run DRC via GUI or
`kicad-cli pcb drc` headless (exit code + JSON report — ideal for scripted loops).

Export/import: design rules live inside the .kicad_pro/.kicad_prl files; keep a
human-readable copy of your intended rules in the project journal or a rules.csv
(`../../scripts/check_rules.py` validates the CSV before you type it into the tool).

## §2 Altium Designer

Rules engine: **Design → Rules** tree, each rule = a constraint + a scope (query).
Priority order matters (first-match-wins per violation class). Typical set:
- Clearance (Binary, scope `InNetClass('HV')`, min 3 mm)
- Routing Width (`InNetClass('PWR_2A')`, min-pref-max 0.8-1.0-1.2 mm)
- Routing Via Style (per class)
- Plane connect style (Direct for EPs/`IsThermalPad`-style queries, Relief default)
- Mask expansions/paste (SolderMaskExpansion, SilkToPadClearance)
- Room/placement rules for zones.
Scope with net-class queries, NOT individual nets, so renaming doesn't break rules.
Rules are saved in the .PcbDoc; export a rule report for the journal.

## §3 EasyEDA (Std/Pro)

Design Manager → Design Rules: track width/via/clearance globals, then per-net
overrides via Net Classes (Pro) or manually assigning nets to rules. Pro keeps
"Constraint Manager" closer to Altium's model. EasyEDA's default clearance is often
LOOSER than your fab's real limit — tighten globals first, then per-class. Zones
(copper areas) carry their own clearance + connection-style properties.

## §4 Generic (no EDA tool / scripted / advising a human)

Keep the rule matrix as the CSV (`../../assets/rules_template.csv`) and treat it as
the source of truth:

1. Validate: `python ../../scripts/check_rules.py rules.csv`
2. When the human/tool applies geometry, spot-check the tightest constraints in the
   output artifacts (gerbers) — e.g. measure the smallest gap in the copper layers
   (a small script or the fab's online analyzer does this).
3. For scripted board manipulation (headless kicad-cli / s-expression editing),
   enforce classes in the script's own geometry model: block cells at
   clearance+trace/2, exempt same-net, honor via pads — the DRC-then-fix loop is the
   acceptance criterion, not the script's self-belief.
