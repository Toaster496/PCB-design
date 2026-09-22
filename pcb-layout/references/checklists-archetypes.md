# Placement checklists per board archetype

TOC: §1 MCU/digital board · §2 SMPS/power board · §3 RF/wireless board · §4 Sensor
front-end · §5 Motor-driver board

Use the archetype closest to your board; mixed boards use the union of applicable
sections (dirty sections from the power/motor lists, clean sections from the
sensor/RF lists — and the separation rule dominates everything).

## §1 MCU / digital board

- [ ] MCU at zone center; decap ring complete (every VDD pin has a 100 nF-class cap
      ≤2 mm away, via down).
- [ ] Crystal + load caps tight to pins, guard region clear beneath on adjacent layer.
- [ ] Reset RC/boot strap parts near their pins (strap networks must not be
      high-inductance).
- [ ] Programming/debug connector (SWD/JTAG/UART) near board edge with TP access.
- [ ] USB/communication connectors at edge with ESD clamp + common-mode choke at the
      entry.
- [ ] Rail entry: LDO/buck at its own corner; bulk cap at rail entry.
- [ ] Component orientation predominantly uniform.
- [ ] BGA/QFN escape space unobstructed (anchor placement leaves routing channels).

## §2 SMPS / power board

- [ ] Hot loops minimized BY PLACEMENT: input cap adjacent to switch IC pins; diode
      adjacent; loop perimeter measurable in single-digit mm for a 1–5 A converter.
- [ ] Inductor away from everything clean; no sensitive trace parallel to it.
- [ ] Feedback divider close to the FB pin, sense trace routed far from the switch
      node (routing concern flagged now, placed for later).
- [ ] Output caps + bulk at the load side, completing the output loop small.
- [ ] Current path: input connector → fuse/protection → converter → output connector,
      following one flow direction; return path poured under the WHOLE forward path.
- [ ] Sense (Kelvin) points identified (Rsense differential pads or remote-sense at
      the load).
- [ ] Thermal pad via array area reserved on the opposite layer (no routing there
      later).
- [ ] Creepage/clearance zones for the input voltage class marked
      (`../../pcb-design-rules/SKILL.md`).

## §3 RF / wireless board

- [ ] Antenna keepout: all copper layers, extending beyond the antenna section of the
      module/antenna; keepout includes the board edge region under an edge antenna.
- [ ] Feedline short, straight, at 50 Ω class impedance; no via in it if avoidable
      (each via adds inductive discontinuity).
- [ ] Module placed at board edge/corner, antenna pointing off-board.
- [ ] Shield-can footprint zones for the RF section (castellations + ground stitch
      row) if the design will need shielding.
- [ ] Crystal/TCXO for the radio placed per its keepout guidance (some radios specify
      placement regions — read the radio's layout appnote, it is binding).
- [ ] No digital bus traces under/through the RF section on any layer.
- [ ] Ground stitch via fence along the RF section boundary planned.

## §4 Sensor front-end / precision analog

- [ ] Clean zone: sense nodes, gain network, reference — as far from buck/MCU/driver
      zones as the outline allows.
- [ ] Guard ring / moat plan around the clean zone (GND pour boundary with a single
      controlled crossing for the signal).
- [ ] Kelvin sense connections at the measurement point (shunt or remote node), not
      "somewhere on the net".
- [ ] Reference IC decap local; reference trace treated as sensitive (shielded,
      short).
- [ ] Differential pairs for bridge/transducer signals placed symmetric — the LAYOUT
      symmetry is part of the circuit's CMRR.
- [ ] Thermal: sense element away from regulators; away from any on-board heater.
- [ ] No switching-node copper on any layer under the analog zone (check the layer
      stack for what lies beneath!).

## §5 Motor-driver board (high-current, half-bridge/H-bridge)

- [ ] Driver + FETs + shunt form one tight cluster per channel; gate-drive loops
      (driver→FET gate→return) as physically small as possible.
- [ ] Per-channel symmetry: every repeated channel's cluster has the SAME placement
      pattern (assembly + debugging sanity; asymmetric channels hide their
      differences).
- [ ] Current shunt at the load return with Kelvin pads; amplifier local.
- [ ] Bulk electrolytics near the supply entry, before the drivers, with the ripple
      current rating checked (BOM task).
- [ ] Bulk cap + FET cluster forms the smallest possible switching loop (input loop).
- [ ] Motor OUT nets leave on thick traces/pours toward the output connector with
      NO detour through the logic zone.
- [ ] Logic-side inputs (PWM/EN) with their pull resistors on the CLEAN side of the
      driver cluster; each input has its defined default state (pullup/pulldown —
      floating gate inputs at power-up are a fires-not-embarrassments failure class
      on bridge stages).
- [ ] Thermal pad pour + via array per driver; drivers spread from each other.
- [ ] Desat/overcurrent sense networks local to their driver (long sense traces
      pick up the switching node they're protecting against).

## Cross-archetype reminder

For every archetype, the common exit list from `../../SKILL.md` §7 still applies —
archetype lists extend it, never replace it.
