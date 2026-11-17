#!/bin/zsh
set -e

SSH_HOST="${SO101_SSH_HOST:-cicero}"
SSH_CONFIG="${SO101_SSH_CONFIG:-$HOME/.ssh/config-so101}"
LOCAL_PORT="${SO101_LOCAL_PORT:-18766}"

if lsof -nP -iTCP:"$LOCAL_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Error: Mac port $LOCAL_PORT is already in use."
  exit 1
fi

SSH_OPTIONS=(
  -tt
  -o ExitOnForwardFailure=yes
  -o ServerAliveInterval=30
  -L "127.0.0.1:${LOCAL_PORT}:127.0.0.1:18765"
)

if [[ -f "$SSH_CONFIG" ]]; then
  SSH_OPTIONS=(-F "$SSH_CONFIG" "${SSH_OPTIONS[@]}")
else
  echo "Notice: SSH config not found at $SSH_CONFIG."
  echo "Using default SSH configuration."
fi

echo "Starting SO-101 simulation on $SSH_HOST..."
echo "Foxglove: ws://localhost:$LOCAL_PORT"

exec ssh "${SSH_OPTIONS[@]}" "$SSH_HOST" \
  'cd ~/so101-robotics-env/ros2_ws && \
   export ROS_DOMAIN_ID=73 && \
   export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST && \
   ~/.pixi/bin/pixi run bash -c "source install/setup.bash && exec ros2 launch so101_bringup simulation.launch.py"'
