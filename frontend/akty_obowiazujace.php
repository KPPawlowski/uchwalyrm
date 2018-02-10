<h1>Uchwaly RM w Zlotoryi ogloszone po 2000 roku ktore sa aktami prawa miejscowego i nigdy nie zostaly uchylone</h1>

<?php

    function drukujZmiany(&$db, $numerUchwaly)
    {
	$sth = $db->prepare("SELECT Uchwaly.* FROM UchwalyZmieniajace 
		          JOIN Uchwaly ON UchwalyZmieniajace.NumerUchwaly = Uchwaly.NumerUchwaly
			  WHERE UchwalyZmieniajace.ZmieniaUchwale LIKE '%$numerUchwaly%'
			  ORDER BY DataUchwalenia");
	$sth->execute();
	foreach ($sth->fetchAll(PDO::FETCH_ASSOC) as $row)
	{
		echo("<li>");
		echo($row["NumerUchwaly"]."<br />".$row["AdresPublikacyjny"]."<br />Data Uchwalenia: ".$row["DataUchwalenia"]."<br />Data wejścia w życie: ".$row["WchodziWZycie"]);
		echo("</li>");
	}
    }

    function drukujUchylone(&$db, $numerUchwaly)
    {

 	$sth = $db->prepare("SELECT Uchwaly.* FROM `UchwalyUchylajace` 
		JOIN Uchwaly ON UchwalyUchylajace.UchylaUchwale LIKE CONCAT('%', Uchwaly.NumerUchwaly, '%')  
		WHERE UchwalyUchylajace.`NumerUchwaly` = '$numerUchwaly'
		ORDER BY DataUchwalenia");
        $sth->execute();
        foreach ($sth->fetchAll(PDO::FETCH_ASSOC) as $row)
	{
		echo("<li>");
	     	echo($row["NumerUchwaly"]."<br />".$row["AdresPublikacyjny"]."<br />Data Uchwalenia: ".$row["DataUchwalenia"]."<br />Data wejścia w życie: ".$row["WchodziWZycie"]);
	     	echo("</li>");
	}


    }

    $db = new PDO("mysql:host=localhost;dbname=uchwalyrm; port=3306", 'uchwalyrm', 'DBPASS');
    $db->query("SET CHARACTER SET utf8");
    $db->query("SET NAMES utf8");
    $sth = $db->prepare("SELECT * FROM AktyPrawaMiejscowegoPierwotne WHERE Uchylony IS NULL");
    $sth->execute();

    echo("<table style='border: 1px;'>");
    echo("<tr><td><strong>Numer uchwały</strong></td><td><strong>Tytul</strong></td><td><strong>Adres publikacyjny</strong></td><td><strong>DataUchwalenia</strong></td><td><strong>Ogłoszony</strong></td><td><strong>Wchodzi w życie</strong></td><td><strong>Zmiany do uchwały</strong></td><td><strong>Uchyla uchwały</strong></td><td><strong>Szczegóły uchwały</strong></td></tr>");

    foreach ($sth->fetchAll(PDO::FETCH_ASSOC) as $row)
    {
	echo("<tr>");
	echo("<td width='200' valign='top'>".$row["NumerUchwaly"]."</td>");
	echo("<td width='250' valign='top'>".$row["Tytul"]."</td>");
	echo("<td width='150' valign='top'>".$row["AdresPublikacyjny"]."</td>");
	echo("<td width='100' valign='top'>".$row["DataUchwalenia"]."</td>");
	echo("<td width='100' valign='top'>".$row["Ogloszony"]."</td>");
	echo("<td width='100' valign='top'>".$row["WchodziWZycie"]."</td>");

	echo("<td width='300' valign='top'>");
	drukujZmiany($db, $row["NumerUchwaly"]);
	echo("</td>");

	echo("<td width='300' valign='top'>");
	drukujUchylone($db, $row["NumerUchwaly"]);
	echo("</td>");

	echo("<td width='100' valign='top'><a href='http://lex.kacperpawlowski.pl/#".$row["NumerUchwaly"]."'>Link</a></td>");

	echo("</tr>");
    }

    echo("</table>");

?>
