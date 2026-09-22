# Trace width & current capacity — method detail

TOC: §1 The physics · §2 IPC-2152 method · §3 Ready tables · §4 Pulses & transients ·
§5 Pours vs traces · §6 Working examples

## §1 The physics

Current heats the copper (I²R per unit length); heat leaves by conduction into the
board (dielectric + planes) and convection/radiation from surfaces. The steady state
sets ΔT; you pick the ΔT you can tolerate, then find the cross-section that holds it.
External traces shed heat both ways; internal traces only conduct into the laminate —
that's why internal widths ≈ 2× external for the same current. Copper weight sets
cross-section per width. (Charts, not formulas, are the standard's answer because
heat-spreading into planes dominates real geometry.)

## §2 IPC-2152 method (the modern standard; cite it)

1. Choose ΔT (10 °C default; 5 °C for sealed/dense products; 20 °C acceptable for
   open-air hobby-class where nobody touches the trace).
2. Identify layer type (external / internal) and copper weight (1 oz = 35 µm).
3. Use the IPC-2152 charts (or a reputable IPC-2152-based calculator — several exist
   online; verify the calculator cites the standard) to read width for (I, ΔT, copper).
4. Round UP to a fabricable width (0.05 mm steps), and prefer a wider margin class
   when routing room exists — temperature rise is not a cliff, but electrolytic caps
   and connectors sitting above the trace see every degree.
5. For power rails: consider a plane/pour instead (§5).

IPC-2221 ch.6 curves (the legacy) remain conservative and usable; IPC-2152 is
tighter-to-reality. Never mix: pick one basis per project and note it in the rules.

## §3 Ready tables — conservative defaults (1 oz, ΔT 10 °C, free convection,
IPC-2152-consistent rounded; verify for your exact case)

External (air-facing) traces:

| Current (A) | Width (mm) | Width (mil) |
|---|---|---|
| 0.5 | 0.20 | 8 |
| 1.0 | 0.40 | 16 |
| 1.5 | 0.65 | 26 |
| 2.0 | 0.80 | 32 |
| 2.5 | 1.1 | 43 |
| 3.0 | 1.3 | 52 |
| 4.0 | 1.9 | 75 |
| 5.0 | 2.5 | 98 |
| 7.0 | 4.0 | 157 |
| 10.0 | 6.0 | 236 |

Internal layers ≈ 2× the external width. 2 oz copper ≈ 0.6–0.7× the widths above.
High-ambient designs: derate the current ~1.25× for every 25 °C above 25 °C ambient
(rough thermal budgeting, verify).

## §4 Pulses & transients

Short pulses average out: thermal mass means a 10 ms, 10×-rated pulse may barely warm
the trace. Estimate via I²t (fuse-wire-style adiabatic reasoning): acceptable
I²t ∝ cross-section² × constant — conservative check for motor-start currents, LED
strobe rails, cap inrush. For recurring pulses, compute the RMS current and use the
steady-state table on the RMS. Copper is forgiving; the solder joints and via
barrels are the fatigue-prone elements (thermal cycling cracks them, not the copper).

## §5 Pours vs traces

At ≥3–5 A, a pour region (or plane) beats any trace: current distributes across the
width (lower effective resistance AND inductance), heat spreads, and you pay nothing
in fab. Rules for pours as conductors: enter/exit through full-width necks (no
trumpet funnels), stitch layer transitions with via PAIRS/arrays (each via ~1 A-class,
`vias.md` §3), and watch neck-down points where the pour feeds a pin — the neck is the
real current path.

## §6 Working examples (labeled)

**Example 1 — 1.8 A motor supply rail, external, 2-layer, 1 oz:**
Table: 1.5 A → 0.65 mm; 2 A → 0.8 mm. Choose 0.8 mm (next row up — motor stall
currents spike; RMS sizing + margin). If the rail were internal: 1.6 mm, or route as
a pour region on the top layer instead.

**Example 2 — 12 V, 100 mA sensor rail, length 60 mm:**
0.2 mm default width, no derating — voltage-drop check: 0.2 mm × 35 µm ≈ 0.07 mm² ≈
0.25 Ω/m → 60 mm ≈ 15 mΩ → 1.5 mV drop at 100 mA. Irrelevant. (Do this drop sanity
check for long analog sense leads — THERE, mV matter.)
