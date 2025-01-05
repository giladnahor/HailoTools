#!/bin/bash

# Update package list and install dependencies
sudo apt update
sudo apt install -y git meson ninja-build pkg-config libgstreamer1.0-dev libglib2.0-dev graphviz

# Clone the Gst-Instruments repository
git clone https://github.com/kirushyk/gst-instruments.git
cd gst-instruments

# Build and install Gst-Instruments
meson build
ninja -C build
sudo ninja -C build install

# Determine the installation path of libgstintercept.so
LIB_PATH=$(find /usr/local/lib* -name libgstintercept.so | head -n 1)

# Check if the library was found
if [[ -z "$LIB_PATH" ]]; then
  echo "Error: libgstintercept.so not found. Please verify the installation."
  exit 1
fi

# Define functions to add to .bashrc
add_functions_to_bashrc() {
  {
    echo ''
    echo '# GStreamer Debugging Functions'
    echo 'gst_enable_debug() {'
    echo '  export GST_DEBUG="GST_TRACER:7"'
    echo '  export GST_TRACERS="cpuusage;proctime;interlatency;framerate;queuelevel;bufferdrop;graphic"'
    echo "  export LD_PRELOAD=$LIB_PATH"
    echo '  export GST_DEBUG_DUMP_TRACE_DIR=/tmp/gst_traces'
    echo '  mkdir -p /tmp/gst_traces'
    echo '  echo "GStreamer debugging enabled."'
    echo '}'
    echo ''
    echo 'gst_disable_debug() {'
    echo '  unset GST_DEBUG'
    echo '  unset GST_TRACERS'
    echo '  unset LD_PRELOAD'
    echo '  unset GST_DEBUG_DUMP_TRACE_DIR'
    echo '  echo "GStreamer debugging disabled."'
    echo '}'
    echo ''
    echo 'gst_display_debug() {'
    echo '  local latest_trace=$(ls -t /tmp/gst_traces/*.gsttrace 2>/dev/null | head -n 1)'
    echo '  if [[ -z "$latest_trace" ]]; then'
    echo '    echo "No trace files found in /tmp/gst_traces."'
    echo '    return 1'
    echo '  fi'
    echo '  echo "Analyzing $latest_trace..."'
    echo '  gst-report-1.0 "$latest_trace"'
    echo '  gst-report-1.0 --dot "$latest_trace" | dot -Tsvg -o /tmp/gst_performance_graph.svg'
    echo '  echo "Performance graph saved to /tmp/gst_performance_graph.svg."'
    echo '}'
    echo ''
  } >> ~/.bashrc
}

# Add functions to .bashrc if not already present
if ! grep -q "gst_enable_debug" ~/.bashrc; then
  add_functions_to_bashrc
  echo "Functions added to ~/.bashrc. Please run 'source ~/.bashrc' to apply changes."
else
  echo "Functions already exist in ~/.bashrc."
fi
