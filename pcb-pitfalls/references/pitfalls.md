# Pitfalls catalog — full, by phase

Five fields per entry: **Pitfall | Symptom | Why it happens | Fix / prevention**.
Provenance marks: [std] = grounded in IPC/IEC-standard reasoning; [proc] = fab/
assembly process mechanism; [ft] = field-tested pattern from completed boards
(anonymized, mechanism-generalized); [gen] = conservative generic default.

TOC: §1 Board setup · §2 Placement · §3 Routing · §4 Rules/DFM · §5 BOM/sourcing ·
§6 Solder/assembly · §7 EMC/ESD · §8 Scripted/headless EDA

## §1 Board setup

| Pitfall | Symptom | Why | Fix/prevention |
|---|---|---|---|
| Wrong layer count for the job | unroutable board or 3× cost | "2 layers are cheaper" until re-spins cost more than the layer delta | decision tree (`../../pcb-board-format/SKILL.md` §2) |
| Outline on wrong layer | fab mills nothing / wrong shape | outline drawn on silk/mech layer by habit | Edge_Cuts only; exactly one closed shape [ft] |
| Slots without copper clearance | slots mill through copper → shorts/opens | router bit follows the line; copper was closer than the wall | ≥0.5 mm copper keepout from routed edges (more per creepage) [gen] |
| Mounting hole keepout violated | screw head shorts a pad | keepout drawn but later placement creeped into it | keepout ZONES not just holes; check at placement gate |
| Fiducials missing/obstructed | PCBA line stops or mis-places | fiducials "took space" or got silked over | 3 global + local on ≤0.5 mm pitch; silk clear [proc] |
| Panelization the assembler can't run | quote rejected: "cannot conveyor" | rails/tooling holes invented, not from assembler spec | get the assembler's panel spec FIRST [ft] |
| Board thickness vs connector mismatch | connector won't mate | 1.6 mm assumed; SMD edge connectors vary | check mating spec per connector at setup |

## §2 Placement

| Pitfall | Symptom | Why | Fix/prevention |
|---|---|---|---|
| Decoupling too far / wrong via | rail noise, flaky MCU | cap loop inductance ~1 nH/mm; far cap is off the network at HF | ≤2 mm from pin + via straight down; bulk lenient [std-2152] |
| Crystal far from MCU / traces under it | boot jitter, USB enumeration fails | every mm of crystal trace is an antenna + load mismatch | ≤3–5 mm, guard, no pours beneath on adjacent layers |
| Connector fights the cable | connector ripped off in service | cable exit direction not simulated at placement | place then CHECK the cable bend + strain relief |
| Hot parts clustered | thermal shutdowns, cap aging | heat zones stack | spread + victims clear (`../../pcb-layout` §4) |
| Test points forgotten | bring-up surgery | TPs deferred "until after routing" — there is no space after | TPs are placement pass 4 |
| Antenna keepout encroached by pour | poor RF range | pour fills the "empty" region by default | keepout RULE AREA all layers, extending past antenna [ft] |
| Filter parts far from boundary | ESD still kills the port | clamp at IC = surge crossed the whole board first | protection AT connector entry pads (`../../pcb-layout` §5) |

## §3 Routing

| Pitfall | Symptom | Why | Fix/prevention |
|---|---|---|---|
| 90° corners on fast/RF | DFM flag, impedance bumps, acid traps | inside corner under-etch slivers [proc] | 45°/arcs on anything fast |
| Return path crosses plane split | EMC failure, crosstalk victim created | return detour = loop antenna [std physics] | no splits under signals; stitch-cap bridge if forced |
| Long stubs | reflections, ghost logic | unterminated stub = resonator | point-to-point; T-taps only low-speed |
| Diff pair split across layers w/o treatment | pair errors under load | skew + return discontinuity | both members transition together + adjacent return vias |
| Length matched AT the receiver | noise where margins are spent | serpentine at the noisiest end couples worst | accordion near source; amplitude ≥3× width |
| Power as thin trace vs needed pour | trace heats, voltage sags | width vs current ignored (`../../pcb-design-rules` §3) | width table / pours; necks deliberate |
| Switching loop area enormous | radiated spikes, ADC noise | hot loop not identified | name hot loops aloud; place + route them small [std] |
| Ground via count too low at transitions | return detours per via = loop per via | each signal via needs a return companion | return via within 1–3 mm of layer changes [std] |
| Acid traps / starved thermals left in | fab flags, etch artifacts | acute angles + 4-way relief spokes at low pour density | post-route cleanup pass; DRC silk/zone warnings reviewed [proc] |
| Orphaned tracks from replaced parts | works at DC, fails with edges | netlist connected, geometry has a stub | purge replaced parts' tracks; connectivity audit [ft] |
| Zone islands / floating copper | resonators at unknown harmonics | pour fragmented by routing | refill, stitch or delete islands (DRC) [ft] |
| Unconnected-list ignored | real gaps ship | zone artifacts taught people to ignore the list | triage: artifact vs real gap each time [ft] |

## §4 Rules / DFM

| Pitfall | Symptom | Why | Fix/prevention |
|---|---|---|---|
| Below fab minimums | surcharge queue / fabbed wrong | advertised limit ≠ design-to value | design-to tier A: 0.15/0.15, 0.3 drill, 0.15 ring [gen-verify] |
| Annular ring too small | intermittent opens | drill registration tolerance eats ring on one side | ≥0.125–0.15 mm ring quick-turn [proc-verify] |
| Mask dams unprintable between fine-pitch pads | mask slivers lift → shorts | web below fab's print limit | let mask openings merge; check fab silk/mask mins [proc] |
| Silkscreen over pads | paste/vision defects | refdes boxes overlap pads | post-route silk pass; refdes off pads [proc] |
| Un-tented vias in paste zone | solder wicking, starved joints | open barrel drains paste mid-reflow | tent vias near BGAs/paste [proc] |
| HV clearance from vibes | arc-over | no derivation recorded | `../../pcb-design-rules` §2 + human review [std] |

## §5 BOM / sourcing

| Pitfall | Symptom | Why | Fix/prevention |
|---|---|---|---|
| NRND designed in | can't build the reorder | status not checked at freeze | check + date + alternates (`../../pcb-bom` §3) [ft] |
| Single-source connector | line down | no drop-in alternate exists | second source or stocked family [ft] |
| Wrong supplier PN (reel/qty) | wrong part arrives | PN suffixes encode packaging | paste PN from supplier page; verify packaging [ft] |
| MPN missing | assembler substitutes | BOM row said "10k 0603" only | MPN mandatory (non-DNP); bom_lint enforces [ft] |
| Polarized parts w/o orientation marks | reversed assembly | silk lacked polarity | polarity marks visible post-assembly [proc] |
| Mixing 0402/0201 needlessly | assembly cost up | value/package consolidation skipped | one package per class; merge values [proc] |
| Schematic value ≠ what MPN is | wrong part "correctly" placed | value col stale after MPN change | BOM lint value/footprint sanity; single source of truth [ft] |
| Converter repurposed w/o recompute | wrong Vout / unstable loop | feedback divider + compensation tied to old Vout | recompute divider/comp/Cout on every voltage change [ft] |

## §6 Solder / assembly

| Pitfall | Symptom | Why | Fix/prevention |
|---|---|---|---|
| Tombstone-prone passives | parts standing upright | one pad tied to big pour (heats late) vs other | thermal balance; relief ties on wave/hand pads [proc] |
| Heavy parts w/o mechanical anchor | connector tears pads | only solder holds mechanical load | anchor holes/epoxy tabs on heavy connectors [proc] |
| BGA via-in-pad unplugged | starved joints | paste wicks into barrel | plug+cap or dogbone [proc] |
| No rework access under shields | debug = desolder the shield | shield over the debug parts | access windows / no shield over TPs |
| One-sided vs two-sided stuffing choices | surprise cost | second side = second setup fee | prefer single side; decide at BOM freeze [proc] |

## §7 EMC / ESD

| Pitfall | Symptom | Why | Fix/prevention |
|---|---|---|---|
| ESD after the sensitive IC | dead ports | surge coupled before clamp | clamp at connector (`../../pcb-layout` §5) [std] |
| Filter ground return long/inductive | filter ineffective | the RETURN is half the filter | shunt grounds via'd immediately below [std] |
| Enclosure seam/gap resonances | emissions peaks at freqs | seam = slot antenna at harmonics | seam stitching, conductive gasket; coordinate mechanicals |
| Shield cans w/o grounding stitches | shield floats = useless | can is a capacitor, not a shield, without RF ground | stitch walls at λ/20 of worry frequency [std] |
| Crystal noise into long trace | FCC failures at clock harmonics | unterminated clock trace = transmitter | series termination, short clock routes, plane under |
| Cable common-mode | board passes alone, fails with cables | cables are the antennas; CM currents ride the shield | CM chokes at ports, shield termination strategy [std] |

## §8 Scripted / headless EDA

| Pitfall | Symptom | Why | Fix/prevention |
|---|---|---|---|
| Re-serialized KiCad libs break | board/schematic files won't open | parser is quoting-sensitive; round-trip rewrites strings [ft] | edit surgically; preserve unedited subtrees verbatim [ft] |
| Script router "succeeds", DRC disagrees | phantom clearance violations | router's clearance model ≠ DRC's model (own-net, widths, edges) [ft] | model exactly: own-net exempt, others at clearance+half-widths, edge margins [ft] |
| Placement from memory/labels | wrong net on pad | pad-nets must come from netlist | export netlist; drive edits from it [ft] |
| No DRC-in-the-loop | errors accumulate silently | script self-belief ≠ geometry truth | kicad-cli drc --json every iteration [ft] |

*(§8 entries are field-tested patterns from agent-driven board builds —
mechanism-generalized, board-anonymized.)*
