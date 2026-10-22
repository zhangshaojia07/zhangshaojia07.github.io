# Agent notes

Read [docs/site-maintenance.md](docs/site-maintenance.md) before working on site
configuration, templates, images, or deployment. It records known issues, their
status, and checks for confirming fixes.

When your work addresses an issue in that file, update its status and add a dated
entry to the resolution log with the change and verification performed. Keep the
original issue entry so future maintainers can see what was fixed. Keep work within
the user's requested scope; open issues are context for future work.

Before committing image changes in this clone, enable the checked-in hook with
`git config --local core.hooksPath .githooks`. If it reports image warnings, show
them to the user and wait for an explicit decision before confirming the prompt.
Do not bypass the hook.
