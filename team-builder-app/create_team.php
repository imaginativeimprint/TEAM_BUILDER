<?php
header('Content-Type: application/json');
require_once 'config.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['success' => false, 'message' => 'Invalid request method']);
    exit;
}

$teamName = $_POST['teamName'] ?? '';
$secretKey = $_POST['secretKey'] ?? '';
$members = $_POST['members'] ?? '';

if (empty($teamName) || empty($secretKey) || empty($members)) {
    echo json_encode(['success' => false, 'message' => 'All fields are required']);
    exit;
}

// Validate members count
$membersArray = json_decode($members, true);
if (count($membersArray) < 3 || count($membersArray) > 4) {
    echo json_encode(['success' => false, 'message' => 'Team must have 3-4 members']);
    exit;
}

// Hash the secret key
$hashedKey = password_hash($secretKey, PASSWORD_DEFAULT);

try {
    $pdo = getDB();
    
    // Check if team name already exists
    $stmt = $pdo->prepare("SELECT id FROM teams WHERE team_name = ?");
    $stmt->execute([$teamName]);
    if ($stmt->fetch()) {
        echo json_encode(['success' => false, 'message' => 'Team name already exists']);
        exit;
    }
    
    // Insert team
    $stmt = $pdo->prepare("INSERT INTO teams (team_name, secret_key, members) VALUES (?, ?, ?)");
    $stmt->execute([$teamName, $hashedKey, $members]);
    
    echo json_encode(['success' => true, 'message' => 'Team created successfully']);
    
} catch (PDOException $e) {
    echo json_encode(['success' => false, 'message' => 'Database error: ' . $e->getMessage()]);
}
?>