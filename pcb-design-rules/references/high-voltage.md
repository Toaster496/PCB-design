# High-voltage addendum — reinforced insulation, slots, potting, corona

⚠️ **HV/mains designs require a qualified human review before fabrication.** An agent
can prepare the design and the documentation; it cannot sign off. This reference is
preparation guidance, not a certification path.

TOC: §1 Insulation classes · §2 Reinforced geometry · §3 Slots & grooves · §4 Potting
& conformal coating · §5 Corona & partial discharge · §6 Design checklist

## §1 Insulation classes (cite IEC 62368-1 for audio/IT/AV equipment; IEC 60664-1 for
low-voltage installations' insulation coordination)

| Class | Purpose |
|---|---|
| Functional | failure won't shock anyone, just stop working |
| Basic | one fault → protective earth takes over |
| Supplementary | second, independent barrier after basic |
| Reinforced | basic+supplementary in one barrier (≈ 2× basic creepage) |

## §2 Reinforced geometry

- Creepage ≈ 2× basic per the standard's tables (not "2× whatever I guessed").
- Clearance sized to the OVERVOLTAGE CATEGORY impulse level (IEC 60664 tables: a
  230 V cat-II circuit must survive a 2.5 kV impulse; cat-III 4 kV) — the transient,
  not the working voltage, usually dominates clearance.
- Series resistors/ferrites before sensitive pins buy nothing here; geometry and
  clamps do.

## §3 Slots & grooves

- A slot forces creepage to travel around it: 1 mm-wide slot × 3 mm-deep into a
  barrier can add ~6 mm creepage in ~2 mm of board real estate.
- Slots are routed: minimum router width ~1 mm (verify fab), inner corners limited by
  bit radius, copper keeps clear ≥0.5 mm from routed walls (conservative generic;
  more at HV per derivation).
- Grooves (V-cut-ish surface tracks) also count as creepage extenders per the
  standards' geometry rules — rarely worth it vs a slot.

## §4 Potting & conformal coating

- Qualified conformal coating (acrylic/urethane/silicone, typed thickness) moves
  surfaces toward "coated/pollution-degree-1" creepage values — but ONLY if coverage
  is complete and qualified (a pinhole defeats it); the coating must be listed for
  the pollution degree and voltage.
- Full potting (epoxy) mechanically locks the design AND fixes clearances — but
  rework dies, thermal design changes (insulation!), CTE stresses parts; pot a
  DESIGN, not an escape from one.
- Decide potting at Phase 0/1 (`../../pcb-flow/SKILL.md`) — it changes BOM (connector
  styles, part heights), thermal budget, and test access.

## §5 Corona & partial discharge

Above ~400 V field-strength-prone geometries (sharp pad corners, pin tips), partial
discharge eats insulation silently over months. Mitigations: round pad corners (or
simply larger pads), avoid pointy copper shapes, keep gradient distributed (series
creepage segments), use materials rated for PD. Detectable only with PD test gear —
another reason HV needs humans with instruments.

## §6 HV design checklist (preparation for human review)

- [ ] Working voltage + overvoltage category assigned and documented.
- [ ] Clearance/creepage derived from the actual standard tables; margin stated.
- [ ] Slots where creepage was tight; slot geometry within fab capability.
- [ ] Coating/potting decision made, material + thickness specified in fab notes.
- [ ] Sharp-copper audit done (pad shapes, copper corners near HV).
- [ ] Failure modes listed (what arcs first, what it arcs TO, who is touching).
- [ ] Human reviewer identified, given the derivation record, and scheduled BEFORE
      the fab order date.
