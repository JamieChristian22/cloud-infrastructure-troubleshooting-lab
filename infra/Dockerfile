FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir . && \
    useradd --system --uid 10001 --create-home labuser && \
    mkdir -p /app/.lab && chown labuser:labuser /app/.lab
USER labuser
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=4s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health/ready',timeout=2)" || exit 1
CMD ["python", "-m", "cloudops_lab", "serve", "--bind", "0.0.0.0", "--allow-non-loopback", "--port", "8080"]
