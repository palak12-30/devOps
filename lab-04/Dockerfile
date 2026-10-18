FROM python:3.12-slim
WORKDIR /app
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get -o Acquire::Retries=2 -o Acquire::https::Timeout=20 -o APT::Update::Error-Mode=any update \
    && apt-get -o Acquire::Retries=2 -o Acquire::https::Timeout=20 install -y --no-install-recommends iputils-ping \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5001
CMD ["python", "app.py"]
