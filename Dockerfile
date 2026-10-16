FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project code
COPY . /app/

# Expose port
EXPOSE 8000

# Start Gunicorn server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "healthcare_project.wsgi:application"]
