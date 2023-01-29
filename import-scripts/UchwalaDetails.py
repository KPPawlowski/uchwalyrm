import requests
import re

def remove_multiple_spaces(input):
    return " ".join(input.replace("&nbsp;", " ").split())

class UchwalaDetails():
    def __init__(self):
        self.WejscieWZycie = ""
        self.ZDniemPodjecia = False
        self.Ogloszenie = False
        self.OgloszenieUplywDni = 0
        self.OgloszenieUplywMiesiecy = 0
        self.details = dict()
        self.Wykonujacy = ""
        self.PodstawaPrawna = ""
        self.Data = ""
        self.Tytul = ""
        self.NumerUchwaly = ""

    def get_url(self, url):
        self.req = requests.get(url)
        self.content = self.req.content.decode("utf-8")
        self.act_table = self.__substract_act()
        self.__set_fields()

    def __substract_act(self):
        result = []
        content = self.content.replace("&oacute;", "ó").replace("\n", " ").replace("\t", " ").replace("\r", " ").replace("<br />", "\n").replace("</p>", "\n")
        r1 = re.compile("<div class=\"doc-body\">(.*?)<div class=\"doc-info\">", re.DOTALL)
        content_results = r1.findall(content)
        act_content = content_results[0]
        for item in re.sub('<[^<]+?>', '', act_content).strip().split("\n"):
            if item.strip():
                result.append(item.strip())
        return result

    def __set_fields(self):
        i = 0
        for item in self.act_table:
            current_item = remove_multiple_spaces(item.strip())
            if i == 0:
                self.NumerUchwaly = current_item.split(" ")[-1]
            elif i == 2:
                self.Data = current_item.strip().replace("z dnia ", " ");
            elif i == 3:
                self.Tytul = current_item
            elif current_item.find("Na podstawie") == 0:
                it_b = current_item.find("Na podstawie")
                it_e = current_item.rfind("uchwala się")
                if not it_e:
                    it_e = current_item.rfind("Rada Miejska uchwala")
                    if not it_e:
                        it_e = current_item.rfind("Rada Miejska w Złotoryi uchwala")
                self.PodstawaPrawna = current_item[it_b+13:it_e]
            elif current_item.lower().find("wykonanie uchwały") and current_item.lower().find("powierza się") >= 0:
                it = current_item.lower().rfind("powierza się")
                wykonujacy = current_item[it+13:-1]
                if wykonujacy.find("Burmistrzowi") >= 0:
                    wykonujacy = "Burmistrz"
                elif wykonujacy.find("Przewodniczącemu") >= 0:
                    wykonujacy = "Przewodniczący"
                self.Wykonujacy = wykonujacy
            elif current_item.lower().rfind("wchodzi w życie") >= 0:
                it = current_item.lower().rfind("wchodzi w życie")
                wejscie = current_item[it+16:-1]
                if wejscie.find("z dniem podjęcia") >= 0:
                    self.ZDniemPodjecia = True
                    self.Ogloszenie = False
                elif wejscie.find("po upływie") >= 0 and (wejscie.find("ogłoszenia") >= 0 or wejscie.find("publikacji") >= 0):
                    self.Ogloszenie = True
                    if wejscie.find("14 dni") >= 0:
                        self.OgloszenieUplywDni = 14
                    elif wejscie.find("30 dni") >= 0:
                        self.OgloszenieUplywDni = 30
                self.WejscieWZycie = wejscie
            i = i+1
