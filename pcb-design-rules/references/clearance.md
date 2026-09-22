# Clearance & creepage — method detail

TOC: §1 Definitions & why two numbers · §2 The derivation workflow · §3 IPC-2221-style
tables · §4 Environment modifiers · §5 Working example

## §1 Definitions & why two numbers

- **Clearance**: shortest distance THROUGH AIR between conductors.
- **Creepage**: shortest distance ALONG A SURFACE (FR-4, mask, dust film).

Air breaks down (~3 kV/mm in ideal dry air, less with altitude/humidity/contamination —
never design to the ideal); surfaces track: contamination + moisture + field →
carbonized track → arc at well below the pure-air figure. Hence creepage ≥ clearance,
and creepage is the governing number for most polluted-environment designs.

## §2 The derivation workflow

1. Determine **working voltage** (RMS or DC; for transients, peak) between the two
   conductors — not the nominal supply: a 230 VAC mains has 325 V peak, plus surge
   categories (IEC 62368-1 / IEC 60664-overvoltage categories assign a transient
   overvoltage per category — a 230 V installation on category II gets a 2.5 kV
   impulse rating the clearance must survive).
2. Pick the insulation type (functional / basic / reinforced — reinforced ≈ 2× basic
   creepage; cite IEC 62368-1 for equipment-safety classes).
3. Apply modifiers (§4): altitude, pollution degree, coating.
4. Read the table (§3) and ADD prototype margin (2× where space allows).
5. Where the number is unachievable: cut a SLOT — creepage along the surface must go
   around it; a 1 mm-wide slot can buy multiple mm of creepage in 1 mm of board.
   (Slots: mind fab minimum router width ~1 mm and copper-edge clearance per
   `../../pcb-board-format/SKILL.md`.)
6. Record derivation in the journal (voltage used, category, table, margin taken) —
   a reviewer must be able to reproduce your number.

## §3 IPC-2221-style generic tables (rounded conservative; consult the standard's
actual rows for a safety-relevant design)

External, uncoated, sea level, pollution degree 2 — B1-ish conditions:

| Working V | Clearance (mm) | Creepage (mm) |
|---|---|---|
| ≤30 | 0.1 (use 0.2+) | 0.2 |
| 31–50 | 0.6 | 0.6 |
| 51–100 | 0.9 (use 1.0) | 1.0 |
| 101–170 | 2.0 | 2.0 |
| 171–250 | 3.0 | 3.0 |
| 251–300 | 4.0 | 4.0 |
| 301–500 | 6.4 | 6.4+ |

Internal layers / coated (mask or conformal): roughly 1/2 to 1/4 of the external
uncoated values; many quick-turn fabs enforce a flat 0.2 mm minimum gap regardless.

⚠️ Provenance note: these are IPC-2221 Table 6-1-derived generic guidance values,
rounded conservatively, for the stated conditions. Product-safety designs (mains,
medical, automotive) must use the actual IEC 62368-1 / IEC 60664 tables with
overvoltage category + pollution degree + altitude, and get human review.

## §4 Environment modifiers

| Modifier | Effect |
|---|---|
| Altitude > 2000 m | derate clearance (air density ↓) — per IEC 60664 altitude correction |
| Conformal coating | treated like internal (coated) surfaces — big creepage reduction, IF the coating is qualified and complete |
| Pollution degree 1 (sealed/clean) | creepage approaches clearance values |
| Pollution degree 3 (industrial/dusty) | creepage multiplies (~1.5–2×) |
| Reduced pressure / potting | re-derive entirely from the standard's tables |
| Recurring transients (relay coils, motor spikes) | size clearance for the transient peak, not the DC level |

## §5 Working example (labeled)

**Example — 24 V industrial input with load-dump exposure:**
Input: 24 V nominal supply, transient 250 V-class per environment spec, uncoated
external, sea level.
Output: functional clearance sized for the 250 V transient → ~3 mm class (per §3
row); working-voltage creepage for 24 V DC is trivial (0.2 mm class) but the
transient drives clearance; final rule = 3 mm for the input-net-to-everything-else
class, achieved with a slot at the connector zone where board area is tight;
derivation recorded in the journal; human review NOT required (SELV-ish, no safety
cert path) but flagged to the reviewer anyway.

*(Labeled worked example — the numbers came from the method above, not from any one
board.)*
