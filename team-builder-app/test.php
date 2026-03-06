<?php
require_once 'config.php';

echo "Testing database connection...\n<br>";

try {
    $pdo = getDB();
    echo "✅ SUCCESS! Connected to MySQL database!";
    
    // Check if table exists
    $result = $pdo->query("SHOW TABLES LIKE 'teams'");
    if($result->rowCount() > 0) {
        echo "\n<br>✅ 'teams' table exists!";
    } else {
        echo "\n<br>❌ 'teams' table not found. Please create it.";
    }
    
} catch (Exception $e) {
    echo "❌ Connection failed: " . $e->getMessage();
}
?>