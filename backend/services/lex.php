<?php

/* disable class when Service class is not available  */
if (!class_exists("Service"))
    return;

function generuj_dz_u($rok, $nr, $poz) {
    $nr = "$nr";
    $poz = "$poz";
    $res1 = "000";
    $res2 = "0000";

    if (strlen($nr) > 3 || strlen($poz) > 4)
        return "";

    for ($i = 1; $i <= strlen($nr); $i++) {
        $res1[strlen($res1) - $i] = $nr[strlen($nr) - $i];
    }

    for ($i = 1; $i <= strlen($poz); $i++) {
        $res2[strlen($res2) - $i] = $poz[strlen($poz) - $i];
    }

    $nr = $res1;
    $poz = $res2;

    return "http://isap.sejm.gov.pl/DetailsServlet?id=WDU{$rok}{$nr}$poz";
}

function generuj_dz_u_str($str) {

    $pattern = "/Dz\.[ ]*U\.[ ]*z[ ]*([0-9]{4})[ ]*[r\.]*[, ]*([nN]r ([0-9]+))*[, ]*poz[\. ]*([0-9]+)/i";
    preg_match_all($pattern, $str, $res);

    if (count($res)) {
        $rok = (string) $res[1][0];
        $nr = (string) $res[3][0];
        $poz = (string) $res[4][0];
        return "<a href='" . generuj_dz_u($rok, $nr, $poz) . "'>$str</a>";
    }
    return "";
}

function change_dz_u_str($str) {
    $pattern = "/Dz\.[ ]*U\.[ ]*z[ ]*([0-9]{4})[ ]*[r\.]*[, ]*([nN]r ([0-9]+))*[, ]*poz[\. ]*([0-9]+)/i";
    return preg_replace_callback($pattern, function($matches) {
        return generuj_dz_u_str($matches[0]);
    }, $str);
}

/* definition class */

class Lex extends Service {

    private $db;

    public function __construct($ctrl) {
        parent::__construct($ctrl);
        $this->db = new PDO("mysql:host=localhost;dbname=uchwalyrm; port=3306", 'uchwalyrm', 'DBPASS');
        $this->db->query("SET CHARACTER SET utf8");
        $this->db->query("SET NAMES utf8");
    }

    private function decodeNumber($number) {
        $number = str_replace(array("'", "\\"), "", $number);
        $arr_1 = explode("/", $number);
        $arr_2 = explode(".", $number);

        if (count($arr_2) == 4) {
            $year = $arr_2[3];
            $session = $arr_2[1];
        } else if (count($arr_1) == 3) {
            $year = $arr_1[2];
            $session = $arr_1[0];
        }

        return array($year, $session);
    }

    public function executeGetListLexes() {
        $date = "";
        $name = "";

        if ($this->inputJSON["date"]) {
            $date = $this->inputJSON["date"];
        }

        if ($this->inputJSON["name"]) {
            $name = $this->inputJSON["name"];
        }

        if (count($this->inputPath) >= 1) {
            $date = $this->inputPath[0];
        }

        $result = array();

        if (!preg_match("/(\d{4})/", $date) && !preg_match("/(\d{4})-(\d{2})-(\d{2})/", $date))
            $date = "";

        $stmt = $this->db->prepare("SELECT `Uchwaly`.`NumerUchwaly`, `Uchwaly`.`DataUchwalenia`, `Uchwaly`.`Tytul`, `UchwalyTagiNS`.`Tagi` FROM `Uchwaly` LEFT JOIN `UchwalyTagiNS` ON `UchwalyTagiNS`.`NumerUchwaly` = `Uchwaly`.`NumerUchwaly` WHERE (`Uchwaly`.`Tytul` LIKE :name OR `Uchwaly`.`NumerUchwaly` LIKE :name OR `UchwalyTagiNS`.`Tagi` LIKE :name) AND `Uchwaly`.`DataUchwalenia` LIKE :date ORDER BY DataUchwalenia DESC, CONVERT(substring_index(substring_index(`Uchwaly`.`NumerUchwaly`,'.',-2),'.',1),UNSIGNED INTEGER) DESC, CONVERT(substring_index(substring_index(`Uchwaly`.`NumerUchwaly`,'/',-2),'/',1),UNSIGNED INTEGER) DESC");

        $date = "%$date%";
        $name = "%$name%";

        $stmt->bindParam(':date', $date, PDO::PARAM_STR);
        $stmt->bindParam(':name', $name, PDO::PARAM_STR);
        $stmt->execute();

        $i = 0;

        foreach ($stmt->fetchAll(PDO::FETCH_ASSOC) as $row) {
            $result[$i++] = array("NumerUchwaly" => $row["NumerUchwaly"], "DataUchwalenia" => $row["DataUchwalenia"], "Tytul" => $row["Tytul"], "Tagi" => $row["Tagi"]);
        }

        $stmt->closeCursor();
        $this->setData($result);
        return $this->setStatusOK();
    }

    public function executeGetListDates() {
        $result = array();
        $i = 0;

        foreach ($this->db->query("SELECT a.Data FROM (SELECT YEAR(DataUchwalenia) AS `Data` FROM Uchwaly UNION SELECT DATE(DataUchwalenia) AS `Data` FROM Uchwaly) AS a GROUP by a.Data ORDER BY a.Data DESC") as $row)
            $result[$i++] = $row[0];
        $this->setData($result);
        return $this->setStatusOK();
    }

    protected function executeDerogatesLexes() {
        if (count($this->inputPath) >= 1) {
            $number = $this->inputPath[0];
            $number = str_replace("_", "/", $number);
            $number = str_replace("-", ".", $number);
        } else
            return $this->setStatusError();

        $this->setData($this->showDerogatesLexes($number));
        return $this->setStatusOK();
    }

    protected function executeChangesLexes() {
        if (count($this->inputPath) >= 1) {
            $number = $this->inputPath[0];
            $number = str_replace("_", "/", $number);
            $number = str_replace("-", ".", $number);
        } else
            return $this->setStatusError();

        $this->setData($this->showChangesLexes($number));
        return $this->setStatusOK();
    }

    protected function executeGetLex() {
        if (count($this->inputPath) >= 1) {
            $number = $this->inputPath[0];
            $number = str_replace("_", "/", $number);
            $number = str_replace("-", ".", $number);
        } else
            return $this->setStatusError();

        $number = str_replace(array("'", "\\"), "", $number);
        $yearSession = $this->decodeNumber($number);
        $result = array();
        $year = $yearSession[0];
        $session = $yearSession[1];

        $sth = $this->db->prepare("SELECT `Uchwaly`.`NumerUchwaly` AS `NumerUchwaly`,`Uchwaly`.`DataUchwalenia` AS `DataUchwalenia`,`Uchwaly`.`Tytul` AS `Tytul`,`Uchwaly`.`TekstJednolity`,`Uchwaly`.`AdresPublikacyjny` AS `AdresPublikacyjny`,`Uchwaly`.`Ogloszony`,`Uchwaly`.`WchodziWZycie`,`UchwalyObowiazywanie`.`Obowiazywanie` AS `Obowiazywanie`,`UchwalyLinki`.`URL` AS `URL`,`UchwalyPodstawaPrawna`.`PodstawaPrawna` AS `PodstawaPrawna`,`UchwalyRNAU`.`RozstrzygniecieNadzorczeAktUchylajacy` AS `RNAU`,`UchwalyZmieniajace`.`ZmieniaUchwale` AS `ZmieniaUchwale`,`UchwalyUchylajace`.`UchylaUchwale` AS `UchylaUchwale`,`UchwalyTagiNS`.`Tagi` AS `Tagi`, `UchwalyOpisy`.`Opis` AS `Opis`, `UchwalyWynikiGlosowan`.`Glosowalo` AS `Glosowalo`,`UchwalyWynikiGlosowan`.`Za` AS `Za`,`UchwalyWynikiGlosowan`.`Przeciw` AS `Przeciw`,`UchwalyWynikiGlosowan`.`Wstrzymujacy` AS `Wstrzymujacy`,`UchwalyWynikiGlosowan`.`KtoZa` AS `KtoZa`,`UchwalyWynikiGlosowan`.`KtoPrzeciw` AS `KtoPrzeciw`,`UchwalyWynikiGlosowan`.`KtoWstrzymujacy` AS `KtoWstrzymujacy`,`UchwalyWynikiGlosowan`.`KtoNieobecny` AS `KtoNieobecny`, `UchwalyProtokoly`.`Link` AS `ProtokolURL`, `Uchwaly`.`Uzasadnienie` AS `Uzasadnienie` FROM `Uchwaly` LEFT JOIN `UchwalyObowiazywanie` ON `Uchwaly`.`NumerUchwaly` = `UchwalyObowiazywanie`.`NumerUchwaly` LEFT JOIN `UchwalyLinki` ON `Uchwaly`.`NumerUchwaly` = `UchwalyLinki`.`NumerUchwaly` LEFT JOIN `UchwalyPodstawaPrawna` ON `Uchwaly`.`NumerUchwaly` = `UchwalyPodstawaPrawna`.`NumerUchwaly` LEFT JOIN `UchwalyRNAU` ON `Uchwaly`.`NumerUchwaly` = `UchwalyRNAU`.`NumerUchwaly` LEFT JOIN `UchwalyTagiNS` ON `Uchwaly`.`NumerUchwaly` = `UchwalyTagiNS`.`NumerUchwaly` LEFT JOIN `UchwalyUchylajace` ON `Uchwaly`.`NumerUchwaly` = `UchwalyUchylajace`.`NumerUchwaly` LEFT JOIN `UchwalyZmieniajace` ON `Uchwaly`.`NumerUchwaly` = `UchwalyZmieniajace`.`NumerUchwaly` LEFT JOIN `UchwalyWynikiGlosowan` ON `Uchwaly`.`NumerUchwaly` = `UchwalyWynikiGlosowan`.`NumerUchwaly` LEFT JOIN `UchwalyProtokoly` ON `UchwalyProtokoly`.`SesjaNr` = :session AND `UchwalyProtokoly`.`SesjaRok` = :year LEFT JOIN `UchwalyOpisy` ON `UchwalyOpisy`.`NumerUchwaly` = `Uchwaly`.`NumerUchwaly` WHERE `Uchwaly`.`NumerUchwaly` = :number");
        $sth->bindParam(':session', $session, PDO::PARAM_STR);
        $sth->bindParam(':number', $number, PDO::PARAM_STR);
        $sth->bindParam(':year', $year, PDO::PARAM_INT);
        $sth->execute();

        $row = $sth->fetch(PDO::FETCH_ASSOC);
        if ($row)
            $result = array_merge($row, array("UchylonaPrzez" => $this->showDerogatesLexes($row["NumerUchwaly"]), "ZmienionaPrzez" => $this->showChangesLexes($row["NumerUchwaly"])));

        $this->setData($result);
        return $this->setStatusOK();
    }

    protected function executeGetLaterLexes() {
        if (count($this->inputPath) >= 1) {
            $number = $this->inputPath[0];
            $number = str_replace("_", "/", $number);
            $number = str_replace("-", ".", $number);
        } else
            return $this->setStatusError();
        $result = array_merge($this->showChangesLexes($number), $this->showDerogatesLexes($number));
        $this->setData($result);
        return $this->setStatusOK();
    }

    protected function executeGetLeastLexes() {
        if (count($this->inputPath) >= 1) {
            $number = $this->inputPath[0];
            $number = str_replace("_", "/", $number);
            $number = str_replace("-", ".", $number);
        } else
            return $this->setStatusError();

        $str = "";
        $result = array();
        $i = 0;

        $stmt = $this->db->prepare("SELECT GROUP_CONCAT(a.`Uchwala` SEPARATOR ',') AS `Uchwala` FROM (SELECT UchylaUchwale AS `Uchwala` FROM `UchwalyUchylajace` WHERE `NumerUchwaly` = :number UNION SELECT ZmieniaUchwale AS `Uchwala` FROM `UchwalyZmieniajace` WHERE `NumerUchwaly` IN (:number) OR `NumerUchwaly` IN (SELECT `UchylaUchwale` FROM `UchwalyUchylajace` WHERE `NumerUchwaly` = :number)) AS a");
        $stmt->bindParam(':number', $number, PDO::PARAM_STR);
        $stmt->execute();


        foreach ($stmt->fetchAll() as $row) {
            $str = str_replace(" ", "", "'" . str_replace(",", "','", $row["Uchwala"]) . "'");
        }

        $stmt = $this->db->prepare("SELECT * FROM Uchwaly WHERE NumerUchwaly IN ($str) ORDER BY DataUchwalenia ASC");
        $stmt->execute();

        foreach ($stmt->fetchAll() as $row) {
            $result[$i++] = array($row["NumerUchwaly"], $row["DataUchwalenia"], $row["Tytul"]);
        }

        $this->setData($result);
        return $this->setStatusOK();
    }

    protected function executeGetFile() {
        $id = $this->inputJSON["link"];
        $id = str_replace("http://zlotoryja.bip.info.pl/", "", $id);
        $id = str_replace("http://www.zlotoryja.bip.info.pl/", "", $id);

        $id = str_replace("\x00", "", $id);
        $filename = "services/lex/downloads/" . $id;

        if (!file_exists($filename)) {
            file_put_contents($filename, file_get_contents("http://zlotoryja.bip.info.pl/$id"));
        }

        $content = change_dz_u_str(file_get_contents($filename));

        if (strlen($content))
            $this->setData(array("content" => $content));
        return $this->setStatusOK();
    }

    protected function showChangesLexes($number = "") {
        $result = array();
        $i = 0;
        $stmt = $this->db->prepare("SELECT `Uchwaly`.`NumerUchwaly`, `Uchwaly`.`DataUchwalenia`, `Uchwaly`.`Tytul` FROM `Uchwaly` LEFT JOIN UchwalyZmieniajace ON Uchwaly.NumerUchwaly = UchwalyZmieniajace.NumerUchwaly WHERE UchwalyZmieniajace.ZmieniaUchwale REGEXP :number ORDER BY DataUchwalenia ASC");
        $number = "(^|, )" . str_replace(array("\"", "\\"), "", $number) . "(,|$)";
        $stmt->bindParam(':number', $number, PDO::PARAM_STR);
        $stmt->execute();

        foreach ($stmt->fetchAll(PDO::FETCH_ASSOC) as $row)
            $result[$i++] = array($row["NumerUchwaly"], $row["DataUchwalenia"], $row["Tytul"]);
        return $result;
    }

    protected function showDerogatesLexes($number = "") {
        $result = array();
        $i = 0;
        $stmt = $this->db->prepare("SELECT `Uchwaly`.`NumerUchwaly`, `Uchwaly`.`DataUchwalenia`, `Uchwaly`.`Tytul` FROM `Uchwaly` LEFT JOIN UchwalyUchylajace ON Uchwaly.NumerUchwaly = UchwalyUchylajace.NumerUchwaly WHERE UchwalyUchylajace.UchylaUchwale REGEXP :number");
        $number = "(^|, )" . str_replace(array("\"", "\\"), "", $number) . "(,|$)";
        $stmt->bindParam(':number', $number, PDO::PARAM_STR);
        $stmt->execute();

        foreach ($stmt->fetchAll(PDO::FETCH_ASSOC) as $row)
            $result[$i++] = array($row["NumerUchwaly"], $row["DataUchwalenia"], $row["Tytul"]);

        return $result;
    }

}

?>
