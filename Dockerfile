# Use an official Ubuntu image
FROM ubuntu:22.04

# Update and install Python and FFmpeg
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Whisper
RUN pip3 install openai-whisper moviepy

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the FastAPI app files
COPY . .

# Expose the FastAPI default port
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
