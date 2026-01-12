# ADR 002: Event-Driven Architecture with Event Bus

## Status
Accepted

## Context
Modules and components need to communicate without tight coupling. We require:
- Loose coupling between modules
- Asynchronous processing capabilities
- Audit trail of system events
- Integration with external systems via webhooks

## Decision
Implement an internal event bus using pub/sub pattern:
- Central event bus for all platform communication
- Standard event types with extensibility
- Event logging for audit and replay
- Webhook dispatcher for external integrations
- Support for both sync and async handlers

## Consequences

### Positive
- **Loose coupling**: Modules don't need direct references
- **Scalability**: Easy to add new event subscribers
- **Observability**: All events are logged
- **Replay**: Can replay events for debugging/recovery
- **Integration**: Webhooks enable external system integration

### Negative
- **Debugging**: Event-driven code can be harder to trace
- **Performance**: Event overhead for simple operations
- **Complexity**: Asynchronous programming patterns

## Implementation
- Event bus in `core/event_bus/`
- Standard event types enumeration
- Event data structure with metadata
- Publisher/subscriber registration
- Webhook handlers

## Alternatives Considered
1. **Direct method calls**: Tight coupling - rejected
2. **Message queue (RabbitMQ/Kafka)**: Too heavy - may add later
3. **No events**: Simple but inflexible - rejected
