<?php

class Controller {

    // fields
    protected $path, $inputPath, $inputJSON, $output, $service, $serviceName, $type;

    // methods
    public function returnServOpParam($url) {
        $tmp = explode("/", $url);
        $service = $tmp[0];
        if (count($tmp) >= 2)
            $operation = $tmp[1];
        else
            $operation = null;
        $param = array();

        for ($i = 2; $i < count($tmp); $i++) {
            $param[$i - 2] = $tmp[$i];
        }

        return array($service, $operation, $param);
    }

    public function __construct() {
        $path = $_GET["path"];
        $this->inputJSON = json_decode(file_get_contents('php://input'), true);
        $this->inputPath = $this->returnServOpParam($path);
        $this->loadClass($this->inputPath[0]);
        $this->type = "json";
    }

    public function loadClass($name) {
        preg_match('/^[a-zA-Z]+$/u', $name, $res);
        if (count($res) > 0)
            $name = $res[0];
        else
            return;
        $path = "services/$name.php";
        if (file_exists($path))
            include_once($path);
        $name = ucfirst($name);
        $this->serviceName = $name;
        if (!class_exists($this->serviceName))
            return;
        $this->service = new $this->serviceName($this);
        return $this->service;
    }

    public function run() {
        if (!$this->service)
            return json_encode(array("status" => "Error",
                "data" => array("msg" => "Service " . $this->serviceName . " doesn't exists")));
        $this->service->inputPath = $this->inputPath[2];
        $this->service->inputJSON = $this->inputJSON;
        if (!$this->inputPath[1]) {
            if ($this->inputJSON["mode"])
                $this->service->execute($this->inputJSON["mode"]);
        }
        else {
            $this->service->execute($this->inputPath[1]);
        }
        return json_encode($this->service->returnResult(), JSON_UNESCAPED_UNICODE);
    }

}

?>