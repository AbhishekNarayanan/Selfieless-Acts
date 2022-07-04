FROM jfloff/alpine-python:3.4-onbuild


ENV TEAM_ID CC_016_017_019_022

RUN mkdir -p /app
COPY . /app
WORKDIR /app
# Install any needed packages specified in requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip3 install -r requirements.txt

# Run app.py when the container launches
EXPOSE 80
CMD  python acts.py
