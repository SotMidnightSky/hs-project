# Hardware Trojan Insertion Lab - Reproducibility Guide

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10 or higher |
| Jupyter | `pip install jupyter` or use VS Code Jupyter extension |
| OpenAI API key | gpt-4o-mini access required |

No hardware or Verilog simulator is required to run the insertion pipeline.
`iverilog` is optional - syntax validation will be skipped automatically if it is not installed.

---

## 1. Clone / Unzip the Project

Place the project folder somewhere on your machine.  
All commands below are run from inside the **project root** (the folder containing `Hardware_Trojan_Insertion_Lab.ipynb`).

---

## 2. Create a Virtual Environment and Install Dependencies

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install openai anthropic together google-genai python-dotenv tqdm jupyter
```

---

## 3. Set Up Your OpenAI API Key

Create a file named `.env` in the project root (same folder as the notebook) with the following content:

```
OPENAI_API_KEY=sk-...your-key-here...
```

The key must have access to **gpt-4o-mini**.  
Do not commit `.env` to version control.

---

## 4. Open and Run the Notebook

```bash
jupyter notebook Hardware_Trojan_Insertion_Lab.ipynb
```

Or open it directly in VS Code with the Jupyter extension and select your `.venv` kernel.

Run cells top to bottom. Each task section is self-contained:

| Task | What it does |
|---|---|
| Task 1 | Single-sample Trojan insertion on a CPU design using gpt-4o-mini |
| Task 2 | Batch insertion across `aes_sbox.v` and `uart_controller.v` (4 variants each) |
| Task 3 | Metrics extraction and cross-design comparison |
| Task 4 | Structural validation of all trojaned files → writes `validation_log.txt` |
| Task 5 | Heuristic Trojan detector evaluated on trojaned and clean designs |

Tasks 2, 3, and 4 have a `RUN_BATCH = False` / `RUN_INSERTION = False` guard at the top of the cell - set it to `True` to make live API calls. Expected runtime: 2-5 minutes.

---

## 5. Expected Output Files

After a successful run the following files/folders will be present:

```
trojaned_outputs/          # 8 trojaned Verilog files (4 per design)
summary.csv                # batch metrics (lines added, trigger type, etc.)
validation_log.txt         # structural validation results for all 8 files
```

---

## File Overview

| File | Purpose |
|---|---|
| `Hardware_Trojan_Insertion_Lab.ipynb` | Main notebook - run this to reproduce all results |
| `GHOST_Trojan_GPT.py` | Core AI Trojan insertion engine (OpenAI / Together / Anthropic backends) |
| `detector.py` | Heuristic Trojan detector (10-rule weighted scorer) |
| `batch_trojan_designs/` | Input Verilog designs for batch insertion (aes_sbox, uart_controller) |
| `demo_designs/` | Additional sample Verilog designs |
| `summary.csv` | Pre-generated batch metrics (included for reference) |
| `validation_log.txt` | Pre-generated validation results (included for reference) |

---

## Troubleshooting

**`OPENAI_API_KEY` not found** - make sure `.env` is in the same directory as the notebook and contains the key on a single line with no extra spaces.

**API rate-limit errors** - the batch runner uses a `ThreadPoolExecutor` with a small thread count. If you hit 429 errors, wait 60 seconds and re-run the cell.

**`module`/`endmodule` not found in validation** - the API returned malformed Verilog. Re-run the Task 2 cell; the model occasionally produces incomplete output on the first attempt.
