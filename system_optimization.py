# Run these commands in terminal before starting server

# Create swap file
sudo fallocate -l 16G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Install ROCm dependencies
sudo apt install -y libnuma-dev rocm-dev

# Install optimized Python packages
pip install llama-cpp-python \
  --extra-index-url https://repo.radeon.com/rocm/manylinux/rocm-rel-5.6

# Download model (run in models/ directory)
wget https://huggingface.co/microsoft/phi-3-mini-128k-instruct-gguf/resolve/main/phi-3-mini-128k-instruct.Q4_K_M.gguf
