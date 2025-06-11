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

**4.1. The Master Data Extraction Script (`build_definitive_dataset.py`):**
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
   python build_final_dataset.py
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

#### **Appendix B: Master Data Preparation Script (`build_final_dataset.py`)**
*(Contents of the final script from the previous step would be pasted here.)*

#### **Appendix C: Training Configuration File (`mistral-final-config.yml`)**
*(Contents of the final 8-bit YAML configuration from the previous step would be pasted here.)*