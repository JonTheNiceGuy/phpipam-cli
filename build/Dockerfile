FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN useradd --home-dir /app --create-home --shell /bin/bash ipam

WORKDIR /app

COPY --chown=ipam pyproject.toml uv.lock ./

USER ipam
RUN uv sync --frozen --no-dev --no-install-project

COPY --chown=ipam src/ src/
RUN uv sync --frozen --no-dev

ENTRYPOINT ["uv", "run", "--no-sync", "ipam"]
