// ? Register User
async function register(event) {
    event.preventDefault(); // ? Prevent form from reloading the page

    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    if (!email || !password) {
        alert("Please fill out email and password!");
        return;
    }

    const response = await fetch('/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            email,
            password
        })
    });

    const data = await response.json();

    if (data.status === 'success') {
        localStorage.setItem('userEmail', email);
        alert("Registration successful! Please log in.");
        window.location.href = "/login"; // ? Redirect to login page
    } else {
        alert(data.message);
    }
}

// ? Login User (Email/Password)
async function login() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    const response = await fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (data.status === 'success') {
        localStorage.setItem('userEmail', data.email);
        localStorage.setItem('userRole', data.role);

        // ? Redirect based on role
        if (data.role === 'admin') {
            window.location.href = "/admin";  // ? Admin Dashboard
        } else {
            window.location.href = "/dashboard";  // ? User Dashboard
        }
    } else {
        alert(data.message);
    }
}


// ? Fetch Workout History
async function getSessions() {
    const userEmail = localStorage.getItem('userEmail');
    const userRFID = localStorage.getItem('userRFID');
    const user = userEmail || userRFID; // ? Try email first, fall back to RFID

    if (!user) return;

    const response = await fetch('/get-sessions', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email: user })
    });

    const sessions = await response.json();

    const sessionList = document.getElementById('session-list');
    sessionList.innerHTML = '';

    sessions.forEach(session => {
        const listItem = document.createElement('li');
        listItem.textContent = `${session.exercise} (${session.sets} sets, ${session.reps} reps)`;
        sessionList.appendChild(listItem);
    });
}

async function loadDashboard() {
    console.log("Stored userEmail:", localStorage.getItem('userEmail'));
    console.log("Stored userRFID:", localStorage.getItem('userRFID'));

    setTimeout(async () => {
        const userEmail = localStorage.getItem('userEmail');
        const userRFID = localStorage.getItem('userRFID');

        if (userEmail) {
            console.log(`Logged in as: ${userEmail}`);
            document.getElementById('user-email').textContent = userEmail;
            await getSessions(userEmail);
        } else if (userRFID) {
            console.log(`Logged in as: RFID User (${userRFID})`);
            document.getElementById('user-email').textContent = `RFID User (${userRFID})`;
            await getSessions(userRFID);
        } else {
            console.log("No session found. Redirecting to login...");
            window.location.href = '/login'; // ? Redirect if no session found
        }
    }, 100);
}



// ? Create Workout
async function createWorkout() {
    const userEmail = localStorage.getItem('userEmail');
    const userRFID = localStorage.getItem('userRFID');
    const user = userEmail || userRFID;

    if (!user) {
        alert("Please login first.");
        return;
    }

    const exercise = document.getElementById('exercise').value;
    const sets = parseInt(document.getElementById('sets').value);
    const reps = parseInt(document.getElementById('reps').value);

    if (!exercise || !sets || !reps) {
        alert("Please fill out all fields!");
        return;
    }


    const response = await fetch('/log-session', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            user: user,
            exercise,
            sets,
            reps,
            timestamp: new Date().toISOString()
        })
    });

    const data = await response.json();

    if (data.status === 'success') {
        alert("Workout logged!");
        getSessions(); // ? Refresh workout list after saving
    } else {
        alert(data.message);
    }
}

// ? Get Workout Summary
async function getWorkoutSummary() {
    const userEmail = localStorage.getItem('userEmail');
    const userRFID = localStorage.getItem('userRFID');
    const user = userEmail || userRFID;

    if (!user) return;

    const response = await fetch('/get-summary', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email: user })
    });

    const data = await response.json();

    const summary = document.getElementById('workout-summary');
    summary.innerHTML = `
        <p>Total Sets: ${data.total_sets}</p>
        <p>Total Reps: ${data.total_reps}</p>
        <p>Exercise Count: ${JSON.stringify(data.exercise_count)}</p>
    `;
}

// ? Logout Function
async function logout() {
    console.log("Logging out...");
    const response = await fetch('/logout', {
        method: 'POST'
    });

    const data = await response.json();

    if (data.status === 'success') {
        // ? Clear all session data
        localStorage.removeItem('userEmail');
        localStorage.removeItem('userRFID');
        localStorage.removeItem('userRole');

        console.log("User logged out. Redirecting to login...");
        window.location.href = "/login";
    } else {
        alert(data.message);
    }
}

