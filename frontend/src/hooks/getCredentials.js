import { useAuth } from "../context/authContext"


const useGetCredentials = () => {

    const { jwtoken,user } = useAuth()
    const API_URL = process.env.REACT_APP_API_URL;

    const fetchCredentials = async () => {

        let creds = {}
        
        try {
            const response = await fetch(`${API_URL}/auth/getusercreds?username=${user}`, {
              method: "GET",
              headers: {
                Authorization: `Bearer ${localStorage.getItem('jwtoken')}`,
              },
            });
            if (response.ok) {
              const result = await response.json();
              creds = {
                username: result.params.username,
                api_key: result.params.api_key,
              };
            } else {
              console.error("Failed to fetch credentials:", response.statusText);
            }
          } catch (error) {
            console.error("Network error:", error);
          }
        return creds
    }

    return fetchCredentials
}

export default useGetCredentials