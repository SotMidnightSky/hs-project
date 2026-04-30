"""
detector.py - Heuristic Hardware Trojan Detector for Verilog designs.

Usage:
    python detector.py <file_or_directory> [--verbose] [--threshold <0-100>]

Returns:
    Exit code 0 if no suspicious files found, 1 if any flagged.
"""

import argparse
import pathlib
import re
import sys

# ---------------------------------------------------------------------------
# Heuristic rule definitions
# Each rule: (name, description, pattern, score_weight)
# Higher weight = stronger indicator of a trojan.
# ---------------------------------------------------------------------------
RULES = [
    # --- Explicit GHOST markers ---
    (
        "insertion_marker",
        "GHOST trojan insertion markers present",
        re.compile(r'//\s*trojan_insertion_begin', re.IGNORECASE),
        30,
    ),
    (
        "ghost_header",
        "GHOST-generated file header (TROJANED DESIGN)",
        re.compile(r'TROJANED\s+DESIGN', re.IGNORECASE),
        30,
    ),

    # --- Suspicious register / signal names ---
    (
        "trojan_named_signal",
        "Signal named 'trojan_*' found",
        re.compile(r'\b(trojan_\w+)\b', re.IGNORECASE),
        25,
    ),
    (
        "leak_named_signal",
        "Signal named 'leak_*' found",
        re.compile(r'\b(leak_\w+)\b', re.IGNORECASE),
        20,
    ),

    # --- Rare-trigger counter pattern ---
    (
        "large_counter_reg",
        "Large counter register (>= 16-bit) typical of rare-trigger trojans",
        re.compile(r'reg\s*\[\s*1[5-9]\s*:\s*0\s*\]|reg\s*\[\s*[2-9]\d\s*:\s*0\s*\]', re.IGNORECASE),
        15,
    ),
    (
        "magic_number_compare",
        "Comparison to suspiciously specific magic constant (e.g. ==16'hDEAD)",
        re.compile(
            r"==\s*\d+'[bBoOhH][0-9a-fA-F_xXzZ]{3,}",
            re.IGNORECASE,
        ),
        10,
    ),

    # --- Covert channel patterns ---
    (
        "unused_output_drive",
        "Unused/extra output driven inside conditional block (covert exfil)",
        re.compile(r'\bif\b.*\n(?:.*\n){0,3}.*\b(tx|out|send|transmit)\s*<=', re.IGNORECASE),
        15,
    ),

    # --- Always-running accumulator / power trojan ---
    (
        "always_accumulator",
        "Always-running shift register / accumulator (power trojan indicator)",
        re.compile(
            r'always\s*@\s*\(\s*posedge\s+\w+\s*\).*?'
            r'(?:<<|>>|shift_reg|accumulator)',
            re.DOTALL | re.IGNORECASE,
        ),
        10,
    ),

    # --- Denial-of-service reset / disable pattern ---
    (
        "forced_disable",
        "Conditional forced reset/disable on rare condition",
        re.compile(r'if\s*\(.*\)\s*(?:begin\s+)?(?:\w+\s*<=\s*[01]\'b0|\w+\s*<=\s*0)', re.IGNORECASE),
        5,
    ),

    # --- Generic suspicious comment keywords ---
    (
        "suspicious_comment",
        "Comment contains suspicious keyword (trojan, backdoor, payload, malicious)",
        re.compile(r'//.*\b(trojan|backdoor|payload|malicious|covert|exfil)\b', re.IGNORECASE),
        20,
    ),
]

MAX_POSSIBLE_SCORE = sum(w for _, _, _, w in RULES)

# ---------------------------------------------------------------------------

def scan_file(path: pathlib.Path, verbose: bool = False) -> dict:
    """Scan a single Verilog file and return a result dict."""
    try:
        text = path.read_text(encoding='utf-8', errors='replace')
    except OSError as exc:
        return {"file": str(path), "error": str(exc), "score": 0, "flags": []}

    flags = []
    score = 0
    for name, description, pattern, weight in RULES:
        matches = pattern.findall(text)
        if matches:
            flags.append({
                "rule": name,
                "description": description,
                "weight": weight,
                "match_count": len(matches),
            })
            score += weight

    # Clamp to 100
    confidence = min(100, int(score / MAX_POSSIBLE_SCORE * 100))

    return {
        "file": str(path),
        "score": score,
        "confidence_pct": confidence,
        "flags": flags,
        "lines": len(text.splitlines()),
    }


def classify(confidence_pct: int, threshold: int) -> str:
    if confidence_pct >= threshold:
        return "SUSPICIOUS"
    if confidence_pct >= threshold // 2:
        return "LOW_RISK"
    return "CLEAN"


def print_result(result: dict, threshold: int, verbose: bool):
    label = classify(result["confidence_pct"], threshold)
    marker = "[!!]" if label == "SUSPICIOUS" else "[ ?]" if label == "LOW_RISK" else "[ OK]"
    fname = pathlib.Path(result["file"]).name
    print(f"{marker} {fname:<55} score={result['score']:>3}  confidence={result['confidence_pct']:>3}%  ({label})")
    if verbose and result["flags"]:
        for f in result["flags"]:
            print(f"       [{f['weight']:>2}pt] {f['rule']}: {f['description']} (x{f['match_count']})")


def scan_path(target: pathlib.Path, verbose: bool, threshold: int) -> list[dict]:
    if target.is_file():
        files = [target]
    else:
        files = sorted(target.rglob("*.v"))
    return [scan_file(f, verbose) for f in files]


def main():
    parser = argparse.ArgumentParser(
        description="Heuristic Hardware Trojan Detector for Verilog designs."
    )
    parser.add_argument("target", help="Verilog file or directory to scan")
    parser.add_argument(
        "--threshold",
        type=int,
        default=20,
        help="Confidence %% threshold above which a file is flagged SUSPICIOUS (default: 20)",
    )
    parser.add_argument("--verbose", action="store_true", help="Show per-rule details")
    args = parser.parse_args()

    target = pathlib.Path(args.target)
    if not target.exists():
        print(f"[ERROR] Path not found: {target}", file=sys.stderr)
        sys.exit(2)

    results = scan_path(target, args.verbose, args.threshold)

    print()
    print("=" * 70)
    print("  GHOST Hardware Trojan Detector - Heuristic Scan Report")
    print("=" * 70)
    print(f"  Target    : {target}")
    print(f"  Files     : {len(results)}")
    print(f"  Threshold : {args.threshold}% confidence")
    print("=" * 70)
    print()

    suspicious = []
    for r in results:
        print_result(r, args.threshold, args.verbose)
        if classify(r["confidence_pct"], args.threshold) == "SUSPICIOUS":
            suspicious.append(r)

    print()
    print("-" * 70)
    print(f"  Suspicious: {len(suspicious)}/{len(results)}  |  "
          f"Rules applied: {len(RULES)}  |  "
          f"Max score: {MAX_POSSIBLE_SCORE}")
    print("-" * 70)
    print()

    sys.exit(1 if suspicious else 0)


if __name__ == "__main__":
    main()
