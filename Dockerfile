FROM python:3.11-slim

# Create a non-root user for Hugging Face Spaces
RUN useradd -m -u 1000 user

WORKDIR /app

# Install dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code with correct ownership
COPY --chown=user . .

# Set environment variables
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Expose the default Hugging Face port
EXPOSE 7860

# Switch to the non-root user
USER user

# Run the application using the HF default port
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
