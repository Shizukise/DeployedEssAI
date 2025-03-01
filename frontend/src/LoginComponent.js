import React, { useRef,useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "./context/authContext";


/* When loading this page, localstorage needs to be checked to see if there is a user logged in, and redirect it to the dashboard if so */


function Login() {
    const username = useRef();
    const password = useRef();
    const nav = useNavigate()
    const { login, logout, user, jwtoken, refreshToken } = useAuth();
    const API_URL = process.env.REACT_APP_API_URL;



    useEffect(() => {
        if (localStorage.getItem("user") && localStorage.getItem("jwtoken")) {
            nav("/dashboard");
        }
    }, [nav]);

    const createUser = async () => {
        try {
            const result = await fetch ('http://134.122.108.55:8000/api/users/development/create', {
                method: 'POST'
            }
        )
        if (result.ok) {
            console.log("OK MAN")
        };
    } catch (error) {
            console.log(error)
        };
    };

    const loginuser = async (event) => {
        event.preventDefault();

        const usernameValue = username.current.value;
        const passwordValue = password.current.value;

        try {
            const formData = new FormData();
            formData.append("username", usernameValue);
            formData.append("password", passwordValue);

            const response = await fetch("${API_URL}/auth/login", {
                method: "POST",
                credentials: "include",
                body: formData,
            });

            if (response.ok) {
                let result = await response.json();
                let requested_jwtoken = result.access_token;
                let requested_refresh_jwtoken = result.refresh_token;
                console.log("Login successful", result);
                login(usernameValue, requested_jwtoken, requested_refresh_jwtoken);
                nav("/dashboard")
            } else {
                let message = await response.json();
                console.log("Login failed:", message.message);
            }
        } catch (error) {
            console.error("Network error:", error);
        }
    };

    return (
        <div className="login-container">
            <form onSubmit={loginuser}>
                <label htmlFor="username">Username:</label>
                <input type="text" id="username" ref={username} />
                <label htmlFor="password">Password:</label>
                <input type="password" id="password" ref={password} />
                <button type="submit">Login</button>
            </form>
            <button onClick={() => console.log("Logged user details:", { user, jwtoken, refreshToken })}>
                Print logged user
            </button>
            <button onClick={() => createUser()}> Create TestUser </button>
            <button onClick={() => (user ? logout() : console.log("No user logged in"))}>
                Log out
            </button>
        </div>
    );
}

export default Login;
