# DXF Spec Library – NOW SKU Packs (KZN) v1.0

**Machine:** Golden Laser X3 • **Materials:** SS / MS / Galvanized steel / Acrylic • **Max thickness (now):** ≤ 16.0 mm (recommend ≤ 12.0 mm for high-repeat SKUs)  
**Gases:** Air / O₂ / N₂ • **Sheet sizes (primary):** 1225×2450 mm (steel), 1220×2440 mm (acrylic)

---

## 0) Global Standards (applies to every SKU)

### 0.1 File Structure & Naming
- **Root:** `/DXF_LIBRARY/NOW/v1.0/`  
- **Folder per category:** `CONSTRUCTION/`, `SIGNAGE/`, `OEM/`, `ELECTRICAL/`, `FURNITURE/`, `MINING/`, `B2C/`  
- **DXF name format:** `SKU-[CategoryCode]-[Family]-[Size]-[Thk]-[Mat]-v[rev].dxf`  
  - Example: `SKU-CON-BRK-A-80x80-6-MS-v1.dxf`  
- **Cutframe name (CypCut):** `CF-[SKU]-[Gas]-[Sheet]-Nest[v]` → `CF-SKU-CON-BRK-A-80x80-6-MS-N2-1225x2450-Nest1.cfz`

### 0.2 Drawing Conventions
- **Units:** millimetres  
- **Kerf comp:** leave **geometry true-size**; compensation applied in CypCut tool library  
- **Corner radii:** default R3 for outer corners unless otherwise noted (min R1.5 for <4 mm thk)  
- **Holes:** standard Ø for M fasteners (clearance): M6→Ø6.6, M8→Ø9.0, M10→Ø11.0, M12→Ø13.5  
- **Slots:** width = bolt Ø+0.6; length as per table; end radii = width/2  
- **Etch/Mark layers:** `L-ETCH-TEXT`, `L-ETCH-BARCODE` (0.05 mm offset outline for mark)  
- **Part ID text (etched):** `SKU`, material, thickness, revision, and **QR/Code128** of `SKU|Batch|Qty`  
- **Datum:** lower-left; include 50×10 mm **etch-only** datum tag for QC

### 0.3 Nesting & Gaps
- **Default part gap:** 2.0 mm steel; 1.5 mm acrylic  
- **Edge margin from sheet:** 6.0 mm  
- **Common-line cutting:** allowed for brackets/gussets ≤ 6 mm; **disabled** on acrylic  
- **Microjoints:** 0.6–0.8 mm wide × 0.8–1.2 mm long; 2–4 per part edge depending size  
- **Tab locations:** avoid holes/slots corners; symmetric where possible

### 0.4 CypCut Cutframe Standards (templates)
- **Lead-in/out:** perpendicular lead-in 0.8–1.2 mm; no lead-out for small holes (<6 mm)  
- **Pierce strategy:** pre-pierce OFF for ≤3 mm; ON for ≥4 mm plates with dwell  
- **Cut order:** inner features → outer profile; smallest to largest parts  
- **Nozzle standoff:** per material preset; record actuals in `CFZ Notes`  
- **Gas & focus:** selected by Material×Thickness preset; **document any overrides**  
- **Quality flags:** `Enable precision` for holes <6 mm and decorative detail; **defilm** off for metals with no coating; **smooth pierce** off by default  
- **Acrylic:** film ON; cavity cut for small text; **no common-line**; adjust power to avoid melt bridges

### 0.5 QA & Packaging
- **QC kit:** go/no-go gauges for M6/M8/M10/M12; slot gauge; radius templates R3/R6/R10  
- **Flatness check:** place on granite; 0.5 mm feeler (≤300 mm parts), 1.0 mm (>300 mm)  
- **Deburr:** edge break ~0.2–0.4 mm; acrylic flame polish optional  
- **Pack:** interleave kraft for metal; film for acrylic; label box with `SKU | Qty | Batch | PO`

---

## 1) CONSTRUCTION – NOW SKU Packs

### 1.1 Bracket Pack A (L-/T-/Flat)
- **Families:** `BRK-A-L`, `BRK-A-T`, `BRK-A-F`  
- **Materials/Thk:** MS 3/4/6/8 mm  
- **Nominal sizes (L & T):** 60×60, 80×80, 120×120, 160×160 (arm width = 40 mm for ≤6 mm; 50 mm for 8 mm)  
- **Flat plates:** 60×120, 80×160, 120×240, 160×320  
- **Hole grid options:** 40 mm or 80 mm pitch; edge distance = 15 mm  
- **Slot option:** 9×18, 11×22 for M8/M10 variants  
- **Revisions:** `-A` clearance holes; `-B` slotted; `-C` mixed  
- **DXF layers:** `L-CUT`, `L-ETCH-TEXT` (SKU, size, thk, rev), `L-ETCH-BARCODE`  
- **Tolerances:** ±0.3 profile; hole Ø ±0.1; PCD/centres ±0.2  
- **Pack SKUs (examples):**  
  - `SKU-CON-BRK-A-L-80x80-6-MS-v1.dxf`  
  - `SKU-CON-BRK-A-F-120x240-4-MS-v1.dxf`
- **Cutframe presets:** `CF-PRESET-MS-3`, `CF-PRESET-MS-4`, `CF-PRESET-MS-6`, `CF-PRESET-MS-8`  
- **Nest template:** `NEST-CON-BRK-A-1225x2450-MS` (yields per sheet shown in sheet map below)

**Sheet Map (example 1225×2450, MS 6 mm):**  
- 80×80 L-brackets, 2 mm gaps → **10 cols × 14 rows = 140 pcs/sheet**  
- Record actual yield per thickness in `Nest_Yield.xlsx`

### 1.2 Base/Splice Plate Kit
- **Materials/Thk:** MS 6/8/10 mm  
- **Sizes:** 120, 160, 200, 250, 300 mm square; rectangular 120×160, 160×240  
- **Anchor patterns:** 4×Ø12 @ 25 mm from edges; 4×Ø16 @ 30 mm; 8×Ø16 (corner+mid)  
- **Centre hole (optional):** Ø18 (service pass-through)  
- **Edge chamfer:** 3×45° (or R6)  
- **Tolerances:** ±0.4 profile; hole ±0.15  
- **Etch:** arrow for “NORTH/UP” if requested  
- **SKU example:** `SKU-CON-PLT-SQ-200-8-MS-4x16-v1.dxf`

### 1.3 Cable-Tray Clip Set
- **Material/Thk:** Galv/MS 2–4 mm  
- **Widths (tray):** 100, 150, 200, 300, 450 mm (clip length = tray width/2)  
- **Slot:** 8×20 (M8), 10×25 (M10)  
- **Bend marks (etch):** 90° line, centre  
- **SKU example:** `SKU-CON-CLP-TRAY-200-3-MS-v1.dxf`

---

## 2) SIGNAGE – NOW SKU Packs

### 2.1 Traffic Sign Blanks
- **Material/Thk:** Galvanized 1.6/2.0 mm  
- **Shapes & sizes:**  
  - Circle Ø600, Ø750, Ø900, Ø1200  
  - Triangle 900 mm per side (R30 corners)  
  - Rectangle 600×900, 900×1200 (R25 corners)  
- **Mount holes:** 2×Ø10 at standard spacings:  
  - Circle: vertical line, 100 mm apart centred  
  - Rectangles: 4×Ø10, 25 mm in from corners  
- **Edge radius control:** ±0.3  
- **SKU example:** `SKU-SGN-BLNK-CIR-Ø750-2-GALV-v1.dxf`

### 2.2 Street-Name Panels
- **Material/Thk:** Galv 2–3 mm  
- **Sizes:** 150×600, 200×800, 300×1200  
- **Mount pattern:** 4×Ø10 @ 25 mm inset  
- **SKU example:** `SKU-SGN-STNAME-150x600-2-GALV-v1.dxf`

### 2.3 Acrylic Letters/Logos (Packs A–C)
- **Material/Thk:** Acrylic 3/5/10 mm  
- **Heights:** 100, 200, 300 mm (cap-height)  
- **Fonts:** Sans (Pack A), Serif (Pack B), Block (Pack C)  
- **Fixing holes (optional):** Ø4 with paper drill jig DXF  
- **Edge:** flame-polish option  
- **SKU example:** `SKU-SGN-ALPHA-A-200-5-ACR-v1.dxf`

---

## 3) OEM MANUFACTURING – NOW SKU Packs

### 3.1 Gusset Pack (triangular/rounded)
- **Material/Thk:** MS 4/6/8 mm  
- **Common sizes:** cathetus 60, 80, 120, 160; hypotenuse rounded R20–R40  
- **Holes:** optional 2×Ø9 (M8) 20 mm from legs  
- **SKU example:** `SKU-OEM-GUS-R-80-6-MS-v1.dxf`

### 3.2 Trailer Light Plate Pack
- **Material/Thk:** MS 3–5 mm  
- **Sizes:** 120×180, 150×220  
- **Cutouts:** Ø20/Ø25 for grommets; slots 9×18  
- **SKU example:** `SKU-OEM-TR-LGTPLT-150x220-4-MS-v1.dxf`

### 3.3 Machine Guard Panel Set
- **Material/Thk:** MS/SS 2–3 mm  
- **Sizes:** 150×300, 200×400, 300×600  
- **Vent pattern:** 15×60 slots @ 25 pitch or Ø8 perf @ 20 pitch  
- **Edge hem allowance (note):** +10 etch line if client will fold  
- **SKU example:** `SKU-OEM-GRD-300x600-2-MS-SLOT-v1.dxf`

---

## 4) ELECTRICAL / ELECTRONICS – NOW SKU Packs

### 4.1 Enclosure Faceplate Set (6 sizes)
- **Material/Thk:** SS/MS/Alu 1.5–3.0 mm  
- **Base sizes:** 100×150, 120×180, 150×200, 200×300  
- **Cutout templates:** IEC switch, Ø22 pushbutton, RJ45, USB, circular meters  
- **Tolerance:** cutouts ±0.1  
- **Etch:** port labels (layer `L-ETCH-TEXT`)  
- **SKU example:** `SKU-ELC-FP-150x200-SS-2-v1.dxf`

### 4.2 DIN-Rail Plate / Gland Plate Kit
- **Material/Thk:** Galv/MS 2–3 mm  
- **Sizes:** 100×150, 150×200, 200×250  
- **Holes/slots:** 7×15 slots grid @ 25 mm  
- **SKU example:** `SKU-ELC-DIN-150x200-2-GALV-v1.dxf`

### 4.3 Chassis Blank Pack
- **Material/Thk:** MS/Alu 1.2–2 mm  
- **Sizes:** 200×200, 200×300, 300×400  
- **Bend marks:** etch centre-lines if requested  
- **SKU example:** `SKU-ELC-CHS-300x400-1p5-ALU-v1.dxf`

---

## 5) FURNITURE / SHOPFITTING / DÉCOR – NOW SKU Packs

### 5.1 Table/Frame Bracket Pack
- **Material/Thk:** MS 3/4/6 mm  
- **Sizes:** 80×80, 120×120, 160×160  
- **Holes:** M6/M8 options; countersink etch marks  
- **Finish:** black powder-coat default  
- **SKU example:** `SKU-FUR-BRK-120x120-4-MS-v1.dxf`

### 5.2 Shopfitting Shelf Support Kit
- **Material/Thk:** SS/MS 3–6 mm  
- **Sizes:** 100, 150, 200, 300 projection  
- **Slots:** 8×20 for adjustability  
- **SKU example:** `SKU-FUR-SHELF-200-4-MS-v1.dxf`

### 5.3 Small Décor Panel Pack (6 patterns)
- **Material/Thk:** MS/SS 1.6–3 mm  
- **Sizes:** 300×600, 450×900, 600×900  
- **Patterns:** `Lattice-A`, `Floral-B`, `Geo-C`, `Lines-D`, `Mashrabiya-E`, `Wave-F`  
- **Edge radius:** R3 min on sharp nodes  
- **SKU example:** `SKU-FUR-DEC-GEO-C-600x900-2-MS-v1.dxf`

---

## 6) MINING / AGRI – NOW SKU Packs

### 6.1 Shim Pack (slot shims)
- **Material/Thk:** MS/SS 2/3/4/5/6/8 mm  
- **External sizes:** 30×60, 50×80, 80×120  
- **Slot:** width = bolt Ø+0.6 (M8/M10/M12 variants); length 1.8×Ø  
- **Corner:** R3  
- **SKU examples:**  
  - `SKU-MIN-SHM-50x80-M10-3-MS-v1.dxf`  
  - `SKU-MIN-SHM-80x120-M12-6-SS-v1.dxf`

### 6.2 Sensor Bracket Kit
- **Material/Thk:** MS/SS 3–6 mm  
- **Base:** 60×120 with slot grid; side ear 30×60  
- **Holes:** Ø9/Ø11  
- **SKU example:** `SKU-MIN-SNS-60x120-4-MS-v1.dxf`

### 6.3 Thin Wear Strip Pack
- **Material/Thk:** MS 6–12 mm  
- **Sizes:** 100×300, 120×400, 150×500  
- **Chamfer:** 2×45° ends or R10  
- **SKU example:** `SKU-MIN-WEAR-120x400-8-MS-v1.dxf`

---

## 7) B2C – NOW SKU Packs

### 7.1 House Number Set (5 fonts × 3 sizes)
- **Material/Thk:** SS/Acrylic 3/5 mm  
- **Heights:** 100/200/300 mm; stroke ≥ 8 mm  
- **Fix:** 2×Ø4 holes + paper jig DXF  
- **SKU example:** `SKU-B2C-NUM-200-SS-BLOCK-5-v1.dxf`

### 7.2 Stencil Pack (A–Z, 0–9)
- **Material/Thk:** Acrylic 3–5 mm  
- **Sheet size:** A4, A3, A2  
- **Bridge width:** ≥2.5 mm  
- **SKU example:** `SKU-B2C-STN-A3-AZ-3-ACR-v1.dxf`

### 7.3 Braai Grate Pack (3 sizes, 2 patterns)
- **Material/Thk:** SS 3–4 mm  
- **Sizes:** 300×400, 400×500, 500×600  
- **Patterns:** parallel bars / diamond  
- **Reinforce:** underside ribs option (etch lines)  
- **SKU example:** `SKU-B2C-BRGR-400x500-4-SS-DIA-v1.dxf`

---

## 8) Material–Thickness Preset Table (CypCut Library Placeholders)
*(Populate with your proven params; keep IDs stable so cutframes stay valid.)*

| Preset ID | Material | Thickness | Gas | Notes |
|---|---|---:|---|---|
| MS-3-AIR | Mild Steel | 3.0 | Air | general cutting, small brackets |
| MS-6-O2 | Mild Steel | 6.0 | O₂ | plates/structural |
| MS-8-O2 | Mild Steel | 8.0 | O₂ | splice plates |
| MS-10-O2 | Mild Steel | 10.0 | O₂ | heavy plates |
| GALV-2-N2 | Galvanized | 2.0 | N₂ | sign blanks; clean edge |
| SS-2-N2 | Stainless | 2.0 | N₂ | guard panels |
| SS-4-N2 | Stainless | 4.0 | N₂ | braai grates |
| ACR-5-AIR | Acrylic | 5.0 | Air | film on; no common-line |

> Maintain a `Preset Change Log` (date, reason, effect on quality/speed) and revalidate affected SKUs.

---

## 9) QC Sheets (per SKU)
Each SKU folder includes `QC-[SKU].pdf` with:  
- **Critical dims:** with ± tolerances  
- **Hole gauges used**  
- **Flatness check result**  
- **Edge quality score (1–5)**  
- **Operator & timestamp**  
- **Customer sign-off (if first article)**

---

## 10) Nest Templates (per sheet)
Provide `NEST-[Category]-[Sheet]-[Thk]-[Mat]-v1.cfz` with:  
- **Auto-remnant definition:** save offcuts > 150×300 with etched size tag  
- **Common-line toggle map**  
- **Microjoint rule sets**  
- **Estimated runtime per sheet** (target utilization ≥ 85%)

---

## 11) Implementation Plan (2 weeks)
**Day 1–2:** Create DXF masters for Construction Brackets + Base/Splice Plates; validate nest yields  
**Day 3–4:** Signage blanks + street panels; mount-hole jig check  
**Day 5:** Electronics faceplates templates + cutout library  
**Day 6:** OEM gussets + guard panels  
**Day 7:** Mining shims + wear strips  
**Day 8:** Furniture brackets + small décor patterns  
**Day 9:** B2C numbers/stencils/grates  
**Day 10:** Build CypCut presets; generate cutframes  
**Day 11–12:** QC sheets + first-article runs; update tolerances  
**Day 13:** Packaging standards + barcode labels  
**Day 14:** Final audit; lock v1.0; start sales outreach

---

## 12) Sales Collateral (per SKU Pack)
- 1-page **Spec Sheet** (PNG/PDF) with photo, dims, MOQ, price tiers  
- **DXF preview** image for quoting  
- **Use-case list** (industries & applications)  
- **Lead time** tables (stock vs. make-to-order)

---

## 13) Change Control & Versions
- Each DXF revision increments `v#`; maintain `CHANGELOG.md` in root  
- If geometry changes, version new `SKU` and deprecate old; keep both for historical orders  
- Any preset change that affects quality triggers **FAI** (First Article Inspection) on next batch

---

**Ready for next step:** say *proceed* and tell me which **category** to generate first DXFs for (I’ll output a dimensional table + param variants you can hand straight to drawing/CAM).

