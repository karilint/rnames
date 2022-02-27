FROM python:3.9-slim AS compile-image

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y build-essential gcc default-libmysqlclient-dev npm curl && \
    useradd -m user

RUN npm install -g n && n 16
USER user

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --user -r requirements.txt

USER root

COPY ./frontend /home/user/frontend
WORKDIR /home/user/frontend
RUN npm ci && npm run build

# ---------------------------------

FROM python:3.9-slim AS build-image

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /src/app

RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev && \
    useradd -m user && \
    mkdir -p /vol/web/static && \
    chown -R user:user /vol && \
    chmod -R 755 /vol/web

USER user

COPY --from=compile-image /home/user/.local /home/user/.local

ENV PATH=/home/user/.local/bin:$PATH

COPY . .

COPY --from=compile-image /home/user/frontend/static /src/app/frontend/static

CMD ["sh", "./scripts/entrypoint.sh"]
