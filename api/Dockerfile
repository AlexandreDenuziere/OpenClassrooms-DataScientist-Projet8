FROM python:3

WORKDIR /api

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD [ "python", "./api.py" ]
