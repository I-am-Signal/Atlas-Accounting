FROM python:3.12
WORKDIR /app/
COPY . /app/
RUN python -m pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["python", "main.py"]