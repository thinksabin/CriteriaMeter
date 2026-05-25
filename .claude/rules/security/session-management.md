
# session-management rules

- session tokens should be stored in HttpOnly cookies to prevent access via JavaScript and mitigate XSS risks.
- session tokens should have the Secure flag set to ensure they are only sent over HTTPS.
- session tokens should have 60 minutes expiration time.
- cookies should have the SameSite attribute set to 'Strict' to mitigate CSRF risks.
- session should support invalidation on logout and have a mechanism to revoke tokens if needed.
- new session token should be generated after a successful Login.
- session tokens should be unique and unpredictable, ideally using a secure random generator.
- any session related with the user should be invalidated when the user changes their password.
- Implement session fixation protection by regenerating session tokens after successful authentication.
- In JWT, always validate the token signature and check the expiration time before accepting it as valid.
- In JWT, consider using short-lived access tokens and long-lived refresh tokens to enhance security.
- In JWT, avoid storing sensitive information in the token payload, as it can be decoded by anyone with access to the token.
- In JWT, always use a strong signing algorithm (e.g., HS256 or RS256) and keep the signing key secure.
- Implement proper error handling for session-related operations, such as login failures or token validation errors, without exposing sensitive information in error messages.