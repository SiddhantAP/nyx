CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  phone TEXT NOT NULL,
  home_lat DOUBLE PRECISION NOT NULL,
  home_lng DOUBLE PRECISION NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE contacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  phone TEXT NOT NULL,
  is_primary BOOLEAN DEFAULT true,
  consent_accepted BOOLEAN DEFAULT false,
  consent_accepted_at TIMESTAMPTZ,
  consent_token TEXT UNIQUE NOT NULL,
  tracking_active BOOLEAN DEFAULT true
);

CREATE TABLE walk_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  started_at TIMESTAMPTZ DEFAULT now(),
  ended_at TIMESTAMPTZ,
  status TEXT CHECK (status IN ('active','safe','escalated','cancelled')),
  eta_minutes INT,
  eta_time TIMESTAMPTZ
);

CREATE TABLE walk_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES walk_sessions(id),
  event_type TEXT NOT NULL,
  triggered_at TIMESTAMPTZ DEFAULT now(),
  data_shared TEXT,
  recipient TEXT
);