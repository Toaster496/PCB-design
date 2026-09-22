# Vias — sizing, current, annular rings, special types

TOC: §1 Sizing defaults · §2 Annular rings & drill registration · §3 Via current
capacity · §4 Special via types (tented/in-pad/plugged/thermal/stitching) · §5 Aspect
ratio limits

## §1 Sizing defaults

| Via | Drill / finished | Annular ring | Use |
|---|---|---|---|
| Standard signal | 0.3 / 0.6 mm pad | 0.15 mm | default everywhere, quick-turn safe |
| Dense fanout | 0.25 / 0.5 mm | 0.125 mm | BGA dogbones, tight escapes (verify fab) |
| Power transition | 0.4–0.5 / 0.8–0.9 mm | 0.15+ | use ARRAYS for amps |
| Stitching (GND) | 0.3 / 0.6 | 0.15 | every 5–15 mm along boundaries |
| Thermal under EP | 0.3 / 0.6 | solid connect | 3×3–5×5 arrays |

## §2 Annular rings & drill registration

Drill-to-layer registration is not perfect (typical quick-turn ~0.075–0.1 mm offset
possible; verify per fab). The annular ring must survive the worst-case offset on EVERY
layer: ring ≥ registration tolerance + etch tolerance + margin. That's why 0.15 mm ring
is the safe quick-turn default and 0.10 mm is the advertised floor. Symptoms of
too-small rings: intermittent opens on layer transitions, drill breakout visible in fab
X-ray/inspection. IPC Class 3 (high-reliability) demands larger rings + 100% annular
inspection — cite IPC-A-600 class criteria.

## §3 Via current capacity

The plated barrel (≈25 µm copper wall on a 0.3 mm drill) is the bottleneck, not the
capture pads. Conservative guidance (verify with IPC-2152 via charts where it matters):

| Drill (mm) | Steady current @ ΔT10 (A, conservative) |
|---|---|
| 0.25 | ~0.7 |
| 0.3 | ~1.0 |
| 0.4 | ~1.4 |
| 0.5 | ~1.8 |
| 0.8 | ~3 |

Multiple vias share current roughly evenly IF placed adjacent (within a few mm);
spreading them lowers nothing electrically but also rarely hurts — adjacency is what
cuts loop inductance. For a 5 A layer transition: 4–6 × 0.5 mm vias, clustered at the
neck. High-current boards also use filled/coin vias — specialist territory, engage fab.

## §4 Special via types

| Type | What | Rules |
|---|---|---|
| Tented | soldermask closed over the via | default ON near assembly paste; free; prevents solder wicking into the barrel during reflow |
| Via-in-pad | via in a SMT pad (BGA/QFN) | MUST be plugged+capped (epoxy fill, plated over) or paste starves; budget-tier alternative = dogbone fanout (`../../pcb-routing/SKILL.md`) |
| Plugged | barrel filled with epoxy (no cap) | for void-suppression under pads, vacuum-clean assemblies; fab option |
| Thermal via | under EPs/pads to opposite pour | SOLID pad connection (no relief spokes); 3×3–5×5 arrays of 0.3 mm drills; under-plane area kept pour-solid |
| Stitching | plane-to-plane GND ties | along edge transitions, connector entries, plane splits being bridged; every 5–15 mm; λ/20 spacing concept for RF zones (at RF frequencies, spacing ≪ shortest wavelength of concern) |
| Skip/back-drill | controlled-depth removal of stub | multi-Gb SerDes territory; fab option, ask engineering |

## §5 Aspect ratio

AR = board thickness / drill diameter. ≈10:1 is the common process ceiling (verify per
fab), 8:1 the safe zone; 12:1+ costs money (laser drills / special plating). 1.6 mm
board → 0.2 mm minimum drill at 8:1 → practical floor 0.3 mm. Thick multi-layer
(2.4 mm, 8 layers): floor ~0.3 mm AR 8 — plan fanout density accordingly.
