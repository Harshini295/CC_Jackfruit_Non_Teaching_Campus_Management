# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install any needed packages (assuming Flask is used)
RUN pip install --no-cache-dir flask

# Expose the port the app runs on
EXPOSE 5001

# Run the application
CMD ["python", "app.py"]
