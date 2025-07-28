import asyncio
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any
import json

mcp = FastMCP("LogAnalyzer")

def safe_str(value: Any) -> str:
    return str(value) if value is not None else ""

@mcp.tool()
def analyze_logs(logs: List[Dict]) -> Dict:
    """
    Analyze log entries to extract errors and warnings.
    """
    errors = []
    warnings = []

    for log in logs:
        level = safe_str(log.get("level")).upper()
        if level == "ERROR":
            errors.append({
                "timestamp": safe_str(log.get("timestamp")),
                "component": safe_str(log.get("component")),
                "message": safe_str(log.get("message")),
                "stack_trace": safe_str(log.get("stack_trace"))
            })
        elif level == "WARNING":
            warnings.append({
                "timestamp": safe_str(log.get("timestamp")),
                "component": safe_str(log.get("component")),
                "message": safe_str(log.get("message"))
            })

    result = {
        "summary": {
            "total_logs": len(logs),
            "error_count": len(errors),
            "warning_count": len(warnings)
        },
        "errors": errors,
        "warnings": warnings
    }
    return result


@mcp.tool()
def suggest_fix(errors_and_warnings: Dict) -> List[str]:
    """
    Suggest potential fixes for each issue based on the log message content.

    Args:
        errors_and_warnings (Dict): Dictionary containing analyzed errors and warnings.

    Returns:
        List of textual suges or actions to take for each issue.
    """
    suges = []

    # Process ERROR level issues
    for error in errors_and_warnings.get("errors", []):
        msg = safe_str(error.get("message")).lower()
        component = safe_str(error.get("component")).lower()
        stack_trace = safe_str(error.get("stack_trace")).lower()

        # Database-related errors
        if any(keyword in msg for keyword in ["database", "connection timeout", "deadlock", "sql"]):
            if "timeout" in msg:
                suges.append(
                    "🔧 Database: Increase connection timeout, optimize slow queries, and check network connectivity between application and database server.")
            elif "deadlock" in msg:
                suges.append(
                    "🔧 Database: Review transaction isolation levels, minimize transaction duration, and implement proper lock ordering to prevent deadlocks.")
            elif "pool" in msg and ("exhausted" in msg or "running low" in msg):
                suges.append(
                    "🔧 Database: Increase connection pool size, implement connection pooling best practices, and monitor connection leaks.")

        # Memory-related errors
        elif any(keyword in msg for keyword in ["outofmemoryerror", "heap space", "memory"]):
            if "heap space" in msg:
                suges.append(
                    "🔧 Memory: Increase JVM heap size (-Xmx), optimize memory usage in DataProcessor, and implement memory profiling to identify leaks.")
            elif "outofmemory" in msg:
                suges.append(
                    "🔧 Memory: Monitor memory usage patterns, implement garbage collection tuning, and consider using memory-efficient data structures.")

        # Authentication errors
        elif any(keyword in msg for keyword in ["nullpointer", "authentication", "oauth", "ldap", "token"]):
            if "nullpointer" in msg:
                suges.append(
                    "🔧 Authentication: Add comprehensive null checks in AuthService, implement proper error handling, and validate input parameters before processing.")
            elif "token expired" in msg or "oauth" in msg:
                suges.append(
                    "🔧 Authentication: Implement automatic token refresh mechanism, add token expiry validation, and configure proper token lifetime management.")
            elif "ldap" in msg:
                suges.append(
                    "🔧 Authentication: Check LDAP server connectivity, verify credentials, implement connection retry logic, and add fallback authentication methods.")

        # Network and timeout errors
        elif any(keyword in msg for keyword in ["timeout", "ssl", "connection", "network"]):
            if "timeout" in msg:
                if "payment" in msg or "gateway" in msg:
                    suges.append(
                        "🔧 Network: Increase PaymentGateway timeout settings, implement circuit breaker pattern, and add retry logic with exponential backoff.")
                else:
                    suges.append(
                        "🔧 Network: Check network connectivity, increase timeout values, implement connection pooling, and add health checks for external services.")
            elif "ssl" in msg:
                suges.append(
                    "🔧 Network: Verify SSL certificates, update certificate trust store, check TLS version compatibility, and implement proper SSL configuration.")

        # File and configuration errors
        elif any(keyword in msg for keyword in ["filenotfound", "config", "properties"]):
            suges.append(
                "🔧 Configuration: Verify file paths, ensure configuration files exist, implement configuration validation, and add default fallback configurations.")

        # Cache and Redis errors
        elif any(keyword in msg for keyword in ["redis", "cache", "pool exhausted"]):
            if "pool exhausted" in msg:
                suges.append(
                    "🔧 Cache: Increase Redis connection pool size, implement connection management, monitor cache hit ratios, and add connection health checks.")

        # External service errors
        elif any(keyword in msg for keyword in ["elasticsearch", "kafka", "service discovery"]):
            if "elasticsearch" in msg:
                suges.append(
                    "🔧 External Services: Check Elasticsearch cluster health, verify connectivity, implement retry mechanisms, and add service monitoring.")
            elif "kafka" in msg:
                suges.append(
                    "🔧 External Services: Verify Kafka broker connectivity, check network configuration, implement producer/consumer error handling.")
            elif "service discovery" in msg:
                suges.append(
                    "🔧 External Services: Check service registry health, implement service discovery fallbacks, and verify network connectivity to registry.")

        # Threading and execution errors
        elif any(keyword in msg for keyword in ["thread", "rejected execution", "circuit breaker"]):
            if "rejected execution" in msg:
                suges.append(
                    "🔧 Threading: Increase thread pool size, implement proper task queuing, monitor thread pool metrics, and add backpressure handling.")
            elif "circuit breaker" in msg:
                suges.append(
                    "🔧 Resilience: Review circuit breaker thresholds, implement proper fallback mechanisms, and monitor service health metrics.")

        # Serialization and data format errors
        elif any(keyword in msg for keyword in ["json", "serialization", "parsing"]):
            if "json" in msg:
                suges.append(
                    "🔧 Data Processing: Implement robust JSON validation, add proper error handling for malformed data, and use schema validation.")
            elif "serialization" in msg:
                suges.append(
                    "🔧 Data Processing: Ensure all objects implement Serializable, review serialization compatibility, and consider using alternative serialization formats.")

        # Validation and constraint errors
        elif any(keyword in msg for keyword in ["validation", "constraint", "integrity"]):
            suges.append(
                "🔧 Data Validation: Implement comprehensive input validation, review database constraints, and add proper error handling for validation failures.")

        # Container and deployment errors
        elif any(keyword in msg for keyword in ["docker", "container"]):
            suges.append(
                "🔧 Deployment: Check Docker configuration, verify resource limits, review container logs, and ensure proper image dependencies.")

        # WebSocket and real-time communication errors
        elif any(keyword in msg for keyword in ["websocket", "broken pipe"]):
            suges.append(
                "🔧 Real-time Communication: Implement WebSocket reconnection logic, add connection health monitoring, and handle network interruptions gracefully.")

        # GraphQL and API errors
        elif any(keyword in msg for keyword in ["graphql", "query execution"]):
            suges.append(
                "🔧 API: Optimize GraphQL query performance, implement query complexity analysis, add proper timeout handling, and monitor query execution times.")

        # Batch processing errors
        elif any(keyword in msg for keyword in ["batch", "job failed"]):
            suges.append(
                "🔧 Batch Processing: Implement proper error handling in batch jobs, add data validation, implement retry mechanisms, and monitor job execution status.")

        # Lock and concurrency errors
        elif any(keyword in msg for keyword in ["lock", "distributed lock"]):
            suges.append(
                "🔧 Concurrency: Review lock timeout settings, implement proper lock release mechanisms, add lock monitoring, and consider lock-free alternatives where possible.")

        # Cloud service errors (AWS, etc.)
        elif any(keyword in msg for keyword in ["s3", "access denied", "aws"]):
            suges.append(
                "🔧 Cloud Services: Verify IAM permissions, check AWS credentials, review bucket policies, and implement proper error handling for cloud service failures.")

        # Generic error handling
        else:
            suges.append(
                f"🔧 General: Review {component} component logs, implement proper error handling, add monitoring and alerting for this error type.")

    # Process WARNING level issues
    for warning in errors_and_warnings.get("warnings", []):
        msg = safe_str(warning.get("message")).lower()
        component = safe_str(warning.get("component")).lower()

        # System resource warnings
        if any(keyword in msg for keyword in ["disk usage", "disk"]):
            suges.append(
                "💡 System Resources: Set up automated log rotation, clean old temporary files, monitor disk usage proactively, and implement disk space alerts.")
        elif any(keyword in msg for keyword in ["memory usage", "memory"]):
            suges.append(
                "💡 System Resources: Monitor memory usage patterns, implement memory optimization, consider increasing available memory, and add memory usage alerts.")
        elif any(keyword in msg for keyword in ["cpu usage", "cpu"]):
            suges.append(
                "💡 System Resources: Optimize CPU-intensive operations, implement load balancing, monitor CPU usage trends, and consider scaling resources.")

        # Performance warnings
        elif any(keyword in msg for keyword in ["response time", "performance", "degradation"]):
            suges.append(
                "💡 Performance: Optimize slow operations, implement caching strategies, review database query performance, and add performance monitoring.")
        elif any(keyword in msg for keyword in ["latency", "network"]):
            suges.append(
                "💡 Performance: Optimize network calls, implement connection pooling, review network infrastructure, and add latency monitoring.")

        # Queue and throughput warnings
        elif any(keyword in msg for keyword in ["queue", "limit", "approaching"]):
            suges.append(
                "💡 Capacity: Monitor queue sizes, implement auto-scaling, optimize message processing, and add queue depth alerts.")
        elif any(keyword in msg for keyword in ["rate limit", "requests"]):
            suges.append(
                "💡 Capacity: Review rate limiting policies, implement request throttling, consider increasing limits, and add rate limiting alerts.")

        # Cache performance warnings
        elif any(keyword in msg for keyword in ["cache", "hit ratio"]):
            suges.append(
                "💡 Caching: Optimize cache configuration, review cache key strategies, implement cache warming, and monitor cache performance metrics.")

        # Scheduled task warnings
        elif any(keyword in msg for keyword in ["scheduled", "task", "delayed"]):
            suges.append(
                "💡 Scheduling: Review task scheduling configuration, optimize task execution time, implement task monitoring, and add scheduling alerts.")

        # Garbage collection warnings
        elif any(keyword in msg for keyword in ["garbage collection", "gc"]):
            suges.append(
                "💡 JVM: Tune garbage collection parameters, review heap configuration, implement GC monitoring, and optimize memory allocation patterns.")

        # Connection pool warnings
        elif any(keyword in msg for keyword in ["connection pool", "connections available"]):
            suges.append(
                "💡 Connection Management: Increase connection pool size, implement connection monitoring, optimize connection usage, and add pool health checks.")

        # Generic warning handling
        else:
            suges.append(
                f"💡 Monitoring: Monitor {component} component closely, implement alerting for this warning type, and review system metrics regularly.")

    # Handle empty results
    if not suges:
        if errors_and_warnings.get("errors") or errors_and_warnings.get("warnings"):
            suges.append(
                "✅ Review the identified issues above and implement appropriate monitoring and logging practices.")
        else:
            suges.append(
                "✅ No critical issues found. Continue monitoring system health and maintain current operational practices.")

    # Add general recommendations if there are multiple issues
    error_count = len(errors_and_warnings.get("errors", []))
    warning_count = len(errors_and_warnings.get("warnings", []))

    if error_count > 3:
        suges.append(
            "🚨 High Error Volume: Consider implementing comprehensive error tracking, alerting systems, and automated incident response procedures.")

    if warning_count > 5:
        suges.append(
            "⚠️ Multiple Warnings: Review system capacity planning, implement proactive monitoring, and consider performance optimization initiatives.")

    return suges


if __name__ == "__main__":
    mcp.run(transport='stdio')
