import { useAuth } from "../../../context/authContext";
import useRefreshJWToken from "../../../hooks/sessionHooks/refreshJWToken";
import { useNavigate } from "react-router-dom";

const useDiveOut = () => { 
    const { user, logout } = useAuth();
    const nav = useNavigate();
    const refreshJWToken = useRefreshJWToken();

    const diveOut = async (token) => {
        try {
            const formData = new FormData();
            formData.append("username", user);

            const request = await fetch("http://134.122.108.55:8000/api/dive/diveout", {
                method: "POST",
                body: formData,
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (request.ok) {
                console.log("OK!");
                return request.json();
            } else {
                console.log("NOT OK!");
                console.log("Checking refresh token to validate session");

                try {
                    await refreshJWToken(); // This is the userefreshJWToken hook, not the context method
                    console.log("Session validated!");
                    const new_token = localStorage.getItem("jwtoken");
                    return diveOut(new_token); // 
                } catch (error) {
                    console.log(error);
                    nav("/"); // Redirect if refresh fails
                    logout(user); // Clear user session
                    return; // Break out of the function here
                }
            }
        } catch (error) {
            console.log("Network error:", error);
        }
    };

    return diveOut; 
};

export default useDiveOut;
