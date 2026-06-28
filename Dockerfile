# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir --quiet pytest

# Default command generates the Meridian Advisory intranet to /app/out. Override:
#   docker run --rm -v $(pwd)/out:/app/out <image>                            # bind out/ to host
#   docker run --rm <image> python cli.py validate site-definition.json
#   docker run --rm <image> python cli.py generate examples/site-definition-acme-manufacturing.json --out out
#   docker run --rm <image> python evals/run.py
#   docker run --rm <image> python -m pytest -q
CMD ["python", "run.py"]
