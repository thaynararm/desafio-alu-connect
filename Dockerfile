FROM python:3.12-slim
WORKDIR /app



COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY setup/ .

EXPOSE 8000

CMD ["gunicorn", "setup.wsgi:application", "--bind", "0.0.0.0:8000"]
