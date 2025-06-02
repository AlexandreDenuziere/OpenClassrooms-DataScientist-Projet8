FROM python:3

WORKDIR /dashboard

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8502

CMD [ "streamlit", "run", "dashboard.py", "--server.port=8502", "--server.address=0.0.0.0" ]
