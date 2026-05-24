# RBAC (Role based access control) rules
- Review each request to ensure the user has the necessary permissions to access the requested resource or perform the requested action.
- Redirect users to user home page after successful login, instead of admin dashboard, to prevent unauthorized access to admin features.
- Redirect users to login page when request have invalid or missing authentication, instead of showing 403 forbidden page.
- Only users with admin role should have access to administration page and its sub-pages and features.
- User can belong to multiple groups, and each group can have different permissions. The system should check all groups the user belongs to when determining access rights.
- Implement a mechanism to manage user roles and permissions, allowing administrators to easily assign and revoke access rights as needed.
- Administration page is only accessible to users with admin role, and should not be accessible to regular users or unauthenticated users.
- Implement http header cache-control: private, max-age=0, no-cache, no-store, to remediate issue with browser cache and expose of sensitive information through page cache.
