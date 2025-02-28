export const oauthConfig = {
  authority: "https://robotics.digikala.com/oauth", // Your DOT SSO domain
  client_id: "W0YHUvCgoW93SnOJvpNJJbNyUMUKoGTg9WzsW40a",
  redirect_uri: "http://localhost:3000/callback",
  response_type: "code",
  scope: "user:profile", // Scopes allowed by your DOT SSO server
  post_logout_redirect_uri: "http://localhost:3000/login/",
};
