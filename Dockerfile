FROM python:3.8-slim as base
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

#####################################
#    POLLING SERVICE ENVIRONMENT    #
#####################################

FROM base AS polling-base
COPY ./polling_service/requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY ./polling_service/api_poller ./api_poller

#####################################
#    BACKEND SERVICE ENVIRONMENT    #
#####################################

FROM base AS backend-base
COPY ./backend_service/requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY ./backend_service/app ./app