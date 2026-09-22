# High-speed routing addendum

TOC: §1 What "high-speed" means here · §2 Controlled-impedance workflow · §3
Reference-plane changes · §4 Layer-change discipline · §5 AC-coupling & topology

## §1 What "high-speed" means here

Not clock rate — EDGE rate. If the rise time is faster than ~6× the one-way
propagation of the trace (the classic "long trace" criterion: trace > l/6 of the
edge's spatial length), the trace is a transmission line and the return-path physics
of SKILL.md §2 stops being optional. Practical triggers: USB2-HS (480 Mbps) and
above, Ethernet, DDR, LVDS, anything with a SerDes, SPI clocks above ~30–50 MHz with
long runs, and ANY design that must pass radiated-emissions testing on the first try.

## §2 Controlled-impedance workflow

1. Enumerate impedance nets per protocol (USB 90 Ω diff, Ethernet 100 Ω diff, LVDS
   100 Ω, PCIe 85 Ω — typical; the spec + fab worksheet govern).
2. Fix stackup and routing layers for those nets (`../../pcb-board-format/
   references/stackups.md`).
3. Request the fab's impedance worksheet values for THAT stackup; enter returned
   width/gap as class rules; route.
4. Verify: gerber spot-check that the manufactured geometry matches the class
   (fab pre-review will catch width drift); ask for the coupon report on production
   runs.
5. Document the sheet version + date in fab notes — a re-order months later with a
   changed fab process needs re-confirmation.

## §3 Reference-plane changes

- A signal may change layers freely BETWEEN two planes that are the same net (GND→
  GND) IF a return via accompanies the transition within ~1–3 mm (the return current
  swaps planes through the via pair; without it, the return detours =
  radiating loop).
- Changing reference from GND-plane to PWR-plane requires a stitching CAPACITOR at
  the transition (the return crosses as displacement current) — place the cap's
  pads beside the signal via, route both short.
- Never change reference across a split/slot.

## §4 Layer-change discipline (diff pairs & buses)

- Diff pairs: both members change layers together, adjacent return vias; pair skew
  is consumed by asymmetry at transitions — account for it in the budget.
- Multi-bit buses: keep the bus on one reference pair end-to-end where possible;
  each member's transitions clustered so the group's return path stays coherent.

## §5 AC-coupling & topology

- AC-coupling caps (SerDes links): series caps placed together near the SOURCE
  (transmitter side) per common practice (exceptions per protocol spec — check the
  receiver's spec for termination placement), same net class on both sides (two
  nets: pre/post-cap — assign class to both).
- Series termination resistors: at the driver end, within ~10 mm of the pin — the
  resistor is part of the source impedance; mid-run resistors split the line and
  double reflections.
- Point-to-point beats any topology; if a T-branch is forced (multi-drop), treat
  each leg's impedance honestly (series stubs are the SerDes way; parallel stubs
  are DDR's problem — see protocol guides).
- Keep-outs: high-speed nets away from board edges (edge radiation), away from the
  crystal/RF zones, away from the antenna keepout entirely.
