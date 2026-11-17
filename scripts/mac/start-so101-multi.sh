#!/bin/zsh
set -eu

CONFIG_FILE="${SO101_CONFIG_FILE:-$HOME/.config/so101/sim.env}"

if [[ -f "$CONFIG_FILE" ]]; then
  source "$CONFIG_FILE"
fi

: "${SO101_DOMAIN_ID:?SO101_DOMAIN_ID is required}"
: "${SO101_REMOTE_PORT:?SO101_REMOTE_PORT is required}"

SSH_HOST="${SO101_SSH_HOST:-cicero}"
SSH_CONFIG="${SO101_SSH_CONFIG:-$HOME/.ssh/config-so101}"
LOCAL_PORT="${SO101_LOCAL_PORT:-18766}"

if [[ "$SO101_DOMAIN_ID" != <-> ]] ||
   (( SO101_DOMAIN_ID > 101 )); then
  echo "Invalid ROS_DOMAIN_ID (use 0-101)"
  exit 1
fi

for port in "$SO101_REMOTE_PORT" "$LOCAL_PORT"; do
  if [[ "$port" != <-> ]] ||
     (( port < 1024 || port > 65535 )); then
    echo "Invalid port: $port"
    exit 1
  fi
done

if [[ ! -f "$SSH_CONFIG" ]]; then
  echo "SSH config not found: $SSH_CONFIG"
  exit 1
fi

if lsof -nP -iTCP:"$LOCAL_PORT" -sTCP:LISTEN \
  >/dev/null 2>&1; then
  echo "Local port $LOCAL_PORT is already in use"
  exit 1
fi

echo "SO-101 simulation"
echo "  Host: $SSH_HOST"
echo "  ROS domain: $SO101_DOMAIN_ID"
echo "  Remote Foxglove port: $SO101_REMOTE_PORT"
echo "  Foxglove URL: ws://localhost:$LOCAL_PORT"

REMOTE_COMMAND="cd ~/so101-robotics-env/ros2_ws && \
export ROS_DOMAIN_ID=$SO101_DOMAIN_ID && \
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST && \
~/.pixi/bin/pixi run bash -c 'source install/setup.bash && exec ros2 launch so101_bringup simulation_multi.launch.py foxglove_port:=$SO101_REMOTE_PORT'"

exec ssh -F "$SSH_CONFIG" -tt \
  -o ExitOnForwardFailure=yes \
  -o ServerAliveInterval=30 \
  -L "127.0.0.1:${LOCAL_PORT}:127.0.0.1:${SO101_REMOTE_PORT}" \
  "$SSH_HOST" \
  "$REMOTE_COMMAND"
