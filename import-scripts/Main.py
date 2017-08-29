#!/usr/bin/python3
# coding=utf8
from ConnectionSettings import *
import argparse

if __name__ == "__main__":
    from DzUrzWojDoln import *
    from UchwalyRM import *
    def execute_duw_service(p_log=True):
        if p_log:
            print("Wybrano serwis duw")
        duwd_object = DzUrzWojDoln()
        duwd_object.log_on = p_log
        year = 2017
        start_month = 8
        end_month = 8
        for i_month in range(start_month, end_month+1):
            duwd_object.get_json(year, i_month)
        for i_month in duwd_object.results.get(year).keys():
            duwd_object.insert_db(year, i_month, "pgsql", ConnectionSettings.param_values)
            duwd_object.insert_db(year, i_month, "mysql", ConnectionSettings.param_values)
    def execute_rmz_service(p_log=True):
        if p_log:
            print("Wybrano serwis uchwalyRm")
        urm_object = UchwalyRM('mysql', ConnectionSettings.param_values)
        urm_object.log_on = p_log
        urm_object.get_acts_list(1)
        urm_object.get_acts_list(2)
        urm_object.get_protocol_list(1)
        urm_object.get_protocol_list(2)
        urm_object.get_protocol_list(3)
        urm_object.insert_acts()
        urm_object.insert_protocols()
    def control():
        l_parser = argparse.ArgumentParser()
        l_parser.add_argument("-s", "--service", help="Legalbase", choices=["duw", "rmz"])
        l_parser.add_argument("-l", "--log", help="Log output console", action="store_true")
        l_args = l_parser.parse_args()
        if l_args.service == "duw":
            execute_duw_service(l_args.log)
        elif l_args.service == 'rmz':
            execute_rmz_service(l_args.log)
    control()
