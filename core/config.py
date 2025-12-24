# Thresholds (percentage)
CPU_LIMIT = 85
MEM_LIMIT = 80
SWAP_LIMIT = 20

# Timing (seconds)
# CHECK_EVERY controls how often resource usage is sampled.
# Lower values (e.g. 5s) provide more responsive monitoring but increase CPU usage
# and power consumption, especially when this tool runs continuously.
# For production or battery-sensitive environments, consider using a higher value
# (e.g. 10–30 seconds) unless you specifically need near-real-time alerts.
CHECK_EVERY = 5
COOLDOWN = 120

