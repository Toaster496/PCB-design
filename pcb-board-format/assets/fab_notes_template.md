# FAB NOTES — fill per order, paste into the fab's notes field / readme of the zip

Board: <project name / rev>
Date: <YYYY-MM-DD>
Designed by: <name/contact>

## SPECIFICATION

- Layer count: <N>
- Board thickness: <1.6 mm>
- Material: <FR-4, Tg >= 130>
- Copper weight: outer <1 oz> / inner <1 oz>
- Surface finish: <HASL lead-free / ENIG / OSP>
- Solder mask: <matte green, both sides>
- Silkscreen: <white, both sides>
- Quantity: <N>
- Min trace/space used: <0.15 / 0.15 mm>
- Min drill used: <0.3 mm>
- Controlled impedance: <NO | YES — see below>

## IF IMPEDANCE-CONTROLLED

- Impedance pairs: <e.g. USB 90 Ω ±10% diff on L1; 100 Ω diff on L3>
- Fab worksheet dated <date> consulted; widths entered as returned:
  <w=0.19 mm s=0.15 mm for L1 90 Ω etc.>
- Coupon report requested: <YES/NO>

## SPECIAL PROCESS

- Castellated edges: <NO/YES, count>
- Gold fingers / edge connector beveling: <NO/YES>
- Edge plating: <NO/YES>
- Counterbore/depth routing: <NO/YES>
- V-scoring (if I supplied a panel): <NO/YES>
- Via plugging/capping: <NO/YES — type>
- Heavy copper > 2 oz: <NO/YES>

## FILES IN PACKAGE

- Gerbers: <n> files, RS-274X, extension map: top .gtl, bottom .gbl, inner .g2/.g3,
  mask .gts/.gbs, silk .gto/.gbo, paste .gtp/.gbp, outline .gm1
- Drill: Excellon <name>.drl, <units: mm>, <embedded/headed headers>
- Assembly (if ordering PCBA): pos.csv (centroid), BOM csv
- Readme: this file

## NOTES FOR THE FAB

- <e.g. "panelization not required; single board shipping">
- <e.g. "0.9 mm slots in outline, 4 places">
- <e.g. "please confirm ENIG on module antenna pads">
- <e.g. "accept silkscreen reference designators partially under connectors as marked">

## CONTACT PREFERENCES

- Email <address> with engineering questions before proceeding if anything is unclear.
- Timezone: <TZ>
