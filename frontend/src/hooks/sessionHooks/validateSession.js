import { useAuth } from "../../context/authContext";

const useValidateSession = () => {
    const { user, logout, refreshToken } = useAuth();
    const API_URL = process.env.REACT_APP_API_URL;

    const validateSession = async () => {
        try {
            const formData = new FormData()
            formData.append('username',user)
            const response = await fetch(`${API_URL}/auth/validateSession`, {
                method: "POST",
                body: formData,
                headers: {
                    Authorization: `Bearer ${refreshToken}`,
                },
            });

            if (response.ok) {
                // Session is valid, do nothing or handle as needed
            } else {
                console.log("User session expired");
                logout(user); // Log out the user
            }
        } catch (error) {
            console.error("Network error:", error);
        }
    };

    return validateSession;
};

export default useValidateSession;
