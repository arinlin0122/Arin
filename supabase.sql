create table if not exists public.learning_profiles (
 user_id uuid primary key references auth.users(id) on delete cascade,
 data jsonb not null default '{}'::jsonb,
 updated_at timestamptz not null default now()
);
alter table public.learning_profiles enable row level security;
create policy "read own profile" on public.learning_profiles for select to authenticated using ((select auth.uid())=user_id);
create policy "insert own profile" on public.learning_profiles for insert to authenticated with check ((select auth.uid())=user_id);
create policy "update own profile" on public.learning_profiles for update to authenticated using ((select auth.uid())=user_id) with check ((select auth.uid())=user_id);
