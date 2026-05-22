# Use the official Streamlit Docker image as a base
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit app and other necessary files
COPY . .

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_PORT=7860
EXPOSE 7860

# Command to run the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]
