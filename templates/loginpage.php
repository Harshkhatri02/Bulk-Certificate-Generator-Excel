<?php
$servername="localhost";
$username="root";
$password="";
$database_name="eplatform_login"

 $conn=mysqli_connect($server_name,$username,$password,$database_name);
 //now check the connection
 if(!$conn)
 {
    die("Connection Failed: " .mysqli_connect_error());
 }

 if(isset($_POST['login']))
 {
    $username = $_POST['luname'];
    $password = $_POST['lpass'];

    $sql_query = "INSERT INTO login (username,password)
    VALUES ('$username','$password')";
 }

 if (mysqli_query($conn, $sql_query))
 {
    echo "New Details Inserted Successfully!";
 }
 else
 {
    echo "Error: " . $sql_query . "<br>" . mysqli_error($conn);
 }
 mysqli_close($conn);
?>