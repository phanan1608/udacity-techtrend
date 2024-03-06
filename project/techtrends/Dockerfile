# Use Python 3.8 base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Expose the port the app runs on
EXPOSE 3111

# Run init_db.py to initialize the database with pre-defined posts
RUN python init_db.py

# Command to run the application
CMD ["python", "app.py"]
