import { useState, useEffect } from "react";
import { fetchToken, fetchUserData } from "./api";
import { generateCodeChallenge, generateRandomString } from "./pkceUtils";

const OAUTH2_CONFIG = {
  clientId: "W0YHUvCgoW93SnOJvpNJJbNyUMUKoGTg9WzsW40a",
  authorizationEndpoint: "https://robotics.digikala.com/oauth/o/authorize/",
  tokenEndpoint: "https://robotics.digikala.com/oauth/o/token/",
  redirectUri: "http://localhost:3000/trf/",
};

export const useAuth = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userData, setUserData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const handleAuthorizationCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get("code");
      const storedCodeVerifier = localStorage.getItem("code_verifier");

      if (code && storedCodeVerifier) {
        try {
          const tokenData = await fetchToken(
            OAUTH2_CONFIG.tokenEndpoint,
            code,
            storedCodeVerifier
          );
          localStorage.setItem("access_token", tokenData.access_token);
          setIsLoggedIn(true);
          const user = await fetchUserData(tokenData.access_token);
          setUserData(user);
        } catch (error) {
          console.error("Error during token exchange:", error);
        } finally {
          setIsLoading(false);
          localStorage.removeItem("code_verifier");
        }
      } else {
        const token = localStorage.getItem("access_token");
        try {
          if (!token) {
            throw new Error("No token found");
          }
          const user = await fetchUserData(token);
          setUserData(user);
          setIsLoggedIn(true);
        } catch (error) {
          console.error("Error fetching user data:", error);
        } finally {
          setIsLoading(false);
        }
      }
    };

    handleAuthorizationCallback();
  }, []);

  const handleLogin = async () => {
    const codeVerifier = generateRandomString(128);
    const codeChallenge = await generateCodeChallenge(codeVerifier);
    localStorage.setItem("code_verifier", codeVerifier);

    const authorizationUrl = `${
      OAUTH2_CONFIG.authorizationEndpoint
    }?${new URLSearchParams({
      client_id: OAUTH2_CONFIG.clientId,
      response_type: "code",
      redirect_uri: OAUTH2_CONFIG.redirectUri,
      scope: "user:profile",
      code_challenge: codeChallenge,
      code_challenge_method: "S256",
    }).toString()}`;

    window.location.href = authorizationUrl;
  };

  const logout = (navigate) => {
    localStorage.removeItem("access_token");
    setIsLoggedIn(false);
    setUserData(null);
    navigate("/login");
  };

  return { isLoggedIn, userData, handleLogin, isLoading, logout };
};
