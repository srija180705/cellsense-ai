# CellSense AI - backend image
FROM python:3.11-slim

WORKDIR /app

# System deps for scientific Python wheels are already covered by manylinux wheels,
# so we only need pip installs.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (datasets & artifacts are mounted at runtime, see compose)
COPY . .

EXPOSE 8000

ENTRYPOINT ["bash", "deployment/entrypoint.sh"]
