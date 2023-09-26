import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def initialize():
    resource = Resource(attributes={
        "service.name": os.environ.get("OTEL_SERVICE_NAME", "unknown_service")
    })
    provider = TracerProvider(resource=resource)
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
        insecure=bool(os.environ.get("OTEL_EXPORTER_OTLP_INSECURE", False)),
    )
    processor = BatchSpanProcessor(otlp_exporter)  # ConsoleSpanExporter()
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
