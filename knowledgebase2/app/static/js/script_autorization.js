async function login() {
    let login = document.getElementById("login").value;
    let password = document.getElementById("password").value;

    // Create the request payload
    const authData = {
        login: login,
        password: password
    };

    try {
        // Make the POST request to the /sign_in endpoint
        const response = await fetch('/main/sign_in', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(authData),
        });

        // Check the response status
        if (response.ok) {
            // Parse the JSON response
            const data = await response.json();
            const token = data.regular_token;

            // Store the token in localStorage or a cookie
            localStorage.setItem("Token", token);

            // Make a GET request to the /base/teams endpoint
            const teamsResponse = await fetch('/base/teams', {
                method: 'GET',
                headers: {
                    'Authorization': token,
                    'Content-Type': 'text/html', // Ensure the response is treated as HTML
                },
            });

            if (teamsResponse.ok) {
                // Get the HTML content
                const teamsHtml = await teamsResponse.text();

                // Set the HTML content to the current page
                document.open();
                document.write(teamsHtml);
                document.close();
            } else {
                console.error('Failed to load teams page:', teamsResponse.statusText);
            }
        } else if (response.status === 401) {
            // If the response is 401 Unauthorized, show an error message
            document.getElementById("error-message").style.display = "block";
        } else {
            // Handle other potential errors
            console.error('Unexpected error:', response.statusText);
        }
    } catch (error) {
        // Handle network or other errors
        console.error('Network error:', error);
    }
}
