import { useNavigate } from "react-router-dom";
import { useAuth } from "../../../context/authContext";
import useRefreshJWToken from "../../../hooks/sessionHooks/refreshJWToken";

const useDiveIn = () => {

    const API_URL = process.env.REACT_APP_API_URL;

    const { logout, user } = useAuth();
    const refreshJWToken = useRefreshJWToken(); 
    const nav = useNavigate();

    const diveIn = async (token,api_key,username,password) => {
        try {
            const formData = new FormData()
            formData.append("api_key",api_key)
            formData.append('username',username)
            formData.append('password',password)
            const response = await fetch(`${API_URL}/dive/divein`, {
                method: "POST",
                body : formData,
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (response.ok) {
                console.log("OK!");
                return response.json()
            } else {
                console.log("NOT OK!");
                if (response.status == 401) {
                console.log("Checking refresh token to validate session");

                    try {
                        await refreshJWToken();  //This is the userefreshJWToken hook, not the context method
                        console.log("Session validated!");
                        const new_token = localStorage.getItem('jwtoken')
                        diveIn(new_token)
                        return;          
                    } catch (error) {
                        console.log(error);
                        nav('/');  // Redirect if refresh fails
                        logout(user);  // Clear user session
                        return;  // Break out of the function here
                    }; 
                } else {
                    console.log(response)
                }
            };                                
        } catch (error) {
            console.error("Network error:", error);
        }
    };

    return diveIn;
};

export default useDiveIn;
