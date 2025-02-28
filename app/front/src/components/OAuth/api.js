import axios from "axios";

export const fetchToken = async (tokenEndpoint, code, codeVerifier) => {
  const response = await axios.post(
    tokenEndpoint,
    new URLSearchParams({
      grant_type: "authorization_code",
      code,
      redirect_uri: "http://localhost:3000/trf/",
      code_verifier: codeVerifier,
      client_id: "W0YHUvCgoW93SnOJvpNJJbNyUMUKoGTg9WzsW40a",
    }).toString(),
    {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    }
  );

  return response.data;
};

export const fetchUserData = async (token) => {
  const response = await axios.get(
    "https://robotics.digikala.com/oauth/api/users/me/",
    {
      headers: { Authorization: `Bearer ${token}` },
    }
  );
  if (response.status !== 200) {
    throw new Error("Failed to fetch user data");
  }
  return response.data;
};
