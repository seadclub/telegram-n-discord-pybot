FROM python:3.8
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
# make port 80 available to the world outside this container!!!
EXPOSE 80
ENV NAME seadman
CMD ["python", "src/main.py"]
