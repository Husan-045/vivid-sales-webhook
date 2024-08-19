FROM public.ecr.aws/lambda/python:3.10

## Set environment varibles
ARG SRC
RUN test -n "SRC" || (echo "SRC not set" >&2 && exit 1)
ENV SRC=${SRC}

# Copy function code
COPY ${SRC}/ ${LAMBDA_TASK_ROOT}/${SRC}

## Install python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}" --no-cache-dir

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.api.vivid_webhook.vivid_webhook" ]
