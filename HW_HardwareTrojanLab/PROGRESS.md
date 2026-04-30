# Hardware Trojan Insertion Lab — Progress & Report Notes
**Course:** Hardware Security  
**Team Members:**
- Member 1: [Full Name] | RIN: [RIN]
- Member 2: [Full Name] | RIN: [RIN]
- Member 3: [Full Name] | RIN: [RIN]

**API Used:** [ ] OpenAI  [ ] Anthropic  [ ] Google Gemini  [ ] TogetherAI  
**Model Used:** _______________

---

## Setup Checklist
- [ ] API key configured in environment
- [ ] `GHOST_Trojan_GPT.py` imported successfully (Cell 3)
- [ ] `ghost.model` set to chosen model (Cell 7 / Cell 13)
- [ ] All pip packages installed (Cell 2)
- [ ] Output directory created: `./trojaned_outputs/` or `./batch_trojan_designs/`

---

## Vulnerability Taxonomy (Task 1 Report Content)

> Fill this in from `ghost.vulnerabilities` and `ghost.prompting_strategies`

| ID | Name | Prompting Strategy Summary |
|----|------|----------------------------|
| T1 | Change functionality | Subtly alter logic to produce incorrect results under specific conditions |
| T2 | Leak information | Design a covert data transmission mechanism activated by a specific signal pattern |
| T3 | Denial of service | Introduce a condition that temporarily disables the module via a rare event sequence |
| T4 | Performance degradation | Implement a running shift register/accumulator to increase power consumption |

**Safety Statement:**  
> All Trojans generated in this lab are for educational and defensive hardware security research only. No generated designs should be deployed in production or real hardware systems. This work follows institutional research ethics guidelines.

---

## Task 1: Single Trojan Insertion

**Target Design:** `simple_cpu` (from notebook Cell 13)  
**Vulnerability type applied:** T1 (Change functionality)  
**Model used:** _______________  
**Date run:** _______________  
**Assigned to:** _______________

### Steps Taken
1. [ ] Ran setup cells (Cells 2–5)
2. [ ] Set `ghost.model` to chosen model
3. [ ] Set `RUN_INSERTION = True` and executed Cell 13
4. [ ] Captured output

### API Response Captured

**Explanation:**
```
[Paste the Explanation section from the AI output here]
```

**Trigger:**
```
[Paste the Trigger section here]
```

**Payload:**
```
[Paste the Payload section here]
```

**Taxonomy:**
```
[Paste the Taxonomy section here]
```

### Trojaned Code Excerpt
```verilog
[Paste the key trojan_insertion_begin ... trojan_insertion_end block here]
```

### Analysis Notes
- How does the trigger activate? _______________
- What does the payload do when triggered? _______________
- Is the Trojan stealthy (hard to notice in a code review)? _______________
- Does the original functionality still work correctly? _______________

### Report Paragraph (draft)
> We inserted a T1 (change-functionality) Hardware Trojan into a simple 32-bit CPU design using the GHOST system with [model]. The trigger condition is [describe trigger]. When activated, the Trojan [describe payload effect]. The Trojan was inserted at the RTL level within synthesizable Verilog, using a counter-based trigger at [location in code]. Original CPU functionality is preserved in all non-trigger states.

---

## Task 2: Batch Trojan Generation

**Designs used:**
- `aes_sbox.v` — AES S-Box substitution logic
- `uart_controller.v` — UART serial transmitter

**Vulnerability types generated:** T1, T2, T3, T4  
**Batch option used:** [ ] A (all × all)  [ ] B (specific vulns)  [ ] C (single design)  
**Total API calls made:** ___  
**Output directory:** `./trojaned_outputs/`  
**Date run:** _______________  
**Assigned to:** _______________

### Steps Taken
1. [ ] Cell 15 executed — baseline designs written to `./batch_trojan_designs/`
2. [ ] Set `RUN_BATCH = True`, chose option, executed
3. [ ] Confirmed output files created in `./trojaned_outputs/`

### Files Generated
| File | Vulnerability | Lines | Notes |
|------|---------------|-------|-------|
| aes_sbox_HT1_[model]_A1.v | T1 | | |
| aes_sbox_HT2_[model]_A1.v | T2 | | |
| aes_sbox_HT3_[model]_A1.v | T3 | | |
| aes_sbox_HT4_[model]_A1.v | T4 | | |
| uart_controller_HT1_[model]_A1.v | T1 | | |
| uart_controller_HT2_[model]_A1.v | T2 | | |
| uart_controller_HT3_[model]_A1.v | T3 | | |
| uart_controller_HT4_[model]_A1.v | T4 | | |

### Observations
- Any designs where the API failed or produced malformed output: _______________
- Any interesting differences between T1–T4 across the two designs: _______________

### Report Paragraph (draft)
> We ran batch Trojan generation on two hardware designs (AES S-Box and UART controller) across all four vulnerability types (T1–T4) using the GHOST batch processing API (Cell 15). [X] of 8 files were generated successfully. Generation used [model] with [N] parallel threads. Failures (if any): [describe].

---

## Task 3: Trojan Analysis & Comparison

**Function used:** `analyze_trojan_characteristics()` (Cell 17)  
**Input directory:** `./trojaned_outputs/`  
**Date run:** _______________  
**Assigned to:** _______________

### Steps Taken
1. [ ] Confirmed output files exist from Task 2
2. [ ] Executed Cell 17
3. [ ] Captured printed analysis output

### Metrics Captured (fill from printed output)

| Vulnerability | Avg Lines | Avg If-Stmts | Avg Registers | Avg Counters | Sample Trigger Summary |
|---------------|-----------|--------------|---------------|--------------|------------------------|
| T1 | | | | | |
| T2 | | | | | |
| T3 | | | | | |
| T4 | | | | | |

### Design Complexity Rankings (from printed output)
| Design | Avg Complexity Score |
|--------|----------------------|
| aes_sbox | |
| uart_controller | |

### Key Findings / Observations
- Which vulnerability type produced the most complex Trojans? _______________
- Which design was easiest/hardest to trojanize? _______________
- Noticeable patterns in how triggers were constructed? _______________
- Surprising or unexpected results? _______________

### Report Paragraph (draft)
> Across [N] Trojaned designs, T[X] Trojans were the most complex (avg [N] lines, [N] if-statements), while T[Y] Trojans were simplest. AES S-Box / UART designs showed [difference] in Trojan complexity. T2 (information leakage) Trojans consistently used [pattern] as a covert channel trigger. T3 (DoS) Trojans relied on [pattern]. These differences reflect the distinct attack strategies required per vulnerability class.

---

## Task 4: Trojan Validation & Testing

**Function used:** `validate_trojaned_designs()` (Cell 19)  
**Date run:** _______________  
**Assigned to:** _______________

### Steps Taken
1. [ ] Executed Cell 19
2. [ ] Captured validation summary output
3. [ ] Noted any syntax errors or structural issues

### Validation Results (fill from output)

| File | Module Structure | iverilog Syntax | Trojan Markers | Issues |
|------|-----------------|-----------------|----------------|--------|
| | ✅ / ❌ | ✅ / ❌ / N/A | ✅ / ❌ | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |

**iverilog available?** [ ] Yes  [ ] No (syntax check skipped)  
**Total validated:** ___ files  
**Passed module structure:** ___ / ___  
**Syntax passed:** ___ / ___  
**Trojan markers detected:** ___ / ___

### Limitations Noted
- _______________

### Report Paragraph (draft)
> We validated [N] Trojaned designs using the `validate_trojaned_designs()` function (Cell 19). All [N] / [N-x] files contained valid `module`/`endmodule` structure. Syntax validation via iverilog [was / was not] available — [X] files passed / iverilog was unavailable so we relied on structural pattern checks. Trojan markers (`trojan_insertion_begin`/`end`) were detected in [X] / [N] files. Issues found: [list]. Limitation: without formal synthesis testing (e.g., Vivado/Yosys), full functional correctness cannot be guaranteed.

---

## summary.csv Contents

> Fill this in once Tasks 2–4 are done. One row per generated .v file.

```csv
design,vuln_type,trigger_type,payload_type,lines,always_blocks,hardcoded_values,validation_pass
aes_sbox,T1,,,,,,
aes_sbox,T2,,,,,,
aes_sbox,T3,,,,,,
aes_sbox,T4,,,,,,
uart_controller,T1,,,,,,
uart_controller,T2,,,,,,
uart_controller,T3,,,,,,
uart_controller,T4,,,,,,
```

---

## detector.py Plan (Task 5 / Report Section)

> Build after Tasks 2–4 are done. Use observed Trojan patterns to write heuristic rules.

### Heuristic Rules to Implement
Based on what was observed in Tasks 2–4:
1. Counter-based trigger: flag `always` blocks with a counter incrementing toward a hardcoded threshold
2. Magic constant comparisons: flag `== N'hXXXX` patterns with values not used in the clean design
3. Shift register chains: flag long shift register chains in `always` blocks (T4 indicator)
4. Rare input combinations: flag conditions with 3+ AND-ed input signals compared to constants (T3 indicator)
5. Secondary output assignments: flag assignments to outputs only inside deeply nested `if` blocks (T2 indicator)

### Evaluation Results (fill after running detector.py)
| File | Flagged? | Correct? | Notes |
|------|----------|----------|-------|
| | | | |

**False Positives:** ___  **False Negatives:** ___  
**Discussion:** _______________

---

## Overall Notes / Issues Encountered
- _______________
- _______________

## Submission Packaging Checklist
- [ ] `Hardware_Trojan_Insertion_Lab.ipynb` — all cells executed, outputs saved
- [ ] `GHOST_Trojan_GPT.py`
- [ ] `detector.py`
- [ ] `summary.csv`
- [ ] `validation_log.txt` (populated)
- [ ] `trojaned_outputs/` directory with all generated `.v` + `_taxonomy.txt` files
- [ ] `README.md` (how to reproduce the project)
- [ ] `report.pdf` (≤6 pages, ≥10pt font, team names/RINs/contributions)
- [ ] `video.mp4` (≤10 min)
- [ ] Top-level zip with report, video, and inner `code.zip`
