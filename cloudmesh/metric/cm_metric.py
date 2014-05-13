#!/usr/bin/env python
import types
import textwrap
from docopt import docopt
import inspect
import sys
import importlib
import cloudmesh
from pprint import pprint

from cloudmesh.cm_mongo import cm_mongo
from cloudmesh.config.cm_config import cm_config
from prettytable import PrettyTable
from cloudmesh.metric.api.metric import metric_api

from cloudmesh.util.logger import LOGGER

log = LOGGER(__file__)

def shell_command_metric(arguments):
    """
    Usage:
	cm-metric -h | --help
        cm-metric --version
        cm-metric [CLOUD]
                  [-s START|--start=START] 
                  [-e END|--end=END] 
                  [-u USER|--user=USER] 
                  [-m METRIC|--metric=METRIC]
                  [-p PERIOD|--period=PERIOD] 
                  [-c CLUSTER]

   Options:
       -h                   help message
       -m, --metric METRIC  use either user|vm|runtime in METRIC
       -u, --user USER      use username in USER
       -s, --start_date START    use YYYYMMDD datetime in START
       -e, --end_date END        use YYYYMMDD datetime in END
       -c, --cluster CLUSTER    use cluster name e.g. india, sierra, etc
       -p, --period PERIOD  use either month|day|week
 
    Arguments:
        CLOUD               Name of the IaaS cloud e.g. openstack, nimbus, Eucalyptus
        CLUSTER             Name of cluster e.g. india, sierra, foxtrot,
                            hotel, alamo, lima
    
    Description:
       metric command provides usage data with filter options.

    Result:
      The result of the method is a datastructure specified in a given format.
      If no format is specified, we return a JSON string of the following format:

         {
            "start_date"    :   start date of search    (datetime),
            "end_date"      :   end date of search      (datetime),
            "ownerid"       :   portal user id          (str),
            "metric"        :   selected metric name    (str),
            "period"        :   monthly, weekly, daily  (str),
            "clouds"        :   set of clouds           (list)
            [
               {"service"     :   cloud service name  (str),
                "hostname"     :   hostname (str),
                "stats"        :   value (int) }
                ...
            ]
         }

    Examples:
        $ cm-metric openstack -c india -u hrlee        
        - Get user statistics
        
    """

    #log.info(arguments)

    # stage 1
    # ----------
    # (make sure) all data is in database
    # it is not real-time
    # create api to update data into the database
    # otherwise, cached metrics data will be loaded from the database

    # stage 2
    # ----------
    # db access
    # select data with search options
    # return in table
    m = metric_api()
    m.set_date(arguments["--start_date"], arguments["--end_date"])
    m.set_period(arguments["--period"])
    m.set_metric(arguments["--metric"])
    m.set_user(arguments["--user"])
    m.set_cloud(arguments["CLOUD"])
    
    res = m.get_stats()

class cm_metric:
    from_date = None
    to_date = None
    period = None
    metric = None
    cluster = None
    iaas = None
    user = None

    def __init__(self):
        from_date = None
        to_date = None
        period = None
        metric = None
        cluster = None
        iaas = None
        user = None

        
    def __str__(self):
        result = ""
        result += "from_date: %s\n" % self.from_date
        result += "to_date:   %s\n" % self.to_date
        result += "period:    %s\n" % self.period
        result += "metric:    %s\n" % self.metric
        result += "cluster:   %s\n" % self.cluster
        result += "iaas:      %s\n" % self.iaas
        result += "user:      %s\n" % self.user
        return result
    
    def set_date(self, from_date, to_date):
        self.from_date = from_date
        self.to_date = to_date

    def set_period(self, period):
        self.period = period

    def set_metric(self, metric):
        self.metric = metric

    def set_cluster(self, cluster):
        self.cluster = cluster

    def set_iaas(self, cloud):
        self.iaas = cloud

    def set_cloud(self, cloud):
        ''' link to set_iaas '''
        self.set_iaas(cloud)

    def set_user(self, user):
        self.user = user

    def get_stats(self):
        print "get_stats called"
        print vars(self)
        return

    def stats(self):
        ''' link to get_stats '''
        return self.get_stats()

def main():
    arguments = docopt(shell_command_metric.__doc__)
    shell_command_metric(arguments)
        
if __name__ == "__main__":
    print sys.argv
    main()