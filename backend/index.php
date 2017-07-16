<?php

header('Access-Control-Allow-Origin: *');

/*
 * Author: Kacper Pawłowski <kacper.pawlowski@gmail.com>
 * Wykonano wolontarystycznie dla Urzędu Miejskiego w Złotoryi
 */

error_reporting(0);
header('Content-Type: application/json');

include_once("engine/service.class.php");
include_once("engine/controller.class.php");

$ctrl = new Controller();
echo $ctrl->run();
?>
