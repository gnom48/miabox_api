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
        const response = await fetch('/knowledgebase2/sign_in', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(authData),
            credentials: 'include' // обязательно включаем куки
        });

        // Check the response status
        if (response.ok) {
            // Parse the JSON response
            const data = await response.json();
            const token = data.regular_token;

            const sessionId = response.headers.get('X-Session-Id');
            if (sessionId) {
                // Сохраняем ID сессии в localStorage
                localStorage.setItem('sessionId', sessionId);
                console.log('ID сессии успешно сохранен:', sessionId);
            } else {
                console.error('Заголовок X-Session-Id отсутствует.');
            }

            // Store the token in localStorage or a cookie
            localStorage.setItem("Token", token);

            // Make a GET request to the /base/teams endpoint
            const teamsResponse = await fetch('/knowledgebase2/base/teams', {
                method: 'GET',
                headers: {
                    'X-Session-Id': localStorage.getItem('sessionId'),
                    'Authorization': token,
                    'Content-Type': 'text/html', // Ensure the response is treated as HTML
                },
                credentials: 'include' // обязательно включаем куки
            });

            if (teamsResponse.ok) {
                // Get the HTML content
                const teamsHtml = await teamsResponse.text();

                // Set the HTML content to the current page
                document.open();
                document.write(teamsHtml);
                document.close();

                const sessionId = response.headers.get('X-Session-Id');
                if (sessionId) {
                    // Сохраняем ID сессии в localStorage
                    localStorage.setItem('sessionId', sessionId);
                    console.log('ID сессии успешно сохранен:', sessionId);
                } else {
                    console.error('Заголовок X-Session-Id отсутствует.');
                }
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
