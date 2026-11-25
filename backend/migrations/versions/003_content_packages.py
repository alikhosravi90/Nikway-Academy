"""Immutable portable content drafts and tenant-bound local publication."""
from alembic import op
revision = '003_content_packages'
down_revision = '002_least_privilege'

def upgrade():
    op.execute('''
    ALTER TABLE courses ADD COLUMN metadata jsonb NOT NULL DEFAULT '{}'::jsonb;
    ALTER TABLE lessons ADD COLUMN metadata jsonb NOT NULL DEFAULT '{}'::jsonb;
    CREATE TABLE content_packages (
      id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES tenants(id),
      package_id uuid NOT NULL, version text NOT NULL, digest char(64) NOT NULL,
      document jsonb NOT NULL, status text NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','published')),
      revision integer NOT NULL DEFAULT 1 CHECK(revision > 0),
      imported_by uuid NOT NULL, imported_at timestamptz NOT NULL DEFAULT now(),
      published_at timestamptz, course_id uuid,
      UNIQUE(tenant_id,package_id,version), UNIQUE(tenant_id,course_id),
      FOREIGN KEY(tenant_id,course_id) REFERENCES courses(tenant_id,id),
      CHECK((status='draft' AND course_id IS NULL AND published_at IS NULL) OR
            (status='published' AND course_id IS NOT NULL AND published_at IS NOT NULL)));
    ALTER TABLE content_packages ENABLE ROW LEVEL SECURITY;
    ALTER TABLE content_packages FORCE ROW LEVEL SECURITY;
    CREATE POLICY content_read ON content_packages FOR SELECT USING (
      tenant_id::text=current_setting('app.tenant_id',true) AND
      (status='published' OR EXISTS (SELECT 1 FROM memberships WHERE subject::text=current_setting('app.subject',true) AND role='reviewer' AND active)));
    CREATE POLICY content_insert ON content_packages FOR INSERT WITH CHECK (
      tenant_id::text=current_setting('app.tenant_id',true) AND imported_by::text=current_setting('app.subject',true) AND
      status='draft' AND EXISTS (SELECT 1 FROM memberships WHERE subject::text=current_setting('app.subject',true) AND role='reviewer' AND active));
    CREATE POLICY content_publish ON content_packages FOR UPDATE USING (
      tenant_id::text=current_setting('app.tenant_id',true) AND status='draft' AND
      EXISTS (SELECT 1 FROM memberships WHERE subject::text=current_setting('app.subject',true) AND role='reviewer' AND active))
      WITH CHECK (tenant_id::text=current_setting('app.tenant_id',true) AND status='published');
    GRANT SELECT, INSERT ON content_packages TO academy_app;
    GRANT UPDATE(status,revision,published_at,course_id) ON content_packages TO academy_app;
    GRANT INSERT ON courses,lessons TO academy_app;
    CREATE POLICY catalog_reviewer_insert ON courses AS RESTRICTIVE FOR INSERT WITH CHECK (
      EXISTS (SELECT 1 FROM memberships WHERE subject::text=current_setting('app.subject',true) AND role='reviewer' AND active));
    CREATE POLICY catalog_reviewer_insert ON lessons AS RESTRICTIVE FOR INSERT WITH CHECK (
      EXISTS (SELECT 1 FROM memberships WHERE subject::text=current_setting('app.subject',true) AND role='reviewer' AND active));
    ''')

def downgrade():
    raise RuntimeError('Preserve published learning evidence; no destructive downgrade')
