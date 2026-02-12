FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

# Ejecuta pipeline por defecto; para dashboard:
# docker run -p 8501:8501 <image> streamlit run apps/dashboard/app.py --server.address=0.0.0.0
CMD ["python", "-m", "src.pipeline.run_all", "--seed", "42", "--forecast-horizon", "6", "--top-ingredients", "12", "--run-id", "2026-02-11"]
