document.addEventListener('DOMContentLoaded', function() {
    // Get the teams data from the hidden div
    const teamsDataElement = document.getElementById('teams-data');
    if (teamsDataElement) {
        const teamsData = JSON.parse(teamsDataElement.textContent);
        // const teamsData = JSON.parse(teamsDataElement.getAttribute('data-teams'));

        // Iterate over each team item and attach the click handler
        Object.keys(teamsData).forEach(teamId => {
            const teamItem = document.getElementById(teamId);
            if (teamItem) {
                teamItem.addEventListener('click', function(event) {
                    event.preventDefault(); // Prevent the default link behavior
                    handleTeamClick(teamId, teamsData[teamId].is_admin);
                });
            }
        });
    }
});

// Function to handle team click
async function handleTeamClick(teamId, isAdmin) {
    try {
        const response = await fetch(`/base/${teamId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Is-Admin': isAdmin,
                'Token': localStorage.getItem('Token')
            }
        });

        if (response.ok) {
            const teamsHtml = await response.text();
            document.open();
            document.write(teamsHtml);
            document.close();
        } else {
            console.error('Unexpected error:', response.statusText);
        }
    } catch (error) {
        console.error('Network error:', error);
    }
}
