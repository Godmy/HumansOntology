# Implement Redis Service-Level Caching for Frequently Accessed Data

## 📖 Context

Currently, the application has HTTP-level caching (Cache-Control, ETag) but lacks **application-level caching** at the service layer. Many database queries fetch rarely-changed data (e.g., languages list, concept hierarchy) on every request, creating unnecessary database load.

This task implements a **Redis-based caching decorator** for service methods to cache expensive or frequently accessed queries.

## 🎯 Objectives

1. Create a reusable `@cached` decorator for service methods
2. Implement cache invalidation strategies (TTL, manual invalidation)
3. Cache the following data:
   - List of all languages (`languages/services/language_service.py`)
   - Concept tree/hierarchy (`languages/services/concept_service.py`)
4. Add cache hit/miss metrics for Prometheus
5. Provide clear cache management utilities (clear, invalidate by pattern)

## ✅ Acceptance Criteria

### Core Functionality

- [ ] **Decorator implemented**: `@cached(key_prefix="...", ttl=300)` decorator works on async service methods
- [ ] **Automatic key generation**: Cache keys are auto-generated from function name and arguments
- [ ] **TTL support**: Cache entries expire after configured TTL
- [ ] **JSON serialization**: Complex objects (Pydantic models, SQLAlchemy models) are properly serialized
- [ ] **Cache invalidation**: Provide `invalidate_cache(pattern)` function to clear specific cache entries
- [ ] **Fallback on Redis failure**: If Redis is unavailable, functions execute normally without caching (graceful degradation)

### Specific Implementations

- [ ] **Languages caching**: `language_service.get_all_languages()` is cached with 1-hour TTL
- [ ] **Concept tree caching**: `concept_service.get_concept_tree()` is cached with 5-minute TTL
- [ ] **Cache invalidation on mutation**: When a language/concept is created/updated/deleted, relevant cache is invalidated

### Observability

- [ ] **Prometheus metrics**: Add counters for cache hits, misses, and errors
  ```python
  service_cache_hits_total{service="language", method="get_all_languages"}
  service_cache_misses_total{service="language", method="get_all_languages"}
  service_cache_errors_total{service="language", method="get_all_languages"}
  ```
- [ ] **Structured logs**: Log cache hit/miss events with relevant context
- [ ] **Health check**: Add cache health status to `/health/detailed` endpoint

### Testing

- [ ] **Unit tests**: Test decorator with different TTL values, key generation, serialization
- [ ] **Integration tests**: Test actual caching behavior with Redis
- [ ] **Cache invalidation tests**: Verify cache is cleared when data changes
- [ ] **Redis failure tests**: Verify graceful fallback when Redis is down
- [ ] **Performance test**: Demonstrate measurable performance improvement (e.g., response time reduced by 50%+)

## 🛠 Technical Requirements

### File Structure

```
core/
├── decorators/
│   ├── __init__.py
│   └── cache.py           # @cached decorator implementation
└── services/
    └── cache_service.py   # Cache management utilities

languages/
└── services/
    ├── language_service.py  # Add @cached to get_all_languages()
    └── concept_service.py   # Add @cached to get_concept_tree()

tests/
└── test_service_cache.py  # Comprehensive test suite
```

### Implementation Details

**1. Cache Key Format**
```
cache:{service}:{method}:{args_hash}
Example: cache:language:get_all_languages:d41d8cd98f00b204
```

**2. Decorator Signature**
```python
@cached(
    key_prefix: str,           # Prefix for cache key (e.g., "language:list")
    ttl: int = 300,            # Time-to-live in seconds
    cache_none: bool = False,  # Whether to cache None results
    key_builder: Optional[Callable] = None  # Custom key generation function
)
```

**3. Cache Invalidation**
```python
# Invalidate specific key
await invalidate_cache("cache:language:get_all_languages:*")

# Invalidate all language cache
await invalidate_cache("cache:language:*")

# Clear all cache
await clear_all_cache()
```

**4. Serialization**
- Use `pydantic.BaseModel.model_dump_json()` for Pydantic models
- Use custom serializer for SQLAlchemy models
- Support nested objects and lists

### Configuration (Environment Variables)

Add to `.env` and `.env.example`:

```env
# Enable/disable service-level caching
SERVICE_CACHE_ENABLED=true

# Default TTL for cached items (seconds)
SERVICE_CACHE_DEFAULT_TTL=300

# Maximum number of cached keys (prevent memory bloat)
SERVICE_CACHE_MAX_KEYS=10000
```

## 📊 Success Metrics

After implementation, the following should be measurable:

1. **Performance**:
   - `get_all_languages()` response time: < 5ms (cached) vs ~50ms (uncached)
   - `get_concept_tree()` response time: < 10ms (cached) vs ~200ms (uncached)

2. **Database Load**:
   - 80%+ reduction in database queries for cached endpoints

3. **Cache Hit Rate**:
   - Target: > 90% cache hit rate for languages list
   - Target: > 70% cache hit rate for concept tree

## 🧪 Testing Scenarios

### Manual Testing

```bash
# 1. Test cache hit
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "query { languages { id name code } }"}'

# Check Redis for cached data
docker exec humans_ontology_backend redis-cli -h redis keys "cache:*"

# View cached value
docker exec humans_ontology_backend redis-cli -h redis get "cache:language:get_all_languages:<hash>"

# 2. Test cache invalidation
# Modify a language via GraphQL mutation
curl -X POST http://localhost:8000/graphql \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { updateLanguage(id: 1, name: \"Updated\") { id name } }"}'

# Verify cache was cleared
docker exec humans_ontology_backend redis-cli -h redis keys "cache:language:*"

# 3. Check metrics
curl http://localhost:8000/metrics | grep service_cache

# Expected output:
# service_cache_hits_total{service="language",method="get_all_languages"} 42
# service_cache_misses_total{service="language",method="get_all_languages"} 3
```

### Automated Testing

```bash
# Run cache tests
pytest tests/test_service_cache.py -v

# Run with coverage
pytest tests/test_service_cache.py --cov=core.decorators.cache --cov=core.services.cache_service

# Run performance benchmark
pytest tests/test_service_cache.py::test_cache_performance_improvement -v
```

## 📚 Documentation Requirements

- [ ] Create `docs/features/redis_caching.md` with:
  - Overview of caching strategy
  - Usage examples
  - Configuration options
  - Troubleshooting guide
  - Best practices
- [ ] Add comprehensive docstrings to `@cached` decorator with usage examples
- [ ] Update `docs/ARCHITECTURE.md` with caching layer explanation
- [ ] Update `packages/backend/CLAUDE.md` with caching information
- [ ] Add code comments explaining key design decisions

## 🔗 Related

- **BACKLOG.MD**: P2 task - "Улучшение стратегии кэширования (Backend)"
- **Related to**: Rate Limiting (#5) - uses same Redis infrastructure
- **Related to**: HTTP Caching Middleware (#22) - complementary caching layer
- **Stack**: Python, Redis, FastAPI, SQLAlchemy, Prometheus

## 💡 Implementation Hints

1. **Start with the decorator**: Create `core/decorators/cache.py` first
2. **Use functools.wraps**: Preserve original function metadata
3. **Hash function args**: Use `hashlib.md5(json.dumps(args, sort_keys=True))` for cache keys
4. **Handle async**: Decorator must work with `async def` functions
5. **Test Redis failure**: Use `try/except` and fallback to direct function call
6. **Invalidation on write**: Add cache invalidation to mutation resolvers
7. **Inspect existing code**: Check `core/redis_client.py` for Redis connection patterns
8. **Follow patterns**: Use same logging/metrics patterns as `core/middleware/rate_limit.py`

## ⚠️ Edge Cases to Consider

- **Stale data**: What if cached data is stale but hasn't expired? (Consider manual invalidation)
- **Cache stampede**: What if two requests arrive simultaneously and both miss cache? (Consider implementing cache locking)
- **Size limits**: What if serialized data exceeds Redis value size limit (512MB)? (Add size validation)
- **Non-serializable args**: What if function arguments include non-serializable objects? (Handle gracefully, skip caching)
- **None results**: Should `None` be cached? (Make it configurable via `cache_none` parameter)
- **Database transactions**: What if cache is invalidated but DB transaction fails? (Invalidate cache AFTER successful commit)

## 📋 Checklist for Reviewer

When reviewing this implementation, verify:

- [ ] Code follows project patterns (see `docs/PATTERNS.md`)
- [ ] All acceptance criteria are met
- [ ] Tests pass and have good coverage (>80%)
- [ ] Metrics are properly implemented
- [ ] Logging follows structured format
- [ ] Documentation is clear and complete
- [ ] Edge cases are handled
- [ ] Performance improvement is measurable
- [ ] Redis failure doesn't break the app
- [ ] Cache invalidation works correctly
- [ ] Code is well-commented
- [ ] No memory leaks (Redis keys are properly expired)

## 🎯 Definition of Done

This task is considered complete when:

1. ✅ All acceptance criteria checkboxes are ticked
2. ✅ `pytest` passes with >80% coverage for new code
3. ✅ Manual testing scenarios work as expected
4. ✅ Metrics appear in `/metrics` endpoint
5. ✅ Documentation is written and reviewed
6. ✅ Performance improvement is demonstrated (benchmark results included)
7. ✅ Code review is approved
8. ✅ CI/CD pipeline passes

---

**Labels**: `enhancement`, `backend`, `performance`, `P2`
**Priority**: P2 (Important improvement)
**Complexity**: Medium
**Estimated effort**: 6-8 hours
**Skills required**: Python, Redis, FastAPI, SQLAlchemy, Testing, Decorators
**Assigned to**: Claude Sonnet 4.5 (AI)
