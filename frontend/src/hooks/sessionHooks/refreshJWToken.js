import { useAuth } from "../../context/authContext";

const useRefreshJWToken = () => {
    const { user, refreshToken, refreshJWToken } = useAuth();
    const API_URL = process.env.REACT_APP_API_URL;

    const refreshTokenHandler = async () => {
        const formData = new FormData();
        formData.append('username', user);
        
        try {
            const request = await fetch(`${API_URL}/auth/refreshjwtoken`, {
                method: 'POST',
                body: formData,
                headers: {
                    Authorization: `Bearer ${refreshToken}`,
                },
            });

            if (request.ok) {
                const result = await request.json();
                console.log(result.access_token);
                refreshJWToken(result.access_token); // Update the token
            } else {
                throw new Error('User session expired!');
            }
        } catch (error) {
            console.log("Error refreshing token: ", error);
            throw error; // Propagate error to the calling function
        }
    };

    return refreshTokenHandler;
};

export default useRefreshJWToken;
