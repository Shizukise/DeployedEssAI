import { useAuth } from "../../context/authContext";

const useRefreshJWToken = () => {
    const { user, refreshToken, refreshJWToken } = useAuth();

    const refreshTokenHandler = async () => {
        const formData = new FormData();
        formData.append('username', user);
        
        try {
            const request = await fetch('http://134.122.108.55:8000/api/auth/refreshjwtoken', {
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
