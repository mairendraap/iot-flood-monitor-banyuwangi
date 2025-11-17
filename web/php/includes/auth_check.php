<?php
session_start();

if(!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header("Location: ../login/index.php?error=2");
    exit;
}

// Check session timeout (8 jam)
$session_timeout = 8 * 60 * 60; // 8 jam dalam detik
if(isset($_SESSION['admin_login_time']) && (time() - $_SESSION['admin_login_time'] > $session_timeout)) {
    session_unset();
    session_destroy();
    header("Location: ../login/index.php?error=3");
    exit;
}

// Update waktu login terakhir
$_SESSION['admin_login_time'] = time();
?>