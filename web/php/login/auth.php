<?php
// Data admin
$admin_users = [
    'admin' => 'admin123',
    'herdan' => 'herdan123'
];

if($_SERVER['REQUEST_METHOD'] == 'POST') {
    $username = trim($_POST['username']);
    $password = $_POST['password'];
    
    if(array_key_exists($username, $admin_users) && $password === $admin_users[$username]) {
        // Redirect ke static index.html dengan parameter success
        header("Location: ../../static/index.html?login=success");
        exit;
    } else {
        header("Location: index.php?error=1");
        exit;
    }
}

header("Location: index.php");
exit;
?>