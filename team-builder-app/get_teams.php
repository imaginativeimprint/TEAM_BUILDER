<?php
header('Content-Type: application/json');
require_once 'config.php';

try {
    $pdo = getDB();
    $stmt = $pdo->query("SELECT id, team_name, members, created_at FROM teams ORDER BY created_at DESC");
    $teams = $stmt->fetchAll();
    
    echo json_encode($teams);
    
} catch (PDOException $e) {
    echo json_encode(['error' => 'Database error: ' . $e->getMessage()]);
}
?>