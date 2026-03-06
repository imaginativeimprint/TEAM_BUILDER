<?php
header('Content-Type: application/json');
require_once 'config.php';

$usn = $_GET['usn'] ?? '';

if (empty($usn)) {
    echo json_encode(['success' => false, 'message' => 'USN is required']);
    exit;
}

// Read from CSV file
$students = [];
if (($handle = fopen(CSV_FILE, 'r')) !== false) {
    while (($data = fgetcsv($handle)) !== false) {
        $students[$data[0]] = $data[1];
    }
    fclose($handle);
}

// Extract last 3 digits for search
$last3 = substr($usn, -3);
$found = false;

foreach ($students as $fullUsn => $name) {
    if (substr($fullUsn, -3) === $last3) {
        echo json_encode([
            'success' => true,
            'usn' => $fullUsn,
            'name' => $name
        ]);
        $found = true;
        break;
    }
}

if (!$found) {
    echo json_encode([
        'success' => false,
        'message' => 'Student not found'
    ]);
}
?>