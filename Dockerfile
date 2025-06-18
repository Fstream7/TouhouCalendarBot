FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache tzdata

RUN pip3 install --no-cache-dir -r requirements.txt

COPY days days
COPY post_calendar.py .
COPY touhou_calendar.py .

CMD ["python3", "post_calendar.py", "--twitter"]