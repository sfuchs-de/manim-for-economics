FROM python:3.12.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/econ-manim-venv \
    PATH="/opt/econ-manim-venv/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        dvisvgm \
        ffmpeg \
        fontconfig \
        fonts-dejavu-core \
        libcairo2-dev \
        libpango1.0-dev \
        pkg-config \
        texlive-fonts-recommended \
        texlive-latex-base \
        texlive-latex-extra \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --no-cache-dir uv==0.10.2

WORKDIR /workspace
COPY . /workspace
RUN uv sync --frozen

CMD ["bash"]
