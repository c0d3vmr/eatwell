create table if not exists public.eatwell_resources (
    resource_id text primary key,
    name text not null,
    resource_type text not null,
    city text not null,
    state text not null,
    zip_code text,
    source_url text,
    last_verified date,
    updated_at date,
    payload jsonb not null
);

create index if not exists eatwell_resources_city_state_zip_idx
    on public.eatwell_resources (city, state, zip_code);

alter table public.eatwell_resources enable row level security;

grant select on public.eatwell_resources to anon, authenticated;
grant select, insert, update on public.eatwell_resources to service_role;

drop policy if exists "Public can read Houston resources"
    on public.eatwell_resources;
create policy "Public can read Houston resources"
    on public.eatwell_resources
    for select
    to anon, authenticated
    using (city = 'Houston' and state = 'TX');

create table if not exists public.eatwell_profiles (
    user_id uuid primary key references auth.users (id) on delete cascade,
    weekly_budget numeric(8, 2) not null check (weekly_budget >= 0),
    household_size integer not null check (household_size between 1 and 20),
    snap_status boolean not null default false,
    wic_status boolean not null default false,
    zip_code text not null,
    has_vehicle boolean not null default false,
    has_transit boolean not null default false,
    trips_per_week integer not null check (trips_per_week between 1 and 7),
    dietary_preference text,
    allergies text[] not null default '{}',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

alter table public.eatwell_profiles enable row level security;

grant select, insert, update, delete
    on public.eatwell_profiles to authenticated;

drop policy if exists "Users can read their own profile"
    on public.eatwell_profiles;
create policy "Users can read their own profile"
    on public.eatwell_profiles
    for select
    to authenticated
    using (auth.uid() = user_id);

drop policy if exists "Users can insert their own profile"
    on public.eatwell_profiles;
create policy "Users can insert their own profile"
    on public.eatwell_profiles
    for insert
    to authenticated
    with check (auth.uid() = user_id);

drop policy if exists "Users can update their own profile"
    on public.eatwell_profiles;
create policy "Users can update their own profile"
    on public.eatwell_profiles
    for update
    to authenticated
    using (auth.uid() = user_id)
    with check (auth.uid() = user_id);

drop policy if exists "Users can delete their own profile"
    on public.eatwell_profiles;
create policy "Users can delete their own profile"
    on public.eatwell_profiles
    for delete
    to authenticated
    using (auth.uid() = user_id);

create or replace function public.set_eatwell_profile_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists set_eatwell_profile_updated_at
    on public.eatwell_profiles;
create trigger set_eatwell_profile_updated_at
    before update on public.eatwell_profiles
    for each row
    execute function public.set_eatwell_profile_updated_at();
