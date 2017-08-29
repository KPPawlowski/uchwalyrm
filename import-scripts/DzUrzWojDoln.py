#!/usr/bin/python3
# coding=utf8
## @author Kacper Pawłowski
#  Dokumentacja dla modułu DzUrzWojDoln
#
#  Wrapper do zasilania bazy danych z pozycji Dziennika Urzędowego Województwa Dolnośląskiego.

import re
import requests
import json
from IActLawBase import *
from UchwalyRM import *

## Dokumentacja dla kasy DzUrzWojDoln
#
#  Klasa do parsowania pozycji w Dzienniku Urzędowym Województwa Dolnośląskiego
class DzUrzWojDoln(IActLawBase):
    ## Konstruktor klasy
    #
    # Ustawia nagłówki połączenia, wartość tokena, podstawowe zmienne
    def __init__(self):
        super(IActLawBase, self).__init__()
        self.url = "http://edzienniki.duw.pl/duw"
        self.headers = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                      "Chrome/55.0.2883.87 Safari/537.36", 'Connection': "keep-alive",
                        'Referer': self.url}
        self.csession = None
        self.auth_code = None
        self.token = self.get_token()
        self.results = dict()
        self.log_on = True

    ## Pobranie tokena
    #
    # @return   Token
    #
    # Metoda pobiera token wymagany przez API do uzyskania JSON i ustawia go nagłówku HTTP
    def get_token(self):
        token_request = requests.get(url=self.url + "/#/actbymonths", headers=self.headers)
        token_value_regular_expression = re.compile("\"CacheSession\":\"(.*?)\",\"AntiForgeryToken\":\"(.*?)\"")
        token = token_value_regular_expression.findall(token_request.text)[0]
        self.csession = token[0]
        self.auth_code = token[1]
        self.headers['RequestVerificationToken'] = "authentication" + self.auth_code
        return token

    ## Pobranie zawartości dziennika w JSON
    #
    # @param    p_year          Rok w Dz. Urz. (liczba)
    # @param    p_month         Miesiąc w Dz. Urz. (miesiąc)
    # 
    # Ustawia jako pole results tablicę dwuwymiarową według roku i miesiąca z pozycjami z Dziennika Urzędowego
    def get_json(self, p_year, p_month):
        headers = dict(self.headers)
        headers.update({'Accept': "application/json, text/plain, */*",
                        'Accept-Encoding': "gzip, deflate, sdch",
                        'Accept-Language' : "pl-PL,pl;q=0.8,en-US;q=0.6,en;q=0.4"})
        params = ({'year': p_year,
                   'month': p_month,
                   'isList': "true",
                   'Csession': self.csession})
        json_request = requests.get(url=self.url + "/api/positions",
                                    params=params,
                                    headers=headers)
        json_object = json_request.json()
        year, month = json_object['Year'], json_object['Month']
        if not self.results.get(year):
            self.results[year] = dict()
        if not self.results[year].get(month):
            self.results[year][month] = []
        self.results[year][month] = json_object

    ## Zapisanie pobranych wyników do bazy danych
    #
    # @param    p_year          Rok (liczba), którego dotyczą pozycje w Dz. Urz.
    # @param    p_month         Miesiąc (liczba), którego dotyczą pozycje w Dz. Urz.
    # @param    p_dbms          Nazwa DBMS (do wyboru: mysql, pgsql)
    # @param    p_param_values  Parametry do połączenia z DBMS
    # 
    # Przykład:
    # @code
    #   p_paramValues = {'mysql': {'db_host': 'localhost', 'db_name': '', 'user': '', 'password': ''}, 
    #                    'pgsql': {'db_host': 'localhost', 'db_name': '', 'user': '', 'password': ''}}
    #   object.insertDB(p_year, p_month, 'mysql', p_param_values)
    # @endcode
    # Metoda parsująca listę pobranych wyników i dokunująca wstawienia ich do tabeli bazy danych 
    def insert_db (self, p_year, p_month, p_dbms, p_param_values):
        connection = self.create_connection(p_dbms, p_param_values)
        for i_position_item in self.results[p_year][p_month]["Positions"]:
            item_json, position_title, legal_act_type, duplicate_char, publication_date, journal_number, act_type_id, act_date, pdf_book_url_list_url, pdf_book_url_list_name, position, day, month, year, oid, has_expired, publishers_list, publishers_list_l, publisher, publishers_list_flat, case_number, pdf_url, subject, is_technical_position, is_urmz = str(i_position_item), i_position_item.get("Title"), i_position_item.get("LegalActType"), i_position_item.get("DuplicateChar"), i_position_item.get("PublicationDate"), i_position_item.get("JournalNumber"), i_position_item.get("ActTypeId"), i_position_item.get("ActDate"), None, None, i_position_item.get("Position"), i_position_item.get("Day"), i_position_item.get("Month"), i_position_item.get("Year"), i_position_item.get("Oid"), str(i_position_item.get("HasExpired"))[0], str(i_position_item.get("PublishersList")), i_position_item.get("PublishersList"), i_position_item.get("Publisher"), i_position_item.get("PublishersListFlat"), i_position_item.get("CaseNumber"), i_position_item.get("PdfUrl"), i_position_item.get("Subject"), str(i_position_item.get("IsTechnicalPosition"))[0], False
            if i_position_item.get("PdfBookUrlList") is not None and len(i_position_item.get("PdfBookUrlList")) > 0:
                pdf_book_url_list_url, pdf_book_url_list_name = i_position_item.get("PdfBookUrlList")[0].get("Url"), i_position_item.get("PdfBookUrlList")[0].get("Name")
            for i_publisher_iterator in publishers_list_l:
                publisher_oid, publisher_name = i_publisher_iterator.get("Oid"), i_publisher_iterator.get("Name")
                if publisher_oid in (157, 711):
                    is_urmz = True
                if not self.execute_sql(connection, "INSERT INTO DzUrzWojDolnOrgany (Oid, Name, DzUrzWojnDolnOid) VALUES (%s, %s, %s)", (publisher_oid, publisher_name, oid)):
                    self.log("- Nie dodano oznaczen (" + str(publisher_oid) + "," + publisher_name + "," + str(oid) + ")")
            if not self.execute_sql(connection, "INSERT INTO DzUrzWojDoln "
                                                 "(JSON, Title, LegalActType, DuplicateChar, PublicationDate, ActDate, Oid, Year, Month, Day, Position, JournalNumber, ActTypeId, PdfBookUrlListUrl, PdfBookUrlListName, IsTechnicalPosition, Subject, PdfUrl, CaseNumber, PublishersListFlat, Publisher, PublishersList, HasExpired) "
                                                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                    (item_json, position_title, legal_act_type, duplicate_char, publication_date, act_date, oid, year, month, day, position, journal_number, act_type_id, pdf_book_url_list_url, pdf_book_url_list_name, is_technical_position, subject, pdf_url, case_number, publishers_list_flat, publisher, publishers_list, has_expired)):
                self.log("- Nie wstawiono %s" % (str(position)))
            if is_urmz and p_dbms == 'mysql':
                UchwalyRM.update_dzurz_position(connection, publication_date, year, position, case_number, p_parent=self)
        connection.close()

    ## Zwraca słownik z podziałem na publikujących
    #
    # @param    p_year          Rok w Dz. U.
    # @param    p_month         Miesiąc w Dz. U.
    # @return   Słownik, którego kluczem są nazwy organów a w nim lista pozycji dla poszczególnego roku i miesiąca
    # W wynikowym słownikowym znajdują pozycje pogrupowane organami publikującymi w Dz. Urz. pozycje dla podanego miesiąca i roku
    def return_months_publishers(self, p_year, p_month):
        if self.results.get(p_year) and self.results.get(p_year).get(p_month) \
                and self.results.get(p_year).get(p_month).get("Positions"):
            publishers = dict()
            for i_position_item in self.results[p_year][p_month]["Positions"]:
                if i_position_item.get("PublishersList"):
                    for i_publisher_iterator in i_position_item.get("PublishersList"):
                        if i_publisher_iterator.get("Name"):
                            publisher_name = i_publisher_iterator.get("Name")
                            if publishers.get(publisher_name) is None:
                                publishers[publisher_name] = []
                            publishers[publisher_name].append(i_position_item)
            return publishers
        return dict()
