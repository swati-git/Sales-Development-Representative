FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./

COPY src/agents/qualification_agent.py ./agents/qualification_agent.py

RUN pip install --no-cache-dir -r requirements.txt

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "/app/agents/qualification_agent.py", "-v"] 