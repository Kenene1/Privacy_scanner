#!/data/data/com.termux/files/usr/bin/sh

# Define log file for script execution
LOG_FILE="/data/data/com.termux/files/home/pm2_restart.log"

# Log the current date and time
echo "Restart initiated at: $(date)" >> $LOG_FILE

# Ensure PM2 is running
echo "Checking if PM2 is running..." >> $LOG_FILE
if ! pgrep -x "pm2" > /dev/null
then
    echo "PM2 is not running. Starting PM2..." >> $LOG_FILE
    pm2 resurrect >> $LOG_FILE 2>&1
else
    echo "PM2 is already running. Resurrecting PM2 processes..." >> $LOG_FILE
    pm2 resurrect >> $LOG_FILE 2>&1
fi

# Log completion
echo "Restart completed at: $(date)" >> $LOG_FILE
echo "------------------------------------------" >> $LOG_FILE
