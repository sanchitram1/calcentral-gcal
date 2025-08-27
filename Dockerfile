# Start from a uv base image
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Get the same dependencies as the nix config for replit 
# (Would be great if this was pkgx, not apt-get)
RUN apt-get update && apt-get install -y \
    libfreetype6 \
    liblcms2-2 \
    libgl1 \
    libglu1-mesa \
    libimagequant0 \
    libjpeg62-turbo \
    libtiff6 \
    libwebp7 \
    tcl \
    tesseract-ocr \
    tk \
    zlib1g \
    # Clean up the package manager cache to keep the image small
    && rm -rf /var/lib/apt/lists/*

# Set working directory as the /app folder
WORKDIR /app

# Get the requirements from pyproject.toml
COPY pyproject.toml .
RUN uv pip sync pyproject.toml

COPY . . 
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
