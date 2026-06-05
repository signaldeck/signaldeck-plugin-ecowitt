FROM signaldeck:dev

RUN pip install --no-cache-dir \
    "git+https://github.com/signaldeck/signaldeck-plugin-sqlite.git@v1.0.beta.2"