import { useAuth } from "../../context/authContext";

const useValidateSession = () => {
    const { user, logout, refreshToken } = useAuth();

    const validateSession = async () => {
        try {
            const formData = new FormData()
            formData.append('username',user)
            const response = await fetch(`http://134.122.108.55:8000/api/auth/validateSession`, {
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
