<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Headers: access");
header("Access-Control-Allow-Methods: POST");
header("Access-Control-Allow-Credentials: true");
//header('Content-Type: application/json');

define('SERVERNAME', 'localhost');
define('DB_USER', 'root');
define('DB_PASSWORD', '');
define('DB_NAME', 'raspi');

class DBAccessManager {
	private $servername;
	private $username;
	private $password;
	private $dbname;

	function __construct() {
		$this->servername = SERVERNAME;
		$this->username = DB_USER;
		$this->password = DB_PASSWORD;
		$this->dbname = DB_NAME;
	}

	public function getConnection() {
		$conn = new mysqli($this->servername, $this->username, $this->password, $this->dbname);

		// Check connection
		if ($conn->connect_error) {
			die ("Connection failed: " . $conn->connect_error);
			return null;
		}

		return $conn;
	}
}

class SensorDataService extends DBAccessManager {

    const INSERT_SENSOR_DATA = "INSERT INTO BME680 (temperature, gas, humidity, pressure) VALUES (?, ?, ?, ?)";

    function __construct() {
		parent::__construct();
	}

    function insert_sensor_data($temperature, $gas, $humidity, $pressure) {
        $con = parent::getConnection();

        if (!$con) {
			echo 'Cannot connect to database';
            die;
		}

        $stmt = $con->prepare(self::INSERT_SENSOR_DATA);
		if (!$stmt->bind_param("dddd", $temperature, $gas, $humidity, $pressure)) {
			echo $stmt->error;
		}
		
		if (!$stmt->execute()) {
			echo $stmt->error;
		}
		
		$stmt->close();
		$con->close();

        echo 'success';
    }
}

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $temperature = $_POST['temperature'];
    $gas = $_POST['gas'];
    $humidity = $_POST['humidity'];
    $pressure = $_POST['pressure'];

    $service = new SensorDataService();
    $service->insert_sensor_data($temperature, $gas, $humidity, $pressure);
}