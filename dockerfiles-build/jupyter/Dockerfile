# Build stage
FROM python:3.10-slim AS pre-build

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org --upgrade pip setuptools wheel && \
    pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org yapf jupyterlab jupyter_contrib_nbextensions jupyterthemes && \
    jupyter contrib nbextension install --user && \
    rm -rf /root/.cache/pip

COPY requirements.txt .

RUN ls -lha ; pwd ; pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org -r requirements.txt && \
    rm -rf /root/.cache/pip

# Final build stage
FROM python:3.10-slim

COPY --from=pre-build /root/.local /root/.local
COPY --from=pre-build /usr/local /usr/local

# Jupyter extensions configuration
RUN jupyter nbextension enable scratchpad/main --sys-prefix && \
    jupyter nbextension enable zenmode/main --sys-prefix && \
    jupyter nbextension enable varInspector/main --sys-prefix && \
    jupyter nbextension enable code_prettify/code_prettify --sys-prefix && \
    jupyter nbextension enable livemdpreview/livemdpreview --sys-prefix && \
    jupyter nbextension enable snippets_menu/main --sys-prefix && \
    jupyter nbextension enable snippets/main --sys-prefix && \
    jupyter nbextension enable hinterland/hinterland --sys-prefix && \
    jupyter nbextension enable execute_time/ExecuteTime --sys-prefix

WORKDIR /lab

EXPOSE 8888

ENTRYPOINT ["jupyter", "notebook", "--allow-root", "--ip", "0.0.0.0"]
