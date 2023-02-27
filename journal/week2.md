# Week 2 — Distributed Tracing

Draft of steps taken with HoneyComb.io

1. created an anvironment for cruddur
2. set HoneyComb API keys as GitPod environment variables: 
```bash
export HONEYCOMB_API_KEY=""
export HONEYCOMB_SERVICE_NAME="Cruddur"
gp env HONEYCOMB_API_KEY=""
gp env HONEYCOMB_SERVICE_NAME="Cruddur"
```
Jessica advised to set honeycomb servoce name in docker compose file instead so service name for multiple services would be different

then these OTEL (open telemetry) variables were added to docker compose for back-end service:
```bash
OTEL_EXPORTER_OTLP_ENDPOINT: "https://api.honeycomb.io"
OTEL_EXPORTER_OTLP_HEADERS: "x-honeycomb-team=${HONEYCOMB_API_KEY}"
OTEL_SERVICE_NAME: "${HONEYCOMB_SERVICE_NAME}"
```
honeycomb is not in our cloud environment, rather our cloud environment sends data to HoneyComb

tagging:
created tag: ```git tag -a week2 -m "my week-2 commits"```
pushed tag: ```git push origin week2```

added these to ```requirements.txt```
```
opentelemetry-api 
opentelemetry-sdk 
opentelemetry-exporter-otlp-proto-http 
opentelemetry-instrumentation-flask 
opentelemetry-instrumentation-requests
```
Added these lines in backend-flask/app.py
```
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
```
```
