FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN useradd --create-home --shell /bin/bash ipam

WORKDIR /app

COPY --chown=ipam pyproject.toml uv.lock ./

USER ipam
RUN uv sync --frozen --no-dev

COPY --chown=ipam src/ src/

ENTRYPOINT ["uv", "run", "ipam"]
