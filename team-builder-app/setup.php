<?php
require_once 'config.php';

header('Content-Type: application/json');

try {
    $pdo = getDB();
    
    // Create teams table if it doesn't exist
    $sql = "CREATE TABLE IF NOT EXISTS teams (
        id INT AUTO_INCREMENT PRIMARY KEY,
        team_name VARCHAR(100) NOT NULL UNIQUE,
        secret_key VARCHAR(255) NOT NULL,
        members TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )";
    
    $pdo->exec($sql);
    
    echo json_encode([
        'success' => true,
        'message' => 'Database setup completed successfully!'
    ]);
    
} catch (PDOException $e) {
    echo json_encode([
        'success' => false,
        'message' => 'Setup failed: ' . $e->getMessage()
    ]);
}
?>