import sys
import time
import json
from js8net import *
import re
import requests
import os
import os.path

# By Paul VandenBosch - KC8WBK
#
# Modified by Joseph A. Counsil - K0OG - 6/24/2022
# * Added user paramater block
# * Added a second trigger to execute an external program
#    specifying an executable file and an output file
#    to read and report back to requesting station's inbox.
#    If no output is generated, a "CMD COMPLETE" message
#    is sent to requester's RX Text window (not to inbox).

##### User Configurable Parameters #####

# The trigger must be in all caps and have a "?" at the end
trigger = 'HELP?'
filename = 'help.txt'

# For external executable which produces output, if desired.
# Leave output blank if no output needed to send back to requester.
trigger2 = 'SOLAR?'
exefile = './solarget'
outputfile = 'solaroutput'

js8host="localhost"
js8port=2442

##### End of configuration #####

print("Connecting to JS8Call...")
start_net(js8host,js8port)
print("Connected.")
get_band_activity()
my_call = get_callsign()
print(my_call + ' QUERY Station Active...')
print()

last=time.time()
while(True):
    time.sleep(0.1)
    if(not(rx_queue.empty())):
        with rx_lock:
            rx=rx_queue.get()
            f=open("rx.json","a")
            f.write(json.dumps(rx))
            f.write("\n")
            f.close()
# Check for a message directed to my callsign    
            if(rx['type']=="RX.DIRECTED" and my_call == rx['params']['TO']):
                directed_message_to_my_call = rx['params']['TEXT']
# Split the recieved directed message
                split_message = re.split('\s', directed_message_to_my_call)
# Search for trigger
                item_count = len(split_message)
                for i in range(item_count):
#                    print(split_message[i])
#                    try:
                    if split_message[i] == trigger:
                        request_call_raw = split_message[0]
                        request_call = request_call_raw.strip(':')
                        report_file = open(filename)
                        report_msg = report_file.read()
                        print(request_call + ' ' + report_msg)
                        send_inbox_message(request_call, report_msg)
                        report_file.close()
                    else:
                        if split_message[i] == trigger2:
                            request_call_raw = split_message[0]
                            request_call = request_call_raw.strip(':')
                            os.system(exefile)
                            if os.path.exists(outputfile):
                              report_file = open(outputfile)
                              report_msg = report_file.read()
                              print(request_call + ' CMD COMPLETE\n' + report_msg)
                              send_inbox_message(request_call, report_msg)
                              report_file.close()
                            else:
                              send_directed_message(request_call, 'CMD COMPLETE')
