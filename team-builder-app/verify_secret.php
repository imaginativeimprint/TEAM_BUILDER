<?php
header('Content-Type: application/json');
require_once 'config.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['success' => false, 'message' => 'Invalid request method']);
    exit;
}

$teamId = $_POST['teamId'] ?? '';
$secretKey = $_POST['secretKey'] ?? '';

if (empty($teamId) || empty($secretKey)) {
    echo json_encode(['success' => false, 'message' => 'Team ID and secret key are required']);
    exit;
}

try {
    $pdo = getDB();
    
    // Get team details
    $stmt = $pdo->prepare("SELECT * FROM teams WHERE id = ?");
    $stmt->execute([$teamId]);
    $team = $stmt->fetch();
    
    if (!$team) {
        echo json_encode(['success' => false, 'message' => 'Team not found']);
        exit;
    }
    
    // Verify secret key
    if (password_verify($secretKey, $team['secret_key'])) {
        echo json_encode([
            'success' => true,
            'team' => $team
        ]);
    } else {
        echo json_encode(['success' => false, 'message' => 'Invalid secret key']);
    }
    
} catch (PDOException $e) {
    echo json_encode(['success' => false, 'message' => 'Database error: ' . $e->getMessage()]);
}
?>