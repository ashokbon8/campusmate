# Admin password entry fix

1. Copy the contents of this update into your existing `campusmate` folder.
   Allow the old setup files to be replaced. Keep the `scripts` folder in place.
2. Open a VS Code terminal inside that `campusmate` folder.
3. Run `.\SETUP_ADMIN_VISIBLE.cmd`.
4. Enter a display name, your admin email and a password of at least 12
   characters. This mode displays the password as you type it locally. Enter
   it again to confirm. A mismatch or short password now asks you to try again.
5. After settings are saved, press any key. Stop any old running servers, then
   run `.\START_CAMPUSMATE.cmd`.
6. Open http://localhost:5173 and choose Admin Login.

Your private configuration is saved in `backend/.env`. Database, college data
and unrelated environment settings are retained. The update contains no admin
credentials.

For hidden entry, use `SETUP_ADMIN.cmd` instead. In hidden mode, no characters
or stars appear; typing still works. Never send your password in a screenshot.

If you prefer editing settings directly, open `backend/.env` and set
`SEED_ADMIN_EMAIL`, `SEED_ADMIN_PASSWORD` and `SEED_ADMIN_NAME` there. Save and
restart the backend. Editing `.env.example` alone does not configure the app.
