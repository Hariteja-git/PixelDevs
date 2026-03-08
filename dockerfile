FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the project files (server.py, graph.py, static folder, etc.)
COPY . .

# Set the PORT environment variable that Cloud Run looks for
ENV PORT=8080
EXPOSE 8080

# Run the FastAPI app using Uvicorn
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT}"]