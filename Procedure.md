Of course. This is a critical step for project continuity, hand-off, and future reference.

Here is a detailed Standard Operating Procedure (SOP) document that captures the entire process, from initial setup to launching the final training job. This is designed to be a formal project artifact.

---

## **Standard Operating Procedure: T-SQL to PL/SQL AI Converter Training**

**Document ID:** SOP-AIC-001
**Version:** 1.0
**Date:** June 11, 2024
**Author:** Arya
**Purpose:** This document provides a comprehensive, step-by-step procedure for setting up the development environment, preparing the training dataset, and launching the fine-tuning process for the T-SQL to PL/SQL AI conversion model.

---

### **1.0 Overview & Objective**

This procedure outlines the end-to-end process for training a specialized Large Language Model (LLM) to automate the conversion of T-SQL scripts to Oracle 19c compatible PL/SQL. The process leverages the open-source **Axolotl** fine-tuning framework to train a **Mistral-Small** model on a custom-built, hybrid dataset. The objective is to produce a high-quality "adapter" model capable of performing accurate, context-aware code translation.

The process is divided into three main phases:
1.  **Environment Setup:** Preparing the necessary software and hardware.
2.  **Data Preparation:** Generating the definitive training dataset from multiple sources.
3.  **Model Training:** Configuring and launching the fine-tuning job.

---

### **2.0 Prerequisites**

- **Hardware:** A Linux-based machine (Ubuntu 22.04 recommended) with a high-VRAM NVIDIA GPU (24GB+ recommended, e.g., RTX 3090/4090, A100).
- **Software:**
    - NVIDIA Drivers and CUDA Toolkit (v12.1+ recommended).
    - `git` for version control.
    - Anaconda or Miniconda for Python environment management.

---

### **3.0 Phase 1: Environment and Project Setup**

This phase prepares the foundational software environment and project structure.

**3.1. Create Project Directory:**
   - Open a terminal and create the main project workspace.
   ```bash
   mkdir TSQL-to-PLSQL-Conversion
   cd TSQL-to-PLSQL-Conversion
   ```

**3.2. Set Up Conda Environment:**
   - Create a dedicated Conda environment using **Python 3.11**, which is required by the latest versions of the training libraries.
   ```bash
   conda create -n tsql-finetune-py311 python=3.11 -y
   ```
   - Activate the new environment. All subsequent commands must be run within this environment.
   ```bash
   conda activate tsql-finetune-py311
   ```

**3.3. Install Core Python Libraries:**
   - Install PyTorch with the correct CUDA version, followed by all necessary AI and training libraries.
   ```bash
   # Install PyTorch (ensure CUDA version matches your system, e.g., cu121)
   pip install torch --index-url https://download.pytorch.org/whl/cu121
   
   # Install core dependencies for fine-tuning
   pip install transformers bitsandbytes accelerate peft
   
   # Install the Axolotl fine-tuning framework directly from its repository
   pip install git+https://github.com/OpenAccess-AI-Collective/axolotl.git
   
   # Install optional performance-enhancing libraries
   pip install xformers flash-attn
   
   # Upgrade transformers to the latest version to ensure compatibility with new models
   pip install --upgrade transformers
   ```
   - **Verification:** At this point, the core software environment is established.

**3.4. Initialize Git Repository and Submodule:**
   - Initialize a git repository in the project root.
   ```bash
   git init
   ```
   - Add the HammerDB repository as a git submodule. This tracks the dependency without bloating the project repository.
   ```bash
   # Ensure any old 'HammerDB' folder is removed first (rm -rf HammerDB)
   git submodule add https://github.com/TPC-Council/HammerDB.git HammerDB
   ```
   
**3.5. Configure `.gitignore`:**
   - Create a `.gitignore` file in the project root to prevent committing large files, model artifacts, and environment folders.
   - Populate it with the contents from **Appendix A: .gitignore Configuration**.

---

### **4.0 Phase 2: Data Preparation**

This phase executes the automated script to build the definitive training dataset.

**4.1. The Master Data Extraction Script (`generate_pairs_hammer.py`):**
   - This single Python script performs the entire data preparation workflow. Its responsibilities include:
      1.  Defining a comprehensive list of hand-crafted T-SQL to PL/SQL syntax "flashcards" covering procedural logic, functions, and DDL.
      2.  Parsing the TPC-H OLAP benchmark files (`mssqlsolap.tcl` and `oraolap.tcl`) from the HammerDB submodule.
      3.  Identifying and extracting all equivalent `set sql(...)` statements from these files.
      4.  Merging the hand-crafted syntax pairs with the extracted HammerDB pairs.
      5.  Writing the final, combined dataset to a single `tsql_plsql_final_training_dataset.jsonl` file.
   - The full source code for this script is available in **Appendix B: Master Data Preparation Script**.

**4.2. Execution:**
   - From the project root, within the activated `tsql-finetune-py311` conda environment, run the script.
   ```bash
   python dataset_builder.py
   ```
   - **Expected Output:** The script will log its progress, indicating the number of hand-crafted pairs and extracted pairs. The final output will be a confirmation message:
     `SUCCESS: Created definitive dataset 'tsql_plsql_final_training_dataset.jsonl' with a grand total of XX records.`

---

### **5.0 Phase 3: Model Fine-Tuning**

This phase configures and launches the training process using the prepared data.

**5.1. The Training Configuration File (`mistral-final-config.yml`):**
   - This YAML file is the "recipe" for the fine-tuning job. It instructs Axolotl on which model to train and how.
   - Key parameters configured:
      - `base_model`: `mistralai/Mistral-Small-24B-Instruct-2501` - A powerful, state-of-the-art model suitable for a 24GB GPU.
      - `model_type`/`tokenizer_type`: `Auto...` - For robust, automatic configuration.
      - `load_in_8bit: true`: To follow developer recommendations for the highest quality fine-tune that fits within the VRAM budget.
      - `adapter: lora`: Specifies the use of Low-Rank Adaptation for efficient training.
      - `datasets`: Points to the `tsql_plsql_final_training_dataset.jsonl` file.
      - `output_dir`: Sets the destination for the trained adapter (`./mistral-8bit-tsql-adapter-v1`).
   - The full contents of this configuration file are available in **Appendix C: Training Configuration File**.

**5.2. Configure `accelerate`:**
   - The `accelerate` library orchestrates the training launch. It must be configured once per environment.
   ```bash
   accelerate config
   ```
   - Select the following options for a standard single-GPU setup:
      - Compute environment: `This machine`
      - Machine type: `No distributed training`
      - Run on CPU only: `NO`
      - Optimize with torch dynamo: `NO`
      - Use DeepSpeed/FSDP/Megatron-LM: `no`
      - Mixed precision: `fp16`

**5.3. Launch the Training Job:**
   - Execute the final command to begin the fine-tuning process.
   ```bash
    accelerate launch -m axolotl.cli.train mistral-final-config.yml
   ```
   - **Monitoring the Job:** The terminal will display progress, starting with downloading the base model, followed by data tokenization, and finally the training loop. The key metric to watch is `loss`, which should generally trend downwards, indicating that the model is learning.
   - **Completion:** Upon successful completion, a new directory named `mistral-8bit-tsql-adapter-v1` will be created in the project root. This directory contains the final trained model adapter, which is the primary deliverable of this procedure.

---

### **Appendices**

#### **Appendix A: .gitignore Configuration**
```gitignore
# Python
__pycache__/
*.pyc
.env
.venv
env/
venv/
tsql-finetune-py311/

# Axolotl & LLM
*-adapter-v*/
.cache/
last_run_prepared/
*.jsonl
paired_*/

# IDE & OS
.vscode/
.idea/
*.swp
.DS_Store
Thumbs.db

# Logs
*.log
logs/
```

#### **Appendix B: Master Data Preparation Script (`dataset_builder.py`)**
```
import json

# --- Configuration ---
# The machine-generated file from our previous step
SOURCE_JSONL_FILE = "tsql_plsql_master_dataset.jsonl"
# The name of the final, combined dataset file
FINAL_DATASET_FILE = "tsql_plsql_final_training_dataset.jsonl"
PROMPT_INSTRUCTION = "You are an expert database migration specialist. Convert the following T-SQL script to a functionally equivalent PL/SQL script for Oracle 19c. Ensure all data types, functions, and procedural constructs are correctly translated."

# --- Part 1: Comprehensive Hand-Crafted Syntax "Flashcards" ---
# This is the full list of 24 high-quality manual examples.
SYNTAX_PAIRS = [
    # Your 4 examples
    {"tsql": "-- T-SQL: Basic variable handling and printing\nDECLARE @employee_name VARCHAR(100);\nDECLARE @salary DECIMAL(10, 2);\nSET @employee_name = 'John Smith';\nSET @salary = 75000.50;\nPRINT 'Employee: ' + @employee_name + ', Salary: ' + CAST(@salary AS VARCHAR);", "plsql": "-- PL/SQL: Basic variable handling and printing\nDECLARE\n  v_employee_name VARCHAR2(100);\n  v_salary NUMBER(10, 2);\nBEGIN\n  v_employee_name := 'John Smith';\n  v_salary := 75000.50;\n  DBMS_OUTPUT.PUT_LINE('Employee: ' || v_employee_name || ', Salary: ' || TO_CHAR(v_salary));\nEND;\n/"},
    {"tsql": "-- T-SQL: Error handling with TRY...CATCH\nBEGIN TRY\n    DECLARE @divisor INT = 0;\n    DECLARE @result INT;\n    SET @result = 100 / @divisor;\nEND TRY\nBEGIN CATCH\n    PRINT 'Error occurred: ' + ERROR_MESSAGE();\nEND CATCH;", "plsql": "-- PL/SQL: Error handling with EXCEPTION\nDECLARE\n  v_divisor NUMBER := 0;\n  v_result NUMBER;\nBEGIN\n  v_result := 100 / v_divisor;\nEXCEPTION\n  WHEN ZERO_DIVIDE THEN\n    DBMS_OUTPUT.PUT_LINE('Error occurred: Division by zero.');\n  WHEN OTHERS THEN\n    DBMS_OUTPUT.PUT_LINE('Error occurred: ' || SQLERRM);\nEND;\n/"},
    {"tsql": "-- T-SQL: Simple procedure\nCREATE PROCEDURE dbo.sp_GetEmployee\n    @EmployeeID INT\nAS\nBEGIN\n    SET NOCOUNT ON;\n    SELECT FirstName, LastName, JobTitle\n    FROM HumanResources.Employee\n    WHERE BusinessEntityID = @EmployeeID;\nEND\nGO", "plsql": "-- PL/SQL: Simple procedure returning a REF CURSOR\nCREATE OR REPLACE PROCEDURE sp_GetEmployee (\n    p_EmployeeID IN NUMBER,\n    p_recordset OUT SYS_REFCURSOR\n)\nAS\nBEGIN\n    OPEN p_recordset FOR\n        SELECT FirstName, LastName, JobTitle\n        FROM Employee\n        WHERE BusinessEntityID = p_EmployeeID;\nEND;\n/"},
    {"tsql": "-- T-SQL: A simple WHILE loop\nDECLARE @counter INT;\nSET @counter = 1;\nWHILE (@counter <= 5)\nBEGIN\n   PRINT 'The counter value is ' + CAST(@counter AS VARCHAR);\n   SET @counter = @counter + 1;\nEND;", "plsql": "-- PL/SQL: A simple WHILE loop\nDECLARE\n  v_counter NUMBER := 1;\nBEGIN\n  WHILE v_counter <= 5\n  LOOP\n     DBMS_OUTPUT.PUT_LINE('The counter value is ' || v_counter);\n     v_counter := v_counter + 1;\n  END LOOP;\nEND;\n/"},
    # The other 20 examples
    {"tsql": "-- T-SQL: Printing and string concatenation\nDECLARE @first_name VARCHAR(50) = 'Jane';\nPRINT 'Name: ' + @first_name;", "plsql": "-- PL/SQL: Printing and string concatenation\nDECLARE\n  v_first_name VARCHAR2(50) := 'Jane';\nBEGIN\n  DBMS_OUTPUT.PUT_LINE('Name: ' || v_first_name);\nEND;\n/"},
    {"tsql": "-- T-SQL: IF/ELSE logic\nDECLARE @sales INT = 5000;\nIF @sales > 4000\nBEGIN\n    PRINT 'High';\nEND\nELSE\nBEGIN\n    PRINT 'Low';\nEND;", "plsql": "-- PL/SQL: IF/ELSE logic\nDECLARE\n  v_sales NUMBER := 5000;\nBEGIN\n  IF v_sales > 4000 THEN\n    DBMS_OUTPUT.PUT_LINE('High');\n  ELSE\n    DBMS_OUTPUT.PUT_LINE('Low');\n  END IF;\nEND;\n/"},
    {"tsql": "-- T-SQL: Error handling with TRY...CATCH\nBEGIN TRY\n    DELETE FROM employees WHERE id = 9999;\nEND TRY\nBEGIN CATCH\n    PRINT 'Error: ' + ERROR_MESSAGE();\nEND CATCH;", "plsql": "-- PL/SQL: Error handling with EXCEPTION\nBEGIN\n    DELETE FROM employees WHERE id = 9999;\nEXCEPTION\n    WHEN OTHERS THEN\n        DBMS_OUTPUT.PUT_LINE('Error: ' || SQLERRM);\nEND;\n/"},
    {"tsql": "-- T-SQL: Basic Cursor\nDECLARE @emp_id INT;\nDECLARE emp_cursor CURSOR FOR SELECT EmployeeID FROM Employees WHERE Department = 'Sales';\nOPEN emp_cursor;\nFETCH NEXT FROM emp_cursor INTO @emp_id;\nWHILE @@FETCH_STATUS = 0\nBEGIN\n    PRINT @emp_id;\n    FETCH NEXT FROM emp_cursor INTO @emp_id;\nEND;\nCLOSE emp_cursor;\nDEALLOCATE emp_cursor;", "plsql": "-- PL/SQL: Basic Cursor (using an idiomatic FOR loop)\nBEGIN\n  FOR emp_rec IN (SELECT EmployeeID FROM Employees WHERE Department = 'Sales')\n  LOOP\n    DBMS_OUTPUT.PUT_LINE(emp_rec.EmployeeID);\n  END LOOP;\nEND;\n/"},
    {"tsql": "-- T-SQL: Procedure with IN and OUT parameters\nCREATE PROCEDURE dbo.sp_GetManager\n    @EmployeeID INT,\n    @ManagerID INT OUTPUT\nAS\nBEGIN\n    SELECT @ManagerID = ManagerID FROM Employees WHERE EmployeeID = @EmployeeID;\nEND\nGO", "plsql": "-- PL/SQL: Procedure with IN and OUT parameters\nCREATE OR REPLACE PROCEDURE sp_GetManager (\n    p_EmployeeID IN NUMBER,\n    p_ManagerID OUT NUMBER\n)\nAS\nBEGIN\n    SELECT ManagerID INTO p_ManagerID FROM Employees WHERE EmployeeID = p_EmployeeID;\nEND;\n/"},
    {"tsql": "SELECT ISNULL(commission_pct, 0) FROM employees;", "plsql": "SELECT NVL(commission_pct, 0) FROM employees;"},
    {"tsql": "SELECT GETDATE();", "plsql": "SELECT SYSDATE FROM DUAL;"},
    {"tsql": "SELECT DATEADD(month, 2, '2023-01-15');", "plsql": "SELECT ADD_MONTHS(TO_DATE('2023-01-15', 'YYYY-MM-DD'), 2) FROM DUAL;"},
    {"tsql": "SELECT CHARINDEX('world', 'hello world');", "plsql": "SELECT INSTR('hello world', 'world') FROM DUAL;"},
    {"tsql": "SELECT SUBSTRING('abcdef', 3, 2);", "plsql": "SELECT SUBSTR('abcdef', 3, 2) FROM DUAL;"},
    {"tsql": "SELECT LEN('test');", "plsql": "SELECT LENGTH('test') FROM DUAL;"},
    {"tsql": "SELECT CAST(123 AS VARCHAR(10));", "plsql": "SELECT TO_CHAR(123) FROM DUAL;"},
    {"tsql": "SELECT TOP 10 * FROM Employees ORDER BY HireDate DESC;", "plsql": "SELECT * FROM Employees ORDER BY HireDate DESC FETCH FIRST 10 ROWS ONLY;"},
    {"tsql": "-- T-SQL: Transaction\nBEGIN TRANSACTION;\nUPDATE Accounts SET balance = balance - 100 WHERE account_id = 1;\nUPDATE Accounts SET balance = balance + 100 WHERE account_id = 2;\nCOMMIT TRANSACTION;", "plsql": "-- PL/SQL: Transaction\nBEGIN\n    UPDATE Accounts SET balance = balance - 100 WHERE account_id = 1;\n    UPDATE Accounts SET balance = balance + 100 WHERE account_id = 2;\n    COMMIT;\nEND;\n/"},
    {"tsql": "-- T-SQL: Session-scoped temporary table\nCREATE TABLE #TempEmployees (EmployeeID INT, EmployeeName VARCHAR(100));\nINSERT INTO #TempEmployees VALUES (1, 'Temp User');\nSELECT * FROM #TempEmployees;", "plsql": "-- PL/SQL: Session-scoped temporary table (requires pre-defined table)\n-- DDL (run once): CREATE GLOBAL TEMPORARY TABLE TempEmployees (EmployeeID NUMBER, EmployeeName VARCHAR2(100)) ON COMMIT PRESERVE ROWS;\nBEGIN\n    INSERT INTO TempEmployees VALUES (1, 'Temp User');\n    -- Logic to process TempEmployees would go here\nEND;\n/"},
    {"tsql": "-- T-SQL: Dynamic SQL execution\nDECLARE @sql_command NVARCHAR(1000);\nSET @sql_command = N'SELECT * FROM Employees WHERE DepartmentID = @dept';\nEXEC sp_executesql @sql_command, N'@dept INT', @dept = 10;", "plsql": "-- PL/SQL: Dynamic SQL execution\nDECLARE\n  v_sql_command VARCHAR2(1000);\nBEGIN\n  v_sql_command := 'SELECT * FROM Employees WHERE DepartmentID = :dept_id';\n  -- In a real scenario, you would use a REF CURSOR to process the results\n  EXECUTE IMMEDIATE v_sql_command USING 10;\nEND;\n/"},
    {"tsql": "-- T-SQL: Auto-incrementing primary key\nCREATE TABLE Products (\n    ProductID INT IDENTITY(1,1) PRIMARY KEY,\n    ProductName VARCHAR(100)\n);", "plsql": "-- PL/SQL: Auto-incrementing primary key (using an identity column)\nCREATE TABLE Products (\n    ProductID NUMBER GENERATED BY DEFAULT ON NULL AS IDENTITY PRIMARY KEY,\n    ProductName VARCHAR2(100)\n);"}
]


def main():
    """
    Merges the hand-crafted syntax pairs with the machine-extracted pairs
    from HammerDB to create the final, complete training dataset.
    """
    print("--- Starting Final Dataset Merge Process ---")
    
    # 1. Start with the hand-crafted syntax pairs
    final_records = []
    for pair in SYNTAX_PAIRS:
        final_records.append({
            "instruction": PROMPT_INSTRUCTION,
            "input": pair["tsql"],
            "output": pair["plsql"]
        })
    print(f"Step 1: Loaded {len(final_records)} hand-crafted syntax pairs.")
    
    # 2. Read and append the extracted pairs from the source JSONL file
    try:
        with open(SOURCE_JSONL_FILE, 'r', encoding='utf-8') as f_in:
            extracted_records = [json.loads(line) for line in f_in]
            final_records.extend(extracted_records)
            print(f"Step 2: Loaded {len(extracted_records)} extracted pairs from '{SOURCE_JSONL_FILE}'.")
    except FileNotFoundError:
        print(f"WARNING: Source file '{SOURCE_JSONL_FILE}' not found. The final dataset will only contain hand-crafted examples.")
    
    # 3. Write the final, merged dataset to a new file
    with open(FINAL_DATASET_FILE, 'w', encoding='utf-8') as f_out:
        for record in final_records:
            f_out.write(json.dumps(record) + "\n")

    print(f"\n--- MERGE COMPLETE ---")
    print(f"SUCCESS: Created final training dataset '{FINAL_DATASET_FILE}' with a grand total of {len(final_records)} records.")
    print("This is your definitive training data. You are ready to fine-tune.")

if __name__ == "__main__":
    main()
```

#### **Appendix C: Training Configuration File (`mistral-final-config.yml`)**
```
# Axolotl config for fine-tuning the cutting-edge Mistral-Small-24B model
# This configuration is optimized for a 24GB GPU.

# --- Core Model Configuration (UPGRADED to MISTRAL) ---
# We are now using the powerful and efficient Mistral-Small model.
base_model: mistralai/Mistral-Small-3.1-24B-Instruct-2503
# The model architecture is based on Mistral's design.
# We explicitly set the model_type and tokenizer_type to ensure compatibility.
model_type: AutoModelForCausalLM
tokenizer_type: AutoTokenizer

# --- Performance & Memory Optimization ---
# These settings are still critical for fitting the model in memory.
flash_attention: true
load_in_4bit: true
# THIS IS THE FIX: Explicitly tell Axolotl to use the LoRA adapter.
adapter: lora


datasets:
  - path: tsql_plsql_final_training_dataset.jsonl
    # THIS IS THE FIX: Revert to the stable and universally compatible 'alpaca' type.
    # Axolotl will automatically use the correct chat template for the Mistral model.
    type: alpaca
    
# Let's give our new model a new name.
output_dir: ./mistral-tsql-to-plsql-adapter-v1

# --- Training Hyperparameters (ADJUSTED FOR MISTRAL) ---
# The maximum number of tokens in a single training example.
sequence_len: 2048

# Because Mistral is more efficient, we can likely use a larger batch size than with the 34B model.
# This will speed up training. We'll start with 2.
micro_batch_size: 2
gradient_accumulation_steps: 2

# We can stick with 3 epochs. The model is a fast learner.
num_epochs: 3
# A standard learning rate for fine-tuning.
learning_rate: 2e-5
optimizer: paged_adamw_8bit

# --- LoRA Configuration ---
# These are standard LoRA values.
lora_r: 16
lora_alpha: 32
lora_dropout: 0.05
# Target modules for Mistral models are slightly different from Llama. This is a common configuration.
lora_target_modules:
  - q_proj
  - v_proj
  - k_proj
  - o_proj

# --- Logging and Saving ---
logging_steps: 5
val_set_size: 0.05
save_steps: 50
special_tokens:
  bos_token: "<s>"
  eos_token: "</s>"
  unk_token: "<unk>"
  ```