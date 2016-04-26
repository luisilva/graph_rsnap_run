#!/usr/bin/python

import sys
import os
import argparse
import logging
import time
import socket
from subprocess import Popen, PIPE
from datetime import datetime


class rsnap_runtime:
  
    def __init__(self):
        self.get_hostname = self.get_hostname()
        self.get_log_list = self.get_log_list()
        self.loop_logs = self.loop_logs()
        
    def get_hostname(self):
        try:
            host_cmd = Popen(['hostname','-s'], stdout=PIPE, stderr=PIPE)
            host_out, host_err = host_cmd.communicate()
            if not host_out and not host_err:
              print "nada!"
            elif not host_out:
              print "Um not getting any host"
            elif host_err.rstrip():
               print "Error:<<%s>>" %host_err
            self.hostname = host_out.strip() 
        except Exception as e:
            print "caught and exception!"
            print e
  
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
            self.get_job_times()
            self.parse_job_durations()
            print self.graph_list
            #self.graph_data()
    
    def get_job_times(self):
        print self.log_path
        date_format = "%d/%b/%Y:%H:%M:%S"
        self.start_times = []
        self.end_times = []
        echo_count = 0 
        with open(self.log_path) as f: 
            for line in f: 
                if 'echo' in line:
                    echo_count += 1
                    start_date = line.split()[0].strip("[").strip("]")
                    startd = datetime.strptime(start_date, date_format)
                    self.start_times.append(startd)
                elif '.pid' in line and 'rm' in line:
                    if echo_count > 1:
                        echo_pop = echo_count - 1
                        for count in range(echo_pop):
                            del self.start_times[-2]
                    echo_count = 0
                    end_date = line.split()[0].strip("[").strip("]")
                    endd = datetime.strptime(end_date, date_format)
                    self.end_times.append(endd)
    
    def parse_job_durations(self):
        self.graph_list = []
        log_name = self.log_path.split('/')[-1].strip(".log")
        if len(self.start_times) == (len(self.end_times) +1):
            del self.start_times[-1]
         
        print len(self.start_times)
        print len(self.end_times)
        if len(self.start_times) == len(self.end_times) and len(self.start_times) != 0:
            duration = [end_i - start_i for end_i, start_i in zip(self.end_times, self.start_times)]
            for end, times in zip(self.end_times,duration):
                end_epoch = end.strftime('%s')
                metric = int(times.total_seconds())
                graph_list = "%s.%s.%s.%s %s %s\n" %(rsnap_service_name, datacenter, self.hostname, log_name, metric, end_epoch)
                self.graph_list.append(graph_list)
                
    def graph_data(self):
        # Open Socket and push all the metrics we have accumulated
        content = self.graph_list
        print "<<< Opening Connection >>>"
        print "Pushing data: \n %s" %content
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((graphite_server, graphite_port))
        s.sendall(content)
        s.shutdown(socket.SHUT_WR)
        while 1:
            data = s.recv(1024)
            if data == "":
                break
            print "Recieved: %s" %(repr(data))
        print "<<< Connection Closed >>>"
        s.close()

if __name__ == '__main__':
  # default global configs
  # production log path
  #rsnap_log_home = '/var/log/rsnapshot/'
  # testing log path
  rsnap_log_home = 'sample_data/'
  # service name <<rsnap_service_name>>.<datacenter>.<hostname>.<metricName> metric epoch
  rsnap_service_name = 'rsnap'
  # datacenter field <rsnap_service_name>.<<datacenter>>.<hostname>.<metricName> metric epoch
  datacenter = 'holyoke'
  # graphite server name
  graphite_server = 'graph.rc.fas.harvard.edu'
  # graphite intake port
  graphite_port = '2003'
  # hours to rollback in logs
  rollback_threshold = '24' 
  # log area for messages that come out of this script
  rsnap_runtime_log = '/var/log/rsnap_runtime.log'
  # Kick off main script
  rsnap_runtime()
