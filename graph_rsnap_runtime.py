#!/usr/bin/python

import sys, os, argparse, logging, time, socket


class rsnap_runtime:
  
    def __init__(self):
        self.get_log_list = self.get_log_list()
        self.loop_logs = self.loop_logs()
  
    def get_log_list(self):
        ls_log = "ls %s" %(rsnap_log_home)
        ls_log_cmd = ls_log.split()
        try:
            logs = Popen(ls_log_cmd, stdout=PIPE, stderr=PIPE))
            logs_out, logs_err = logs.communicate()
            if not logs_out and not logs_err:
              print "nada!"
            elif not logs_out:
              print "Um not getting any logs"
            elif logs_err.rstrip():
               print "Error:<<%s>>" %logs_err
        except:
            print "catch and exception!"
        self.log_list = logs_out
    
    def loop_logs(self):
        for log in self.log_list:
            print log 
            log_path = rsnap_log_home + log
            get_job_start_time(log_path)
            #get_job_stop_time(log_path)
    
    def get_job_start_time():
        print log_path
        return

if __name__ == '__main__':
  #default configs
  rsnap_log_home = '/var/log/rsnapshot/'
  rsnap_runtime()