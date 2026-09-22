# Fab capability reference — budget quick-turn vs premium

⚠️ **These tables are illustrative snapshots of typical capability TIERS, not live
quotes. Fab capabilities change; always verify current values on the fab's capability
page before committing design rules.** (Cite the page + date in your project journal.)

## Tier A: budget quick-turn (JLCPCB/PCBWay/ALLPCB-class)

| Parameter | Typical value (VERIFY) | Design-to value (safe) |
|---|---|---|
| Min trace/space | 0.09–0.127 mm (3.5–5 mil) | 0.15 mm / 6 mil |
| Min drill (mechanical) | 0.2–0.3 mm | 0.3 mm |
| Min annular ring | 0.1–0.15 mm | 0.15 mm |
| Aspect ratio | 8–10:1 | 8:1 |
| Copper | 1 oz default, 2 oz cheap | 1 oz unless current demands |
| Min BGA pitch | 0.4 mm | 0.5 mm (with careful fanout 0.4) |
| Silkscreen min | 0.15 mm text | ≥1 mm text height |
| Surface finish | HASL included; ENIG +cost | HASL for proto, ENIG for fine pitch |
| Impedance control | offered +fee, coupon report extra | request worksheet + report |
| Panelization | V-score included; rails expected | let fab panelize if they assemble |
| 4-layer standard stackup | 1.6 mm, 0.2/0.2 prepreg-ish cores | use their standard stackup |
| Quantity economics | 5–10 pcs promo pricing | — |

Philosophy: **design to the cheapest fab you'd actually use** — at tier A, that means
0.15/0.15 mm trace/space, 0.3 mm drills, 0.15 mm annular ring as your NORMAL values
even though the fab advertises lower. The margin is free insurance for etch tolerance,
and the capability surcharge tier is skipped entirely.

## Tier B: premium/proto houses (Eurocircuits/Advanced Circuits/OSH Park-class)

| Parameter | Typical value (VERIFY) |
|---|---|
| Min trace/space | 0.1 mm / 0.1 mm (4 mil class) standard |
| Min drill | 0.15–0.25 mm |
| Annular ring | 0.125–0.15 mm min |
| Aspect ratio | 10:1+ |
| Copper | up to 3–4 oz |
| Impedance | worksheets + coupons, per-order engineering support |
| DFM feedback | human-reviewed quotes with constraint flags |
| Materials | wide dielectric menu incl. high-Tg, low-Dk RF laminates |
| Cost/unit | 3–10× tier A at qty 5–50 |

Use tier B when: impedance precision matters, the stackup is exotic, the volume is low
and the risk is high (first articles), RF laminates needed, or you want human DFM eyes.

## Assembly capability (same tiers, PCBA side)

| Parameter | Tier A PCBA (VERIFY) | Design-to value |
|---|---|---|
| Min passive | 0402 (0201 at some) | 0603 if any hand rework expected |
| Min pitch | 0.4 mm BGA/QFN fine | 0.5 mm |
| Sides | both, +cost per side | single-side if possible |
| Parts sourcing | their-parts catalog + consigned | prefer their catalog parts |
| Paste inspection | AOI on placement; optional x-ray for BGA | request x-ray for via-in-pad/BGA |
| Fiducials | required (3 global + local fine-pitch) | provide them regardless |

## Verifying a fab quickly (procedure)

1. Fetch the capability page; note the DATE (stale pages are common).
2. Compare against your tightest features: min trace/space, min drill, annular ring,
   BGA pitch, copper weight, stackup availability.
3. If ANY feature is within 20% of a limit → either relax the feature or move up a
   tier / pay the surcharge deliberately.
4. Record in the journal: fab, date checked, page URL, the values you relied on.
5. Before ordering a production run: upload the gerbers to the fab's online analyzer
   and read every warning it returns (they flag silkscreen-over-pad, small drills,
   slot widths you missed).
