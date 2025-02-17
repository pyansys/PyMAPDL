
mkdir "$LOG_NAMES" && echo "Successfully generated directory $LOG_NAMES"

echo "Copying the log files..."
cp *.log ./"$LOG_NAMES"/ || echo "No log files could be found"
cp *apdl.out ./"$LOG_NAMES"/ || echo "No APDL log files could be found"
cp *pymapdl.apdl ./"$LOG_NAMES"/ || echo "No PYMAPDL APDL log files could be found"

echo "Copying the profiling files..."
cp -r prof ./"$LOG_NAMES"/prof || echo "No profile files could be found"

echo "Copying DPF server files..."
cp dpf_server.log ./"$LOG_NAMES"/dpf-standalone || echo "No DPF server files could be found"

ls -la ./"$LOG_NAMES"

echo "Tar files..."
tar cvzf ./"$LOG_NAMES".tgz ./"$LOG_NAMES" || echo "Failed to compress"