#!/usr/bin/python3
## @author Kacper Pawłowski
# Dokumentacja dla modułu UchwalyRM
#
# Wrapper do zasilania bazy danych z BIP-a UM w Złotoryi uchwałami i protokołami
# coding=utf8
import re
import requests
from IActLawBase import *

## Klasa do obsługi ostatnich uchwał i protokołów z BIP UM w Złotoryi
#
# @related IActLawBase
# Wrapper do zasilania bazy danych z BIP Urzędu Miejskiego w Złotoryi listą uchwał oraz protokołów.
class UchwalyRM(IActLawBase):
    ## Konstruktor
    #
    # @param p_dbms Nazwa DBMS (do wyboru: mysql, pgsql)
    # @param p_param_values Parametry połączenia z bazą danych
    # Utworzenie połączenia z bazą danych, pobranie listy ostatnich uchwał, utworzenie wzorców wyrażeń regularnych
    def __init__(self, p_dbms, p_param_values):
        super(IActLawBase, self).__init__()
        self.log_on = True
        self.site_url = "http://zlotoryja.bip.info.pl/"
        self.acts_list = dict()
        self.protocol_list = dict()
        self.database_connection = self.create_connection(p_dbms, p_param_values)
        self.acts_links_regular_expression = re.compile("<td><a .*?href='(dokument\.php\?iddok\=[0-9]+)"
                                                        ".*?' .*?>(.*)</a></td>")
        self.acts_title_regular_expression = re.compile("^(Uchwała|UCHWAŁA)[ ]*(NR|nr|Nr|)[ ]*(.*?) .*? z dnia "
                                                        "(.*?) r\.(.*?)$")
        self.protocols_item_regular_expression = re.compile("<a.*?href=\'(dokument.php\?iddok\=[0-9]+).*?\'.*?>.*?"
                                                            "([XIVLMCDM]+)[\.\/](20[0-2][0-9]).*?([0-9]{1,2} [a-zA-Zźńś]+ "
                                                            "20[0-9]+).*?</a>",
                                                            re.MULTILINE)
        self.encode_charset = "utf-8"

    ## Destruktor
    #
    # Kończy połączenie z bazą danych
    def __del__(self):
        self.database_connection.close()

    ## Pobranie listy uchwał z danej strony
    #
    # @param p_page Strona, z której pobieramy
    def get_acts_list(self, p_page=1):
        acts_list_request = requests.get("%sindex.php" % self.site_url,
                                         params={'idmp': '308',
                                                 'r': 'o',
                                                 'istr': str(p_page)})
        self.acts_list[p_page] = self.acts_links_regular_expression.findall(acts_list_request.text)

    ## Pobranie listy protokołów z danej strony
    #
    # @param p_page Strona, z której pobieramy
    def get_protocol_list(self, p_page=1):
        protocol_list_request = requests.get("%sindex.php" % self.site_url,
                                             params={'idmp': '166',
                                                     'r': 'o',
                                                     'istr': str(p_page)})
        self.protocol_list[p_page] = self.protocols_item_regular_expression.findall(protocol_list_request.text)

    ## Dodaje protokół do bazy danych
    #
    # Dodaje protokół do tabeli UchwalyProtokoly
    def insert_protocol(self, p_session_number, p_session_year, p_session_date, p_protocol_url, p_protocol_text):
        return self.execute_sql(self.database_connection,
                               "INSERT INTO UchwalyProtokoly (SesjaNr, SesjaRok, Data, Link, Tekst) "
                               "VALUES (%s, %s, %s, %s, %s)",
                                (p_session_number, p_session_year, p_session_date, p_protocol_url, p_protocol_text))

    ## Dodaje uchwałę do bazy danych
    #
    # Dodaje uchwałę do tabeli Uchwaly
    def insert_act(self, p_act_number, p_act_date, p_act_title):
        return self.execute_sql(self.database_connection,
                               "INSERT INTO Uchwaly (NumerUchwaly, DataUchwalenia, Tytul) VALUES (%s, %s, %s)",
                                (p_act_number, p_act_date, p_act_title))

    ## Dodaje link do uchwały do bazy danych
    #
    # Dodaje link do uchwały do tabeli UchwalyLinki
    def insert_act_url(self, p_act_number, p_act_url):
        return self.execute_sql(self.database_connection,
                               "INSERT INTO UchwalyLinki (NumerUchwaly, URL) VALUES (%s, %s)",
                                (p_act_number, p_act_url))

    ## Aktualizuje link do uchwały do bazy danych
    #
    # Aktualizuje link do uchwały w tabeli UchwalyLinki
    def update_act_url(self, p_act_number, p_act_url):
        return self.execute_sql(self.database_connection,
                               "UPDATE UchwalyLinki SET URL = %s WHERE NumerUchwaly = %s",
                                (p_act_number, p_act_url))

    ## Dodaje zbuforowane uchwały do bazy danych
    #
    # @related insert_act
    # @related update_act_url
    # @related insert_act_url
    # Dodaje do bazy danych zbuforowane uchwały, wykonuje insert_act, insert_act_url, update_act_url
    def insert_acts(self):
        for i_pages_acts_links in list(self.acts_list.values()):
            for i_acts_links in i_pages_acts_links:
                act = self.acts_title_regular_expression.findall(i_acts_links[1])[0]
                if self.insert_act(act[2], self.to_date(act[3]), act[4].strip()):
                    self.log("+ Dodano uchwale %s" % (act[2]))
                else:
                    self.log("- Nie dodano uchwaly %s" % (act[2]))
                if self.insert_act_url(act[2], self.site_url + i_acts_links[0]):
                    self.log("+ Dodano link %s" % (act[2]))
                else:
                    if self.update_act_url(act[2], self.site_url + i_acts_links[0]):
                        self.log("+ Zmodyfikowano link %s" % (act[2]))
                    else:    
                        self.log("- Nie dodano ani nie zaaktualizowano linku %s" % (act[2]))
        self.database_connection.commit()

    ## Dodaje protokoły zbuforowane do bazy danych
    #
    # Dodaje protokoły z bufora
    def insert_protocols(self):
        for i_pages_protocol in list(self.protocol_list.values()):
            for i_protocol in i_pages_protocol:
                if self.insert_protocol(i_protocol[1], i_protocol[2], self.to_date(i_protocol[3]), self.site_url + i_protocol[0], ''):
                    self.log("+ Dodano protokol %s z %s" % (i_protocol[1], i_protocol[2]))
                else:
                    self.log("- Nie dodano protokołu %s z %s" % (i_protocol[1], i_protocol[2]))
        self.database_connection.commit()
    ## W metryce uchwały pojawia się odniesienie do odpowiedniej pozycji w Dz.Urz.
    #
    # @param p_connection Uchwyt do połączenia z DBMS
    # @param p_publication_date Data ogołoszenia w Dzienniku
    # @param p_year Rok Dziennika
    # @param p_position Pozycja, pod którą ogłoszono
    # @param p_case_number Sygnatura aktu
    # @param p_parent Obiekt powiązany z DzUrzWojDoln
    @staticmethod
    def update_dzurz_position(p_connection, p_publication_date, p_year, p_position, p_case_number, p_parent=None):
        if not p_parent:
            p_parent = self
        if p_parent.execute_sql(p_connection, "UPDATE Uchwaly SET Ogloszony = %s, WchodziWZycie = %s + INTERVAL 15 DAY, AdresPublikacyjny = %s "
                                               "WHERE NumerUchwaly = %s", (p_publication_date[0:10], p_publication_date[0:10], "DZ. URZ. WOJ. " \
                                               + str(p_year) + "." + str(p_position), p_case_number)):
            p_parent.log("Zaaktualizowano DZ. URZ. WOJ. %s.%s" % (str(p_position), str(p_year)))
        else:
            p_parent.log("Nie zaaktualizowano DZ. URZ. WOJ. %s.%s" % (str(p_position), str(p_year)))
