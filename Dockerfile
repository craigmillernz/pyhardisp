# Base image
ARG BASE_IMAGE=python:3.11.9-slim

FROM ${BASE_IMAGE} AS build

WORKDIR /app

# Copy local files
#COPY requirements.txt .
COPY pyproject.toml .
COPY . /app

# Install packages
RUN python -m pip install pipx && \
    python -m pipx install coverage==7.5.1

