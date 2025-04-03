FROM mambaorg/micromamba:1.5.8

# https://micromamba-docker.readthedocs.io/en/latest/quick_start.html
COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/env.yaml
RUN micromamba install -y -n base -f /tmp/env.yaml && \
    micromamba clean --all --yes

COPY src/dat_backend/ ./dat_backend/
COPY test/ ./test/
COPY pyproject.toml .

RUN mkdir -p /tmp/ssl && /opt/conda/bin/openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /tmp/ssl/dat.key -out /tmp/ssl/dat.crt -subj "/CN=nsidc"

EXPOSE 5000

CMD /bin/bash -c "gunicorn --certfile=/tmp/ssl/dat.crt --keyfile=/tmp/ssl/dat.key --bind 0.0.0.0:5000 --workers 9 dat_backend:app"
