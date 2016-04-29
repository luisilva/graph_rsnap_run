#!/usr/bin/python

import sys
import os
import argparse
import logging
import time
import socket
import pickle
from subprocess import Popen, PIPE
from datetime import datetime


class rsnap_runtime:

    def __init__(self):
        self.setup_logging = self.setup_logging()
        self.get_hostname = self.get_hostname()
        self.get_last_times = self.get_last_times()
        self.get_log_list = self.get_log_list()
        self.loop_logs = self.loop_logs()
        self.set_last_times = self.set_last_times()

    def setup_logging(self):
        LOG_FORMAT = "[%(asctime)s][%(levelname)s] - %(name)s - %(message)s"
        log_level = logging.INFO
        if 'debug' in globals():
            log_level = logging.DEBUG
        if '/' in rsnap_runtime_log:
            dir_path = os.path.dirname(rsnap_runtime_log)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)
        log_file = "%s" % rsnap_runtime_log
        logging.basicConfig(filename=log_file,
                            level=log_level,
                            format=LOG_FORMAT)
        logger.debug(" ".join(sys.argv))

    def get_hostname(self):
        try:
            host_cmd = Popen(['hostname', '-s'], stdout=PIPE, stderr=PIPE)
            host_out, host_err = host_cmd.communicate()
            if not host_out and not host_err:
                logger.debug("hostname command returned no Output or Errors.")
            elif not host_out:
                logger.debug("No hostname returned")
            elif host_err.rstrip():
                logger.critical("Hostname command error (hostname -s): "
                                "<<%s>>" % host_err)
            self.hostname = host_out.strip()
        except Exception as e:
            logger.critical("Caught and exception running "
                            "hostname command (hostname -s)!")
            logger.critical("%s" % e)

    def get_last_times(self):
        if os.path.isfile("save.p"):
            self.last_times_dict = pickle.load(open("save.p", "rb"))
        else:
            self.last_times_dict = {}

    def get_log_list(self):
        ls_log = "ls %s" % rsnap_log_home
        ls_log_cmd = ls_log.split()
        try:
            logs = Popen(ls_log_cmd, stdout=PIPE, stderr=PIPE)
            logs_out, logs_err = logs.communicate()
            if not logs_out and not logs_err:
                logger.debug("list command returned Null Output or Errors.")
            elif not logs_out:
                logger.debug("No list infromation was returned.")
            elif logs_err.rstrip():
                logger.critical("Hostname command error "
                                "(hostname -s): <<%s>>" % logs_err)
            self.log_list = logs_out
        except Exception as e:
            logger.critical("Caught and exception running"
                            " list command (ls rsnap_log_home)!")
            logger.critical("%s" % e)

    def loop_logs(self):
        last_time_dict = {}
        for log in self.log_list.splitlines():
            self.log_path = rsnap_log_home + log
            self.get_job_times()
            self.parse_job_durations()
            if self.graph_list:
                last_time_dict[log] = self.graph_list[-1]
            logger.debug("%s" % self.graph_list)
            self.graph_data()
        self.last_times_dict.update(last_time_dict)

    def get_job_times(self):
        logger.debug("looking at log: %s" % self.log_path)
        date_format = "%d/%b/%Y:%H:%M:%S"
        self.start_times = []
        self.end_times = []
        echo_count = 0
        with open(self.log_path) as f:
            if not self.last_times_dict:
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
            else:
                log_key = os.path.basename(self.log_path)
                self.last_times_dict = pickle.load(open("save.p", "rb"))
                try:
                    last_time = int(self.last_times_dict[log_key]
                                    .split()[2].strip("\n"))
                except KeyError:
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
                else:
                    last_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                              time.localtime(last_time))
                    last_time = datetime.strptime(last_time,
                                                  "%Y-%m-%d %H:%M:%S")
                    for line in f:
                        if 'echo' in line:
                            start_date = line.split()[0].strip("[").strip("]")
                            startd = datetime.strptime(start_date, date_format)
                            if startd > last_time:
                                echo_count += 1
                                self.start_times.append(startd)
                        elif '.pid' in line and 'rm' in line:
                            if echo_count > 1:
                                echo_pop = echo_count - 1
                                for count in range(echo_pop):
                                    del self.start_times[-2]
                            echo_count = 0
                            end_date = line.split()[0].strip("[").strip("]")
                            endd = datetime.strptime(end_date, date_format)
                            if endd > last_time:
                                self.end_times.append(endd)

    def parse_job_durations(self):
        self.graph_list = []
        log_name = self.log_path.split('/')[-1].strip(".log")
        if len(self.start_times) == (len(self.end_times) + 1):
            del self.start_times[-1]
        logger.debug("Lenght of Rsnap start "
                     "times: %s" % (len(self.start_times)))
        logger.debug("Lenght of Rsnap start "
                     "times: %s" % (len(self.end_times)))
        if len(self.start_times) == len(self.end_times) and \
           len(self.start_times) != 0 or len(self.end_times) != 0:
            duration = [end_i - start_i for end_i, start_i in
                        zip(self.end_times, self.start_times)]
            for end, times in zip(self.end_times, duration):
                end_epoch = end.strftime('%s')
                self.times = times
                self.total_secs()
                metric = self.metric
                ## This only works in Python 2.7.x
                #metric = int(times.total_seconds())
                graph_list = "%s.%s.%s.%s %s %s\n" \
                    % (rsnap_service_name, datacenter, self.hostname,
                        log_name, metric, end_epoch)
                self.graph_list.append(graph_list)
        if len(self.start_times) > (len(self.end_times) + 1):
            logger.critical("Can't parse this logs properly. You may want to "
                            "clear it.: %s" % self.log_path)

    def total_secs(self):
        self.metric = int((self.times.days * 86400) + self.times.seconds) 

    def graph_data(self):
        content = []
        # Open Socket and push all the metrics we have accumulated
        content = "".join(self.graph_list)
        logger.debug("<<< Opening Connection >>>")
        logger.debug("Pushing data: \n %s" % content)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((graphite_server, graphite_port))
        s.sendall(content)
        s.shutdown(socket.SHUT_WR)
        while 1:
            data = s.recv(1024)
            if data == "":
                break
            logger.debug("Recieved: %s" % (repr(data)))
        logger.debug("<<< Connection Closed >>>")
        s.close()

    def set_last_times(self):
        logger.debug(self.last_times_dict)
        if bool(self.last_times_dict):
            pickle.dump(self.last_times_dict, open("save.p", "wb"))

if __name__ == '__main__':
    # default global configs
    # production log path
    rsnap_log_home = '/var/log/rsnapshot/'
    # testing log path
    #rsnap_log_home = 'sample_data/'
    # service name <<rsnap_service_name>>.<datacenter>.<hostname>.\
    #<metricName> metric epoch
    rsnap_service_name = 'rsnap'
    # log area for messages that come out of this script
    rsnap_runtime_log = '/var/log/rsnap_runtime.log'
    # log level (debug = True,default = False)
    #debug = True
    # Init logging
    logger = logging.getLogger(rsnap_runtime_log)
    # datacenter field <rsnap_service_name>.<<datacenter>>.<hostname>.\
    #<metricName> metric epoch
    datacenter = 'holyoke'
    # graphite server name
    graphite_server = 'graph.rc.fas.harvard.edu'
    # graphite intake port
    graphite_port = 2003
    # Kick off main script
    rsnap_runtime()
