"""Generate summary.csv from trojaned_outputs/."""
import csv, os, re, pathlib

base = pathlib.Path('./trojaned_outputs/gpt-4o-mini')
rows = []

VULN_NAMES = {
    'T1': 'change functionality',
    'T2': 'leak information',
    'T3': 'denial of service',
    'T4': 'performance degradation',
}

for design_dir in sorted(base.iterdir()):
    for vfile in sorted(design_dir.glob('*.v')):
        stem = vfile.stem
        parts = stem.split('_')
        ht = next((p for p in parts if p.startswith('HT')), '')
        vuln_id = ht[1:] if ht else 'unknown'
        design = design_dir.name

        code = vfile.read_text(errors='replace')
        lines = len(code.splitlines())
        ifs = len(re.findall(r'\bif\b', code))
        regs = len(re.findall(r'\breg\b', code))
        counters = len(re.findall(r'counter|cnt', code, re.IGNORECASE))
        has_marker = 1 if 'trojan_insertion_begin' in code else 0
        has_trigger = 1 if re.search(
            r'trojan_active|trojan_counter|trojan_trigger|trojan_insertion_begin',
            code, re.IGNORECASE) else 0

        tax_file = vfile.with_name(stem + '_taxonomy.txt')
        expl = trigger_cond = payload = ''
        if tax_file.exists():
            tax = tax_file.read_text(errors='replace')
            m = re.search(r'Explanation:\s*(.+?)(?=\nTrigger:|\Z)', tax, re.DOTALL)
            if m:
                expl = m.group(1).strip().replace('\n', ' ')[:150]
            m = re.search(r'Trigger:\s*(.+?)(?=\nPayload:|\Z)', tax, re.DOTALL)
            if m:
                trigger_cond = m.group(1).strip().replace('\n', ' ')[:150]
            m = re.search(r'Payload:\s*(.+?)(?=\nTaxonomy:|\Z)', tax, re.DOTALL)
            if m:
                payload = m.group(1).strip().replace('\n', ' ')[:150]

        rows.append({
            'design': design,
            'vulnerability_id': vuln_id,
            'vulnerability_type': VULN_NAMES.get(vuln_id, 'unknown'),
            'model': 'gpt-4o-mini',
            'output_file': vfile.name,
            'lines_of_code': lines,
            'if_statements': ifs,
            'registers': regs,
            'counter_mentions': counters,
            'has_insertion_markers': has_marker,
            'has_trigger_pattern': has_trigger,
            'explanation': expl,
            'trigger_condition': trigger_cond,
            'payload_effect': payload,
        })

out = pathlib.Path('./summary.csv')
fieldnames = list(rows[0].keys())
with open(out, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f'Wrote {len(rows)} rows to {out}')
