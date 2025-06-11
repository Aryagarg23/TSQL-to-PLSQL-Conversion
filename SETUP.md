# 1. Create a new conda environment
conda create -n tsql-finetune python=3.10 -y

# 2. Activate the environment
conda activate tsql-finetune

# 3. Install PyTorch with CUDA support (THIS IS CRITICAL)
# Make sure your CUDA version matches. Check the PyTorch website for the correct command if needed.
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 4. Install the core libraries for fine-tuning
pip install transformers bitsandbytes accelerate peft

# 5. Install Axolotl, our fine-tuning framework, directly from GitHub
pip install git+https://github.com/OpenAccess-AI-Collective/axolotl.git

# 6. Install optional but recommended performance boosters
pip install xformers flash-attn