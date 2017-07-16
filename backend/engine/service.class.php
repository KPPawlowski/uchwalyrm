<?php

abstract class Service {

    // fields
    public $name, $data, $status, $inputPath, $inputJSON, $ctrl, $httpMethod, $headerList;

    // methods
    public function __construct($ctrl) {
        $this->ctrl = $ctrl;
        $this->status = "None";
        $this->headerList = headers_list();
        $this->result = array();
    }

    protected function returnStatus($status) {
        $this->status = $status;
        return array($this->status, $this->result);
    }
    
    protected function setStatusOK() {
        return $this->returnStatus("OK");
    }

    protected function setStatusError() {
        return $this->returnStatus("Error");
    }

    protected function setData($param) {
        if (is_string($param)) {
            $this->data = array("result" => $param);
        } else if (is_array($param)) {
            $this->data = $param;
        }
    }

    public function returnResult() {
        return array("status" => $this->status,
                     "data"   => $this->data);
    }

    public function execute($method) {
        $method_old = $method;
        $this->httpMethod = $_SERVER['REQUEST_METHOD'];
        $method = "execute" . ucfirst($method);
        try {
            $status = $this->{$method}();
        } catch (Exception $e) {
            $this->setData(array("msg" => "Exception " . $e->getMessage()));
            return $this->setStatusError();
        }

        $this->returnResult();
    }

    protected function setHttpStatus($code) {
        switch ($code) {
            case 200:
                $content = "HTTP/1.1 200 OK";
                break;
            case 201:
                $content = "HTTP/1.1 201 Created";
                break;
            case 204:
                $content = "HTTP/1.1 204 No Content";
                break;
            case 400:
                $content = "HTTP/1.1 400 Bad Request";
                break;
            case 403:
                $content = "HTTP/1.1 403 Forbidden";
                break;
            case 404:
                $content = "HTTP/1.1 404 Not Found";
                break;
        }

        header($content);
    }

    protected function __call($name, $args) {
        $this->setHttpStatus(400);
        $this->setData(array("msg" => "Method of " . str_replace("execute", "", $name) . " doesn't exists"));
        return $this->setStatusError();
    }

}

?>
