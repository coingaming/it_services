FROM python:3.10-alpine

LABEL maintainer="Vladislav Kislitsyn"

RUN apk update && apk add python3-dev gcc libc-dev g++
RUN pip install --upgrade pip
ARG username=hr_scraper_connector
RUN adduser -D $username
USER $username
WORKDIR /home/$username

ADD --chown=$username:$username requirements.txt requirements.txt
RUN pip install --user -r requirements.txt

ENV PATH="/home/${username}/.local/bin:${PATH}"
ENV BOB_TOKEN=
ENV BOB_SECRET_KEY=
ENV USER_CMDB=
ENV PASS_CMDB=

ENV PYTHONUNBUFFERED=1

ADD --chown=$username:$username . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]