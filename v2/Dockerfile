FROM python:3.11-slim
RUN apt-get update &&     apt-get install -y ffmpeg inotify-tools &&     apt-get clean
WORKDIR /app
COPY app/requirements.txt ./
RUN pip install -r requirements.txt
COPY app/ /app/
COPY vast/ /vast/
CMD ["python3", "playout.py"]