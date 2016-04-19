#!/usr/bin/python

import sys, os, argparse, logging, time, socket
from subprocess import Popen, PIPE
from datetime import datetime

class rsnap_runtime:
  
    def __init__(self):
        self.get_log_list = self.get_log_list()
        self.loop_logs = self.loop_logs()
  
    def get_log_list(self):
        ls_log = "ls %s" %(rsnap_log_home)
        ls_log_cmd = ls_log.split()
        try:
            logs = Popen(ls_log_cmd, stdout=PIPE, stderr=PIPE)
            logs_out, logs_err = logs.communicate()
            if not logs_out and not logs_err:
              print "nada!"
            elif not logs_out:
              print "Um not getting any logs"
            elif logs_err.rstrip():
               print "Error:<<%s>>" %logs_err
            self.log_list = logs_out 
        except Exception as e:
            print "caught and exception!"
            print e

    def loop_logs(self):
        for log in self.log_list.splitlines():
            self.log_path = rsnap_log_home + log
            self.get_job_start_time()
            #get_job_stop_time(log_path)
    
    def get_job_start_time(self):
        print self.log_path
        date_format = "%d/%b/%Y:%H:%M:%S"
        start_times = []
        end_times = []
        duration = []
        with open(self.log_path) as f: 
            for line in f: 
                if 'echo' in line:
		    start_date = line.split()[0].strip("[").strip("]")
		    startd = datetime.strptime(start_date, date_format)
                    start_times.append(startd)
		elif '.pid' in line and 'rm' in line:
                    end_date = line.split()[0].strip("[").strip("]")
                    endd = datetime.strptime(end_date, date_format)
                    end_times.append(endd)
        print start_times[0]
        print end_times[0]
        duration = end_times[0] - start_times[0]
        print duration
        return

if __name__ == '__main__':
  #default configs
  rsnap_log_home = '/var/log/rsnapshot/'
  rsnap_runtime()
