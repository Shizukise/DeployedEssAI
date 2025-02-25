import { useAuth } from "../context/authContext"


const useGetCredentials = () => {

    const { jwtoken,user } = useAuth()
    

    const fetchCredentials = async () => {

        let creds = {}
        
        try {
            const response = await fetch(`http://134.122.108.55:8000/api/auth/getusercreds?username=${user}`, {
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