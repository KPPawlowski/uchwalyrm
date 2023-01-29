#!/usr/bin/python3
# coding=utf8
## @author Kacper Pawłowski
#  Dokumentacja dla modułu IActLawBase
#
#  Moduł bazowy

import re
import mysql.connector
import psycopg2
import logging

## Klasa bazowa (interfejs)
class IActLawBase:
    ## Konstruktor
    #
    #  Utworzenie IActLawBase
    def __init__(self):
        self.log_on = True

    ## Utworzenie połączenia z bazą danych
    #
    # @param    p_dbType        Nazwa DBMS (do wyboru: mysql, pgsql)
    # @param    p_paramValues   Parametry do nawiązania połączenia z bazami danych
    #
    # @return   Odpowiedni uchwyt polączenia z klasy psycopg2 lub mysql.connector, podobny interfejs
    #
    # W zależności od wybranego sterownika DBMS tworzy odpowiednie połączenie z bazą danych.
    #
    # Przykład:
    # @code
    # p_param_values = {'mysql': {'db_host': 'localhost', 'db_name': '', 'user': '','password': ''},
    #                   'pgsql': {'db_host': 'localhost', 'db_name': '', 'user': '','password': ''}}
    # connection = object.createConnection('mysql', p_paramValues)
    # @endcode
    @staticmethod
    def create_connection(p_dbms, p_param_values):
        if p_dbms == "mysql":
            connection = mysql.connector.connect(user=p_param_values[p_dbms]["user"],
                                                 password=p_param_values[p_dbms]["password"],
                                                 host=p_param_values[p_dbms]["db_host"],
                                                 database=p_param_values[p_dbms]["db_name"])
        elif p_dbms == "pgsql":
            connection = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" %
                                          (p_param_values[p_dbms]["db_name"],
                                           p_param_values[p_dbms]["user"],
                                           p_param_values[p_dbms]["db_host"],
                                           p_param_values[p_dbms]["password"]))
        return connection

    ## Logowanie komunikatów
    #
    #  @param p_text
    #
    #  Przykład:
    #  @code
    #       log("Test")
    #  @endcode
    def log(self, p_text):
        if self.log_on:
            logging.info(p_text)

    ## Wykonanie zapytania SQL
    #
    #  @param p_connection Uchwyt połączenia
    #  @param p_query Wzór zapytania
    #  @param p_data Dane do zapytania
    #
    #  @return Wynik zapytania
    #
    #  Przykład:
    #  @code
    #       object.execute_sql(db_conn, "INSERT INTO `TABLE` (`COLUMN`) VALUES (%s)", ('VALUE'))
    #  @endcode
    @staticmethod
    def execute_sql(p_connection, p_query, p_data):
        cursor = p_connection.cursor()
        sql = (p_query)
        try:
            cursor.execute(sql, p_data)
            p_connection.commit()
        except (mysql.connector.errors.IntegrityError, psycopg2.IntegrityError):
            p_connection.commit()
            cursor.close()
            return False
        except (mysql.connector.errors.DataError):
            logging.warning(f"Błąd odczytu przy zapytaniu {sql} {p_data}")
            p_connection.commit()
            cursor.close()
            return False
        cursor.close()
        return True

    @staticmethod
    def select_sql(p_connection, p_query):
        cursor = p_connection.cursor(dictionary=True)
        sql = (p_query)
        cursor.execute(sql)
        result = []
        for row in cursor:
            result.append(row)
        return result

    ## Zamiana daty w języku polskim na datę SQL
    #
    #  @param p_str Tekst z datą
    #
    #  @return Data YYYY-MM-DD
    #
    #  Przykład:
    #  @code
    #       l_data = object.to_date("25 stycznia 2017"); # 2017-01-25
    #  @endcode
    @staticmethod
    def to_date(p_str):
        date_pattern = re.compile("([0-9]+) (\w+) ([0-9]+)")
        date_array = date_pattern.findall(p_str)[0]
        months_dict = {"stycznia": 1,
                       "lutego": 2,
                       "marca": 3,
                       "kwietnia": 4,
                       "maja": 5,
                       "czerwca": 6,
                       "lipca": 7,
                       "sierpnia": 8,
                       "września": 9,
                       "października": 10,
                       "listopada": 11,
                       "grudnia": 12}
        month_string = date_array[1].lower().strip()
        month_no = months_dict.get(month_string)

        if not month_no:
            month_no = 0

        return date_array[2] + "-" + str(month_no).zfill(2) + "-"  + (date_array[0]).zfill(2)
