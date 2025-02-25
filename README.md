Paths inexistentes devem ser redirecionados para uma página 404
Enviaste
going to "/" while logged in, redirects to dashboard, but if user goes to "/" from Link to "/" it does not redirect in case user is logged in


22/01/2025
next step :

Ensure a good app flow while traversing components. 
Ensure components are rendered according to user role.
Implement first tool for the toolbox ensuring authorization and user validation.
Start to define the overall app design (will ask someone to do it)


25/01/2025

General Feedback

    Local Storage Usage:
        You're using localStorage to store the JWT, refresh token, and user info. This is a common approach, but be cautious:
            Security concern: Storing JWTs in localStorage exposes the tokens to XSS attacks. It might be safer to store them in HTTP-only cookies (which cannot be accessed via JavaScript). If you're storing JWTs in localStorage, ensure your application is secure from XSS vulnerabilities.
            Consider using Secure HTTP-only cookies for the tokens if possible, but this might require adjusting your API server to accept cookies rather than tokens in the body.

    State Management:
        You’re storing the user, jwtoken, and refreshToken in state, which works well. However, the state is reloaded from localStorage on component mount (via useEffect), which means there could be a delay in updating the UI when the user logs in.
        Suggestion: Use a loading state while fetching the session from localStorage so you don’t render components expecting the user to be logged in before the session data is available.     /This one i think is OK NOW!

    Session Expiry:
        You’re correctly handling the case where the JWT might expire and need to be refreshed. However, it’s important to check the expiration of the JWT and refresh token proactively. You should periodically check the expiration time of both tokens and refresh them as needed.
        Suggestion: Consider adding a mechanism that checks the expiration time of the tokens every few minutes (perhaps using setInterval or on each API call) and automatically refreshes the access token if it's near expiration.

    Token Refresh Logic:
        You mention that the validateSession is called on every render and also on each API call, which may be overkill if you're checking the same condition repeatedly. Ideally, you don’t need to validate the session on every component render.
        Suggestion: Instead of calling validateSession on every render and API request, consider doing it less frequently, such as:
            When the app first loads (e.g., check if the session is still valid).
            When a user action requires authentication (e.g., login, accessing a protected route).
            You could also call validateSession after each refresh token expiration to ensure the user is still authenticated.

    Refresh Token Expiry Handling:
        If the refresh token expires, the user will need to log in again. You're correctly calling the /api/auth/refresh-token to refresh the JWT, but you might want to add a mechanism for gracefully handling the case where the refresh token is expired. If the refresh token is expired, you should log the user out.
        Suggestion: Handle refresh token expiration globally (e.g., show a logout prompt if the refresh token has expired).

    Error Handling on API Calls:
        When using the JWT to make API calls, ensure that if an API call results in an authentication error (due to an expired or invalid token), you automatically trigger a refresh of the access token (if the refresh token is still valid) or log the user out.
        Suggestion: Ensure that all API calls that require authentication handle token expiry and refreshing centrally to avoid repeating logic across components.

    Use useEffect to Handle Token Refresh:
        You're storing the tokens in local storage, and when the app starts, you load them into state. Instead of calling the refreshJWToken manually, consider using useEffect to automatically refresh the JWT token when necessary, based on the expiration time.


TO DO :

logging with api keys and block high number of api calls in succession from same api key.
filters for specific matieres page, maybe a db change to hold more data for each object like team, department and so on

huge stepback, dive script needs to run on chrome (with selenium :X)

Diver script: mettre a jour button to have user role availability. not clickable if not allowed.