# Database (Supabase Postgres)

There is no migration runner. Every script here was applied by hand in the
Supabase SQL editor.

- `schema.sql` is the original baseline: core tables, RLS policies, and triggers.
- `migrations/` holds changes made after the baseline, numbered in the order
  they were added to the repo. When several files were committed together,
  the order follows their dependencies: table creation first, then column
  additions, then RLS and security fixes.
- `manual/` holds one-off operational and QA helpers. These are not schema
  changes, so don't run them as part of setup.

## Setting up a fresh project

1. Run `schema.sql`.
2. Run every file in `migrations/` in numeric order.

Most migrations use `IF NOT EXISTS` / `CREATE OR REPLACE`, but not all of
them do. Read a script before re-running it against an existing database.

## Adding a change

Add `migrations/NNN_short_description.sql` with the next number, and write it
so it is safe to re-run.
