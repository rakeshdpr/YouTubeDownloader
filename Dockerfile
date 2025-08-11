# Use official Python slim image
FROM python:3.13-slim

# Install ffmpeg and dependencies
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Set working directory inside container
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your entire app code into the container
COPY . .

# Expose port 5000 (Flask default)
EXPOSE 5000

# Command to run your Flask app with gunicorn for production
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
