FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync --no-dev
ENV GEMINI_API_KEY=""
ENV PORT=8080
EXPOSE 8080
CMD ["uv", "run", "python", "-m", "app.mcp_server"]
