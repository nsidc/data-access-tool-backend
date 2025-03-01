FROM mambaorg/micromamba:1.5.8

# https://micromamba-docker.readthedocs.io/en/latest/quick_start.html
COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/env.yaml
RUN micromamba install -y -n base -f /tmp/env.yaml && \
    micromamba clean --all --yes

COPY src/* .

EXPOSE 5000

# TODO: handle ssl w/ gunicorn? Self-signed cert on this image easiest?
# CMD /bin/bash -c "gunicorn --bind 0.0.0.0:5000 --workers 3 app:app"

# TODO this might not work
CMD /bin/bash -c "PYTHONPATH=./ python dat_backend/app.py"
