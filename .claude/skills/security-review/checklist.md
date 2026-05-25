# Security Review Checklist

## Input Validation
- [ ] All user input sanitized before DB queries
- [ ] File upload MIME types validated
- [ ] Path traversal prevented on file operations

## Authentication
- [ ] JWT tokens expire after 24 hours or less.
- [ ] API keys stored in environment variables
- [ ] Passwords hashed with bcrypt or argon2