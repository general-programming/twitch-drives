# Stage 0: Build the frontend.
FROM node:current-alpine AS frontend_build

WORKDIR /app

# Install node modules first from package.json.
COPY frontend_overlay/package.json .
RUN yarn install

# https://github.com/webpack/webpack/issues/14532#issuecomment-947012063
ENV NODE_OPTIONS --openssl-legacy-provider

# Copy frontend and build it.
COPY frontend_overlay/ .
RUN yarn run build

# Stage 1: Build python service.
FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt .
RUN apk add --no-cache libffi && \
    apk add --no-cache --virtual build build-base libffi-dev && \
    pip install -r requirements.txt && \
    apk del build

# XXX: uh
COPY . .
RUN python setup.py install
COPY --from=0 /app/build/static service_overlay/static/
COPY --from=0 /app/build/index.html service_overlay/
