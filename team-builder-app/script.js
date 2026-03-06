let memberCount = 0;
const MAX_MEMBERS = 4;
const MIN_MEMBERS = 3;

// Student database (you can load this from CSV in production)
const students = {
    '167': 'Shamanth Kanale',
    '153': 'Rohith R',
    '154': 'Rohitha Santhosha Gobbani',
    '148': 'Rakshitha',
    '136': 'Rachana C R',
    '157': 'Sachin Gothe',
    '130': 'Preethi N',
    '158': 'Sagar V',
    '132': 'Priyanka P',
    '134': 'Punyashree Urs K H',
    '135': 'Punyashree V',
    '138': 'Rahul Ramesh',
    '143': 'Rajeshwari B S',
    '144': 'Raksha B gowda',
    '160': 'Sanjana',
    '173': 'Shashikala S',
    '162': 'Santoshi Panchal',
    '166': 'Shamanth K Gowda',
    '171': 'Shashank G P',
    '137': 'Rahul M V',
    '140': 'Rajath A Shetty',
    '145': 'Rakshitha',
    '164': 'Seema',
    '172': 'Shashank P',
    '178': 'Shobitha',
    '159': 'Samana Manjunath',
    '131': 'Priti Ranjan',
    '190': 'spoorthi',
    '149': 'Rangalakshmi H G',
    '186': 'sinchana B N',
    '179': 'sridevi',
    '174': 'Sheela.s',
    '183': 'Shruthi Y',
    '184': 'Shuchita M N',
    '188': 'Sneha',
    '156': 'S Mahamad Jaish',
    '177': 'Shivaraj',
    '175': 'Shivaling',
    '163': 'Satish',
    '146': 'Rakshith M',
    '133': 'Punith Raje Urs K.H',
    '142': 'Rajesh D',
    '139': 'Rahul Ramesh',
    '189': 'Sneha MS',
    '185': 'Sinchana AH',
    '191': 'Sridevi S',
    '152': 'Reshma',
    '141': 'Rajeev Narayan',
    '150': 'Rashmi',
    '165': 'Shalini',
    '147': 'Rakshitha',
    '180': 'Shreya',
    '168': 'sharan. k',
    '155': 'Rushanth r ambore',
    '170': 'sharath pande mr',
    '151': 'Rayan omran',
    '192': 'Srinivas Gowda S D',
    '182': 'Shrujan S',
    '169': 'Sharath M N',
    '176': 'Shivalinga S'
};

// Initialize page based on current file
document.addEventListener('DOMContentLoaded', function() {
    const path = window.location.pathname;
    
    if (path.includes('create_team.html')) {
        initializeCreateTeam();
    } else if (path.includes('view_teams.html')) {
        loadTeams();
    } else if (path.includes('edit_team.html')) {
        initializeEditTeam();
    }
});

// Create Team Page Functions
function initializeCreateTeam() {
    addMemberField(); // Add first member field
    
    document.getElementById('addMemberBtn').addEventListener('click', addMemberField);
    document.getElementById('createTeamForm').addEventListener('submit', handleTeamSubmit);
}

function addMemberField() {
    if (memberCount >= MAX_MEMBERS) {
        alert(`Maximum ${MAX_MEMBERS} members allowed`);
        return;
    }
    
    memberCount++;
    const container = document.getElementById('members-container');
    const memberDiv = document.createElement('div');
    memberDiv.className = 'member-entry';
    memberDiv.innerHTML = `
        <input type="text" placeholder="Enter last 3 digits of USN" class="usn-input" onchange="fetchStudentName(this)">
        <input type="text" placeholder="Student Name" class="name-input" readonly>
        <button type="button" class="remove-member" onclick="removeMember(this)">×</button>
    `;
    container.appendChild(memberDiv);
    updateMemberCount();
}

function removeMember(button) {
    button.parentElement.remove();
    memberCount--;
    updateMemberCount();
    updatePreview();
}

function updateMemberCount() {
    const countDisplay = document.getElementById('memberCount');
    countDisplay.textContent = `Members: ${memberCount}/${MAX_MEMBERS} (Minimum ${MIN_MEMBERS} required)`;
    
    if (memberCount < MIN_MEMBERS) {
        countDisplay.style.color = '#dc3545';
    } else {
        countDisplay.style.color = '#28a745';
    }
}

function fetchStudentName(input) {
    const usnLast3 = input.value.trim();
    const nameInput = input.parentElement.querySelector('.name-input');
    
    if (usnLast3.length === 3 && students[usnLast3]) {
        nameInput.value = students[usnLast3];
        // Check for duplicate
        if (isDuplicate(usnLast3, input)) {
            alert('This student is already in the team!');
            input.value = '';
            nameInput.value = '';
        }
    } else {
        nameInput.value = usnLast3 ? 'Student not found' : '';
    }
    
    updatePreview();
}

function isDuplicate(usn, currentInput) {
    const inputs = document.querySelectorAll('.usn-input');
    let count = 0;
    inputs.forEach(input => {
        if (input.value === usn && input !== currentInput) {
            count++;
        }
    });
    return count > 0;
}

function updatePreview() {
    const previewBody = document.getElementById('previewBody');
    previewBody.innerHTML = '';
    
    const inputs = document.querySelectorAll('.member-entry');
    inputs.forEach(entry => {
        const usn = entry.querySelector('.usn-input').value;
        const name = entry.querySelector('.name-input').value;
        
        if (usn && name && name !== 'Student not found') {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>1EW24CS${usn}</td>
                <td>${name}</td>
            `;
            previewBody.appendChild(row);
        }
    });
}

async function handleTeamSubmit(e) {
    e.preventDefault();
    
    const teamName = document.getElementById('teamName').value;
    const secretKey = document.getElementById('secretKey').value;
    
    if (memberCount < MIN_MEMBERS) {
        alert(`Team must have at least ${MIN_MEMBERS} members`);
        return;
    }
    
    const members = [];
    const inputs = document.querySelectorAll('.member-entry');
    
    for (let entry of inputs) {
        const usn = entry.querySelector('.usn-input').value;
        const name = entry.querySelector('.name-input').value;
        
        if (usn && name && name !== 'Student not found') {
            members.push({
                usn: `1EW24CS${usn}`,
                name: name
            });
        }
    }
    
    if (members.length < MIN_MEMBERS) {
        alert('Please fill all member details correctly');
        return;
    }
    
    const formData = new FormData();
    formData.append('teamName', teamName);
    formData.append('secretKey', secretKey);
    formData.append('members', JSON.stringify(members));
    
    try {
        const response = await fetch('save_team.php', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Team created successfully!');
            window.location.href = 'view_teams.html';
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        alert('Error creating team');
        console.error(error);
    }
}

// View Teams Page Functions
async function loadTeams() {
    try {
        const response = await fetch('get_teams.php');
        const teams = await response.json();
        
        displayTeams(teams);
    } catch (error) {
        console.error('Error loading teams:', error);
    }
}

function displayTeams(teams) {
    const container = document.getElementById('teamsContainer');
    container.innerHTML = '';
    
    teams.forEach(team => {
        const members = JSON.parse(team.members);
        const teamCard = document.createElement('div');
        teamCard.className = 'team-card';
        teamCard.innerHTML = `
            <h3>${team.team_name}</h3>
            <ul class="team-members-list">
                ${members.map(m => `<li>${m.usn} - ${m.name}</li>`).join('')}
            </ul>
            <div class="team-actions">
                <button onclick="editTeam(${team.id})" class="btn btn-secondary">Edit</button>
            </div>
        `;
        container.appendChild(teamCard);
    });
}

function editTeam(teamId) {
    window.location.href = `edit_team.html?id=${teamId}`;
}

// Search functionality
if (document.getElementById('searchTeams')) {
    document.getElementById('searchTeams').addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const teamCards = document.querySelectorAll('.team-card');
        
        teamCards.forEach(card => {
            const text = card.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });
}

// Edit Team Page Functions
function initializeEditTeam() {
    const urlParams = new URLSearchParams(window.location.search);
    const teamId = urlParams.get('id');
    
    if (teamId) {
        document.getElementById('editTeamId').value = teamId;
    }
}

async function verifyTeamSecret() {
    const teamId = document.getElementById('editTeamId').value;
    const secretKey = document.getElementById('verifySecret').value;
    
    const formData = new FormData();
    formData.append('teamId', teamId);
    formData.append('secretKey', secretKey);
    
    try {
        const response = await fetch('verify_secret.php', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            document.getElementById('secretVerification').style.display = 'none';
            document.getElementById('editForm').style.display = 'block';
            loadTeamForEdit(teamId, result.team);
        } else {
            alert('Invalid secret key');
        }
    } catch (error) {
        alert('Error verifying secret');
        console.error(error);
    }
}

function loadTeamForEdit(teamId, team) {
    document.getElementById('editTeamName').value = team.team_name;
    
    const members = JSON.parse(team.members);
    const container = document.getElementById('editMembersContainer');
    container.innerHTML = '';
    
    members.forEach(member => {
        addEditMemberField(member);
    });
}

function addEditMemberField(member = null) {
    const container = document.getElementById('editMembersContainer');
    const memberDiv = document.createElement('div');
    memberDiv.className = 'member-entry';
    
    const usnLast3 = member ? member.usn.slice(-3) : '';
    const name = member ? member.name : '';
    
    memberDiv.innerHTML = `
        <input type="text" placeholder="Enter last 3 digits of USN" class="usn-input" value="${usnLast3}" onchange="fetchStudentName(this)">
        <input type="text" placeholder="Student Name" class="name-input" value="${name}" readonly>
        <button type="button" class="remove-member" onclick="removeMember(this)">×</button>
    `;
    container.appendChild(memberDiv);
}

document.getElementById('editTeamForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const teamId = document.getElementById('editTeamId').value;
    const teamName = document.getElementById('editTeamName').value;
    
    const members = [];
    const inputs = document.querySelectorAll('#editMembersContainer .member-entry');
    
    for (let entry of inputs) {
        const usn = entry.querySelector('.usn-input').value;
        const name = entry.querySelector('.name-input').value;
        
        if (usn && name && name !== 'Student not found') {
            members.push({
                usn: `1EW24CS${usn}`,
                name: name
            });
        }
    }
    
    if (members.length < MIN_MEMBERS || members.length > MAX_MEMBERS) {
        alert(`Team must have ${MIN_MEMBERS}-${MAX_MEMBERS} members`);
        return;
    }
    
    const formData = new FormData();
    formData.append('teamId', teamId);
    formData.append('teamName', teamName);
    formData.append('members', JSON.stringify(members));
    
    try {
        const response = await fetch('update_team.php', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Team updated successfully!');
            window.location.href = 'view_teams.html';
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        alert('Error updating team');
        console.error(error);
    }
});