package com.dlyog.dl_creator.Tracing;


import com.dlyog.dl_creator.TraceStuff;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.weaver.tools.Traceable;
import org.springframework.stereotype.Component;

@Aspect
@Component
public class TracingAspect {

    private final Tracer tracer;

    // Constructor injection for the OpenTelemetry tracer
    public TracingAspect(Tracer tracer) {
        this.tracer = tracer;
    }

    @Around("@annotation(traceStuff)")
    public Object traceMethod(ProceedingJoinPoint pjp, TraceStuff traceStuff) throws Throwable {
        // Create a span with the name provided in the annotation
        Span span = tracer.spanBuilder(traceStuff.value()).startSpan();

        try (var scope = span.makeCurrent()) {
            // Proceed with the original method execution
            return pjp.proceed();
        } catch (Throwable t) {
            // Record exception into the span
            span.recordException(t);
            span.setAttribute("error", true);
            throw t;
        } finally {
            // End the span
            span.end();
        }
    }
}
