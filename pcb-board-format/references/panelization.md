# Panelization — breakaways, rails, fiducials, economics

TOC: §1 When to panelize · §2 Breakaway methods · §3 Rails & tooling · §4 Fiducials ·
§5 Panel sizing · §6 Common panelization bugs

## §1 When to panelize

| Situation | Panelize? |
|---|---|
| Prototype, hand assembly, board ≥ ~50 × 50 mm | No |
| Machine (PCBA) assembly of small boards | Yes — assembler needs panel handling |
| Volume production | Yes — economics + throughput |
| Multiple identical tiny boards (e.g. 10 × 20 mm sensor pucks) | Yes |
| Mixed designs sharing a run (different boards, same fab) | Sometimes (kitting); ask the fab/assembly house first — some refuse mixed panels |

## §2 Breakaway methods

| Method | How | Best for | Watch out |
|---|---|---|---|
| **V-score** | angled groove cut ~1/3 depth from each side, board snapped apart | straight edges, rectangles | only straight lines across the WHOLE panel; edge burrs; part keepout ~0.5 mm from score line |
| **Mouse bites** | 3–5 non-plated drill holes ~0.8–1.0 mm straddling the join, snapped or cut | irregular outlines, tabs | stress cracks propagate toward copper; component keepout ≥2 mm; stubs remain on edge |
| **Stamp holes** | chain of small holes (0.5 mm-ish) perforating a tab | light boards, minimal edge scars | weaker; same keepout logic |
| **Tab + router** | routed outline with retained tabs at chosen spots | cleanest edges | tab locations must avoid copper; requires router access |

Rules that apply to ALL methods:
- Copper/component keepouts near the break line (0.5 mm V-score, ~2 mm mouse bites —
  conservative generic defaults, verify per fab/assembler): depaneling stress cracks
  travel and components shear.
- No vias/pads within the crack-propagation zone.
- Depaneled edges are rough: keep sealed connectors, gold fingers, castellations well
  away from breakaways.

## §3 Rails & tooling

- **Rails** (panel border, ~5 mm typical, VERIFY per assembler): the assembler's
  conveyor clamps them. If your assembler requires rails — and most do — the board is
  unreachable for panelization questions like "can I skip the rails?" (No.)
- **Tooling holes**: 2–4 × 3 mm-ish non-plated holes in rails at the assembler's
  specified positions (often 5 mm from panel corner — get THEIR spec, it varies).
- **Panel fiducials**: 3 on the rails, asymmetric (not a rectangle — prevents
  180°-flipped panel loading), ≥5 mm from edges.
- **Fiducial mark spec** (generic): 1 mm bare-copper circle, 2 mm mask clearance
  (verify per assembler).
- Rails are scrap: rail width × perimeter × cost/m² is the real price of a panel.

## §4 Fiducials

- **Global fiducials**: 3, spread asymmetrically, referenced to the whole panel.
- **Local fiducials**: 2 per fine-pitch component (≤0.5 mm pitch) near its diagonal —
  correct board stretch at that component.
- Fiducials need a clear keepout: nothing silkscreened over them, uniform mask
  clearance around them.
- If the assembler's machine vision can't find a fiducial, it either stops the line or
  guesses — both cost more than the 6 pads you just designed.

## §5 Panel sizing

- Target the fab's standard panel (often ~210 × 297 mm / 8×11" region — VERIFY).
- Step-and-repeat: X×Y array of the single board + breakaways + rails; compute
  utilization (board area / panel area) — below ~60% on a paid run, re-think.
- Rotating one axis can dramatically improve utilization on long boards.
- Mixed panels (several different boards) are great for prototypes but some assemblly
  houses won't run them; also every board on the panel shares the panel's defect
  risk (a scrapped panel scraps all).

## §6 Common panelization bugs (see also `../../pcb-pitfalls/SKILL.md`)

1. Rails forgotten → the PCBA quote comes back "cannot conveyor 30 mm board".
2. Mouse bites through a copper pour → crack propagates and shorts two pours.
3. Fiducials behind silk text → machine vision rejects, line stops.
4. V-score across an irregular outline (V-score is straight-line-ONLY, full panel
   width) → fab rejects or improvises.
5. Local fiducials skipped on a 0.4 mm BGA → placement drift scrapes the reel.
6. Tooling hole positions invented (not from the assembler's spec sheet) → fixture
   misfit.
