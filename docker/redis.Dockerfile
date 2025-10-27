FROM redis

# Copy custom Redis configuration
COPY redis.conf /usr/local/etc/redis/redis.conf

# Expose Redis port
EXPOSE 6379

# Start Redis with custom config
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
