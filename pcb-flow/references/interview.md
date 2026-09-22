# Requirements interview — full script

Run this interview at Phase 0 (and revisit at every revision). Ask in one pass, write
answers verbatim in the journal, then play them back to the user for confirmation.
Structure matters more than speed: every answer you fail to capture here becomes a
rework cycle after layout.

## Section 1 — Function

1. In one sentence: what does this board do in the larger product?
2. What does it talk to, and over what? (USB, UART, CAN, Ethernet, I2C, SPI, wireless,
   discrete GPIO.) For each: how many pins/lanes, host or device, expected data rate.
3. What is the brain? (Specific MCU/SoC family or "recommend one" — if the latter, note
   the constraints: ecosystem familiarity, wireless needs, temperature, safety rating.)
4. What does it control or sense? Actuators, sensors, current levels, analog precision?
5. Are there human interfaces? (buttons, LEDs, displays, connectors the user touches —
   these have mechanical + ESD implications.)

## Section 2 — Power

6. Where does power come in? (mains, 12/24 V brick, USB, battery — chemistry + BMS?)
7. Target rails: list each voltage, its source (converter part or family if known), and
   the loads with realistic currents — peak AND typical. If unknown, estimate 2× the sum
   of the load datasheets and mark it.
8. Efficiency/thermal targets? Any convection-free enclosures? (Sets copper area needs.)
9. Reverse-polarity / surge / ESD exposure at every external port — what does the
   environment throw at it (vehicle transients, hot-plug, outdoor, static-prone humans)?
10. Does anything need power OR-ing or source selection (e.g., USB vs barrel)? How should
    the board behave when both are present?

## Section 3 — Mechanics

11. Enclosure or free-air? Board size limit? Any keep-out the enclosure imposes?
12. Mounting: screw size and pattern? Plastic standoffs vs metal (metal mounts near live
    copper need edge clearance)?
13. Connectors: which ones are position-fixed by the enclosure or cable dressing? What
    cable bend radii must clear the board edge?
14. Height budget: anything overhanging neighbors (shrouds, shields, electrolytics,
    modules with antennas)?
15. Weight/mass constraints? (Anything heavy needs mechanical anchoring — see
    `../../pcb-layout/SKILL.md`.)

## Section 4 — Environment & reliability

16. Operating temperature range (and storage)?
17. Vibration/shock (vehicle, handheld drop, industrial plant)? → connector locking,
    heavy-part anchoring, strain relief.
18. Moisture/dust/conformal coating? → clearance growth, mask/sliver rules, connector
    selection.
19. Regulatory targets: EMC (FCC/CE), safety (IEC 62368-1), automotive segments, medical?
    Note early: this changes creepage/clearance budgets and requires human review of the
    safety paths.

## Section 5 — Cost & production

20. Volume: how many boards, now and at scale? (1–10 prototypes → budget quick-turn fab;
    production → DFM review against a named fab; 10k+ → panelization economics.)
21. Unit cost target for the bare board? For assembly?
22. Who assembles: hand-iron, contract assembler with pick-and-place, fab's own assembly
    service? (Sets the BOM/CPL format and the passive package floor — 0402 is fine for
    machines, 0603/0805 for hands.)
23. Lead-time pain tolerance: are exotic parts acceptable if they cost 8 weeks?

## Section 6 — Tools & standards

24. EDA tool (KiCad / Altium / EasyEDA / other)? Skill instructions have per-tool
    variants; physics does not change.
25. IPC class target (2 default, 3 for high-reliability)? Affects annular rings,
    cleanliness, inspection criteria.
26. Existing preferred parts/libraries the user wants reused?

## Close-out

Playback: "Here's what I captured — correct me where I'm wrong." Then write the
requirements block (Function / Power / Mechanics / Environment / Production / Tools
sections) into the journal, mark every assumption that was guessed rather than answered,
and set the fab/assembly/EDA answers into Phase 5 planning. Any unanswered safety-relevant
question (mains, medical, automotive) → flag for mandatory human review at the
appropriate gate, per `../../pcb-pitfalls/SKILL.md`.
