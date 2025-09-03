package com.dlyog.dl_creator.Tracing;

import com.dlyog.dl_creator.TraceStuff;
import io.opentelemetry.api.GlobalOpenTelemetry;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.springframework.stereotype.Component;

@Aspect
@Component
public class TracingAspect {
    private final Tracer tracer = GlobalOpenTelemetry
            .getTracer("dl-creator-backend");

    @Around("@annotation(traceStuff)")
    public Object traceMethod(ProceedingJoinPoint pjp, TraceStuff traceStuff) throws Throwable {
        // Use the annotation value as span name, fallback to method name if empty
        String spanName = traceStuff.value().isEmpty() 
            ? pjp.getSignature().getName() 
            : traceStuff.value();
            
        Span span = tracer.spanBuilder(spanName)
                .setAttribute("method.name", pjp.getSignature().getName())
                .setAttribute("class.name", pjp.getTarget().getClass().getSimpleName())
                .startSpan();

        try (var scope = span.makeCurrent()) {
            return pjp.proceed();
        } catch (Throwable t) {
            span.recordException(t);
            span.setAttribute("error", true);
            span.setAttribute("error.message", t.getMessage());
            throw t;
        } finally {
            span.end();
        }
    }
}
