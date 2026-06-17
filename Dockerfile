# Stage 1: Build the frontend
FROM node:18-slim AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build the backend
FROM python:3.11-slim

# Create a non-root user for Hugging Face Spaces
RUN useradd -m -u 1000 user

WORKDIR /app

# Install Python dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code and frontend source (for structure)
COPY --chown=user . .

# Copy built frontend from Stage 1 into the correct location
COPY --chown=user --from=frontend-builder /frontend/dist ./frontend/dist

# Set environment variables
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Expose the default Hugging Face port
EXPOSE 7860

# Switch to the non-root user
USER user

# Run the application using the HF default port
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
