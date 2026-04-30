"""
lab_runner.py  -  Hardware Trojan Insertion Lab (flat-Python version)

Each function mirrors one notebook cell. Call them individually or run main()
to execute the full pipeline. Set run=True on task functions to make live
API calls; leave run=False (default) to see a dry-run summary.

Usage:
    python lab_runner.py                # runs main()
    python -c "import lab_runner as lab; lab.setup_backend(); lab.task1_single_insertion(run=True)"
"""

import os
import sys
import glob
import re
import subprocess
import tempfile
from collections import defaultdict

# ── environment hygiene ──────────────────────────────────────────────────────
os.environ.pop('SSLKEYLOGFILE', None)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── shared kernel state (mirrors notebook globals) ───────────────────────────
_ghost = None          # GHOST_Trojan_GPT module reference
_sample_design = None
_vulnerability_desc = None
_strategy = None
_temp_dir = './demo_designs'
_designs = {}


# ── Cell 3: Install packages ─────────────────────────────────────────────────
def setup_packages():
    """pip-install all required packages (idempotent)."""
    pkgs = ['openai', 'anthropic', 'together', 'google-genai', 'python-dotenv']
    for pkg in pkgs:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', pkg])
    print('All packages installed.')


# ── Cell 4: Import GHOST ─────────────────────────────────────────────────────
def import_ghost():
    """Import GHOST_Trojan_GPT and print available vuln/strategy types."""
    global _ghost
    import GHOST_Trojan_GPT as ghost
    _ghost = ghost
    print('GHOST Hardware Trojan Insertion System')
    print('=' * 50)
    print('Available Vulnerability Types:')
    for vid, desc in ghost.vulnerabilities.items():
        print(f'  {vid}: {desc}')
    print('\nAvailable Prompting Strategies:')
    for vid, strat in ghost.prompting_strategies.items():
        print(f'  {vid}: {strat}')
    print('\nGHOST system imported successfully.')


# ── Cell 5: Load API keys ────────────────────────────────────────────────────
def load_api_keys():
    """Load API keys from .env file."""
    from dotenv import load_dotenv
    load_dotenv(override=True)
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print(f'OPENAI_API_KEY loaded (length: {len(openai_key)})')
    else:
        print('WARNING: OPENAI_API_KEY not found in .env')


# ── Cell 6: Setup backend ────────────────────────────────────────────────────
def setup_backend(backend='OpenAI', model='gpt-4o-mini'):
    """Initialise GHOST API backend and set the model."""
    global _ghost
    if _ghost is None:
        import_ghost()
    try:
        _ghost.setup(backend)
        _ghost.model = model
        print(f'GHOST system initialized ({backend} / {model})')
        print('API connection established.')
    except Exception as e:
        print(f'Setup failed: {e}')
        print('Make sure OPENAI_API_KEY is set in your .env file.')


# ── Cell 7: Demo - display sample design ─────────────────────────────────────
def demo_display():
    """Print the sample counter design and select T1 vulnerability."""
    global _ghost, _sample_design, _vulnerability_desc, _strategy
    if _ghost is None:
        import_ghost()

    _sample_design = '''module simple_counter(
    input wire clk,
    input wire rst,
    input wire enable,
    output reg [7:0] count
);

always @(posedge clk or posedge rst) begin
    if (rst) begin
        count <= 8\'b0;
    end else if (enable) begin
        count <= count + 1;
    end
end

endmodule
'''
    print('Original Clean Design:')
    print('=' * 60)
    print(_sample_design)
    print('=' * 60)

    vulnerability_type = 'T1'
    _vulnerability_desc = _ghost.vulnerabilities[vulnerability_type]
    _strategy = _ghost.prompting_strategies[vulnerability_type]
    print(f'Target Vulnerability: {vulnerability_type} - {_vulnerability_desc}')
    print(f'Strategy: {_strategy}')


# ── Cell 8: Demo - live API insertion on sample counter ──────────────────────
def demo_insertion():
    """Call the AI model to insert a T1 Trojan into the sample counter."""
    global _ghost, _sample_design, _vulnerability_desc, _strategy
    if _ghost is None or _sample_design is None:
        print('Run demo_display() first.')
        return

    _ghost.model = 'gpt-4o-mini'
    print('Generating Trojan insertion prompt...')
    prompt = _ghost.construct_prompt(_sample_design, _vulnerability_desc, _strategy)
    print('Calling AI model...')
    try:
        response = _ghost.model_inference(prompt)
        trojan_code, explanation, trigger, payload, taxonomy = \
            _ghost.extract_code_and_metadata(response)

        print('\n' + '=' * 80)
        print('TROJAN INSERTION RESULTS')
        print('=' * 80)
        print(f'\nEXPLANATION:\n{explanation}\n')
        print(f'TRIGGER MECHANISM:\n{trigger}\n')
        print(f'PAYLOAD EFFECTS:\n{payload}\n')
        print(f'TAXONOMY:\n{taxonomy}\n')
        print('=' * 80)
        print('TROJANED VERILOG CODE:')
        print('=' * 80)
        print(trojan_code)
    except Exception as e:
        print(f'Error: {e}')


# ── Cell 9: Batch demo - setup designs ───────────────────────────────────────
def setup_batch_designs():
    """Write alu_simple.v and shift_reg.v to demo_designs/."""
    global _ghost, _designs, _temp_dir
    if _ghost is None:
        import_ghost()

    _temp_dir = './demo_designs'
    os.makedirs(_temp_dir, exist_ok=True)

    _designs = {
        'alu_simple.v': '''\
module alu_simple(
    input [7:0] a, b,
    input [2:0] op,
    output reg [7:0] result
);
always @(*) begin
    case(op)
        3\'b000: result = a + b;
        3\'b001: result = a - b;
        3\'b010: result = a & b;
        3\'b011: result = a | b;
        default: result = 8\'b0;
    endcase
end
endmodule''',
        'shift_reg.v': '''\
module shift_reg(
    input clk, rst, shift_in,
    output reg [7:0] data_out
);
always @(posedge clk or posedge rst) begin
    if (rst)
        data_out <= 8\'b0;
    else
        data_out <= {data_out[6:0], shift_in};
end
endmodule''',
    }

    for filename, content in _designs.items():
        with open(os.path.join(_temp_dir, filename), 'w') as f:
            f.write(content)

    print(f'Created {len(_designs)} designs in {_temp_dir}/')
    for fn in _designs:
        print(f'   {fn}')
    print('\nReady for batch processing.')


# ── Cell 10: Batch demo - execute ────────────────────────────────────────────
def run_batch_demo(run=False):
    """Run batch demo (T1+T2) on alu_simple and shift_reg."""
    global _ghost, _temp_dir, _designs
    if _ghost is None:
        import_ghost()
    if not _designs:
        setup_batch_designs()

    if not run:
        print('Skipping batch demo (run=False).')
        for fn in _designs:
            for vid in ['T1', 'T2']:
                print(f'   Would process: {fn} + {vid}')
        return

    print('Starting batch Trojan insertion job...')
    _ghost.main(
        version_number=1,
        design_file=None,
        base_designs_directory=_temp_dir,
        vulnerable_designs_directory='./trojan_outputs',
        vulnerability_ids=['T1', 'T2'],
        num_threads=2,
    )
    print('Batch job completed. Check ./trojan_outputs/')


# ── Cell 11: Analyze outputs ─────────────────────────────────────────────────
def analyze_outputs(output_dir='./trojan_outputs'):
    """Show file counts and a sample design from the output directory."""
    if not os.path.exists(output_dir):
        print(f'No output directory found at {output_dir}')
        print('Run the batch job first.')
        return

    verilog_files = glob.glob(f'{output_dir}/**/*.v', recursive=True)
    taxonomy_files = glob.glob(f'{output_dir}/**/*_taxonomy.txt', recursive=True)

    print('TROJAN GENERATION ANALYSIS')
    print('=' * 60)
    print(f'Output directory : {output_dir}')
    print(f'Verilog files    : {len(verilog_files)}')
    print(f'Taxonomy files   : {len(taxonomy_files)}')

    if verilog_files:
        print('\nGenerated Trojan Designs:')
        for vfile in verilog_files[:5]:
            print(f'   {os.path.relpath(vfile)} ({os.path.getsize(vfile)} bytes)')
        if len(verilog_files) > 5:
            print(f'   ... and {len(verilog_files) - 5} more')
        with open(verilog_files[0]) as f:
            content = f.read()
        print('\nSample Design:')
        print('-' * 60)
        print(content[:1000] + ('...' if len(content) > 1000 else ''))
    else:
        print('No Trojan designs found.')


# ── Task 1: Single Trojan insertion ──────────────────────────────────────────
def task1_single_insertion(run=False):
    """Task 1: Insert a T1 Trojan into simple_cpu.

    Args:
        run: Set True to make a live API call; False prints a dry-run summary.
    """
    global _ghost
    if _ghost is None:
        import_ghost()

    target_cpu = '''\
module simple_cpu(
    input clk, rst,
    input [31:0] instruction,
    input [31:0] data_in,
    output reg [31:0] data_out,
    output reg [31:0] pc,
    output reg mem_write
);
    reg [31:0] registers [0:7];
    wire [2:0] opcode = instruction[31:29];
    wire [2:0] rd     = instruction[28:26];
    wire [2:0] rs1    = instruction[25:23];
    wire [2:0] rs2    = instruction[22:20];

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            pc        <= 32\'h0;
            mem_write <= 1\'b0;
            data_out  <= 32\'h0;
        end else begin
            case (opcode)
                3\'b000: registers[rd] <= registers[rs1] + registers[rs2]; // ADD
                3\'b001: registers[rd] <= registers[rs1] - registers[rs2]; // SUB
                3\'b010: registers[rd] <= registers[rs1] & registers[rs2]; // AND
                3\'b011: registers[rd] <= registers[rs1] | registers[rs2]; // OR
                3\'b100: data_out <= registers[rs1]; mem_write <= 1\'b1;   // STORE
                3\'b101: registers[rd] <= data_in;                        // LOAD
                default: ;
            endcase
            pc <= pc + 4;
        end
    end
endmodule'''

    print('TASK 1: Single Trojan Insertion')
    print('=' * 50)
    print('Target      : simple_cpu')
    print('Vulnerability: T1 (Change functionality)')
    print('Model        : gpt-4o-mini')

    if not run:
        print('\nSkipping insertion (run=False). Set run=True to execute.')
        return

    _ghost.model = 'gpt-4o-mini'
    vulnerability = _ghost.vulnerabilities['T1']
    strategy = _ghost.prompting_strategies['T1']
    print(f'\nInserting {vulnerability} Trojan...')

    try:
        prompt = _ghost.construct_prompt(target_cpu, vulnerability, strategy)
        response = _ghost.model_inference(prompt)
        code, explanation, trigger, payload, taxonomy = \
            _ghost.extract_code_and_metadata(response)

        print('=' * 60)
        print('TROJAN INSERTION RESULTS')
        print('=' * 60)
        print(f'Explanation : {explanation}')
        print(f'Trigger     : {trigger}')
        print(f'Payload     : {payload}')
        print('\nTrojaned Code:')
        print('-' * 30)
        print(code[:800] + ('\n... (truncated)' if len(code) > 800 else ''))
    except Exception as e:
        print(f'Error: {e}')


# ── Task 2: Batch Trojan generation ──────────────────────────────────────────
def task2_batch_generation(run=False, option='A',
                           selected_vulns=None, selected_design='aes_sbox.v'):
    """Task 2: Batch Trojan generation on aes_sbox and uart_controller.

    Args:
        run            : Set True to make live API calls.
        option         : 'A' all×all, 'B' selected vulns, 'C' single design.
        selected_vulns : List of vuln IDs for option B (default ['T1','T2']).
        selected_design: Design filename for option C.
    """
    global _ghost
    if _ghost is None:
        import_ghost()
    if selected_vulns is None:
        selected_vulns = ['T1', 'T2']

    hw_designs = {
        'aes_sbox.v': '''\
module aes_sbox(
    input [7:0] data_in,
    output reg [7:0] data_out
);
    always @(*) begin
        case(data_in)
            8\'h00: data_out = 8\'h63;
            8\'h01: data_out = 8\'h7C;
            8\'h02: data_out = 8\'h77;
            8\'h03: data_out = 8\'h7B;
            default: data_out = 8\'h00;
        endcase
    end
endmodule''',
        'uart_controller.v': '''\
module uart_controller(
    input clk, rst, tx_start,
    input [7:0] tx_data,
    output reg tx, tx_busy
);
    reg [3:0] bit_count;
    reg [7:0] shift_reg;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            tx        <= 1\'b1;
            tx_busy   <= 1\'b0;
            bit_count <= 4\'h0;
        end else if (tx_start && !tx_busy) begin
            shift_reg <= tx_data;
            tx_busy   <= 1\'b1;
            tx        <= 1\'b0;
            bit_count <= 4\'h0;
        end else if (tx_busy) begin
            if (bit_count < 8) begin
                tx        <= shift_reg[0];
                shift_reg <= {1\'b0, shift_reg[7:1]};
                bit_count <= bit_count + 1;
            end else begin
                tx      <= 1\'b1;
                tx_busy <= 1\'b0;
            end
        end
    end
endmodule''',
    }

    batch_dir  = './batch_trojan_designs'
    output_dir = './trojaned_outputs'
    os.makedirs(batch_dir, exist_ok=True)

    for filename, content in hw_designs.items():
        with open(f'{batch_dir}/{filename}', 'w') as f:
            f.write(content)

    print('TASK 2: Batch Trojan Generation')
    print('=' * 50)
    print(f'Designs written to {batch_dir}/')
    for fn in hw_designs:
        print(f'   {fn}')

    if not run:
        designs_count = len(hw_designs) if option != 'C' else 1
        vulns_count = (len(_ghost.vulnerabilities) if option == 'A'
                       else len(selected_vulns) if option == 'B'
                       else len(_ghost.vulnerabilities))
        print(f'\nSkipping batch job (run=False).')
        print(f'Option {option} would make {designs_count * vulns_count} API calls.')
        return

    _ghost.model = 'gpt-4o-mini'
    print(f'\nStarting Batch Option {option}...')

    if option == 'A':
        _ghost.main(version_number=1,
                    base_designs_directory=batch_dir,
                    vulnerable_designs_directory=output_dir,
                    vulnerability_ids=None,
                    num_threads=2)
    elif option == 'B':
        _ghost.main(version_number=1,
                    base_designs_directory=batch_dir,
                    vulnerable_designs_directory=output_dir,
                    vulnerability_ids=selected_vulns,
                    num_threads=2)
    elif option == 'C':
        _ghost.main(version_number=1,
                    design_file=f'{batch_dir}/{selected_design}',
                    vulnerable_designs_directory=output_dir,
                    vulnerability_ids=None,
                    num_threads=2)

    print(f'\nBatch processing completed! Check {output_dir}/')


# ── Task 3: Trojan analysis ───────────────────────────────────────────────────
def task3_analysis(output_dir='./trojaned_outputs'):
    """Task 3: Analyze and compare generated Trojans."""
    print('TASK 3: Trojan Analysis & Comparison')
    print('=' * 50)

    if not os.path.exists(output_dir):
        print(f'Output directory {output_dir} not found.')
        print('Run task2_batch_generation(run=True) first.')
        return

    verilog_files  = glob.glob(f'{output_dir}/**/*.v', recursive=True)
    taxonomy_files = glob.glob(f'{output_dir}/**/*_taxonomy.txt', recursive=True)

    print(f'Found {len(verilog_files)} Trojaned designs')
    print(f'Found {len(taxonomy_files)} taxonomy files')

    if not verilog_files:
        print('No Trojaned designs found.')
        return

    trojan_stats          = defaultdict(list)
    vulnerability_analysis = defaultdict(lambda: defaultdict(list))

    for vfile in verilog_files:
        basename = os.path.basename(vfile)
        parts = basename.replace('.v', '').split('_')
        if len(parts) < 3:
            continue
        design_name = parts[0]
        vuln_type   = parts[1] if parts[1].startswith('H') else 'Unknown'
        model_name  = parts[2] if len(parts) > 2 else 'Unknown'

        with open(vfile) as f:
            content = f.read()

        stats = {
            'design'          : design_name,
            'vulnerability'   : vuln_type,
            'model'           : model_name,
            'lines'           : len(content.splitlines()),
            'chars'           : len(content),
            'always_blocks'   : len(re.findall(r'always\s*@', content)),
            'if_statements'   : len(re.findall(r'\bif\s*\(', content)),
            'registers'       : len(re.findall(r'\breg\s+', content)),
            'hardcoded_values': len(re.findall(r"\d+'[bh][0-9a-fA-F_xXzZ]+", content)),
            'counters'        : len(re.findall(r'<=\s*\w+\s*\+\s*1', content)),
            'comparisons'     : len(re.findall(r'==\s*\d+', content)),
        }
        trojan_stats[vuln_type].append(stats)
        vulnerability_analysis[vuln_type][design_name].append(stats)

    print('\n' + '=' * 60)
    print('TROJAN CHARACTERISTICS ANALYSIS')
    print('=' * 60)

    for vuln_type, stats_list in trojan_stats.items():
        if not stats_list:
            continue
        n = len(stats_list)
        print(f'\n{vuln_type} Trojans ({n} generated):')
        print('-' * 40)
        print(f'   Average lines         : {sum(s["lines"] for s in stats_list)/n:.1f}')
        print(f'   Average if-statements : {sum(s["if_statements"] for s in stats_list)/n:.1f}')
        print(f'   Average registers     : {sum(s["registers"] for s in stats_list)/n:.1f}')
        print(f'   Average counters      : {sum(s["counters"] for s in stats_list)/n:.1f}')

        for tfile in taxonomy_files:
            if vuln_type.lower() in tfile.lower():
                with open(tfile) as f:
                    tax = f.read()
                trg = re.search(r'Trigger:\s*(.+?)(?:\n\n|Payload:)', tax, re.DOTALL)
                pld = re.search(r'Payload:\s*(.+?)(?:\n\n|Taxonomy:)', tax, re.DOTALL)
                if trg:
                    print(f'   Sample trigger : {trg.group(1).strip()[:100]}')
                if pld:
                    print(f'   Sample payload : {pld.group(1).strip()[:100]}')
                break

    print('\n' + '=' * 60)
    print('CROSS-DESIGN COMPARISON')
    print('=' * 60)
    design_complexity: dict = defaultdict(list)
    for vuln_type, design_dict in vulnerability_analysis.items():
        for design_name, stats_list in design_dict.items():
            for s in stats_list:
                complexity = s['lines'] + s['if_statements'] * 2 + s['registers']
                design_complexity[design_name].append(complexity)

    for design, complexities in design_complexity.items():
        avg = sum(complexities) / len(complexities)
        print(f'   {design}: {avg:.1f} avg complexity ({len(complexities)} Trojans)')


# ── Task 4: Trojan validation ─────────────────────────────────────────────────
def task4_validation(output_dir='./trojaned_outputs',
                     log_path='./validation_log.txt'):
    """Task 4: Validate syntax and Trojan indicators; write validation_log.txt.

    Args:
        output_dir: Path to trojaned_outputs/ directory.
        log_path  : Where to write the validation log.
    """
    from datetime import datetime

    print('TASK 4: Trojan Validation & Testing')
    print('=' * 50)

    if not os.path.exists(output_dir):
        print(f'Output directory {output_dir} not found.')
        print('Run task2_batch_generation(run=True) first.')
        return

    verilog_files = glob.glob(f'{output_dir}/**/*.v', recursive=True)
    if not verilog_files:
        print('No Trojaned designs found for validation.')
        return

    print(f'Validating {len(verilog_files)} Trojaned designs...')
    validation_results = []
    log_lines = [
        'Hardware Trojan Validation Log',
        f'Generated : {datetime.now()}',
        '=' * 60,
        '',
    ]

    suspicious_patterns = [
        r"==\s*\d+'[bh][0-9a-fA-F]+",
        r'<=\s*\w+\s*\+\s*1',
        r'if\s*\([^)]*==\s*\d+',
    ]

    for vfile in verilog_files:
        basename = os.path.basename(vfile)
        print(f'\nValidating: {basename}')
        with open(vfile) as f:
            content = f.read()

        result = {
            'file'        : basename,
            'syntax_valid': None,
            'has_module'  : False,
            'has_trojans' : False,
            'line_count'  : len(content.splitlines()),
            'issues'      : [],
        }

        if 'module' in content and 'endmodule' in content:
            result['has_module'] = True
            print('   Module structure: OK')
        else:
            result['issues'].append('Missing module/endmodule')
            print('   Module structure: MISSING')

        if 'trojan' in content.lower() or 'TROJANED DESIGN' in content:
            result['has_trojans'] = True

        pattern_count = sum(len(re.findall(p, content)) for p in suspicious_patterns)
        if pattern_count > 0:
            result['has_trojans'] = True
            print(f'   Suspicious patterns: {pattern_count} found')

        # Optional iverilog syntax check
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.v', delete=False) as tmp:
                tmp.write(content)
                tmp_name = tmp.name
            rc = subprocess.call(
                ['iverilog', '-t', 'null', tmp_name],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            os.unlink(tmp_name)
            result['syntax_valid'] = (rc == 0)
            print(f'   Syntax (iverilog) : {"PASS" if rc == 0 else "FAIL"}')
        except FileNotFoundError:
            print('   Syntax (iverilog) : skipped (not installed)')

        validation_results.append(result)
        log_lines += [
            f'FILE: {basename}',
            f'  Lines              : {result["line_count"]}',
            f'  Module structure   : {result["has_module"]}',
            f'  Trojan indicators  : {result["has_trojans"]}',
            f'  Syntax valid       : {result["syntax_valid"]}',
            f'  Issues             : {result["issues"] or "None"}',
            '',
        ]

    with open(log_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines))
    print(f'\nValidation log written to {log_path}')

    total = len(validation_results)
    print('\n' + '=' * 60)
    print('VALIDATION SUMMARY')
    print('=' * 60)
    print(f'Files validated        : {total}')
    print(f'Valid module structure : {sum(r["has_module"]   for r in validation_results)}/{total}')
    print(f'Trojan indicators      : {sum(r["has_trojans"]  for r in validation_results)}/{total}')
    synced = [r for r in validation_results if r['syntax_valid'] is not None]
    if synced:
        print(f'Syntax passed (iverilog): {sum(r["syntax_valid"] for r in synced)}/{len(synced)}')


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    """Run full pipeline (dry-run by default; flip run= flags to go live)."""
    load_api_keys()
    import_ghost()
    setup_backend('OpenAI')
    demo_display()

    # ---- flip run=True when you want live API calls ----
    demo_insertion          # call demo_insertion() to run
    task1_single_insertion  # call task1_single_insertion(run=True)
    task2_batch_generation  # call task2_batch_generation(run=True, option='A')
    task3_analysis          # call task3_analysis() after outputs exist
    task4_validation        # call task4_validation() after outputs exist

    print('\nSetup complete. Call individual task functions with run=True to generate Trojans.')


if __name__ == '__main__':
    main()
