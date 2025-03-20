FROM python:3.10-slim

# Install Poetry
RUN pip install poetry

WORKDIR /app

# Copy poetry configuration files
COPY pyproject.toml ./

# Install dependencies without creating a virtual environment
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copy the application code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
