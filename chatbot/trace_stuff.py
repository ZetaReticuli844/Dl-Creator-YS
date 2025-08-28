import os
from functools import wraps
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor

def configure_opentelemetry():
    """Configure OpenTelemetry with OTLP exporter."""
    # Set up resource with service information
    resource = Resource.create({
        "service.name": "chatbot-rasa",
        "service.version": "1.0.0",
        "service.instance.id": os.getenv("HOSTNAME", "localhost"),
    })
    
    # Create tracer provider
    trace.set_tracer_provider(TracerProvider(resource=resource))
    
    # Configure OTLP exporter for port 4317 (gRPC)
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
        insecure=True,  # Use this for local development
    )
    
    # Add span processor
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # Auto-instrument requests library
    RequestsInstrumentor().instrument()
    
    print("✅ OpenTelemetry configured successfully for endpoint:", 
          os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"))

# Initialize OpenTelemetry when module is imported
configure_opentelemetry()

# Get tracer instance
tracer = trace.get_tracer(__name__)

def trace_stuff(span_name):
    """Custom decorator to trace a function with given span name."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator
