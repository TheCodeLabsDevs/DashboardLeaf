FROM python:3.14-alpine AS poetry

RUN apk update && apk upgrade && \
    apk add curl gcc python3-dev libc-dev build-base linux-headers && \
    rm -rf /var/cache/apk
RUN curl https://install.python-poetry.org | python -

COPY pyproject.toml /opt/DashboardLeaf/pyproject.toml
COPY poetry.lock /opt/DashboardLeaf/poetry.lock
COPY dashboard_leaf/ /opt/DashboardLeaf/dashboard_leaf

WORKDIR /opt/DashboardLeaf
RUN /root/.local/bin/poetry install
RUN ln -s $($HOME/.local/share/pypoetry/venv/bin/poetry env info -p) /opt/DashboardLeaf/venv

FROM python:3.14-alpine

RUN apk update && apk upgrade && \
    apk add libstdc++ && \
    rm -rf /var/cache/apk

COPY dashboard_leaf/ /opt/DashboardLeaf/dashboard_leaf
COPY --from=poetry /opt/DashboardLeaf/venv /opt/DashboardLeaf/venv

RUN adduser -D DashboardLeaf && chown -R DashboardLeaf:DashboardLeaf /opt/DashboardLeaf
USER DashboardLeaf

WORKDIR /opt/DashboardLeaf/dashboard_leaf
EXPOSE 10002
CMD [ "/opt/DashboardLeaf/venv/bin/python", "/opt/DashboardLeaf/dashboard_leaf/DashboardLeaf.py"]
