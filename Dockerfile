FROM odoo:19.0

# Install build dependencies for additional Python requirements
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Placeholder for extra Python requirements
# COPY requirements.txt /tmp/requirements.txt
# RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

USER odoo
WORKDIR /var/lib/odoo
