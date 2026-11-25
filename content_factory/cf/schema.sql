CREATE TABLE IF NOT EXISTS principals (
 token_hash text PRIMARY KEY, subject text NOT NULL, tenant text NOT NULL,
 role text NOT NULL CHECK(role IN ('author','reviewer','consumer')),
 active boolean NOT NULL DEFAULT true, expires_at timestamptz NOT NULL
);
CREATE TABLE IF NOT EXISTS heads (
 tenant text NOT NULL, component_id text NOT NULL, number integer NOT NULL DEFAULT 0,
 PRIMARY KEY(tenant,component_id)
);
CREATE TABLE IF NOT EXISTS revisions (
 tenant text NOT NULL, revision_id text NOT NULL, component_id text NOT NULL,
 number integer NOT NULL, semantic_version text NOT NULL, digest text NOT NULL,
 title text NOT NULL, creator text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(tenant,revision_id), UNIQUE(tenant,component_id,number), UNIQUE(tenant,component_id,semantic_version)
);
CREATE TABLE IF NOT EXISTS states (
 tenant text NOT NULL, revision_id text NOT NULL, state text NOT NULL CHECK(state IN ('draft','approved_local','withdrawn')),
 reviewer text, note text, changed_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(tenant,revision_id), FOREIGN KEY(tenant,revision_id) REFERENCES revisions
);
CREATE TABLE IF NOT EXISTS candidates (
 tenant text NOT NULL, candidate_id text NOT NULL, course_id text NOT NULL,
 manifest jsonb NOT NULL, request_key text NOT NULL, request_digest text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(tenant,candidate_id), UNIQUE(tenant,request_key)
);
CREATE TABLE IF NOT EXISTS usages (
 tenant text NOT NULL, candidate_id text NOT NULL, revision_id text NOT NULL,
 PRIMARY KEY(tenant,candidate_id,revision_id), FOREIGN KEY(tenant,candidate_id) REFERENCES candidates,
 FOREIGN KEY(tenant,revision_id) REFERENCES revisions
);
CREATE TABLE IF NOT EXISTS pipeline_runs (
 tenant text NOT NULL, run_id text NOT NULL, state text NOT NULL, data jsonb NOT NULL,
 PRIMARY KEY(tenant,run_id)
);
CREATE TABLE IF NOT EXISTS events (
 tenant text NOT NULL, event_id text NOT NULL, payload jsonb NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(tenant,event_id)
);
CREATE TABLE IF NOT EXISTS receipts (
 tenant text NOT NULL, event_id text NOT NULL, digest text NOT NULL,
 PRIMARY KEY(tenant,event_id)
);
CREATE OR REPLACE FUNCTION immutable_record() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN RAISE EXCEPTION 'immutable record'; END; $$;
DO $$ DECLARE t text; BEGIN
 FOREACH t IN ARRAY ARRAY['revisions','candidates','usages','events'] LOOP
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname=t||'_immutable') THEN
   EXECUTE format('CREATE TRIGGER %I BEFORE UPDATE OR DELETE ON %I FOR EACH ROW EXECUTE FUNCTION immutable_record()',t||'_immutable',t);
  END IF;
 END LOOP;
 FOREACH t IN ARRAY ARRAY['heads','revisions','states','candidates','usages','pipeline_runs','events','receipts'] LOOP
  EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY',t);
  EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY',t);
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename=t AND policyname='tenant_boundary') THEN
   EXECUTE format('CREATE POLICY tenant_boundary ON %I USING (tenant=current_setting(''cf.tenant'',true)) WITH CHECK (tenant=current_setting(''cf.tenant'',true))',t);
  END IF;
 END LOOP;
END $$;
