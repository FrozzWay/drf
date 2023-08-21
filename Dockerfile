FROM python:3.9-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY core ./core
COPY referral_app ./referral_app
COPY manage.py .
COPY wait_for .
CMD ["sleep","3600"]