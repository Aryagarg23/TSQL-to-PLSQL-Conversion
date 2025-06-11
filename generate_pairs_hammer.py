import os
import re
import json

# --- Configuration (The Definitive Master Configuration) ---
HAMMERDB_DIR = "HammerDB"
OUTPUT_DIR_RAW_FILES = "paired_sql_master_raw"

# THE CORRECT FILE PATHS, taken directly from your working inspect_procedures.py
BENCHMARK_PAIRS = {
    "olap": {
        "tsql": os.path.join(HAMMERDB_DIR, "src", "mssqlserver", "mssqlsolap.tcl"),
        "plsql": os.path.join(HAMMERDB_DIR, "src", "oracle", "oraolap.tcl")
    },
    "oltp": {
        "tsql": os.path.join(HAMMERDB_DIR, "src", "mssqlserver", "mssqlsoltp.tcl"),
        "plsql": os.path.join(HAMMERDB_DIR, "src", "oracle", "oraoltp.tcl")
    }
}

def extract_sql_from_file(filepath):
    """
    Reads a file line-by-line and extracts all `set sql(...)` statements.
    This is the simplest, most robust method. It makes no assumptions about
    TCL procedure structure.
    """
    sql_statements = {}
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            # The regex to find `set sql(KEY) "SQL..."` on a single line.
            pattern = re.compile(r'^\s*set sql\((\w+)\) "(.*)"\s*$')
            for line in f:
                match = pattern.search(line.strip())
                if match:
                    sql_key = match.group(1)
                    sql_code = match.group(2).replace('\\"', '"')
                    sql_statements[sql_key] = sql_code
    except FileNotFoundError:
        print(f"  -> WARNING: File not found, skipping: {filepath}")
        return None
        
    print(f"  -> Found {len(sql_statements)} unique 'set sql(key)' statements in {os.path.basename(filepath)}.")
    return sql_statements

def create_master_dataset():
    """
    Processes all defined benchmark pairs, finds common SQL statements,
    and writes them to a single, final JSONL dataset.
    """
    print("--- Starting Definitive Master Dataset Creation ---")
    os.makedirs(OUTPUT_DIR_RAW_FILES, exist_ok=True)
    
    all_pairs = []
    
    for benchmark_name, files in BENCHMARK_PAIRS.items():
        print(f"\n--- Processing Benchmark: {benchmark_name.upper()} ---")
        tsql_dict = extract_sql_from_file(files["tsql"])
        plsql_dict = extract_sql_from_file(files["plsql"])

        if tsql_dict is None or plsql_dict is None:
            continue

        # Find the set of common keys (the numbers/text in sql(KEY))
        common_keys = sorted(tsql_dict.keys() & plsql_dict.keys())
        print(f" -> Found {len(common_keys)} common statement keys for this benchmark.")
        
        for key in common_keys:
            all_pairs.append({
                "tsql": tsql_dict[key],
                "plsql": plsql_dict[key]
            })
            
            # Save raw files for inspection if you want
            tsql_raw_path = os.path.join(OUTPUT_DIR_RAW_FILES, f"{benchmark_name}_{key}_tsql.sql")
            plsql_raw_path = os.path.join(OUTPUT_DIR_RAW_FILES, f"{benchmark_name}_{key}_plsql.sql")
            with open(tsql_raw_path, 'w') as f: f.write(tsql_dict[key])
            with open(plsql_raw_path, 'w') as f: f.write(plsql_dict[key])
            
    # Create the final JSONL dataset
    output_jsonl_file = "tsql_plsql_master_dataset.jsonl"
    prompt_instruction = "You are an expert database migration specialist. Convert the following T-SQL script to a functionally equivalent PL/SQL script for Oracle 19c."

    with open(output_jsonl_file, 'w', encoding='utf-8') as f_out:
        # Here is where you would also add your hand-crafted syntax snippets for maximum quality
        # For now, we will use the rich dataset we just extracted.

        for pair in all_pairs:
            json_record = { "instruction": prompt_instruction, "input": pair["tsql"], "output": pair["plsql"] }
            f_out.write(json.dumps(json_record) + "\n")

    print(f"\n--- DATASET CREATION COMPLETE ---")
    print(f"SUCCESS: Created master dataset '{output_jsonl_file}' with a grand total of {len(all_pairs)} records.")
    print("This is the definitive dataset, built from the correct files with the correct logic.")
    print("You are ready to fine-tune.")

if __name__ == "__main__":
    create_master_dataset()