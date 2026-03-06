<?php
header('Content-Type: application/json');
require_once 'config.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['success' => false, 'message' => 'Invalid request method']);
    exit;
}

$teamId = $_POST['teamId'] ?? '';
$teamName = $_POST['teamName'] ?? '';
$members = $_POST['members'] ?? '';

if (empty($teamId) || empty($teamName) || empty($members)) {
    echo json_encode(['success' => false, 'message' => 'All fields are required']);
    exit;
}

// Validate members
$membersArray = json_decode($members, true);
if (count($membersArray) < 3 || count($membersArray) > 4) {
    echo json_encode(['success' => false, 'message' => 'Team must have 3-4 members']);
    exit;
}

// Check for duplicate USNs in team
$usns = array_column($membersArray, 'usn');
if (count($usns) !== count(array_unique($usns))) {
    echo json_encode(['success' => false, 'message' => 'Duplicate members not allowed']);
    exit;
}

try {
    $pdo = getDB();
    
    // Check if new team name already exists (excluding current team)
    $stmt = $pdo->prepare("SELECT id FROM teams WHERE team_name = ? AND id != ?");
    $stmt->execute([$teamName, $teamId]);
    if ($stmt->fetch()) {
        echo json_encode(['success' => false, 'message' => 'Team name already exists']);
        exit;
    }
    
    // Update team
    $stmt = $pdo->prepare("UPDATE teams SET team_name = ?, members = ? WHERE id = ?");
    $stmt->execute([$teamName, $members, $teamId]);
    
    echo json_encode(['success' => true, 'message' => 'Team updated successfully']);
    
} catch (PDOException $e) {
    echo json_encode(['success' => false, 'message' => 'Database error: ' . $e->getMessage()]);
}
?>