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
        Span span = tracer.spanBuilder(traceStuff.value()).startSpan();

        try (var scope = span.makeCurrent()) {
            return pjp.proceed();
        } catch (Throwable t) {
            span.recordException(t);
            span.setAttribute("error", true);
            throw t;
        } finally {
            span.end();
        }
    }
}
