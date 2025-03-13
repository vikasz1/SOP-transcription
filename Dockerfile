# Use an official Ubuntu runtime as a parent image
FROM ubuntu:20.04

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
# Install pip
RUN apt-get update && apt-get install -y python3-pip

# Install dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg libavcodec-extra && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --no-cache-dir faster-whisper ffmpeg-python python-multipart

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["python", "app.py"]
