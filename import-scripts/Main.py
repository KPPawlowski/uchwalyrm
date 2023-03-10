#!/usr/bin/python3
# coding=utf8
from ConnectionSettings import *
import argparse
import logging
import datetime

if __name__ == "__main__":

    from DzUrzWojDoln import *
    from UchwalyRM import *

    datetime_str = datetime.datetime.now().strftime("%Y%m%d%H%m%s")
    logging.basicConfig(filename=f"Main{datetime_str}.log",
                        filemode='a',
                        level=logging.DEBUG,
                        format='%(asctime)s [%(levelname)s]: %(message)s',
                        datefmt='%Y-%m-%d %H:%m:%s')

    def execute_duw_service(p_log=True):
        if p_log:
            logging.debug("Wybrano serwis duw")
        duwd_object = DzUrzWojDoln()
        duwd_object.log_on = p_log
        year = 2023
        start_month = 1
        end_month = 12
        for i_month in range(start_month, end_month+1):
            logging.info(f"Pobieranie danych z miesiaca {i_month}")
            duwd_object.get_json(year, i_month)
        for i_month in duwd_object.results.get(year).keys():
            logging.info(f"Dodanie do bazy danych z miesiaca {i_month} {year}")
            duwd_object.insert_db(year, i_month, "mysql", ConnectionSettings.param_values)

    def execute_rmz_service(p_log=True):
        if p_log:
            logging.debug("Wybrano serwis uchwalyRm")
        urm_object = UchwalyRM('mysql', ConnectionSettings.param_values)
        urm_object.log_on = p_log

        for i in range(1, 4):
            urm_object.get_acts_list(i)
            urm_object.get_protocol_list(i)

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
