var uchwalyApp = angular.module('uchwalyApp', ['ngSanitize', 'cgNotify', 'ajoslin.promise-tracker', 'ngCsv']);

var ctrl = uchwalyApp.controller('UchwalyCtrl', ['$scope', '$http', 'notify', 'promiseTracker', function ($scope, $http, notify, promiseTracker) {
        /* variables */
        $scope.loadingTracker = promiseTracker();
        $scope.limitedList = [];
        $scope.lexOption = 0;
        $scope.limitedListChbx = false;
        $scope.showAct = false;
        $scope.actNo = null;
        $scope.menuShow = true;
        $scope.url = document.URL.split('#');
        $scope.sitename = "Przeglądarka uchwał Rady Miejskiej w Złotoryi";
        $scope.text = "Od marca 2015 r. w Złotoryi funkcjonuje Obywatelska Inicjatywa Uchwałodawcza. <strong>Aplikacja została opracowana <i>pro publico bono</i> aby ułatwić społeczności lokalnej wyszukiwanie uchwał Rady Miejskiej w Złotoryi. W swoim zamierzeniu ma zwiększyć zainteresowanie prawem lokalnym i obywatelską inicjatywą uchwałodawczą, a także pomóc adresatom lokalnych norm prawnych zapoznanie się z nimi.</strong>";
        $scope.content = null;
        $scope.ordActNo = '';
        $scope.showInstruction = false;
        $scope.controllerURL = 'http://api.kacperpawlowski.pl/lex/';
        $scope.mainURL = "http://lex.kacperpawlowski.pl/";
        $scope.showSearch = false;
        $scope.searchClass = "form-group has-success has-feedback"; // 
        $scope.error = false;
        $scope.searchStatus = true;

        /* json init datas */
        $http.get($scope.controllerURL + 'getListLexes', {tracker: $scope.loadingTracker}).success(function (response, status) {
            $scope.list = response.data;
            notify('W bazie mamy ' + response.data.length.toString() + ' uchwał');
            console.log(response.data.length);
            for (var i = 0; i < $scope.list.length; i++) {
                if (i == 1)
                    break;
                $scope.message = "Ostatnio dodano: Uchwała nr " + $scope.list[i].NumerUchwaly + " " + $scope.list[i].Tytul;
                notify({
                    message: $scope.message,
                    classes: $scope.classes,
                    scope: $scope,
                    templateUrl: '',
                    position: 'center',
                    duration: 8000
                });
            }
        });

        $http.get($scope.controllerURL + 'getListDates', {tracker: $scope.loadingTracker}).success(function (response, status) {
            $scope.dates = response.data;
        });

        /* functions */

        $scope.print = function () {
            window.print();
        };

        $scope.dataPl = function (data) {
            if (!data) {
                return "";
            }
            
            var Rok = data.substr(0,4);
            var Miesiac = data.substr(5,2);
            var Dzien = data.substr(8,2);
            var MiesiacPl = "";
            
            switch(Miesiac)
            {
                case "01":
                    MiesiacPl = "stycznia";
                    break;
                case "02":
                    MiesiacPl = "lutego";
                    break;
                case "03":
                    MiesiacPl = "marca";
                    break;
                case "04":
                    MiesiacPl = "kwietnia";
                    break;
                case "05":
                    MiesiacPl = "maja";
                    break;
                case "06":
                    MiesiacPl = "czerwca";
                    break;
                case "07":
                    MiesiacPl = "lipca";
                    break;
                case "08":
                    MiesiacPl = "sierpnia";
                    break;
                case "09":
                    MiesiacPl = "września";
                    break;
                case "10":
                    MiesiacPl = "października";
                    break;
                case "11":
                    MiesiacPl = "listopada";
                    break;
                case "12":
                    MiesiacPl = "grudnia";
                    break;
            }
            
            if(Dzien[0] == "0") {
                Dzien = Dzien.substr(1,1);
            }
            
            return Dzien + " " + MiesiacPl + " " + Rok;
        };
        
        $scope.toggleInformation = function (data) {
            if (!$scope.showInstruction)
                $scope.showInstruction = true;
            else
                $scope.showInstruction = false;
            console.log($scope.results);
        };

        $scope.toggleSearch = function (data) {
            if (!$scope.showSearch)
                $scope.showSearch = true;
            else
                $scope.showSearch = false;
        };

        $scope.changeSearch = function (data) {
            $scope.searchTextField = data;
            $scope.showAct = false;
            $scope.limitedList = [];
            $scope.limitedListChbx = false;
        };

        $scope.sort = function (data) {
            switch (data) {
                case 'NumerUchwaly':
                    $scope.ordActNo = (($scope.ordActNo == '-NumerUchwaly') ? '+NumerUchwaly' : '-NumerUchwaly');
                    $scope.ord = $scope.ordActNo;
                    break;
                case 'DataUchwalenia':
                    $scope.ordDate = (($scope.ordDate == '-DataUchwalenia') ? '+DataUchwalenia' : '-DataUchwalenia');
                    $scope.ord = $scope.ordDate;
                    break;
                case 'Tytul':
                    $scope.ordTitle = (($scope.ordTitle == '-Tytul') ? '+Tytul' : '-Tytul');
                    $scope.ord = $scope.ordTitle;
                    break;
            }

            window.history.pushState({}, "", "#");
        };

        $scope.isOnLimitedList = function (data) {
            return (($scope.limitedList.indexOf(data) >= 0) || (!$scope.limitedListChbx));
        };

        $scope.searchLex = function () {
            $scope.error = false;
            $scope.showAct = false;
            $scope.limitedList = [];
            $scope.limitedListChbx = false;
            window.history.pushState({}, "", "#");
        };

        $scope.reset = function () {
            $scope.error = false;
            $scope.searchTextField = "";
            $scope.searchDateField = "";
            $scope.showAct = false;
            $scope.limitedList = [];
            $scope.limitedListChbx = false;
            window.history.pushState({}, "", "#");
        };

        $scope.goToBIP = function (data) {
            window.open($scope.content.URL, '_blank');
        };

        $scope.goToAuthorPage = function (data) {
            window.open("http://złotoryja.pl/asp/pl_start.asp?typ=14&menu=214&strona=1", '_blank');
        };

	$scope.createLinkDUW = function(adr) {
	    if(adr) {
		pattern = /([0-9]{4})\.([0-9]+)\.*([0-9]*)/i;
		no = adr.replace("DZ. URZ. WOJ. ", "").trim();
		numbers = pattern.exec(no);
		number = parseInt(numbers[2]);
		year = parseInt(numbers[1]);

		if(year == 2000) {
		    return "http://oi.uwoj.wroc.pl/dzienniki/Dzienniki/Dz" + numbers[2] + "/poz" + numbers[3] + "/poz" + numbers[3] + ".html";
		}
		else if(year >= 2001 && year <= 2004) {
		    if((number >= 229 && year == 2002) || year >= 2003) {
			filetype = "html"
			if((number < 49 || number >= 65) && year == 2003) {
				filetype = "htm"
			}
			return "http://oi.uwoj.wroc.pl/dzienniki/Dzienniki" + numbers[1] + "/" + numbers[2].padStart(3,"0") + "/" + numbers[3] + "." + filetype;
		    }
		    return "http://oi.uwoj.wroc.pl/dzienniki/Dzienniki" + numbers[1] + "/" + numbers[2] + "/" + numbers[3] + "/" + numbers[3] + ".htm";
		} else { 
		    return "http://edzienniki.duw.pl/legalact/" + no.replace(".", "/");
		}
	    }
	    return "";
	}

        $scope.openAct = function (number) {
            $scope.error = false;
            $scope.content = null;
            $scope.actNo = number.trim();
            var oldActNo = $scope.actNo;

            $http.get($scope.controllerURL + 'getLex/' + $scope.actNo.replace(/\./g, "-").replace(/\//g, "_"), {tracker: $scope.loadingTracker}).success(function (data_in) {
                var data = data_in.data;
                $scope.content = data;
		$scope.content.AdrPubURL = $scope.createLinkDUW($scope.content.AdresPublikacyjny);
		$scope.content.TekstJednURL = $scope.createLinkDUW($scope.content.TekstJednolity);
                $scope.content.UchylaUchwale = (($scope.content.UchylaUchwale) ? $scope.content.UchylaUchwale.split(",") : null);
                $scope.content.ZmieniaUchwale = (($scope.content.ZmieniaUchwale) ? $scope.content.ZmieniaUchwale.split(",") : null);
                $scope.content.Tagi = (($scope.content.Tagi) ? $scope.content.Tagi.split(",") : null);
                $scope.content.KtoZa = (($scope.content.KtoZa) ? $scope.content.KtoZa.split(",") : null);
                $scope.content.KtoPrzeciw = (($scope.content.KtoPrzeciw) ? $scope.content.KtoPrzeciw.split(",") : null);
                $scope.content.KtoWstrzymujacy = (($scope.content.KtoWstrzymujacy) ? $scope.content.KtoWstrzymujacy.split(",") : null);
                $scope.content.KtoNieobecny = (($scope.content.KtoNieobecny) ? $scope.content.KtoNieobecny.split(",") : null);
                $scope.content.Nieobecni = (($scope.content.KtoNieobecny) ? $scope.content.KtoNieobecny.length : 0);
                
		$scope.actNo = data.NumerUchwaly;
                $scope.showAct = true;
                $scope.actContentHTML = "";
                $scope.actAttachmentsHTML = "";

                if (data.URL) {
                    $http({url: $scope.controllerURL + 'getFile', method: "POST", data: JSON.stringify({'link': data.URL}), headers: {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}}).success(function (data) {
                    var part_of_html = angular.element(data.data.content).find('div.doc-body > div');
		    select_proper_part_of_html = part_of_html[0];
		    if (part_of_html[0].textContent.search("UCHWAŁA") < 0)
		    {
			select_proper_part_of_html = part_of_html[1];
		    }
		    $scope.actContentHTML = angular.element(select_proper_part_of_html).html().replace(/[0-9]{4}\.[IXVLMCD]+\.[0-9]+\.[0-9]+/g, function (text) {
                            var text = '<a target="_blank" href=\'' + $scope.mainURL + '#' + text + '\'><strong>' + text + '</strong></a>';
                            return text;
                        }).replace(/[IXVLMCD]+\/[0-9]+\/[0-9]+/g, function (text) {
                            var text = '<a target="_blank" href=\'' + $scope.mainURL + '#' + text + '\'><strong>' + text + '</strong></a>';
                            return text;
                        });
                        $scope.actAttachmentsHTML = angular.element(angular.element(data.data.content).find('div.doc-attachments')[0]).html().replace(/plik.php\?/g, "http://zlotoryja.bip.info.pl/plik.php?");
                    });
                }

                $scope.actProtocolHTML = "";
                $scope.actProtocolAttachmentsHTML = "";

                if (data.ProtokolURL) {
                    $http({url: $scope.controllerURL + 'getFile', method: "POST", data: JSON.stringify({'link': data.ProtokolURL}), headers: {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}}).success(function (data) {
                        var data3 = data.data;
                        $scope.actProtocolHTML = angular.element(angular.element(data3.content).find('div.doc-body > div')[0]).html();
                        $scope.actProtocolAttachmentsHTML = angular.element(angular.element(data3.content).find('div.doc-attachments')[0]).html().replace(/plik.php\?/g, "http://zlotoryja.bip.info.pl/plik.php?");
                    });
                }

                if ($scope.actNo) {
                    window.history.pushState({}, "", "#" + data.NumerUchwaly);
                } else {
                    $scope.error = true;
                    $scope.errorMsg = "Uchwała " + oldActNo + " nie istnieje!";
                    $scope.showAct = false;
                }
            });
        };

        $scope.linkedActs = function (type) {
            $scope.error = false;

            var mode = ((type == -1) ? 'getLeastLexes' : 'getLaterLexes');
            $http.get($scope.controllerURL + mode + "/" + $scope.actNo.replace(/\./g, "-").replace(/\//g, "_"), {tracker: $scope.loadingTracker}).success(function (data_in) {
                var data = data_in.data;
                if (data.length == 0) {
                    if (type == -1) {
                        $scope.error = true;
                        $scope.errorMsg = "Brak poprzednich uchwał dla uchwały " + $scope.actNo;
                    } else if (type == 1) {
                        $scope.error = true;
                        $scope.errorMsg = "Brak poźniejszych uchwał dla uchwały " + $scope.actNo;
                    }
                } else {
                    $scope.limitedList = [];
                    for (var i = 0; i < data.length; i++) {
                        $scope.limitedListChbx = true;
                        $scope.showAct = false;
                        $scope.limitedList.push(data[i][0]);
                    }
                }
            });
        };

        $scope.keydown = function (evt) {
            if (!$("input").is(":focus")) {
                if (evt.keyCode == 83)
                    $scope.reset();
                if ($scope.showAct) {
                    if (evt.keyCode == 37)
                        $scope.linkedActs(-1);
                    else if (evt.keyCode == 39)
                        $scope.linkedActs(1);
                    else if (evt.keyCode == 71) {
                        $("a[aria-controls=glosowania]").click();
                    } else if (evt.keyCode == 73) {
                        $("a[aria-controls=informacje]").click();
                    } else if (evt.keyCode == 80) {
                        $("a[aria-controls=protokol]").click();
                    } else if (evt.keyCode == 84) {
                        $("a[aria-controls=tresc]").click();
                    } else if (evt.keyCode == 66) {
                        win = window.open($scope.content.URL, "_blank");
                        win.focus();
                    }
                }
            }
        }

        $scope.toggleMenu = function() {
            if($scope.menuShow) {
                $scope.menuShow = false;
            } else {
                $scope.menuShow = true;
            }
        }

        if ($scope.url[1]) {
            if ($scope.url[1].length > 3) {
                $scope.openAct($scope.url[1]);
            }
        }

    }]);

    ctrl.directive('naglSort', function () {
        return {
            template: function (elem, attr) {
                return '<strong><p ng-click="sort(\'' + attr.type + '\')">' + attr.text + '</p></strong>'
            }
        }
    });
