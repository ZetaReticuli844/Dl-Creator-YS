package com.dlyog.dl_creator.config;

import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.resources.Resource;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import io.opentelemetry.sdk.trace.export.BatchSpanProcessor;
import io.opentelemetry.exporter.otlp.trace.OtlpGrpcSpanExporter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenTelemetryConfig {

    @Bean
    public OpenTelemetry openTelemetry() {
        Resource resource = Resource.getDefault()
                .merge(Resource.create(
                        io.opentelemetry.api.common.Attributes.of(
                                io.opentelemetry.api.common.AttributeKey.stringKey("service.name"), "dl-creator-backend",
                                io.opentelemetry.api.common.AttributeKey.stringKey("service.version"), "1.0.0",
                                io.opentelemetry.api.common.AttributeKey.stringKey("deployment.environment"), "development"
                        )
                ));
t
        OtlpGrpcSpanExporter spanExporter =
                OtlpGrpcSpanExporter.builder()
                        .setEndpoint("http://localhost:4317")
                        .build();

        SdkTracerProvider tracerProvider = SdkTracerProvider.builder()
                .setResource(resource)
                .addSpanProcessor(BatchSpanProcessor.builder(spanExporter).build())
                .build();

        return OpenTelemetrySdk.builder()
                .setTracerProvider(tracerProvider)
                .buildAndRegisterGlobal();
    }

    @Bean
    public Tracer tracer(OpenTelemetry openTelemetry) {
        // Namespace for your service
        return openTelemetry.getTracer("dl-creator-backend");
    }
}
