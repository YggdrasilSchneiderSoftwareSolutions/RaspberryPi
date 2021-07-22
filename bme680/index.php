<!DOCTYPE html>
<html lang="de" encoding="utf-8">
<head>
    <style>
        .content {
            text-align: center;
        }
        table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
            padding: 15px;
        }
        table {
            margin-left: auto;
            margin-right: auto;
        }
    </style>
    <title>BME680</title>
</head>
<body>
    <div class="content">
        <h1>Sensordaten BME680</h1>
        <table>
            <tr>
                <th>Zeit</th>
                <th>Temperatur C</th>
                <th>Luft ohm</th>
                <th>Feuchtigkeit %</th>
                <th>Druck hPa</th>
            </tr>
<?php
$conn = new mysqli("localhost", "root", "", "raspi");
if ($conn->connect_error) {
    die ("Connection failed: " . $conn->connect_error);
}

$stmt = $conn->prepare("SELECT time, temperature, gas, humidity, pressure FROM BME680 ORDER BY time DESC LIMIT 150");
/*if (!$stmt->bind_param("dddd", $temperature, $gas, $humidity, $pressure)) {
	echo $stmt->error;
}*/
if (!$stmt->execute()) {
    echo $stmt->error;
}

$stmt->store_result();
$num_rows = $stmt->num_rows;

if ($num_rows > 0) {
    $stmt->bind_result($time, $temperature, $gas, $humidity, $pressure);
    $stmt->fetch(); // first row
    for ($i = 0; $i < $num_rows; $i++) {
        echo '<tr>';
        echo '<td>' . $time . '</td>';
        echo '<td>' . $temperature . '</td>';
        echo '<td>' . $gas . '</td>';
        echo '<td>' . $humidity . '</td>';
        echo '<td>' . $pressure . '</td>';
        echo '</tr>';
        $stmt->fetch(); // next
    }
}

$stmt->close();
$conn->close();
?>
        </table>
    </div>
</body>
</html>