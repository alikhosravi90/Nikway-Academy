"""Tenant-scoped core with forced RLS and synthetic local fixtures."""
from alembic import op
revision = '001_core'
down_revision = None

def upgrade():
    op.execute('''
    CREATE TABLE tenants (id uuid PRIMARY KEY, name text NOT NULL);
    CREATE TABLE memberships (
      subject uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES tenants(id),
      role text NOT NULL CHECK(role IN ('learner','reviewer')), active boolean NOT NULL DEFAULT true);
    CREATE TABLE courses (
      id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES tenants(id),
      title text NOT NULL, description text NOT NULL, UNIQUE(tenant_id,id));
    CREATE TABLE lessons (
      id uuid PRIMARY KEY, tenant_id uuid NOT NULL, course_id uuid NOT NULL,
      position integer NOT NULL CHECK(position > 0), title text NOT NULL, content text NOT NULL,
      UNIQUE(tenant_id,id), UNIQUE(tenant_id,course_id,position),
      FOREIGN KEY(tenant_id,course_id) REFERENCES courses(tenant_id,id));
    CREATE TABLE enrollments (
      id uuid PRIMARY KEY, tenant_id uuid NOT NULL, course_id uuid NOT NULL, subject uuid NOT NULL,
      created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(tenant_id,course_id,subject),
      UNIQUE(tenant_id,id), FOREIGN KEY(tenant_id,course_id) REFERENCES courses(tenant_id,id));
    CREATE TABLE completions (
      tenant_id uuid NOT NULL, enrollment_id uuid NOT NULL, lesson_id uuid NOT NULL,
      created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(tenant_id,enrollment_id,lesson_id),
      FOREIGN KEY(tenant_id,enrollment_id) REFERENCES enrollments(tenant_id,id),
      FOREIGN KEY(tenant_id,lesson_id) REFERENCES lessons(tenant_id,id));
    CREATE TABLE submissions (
      id uuid PRIMARY KEY, tenant_id uuid NOT NULL, course_id uuid NOT NULL, subject uuid NOT NULL,
      content text NOT NULL CHECK(length(content) BETWEEN 20 AND 10000),
      status text NOT NULL DEFAULT 'submitted' CHECK(status IN ('submitted','accepted','revision_requested')),
      feedback text NOT NULL DEFAULT '', reviewer uuid, revision integer NOT NULL DEFAULT 1,
      rubric_version text NOT NULL DEFAULT '1', created_at timestamptz NOT NULL DEFAULT now(),
      FOREIGN KEY(tenant_id,course_id) REFERENCES courses(tenant_id,id),
      CHECK(reviewer IS NULL OR reviewer <> subject));
    CREATE TABLE workshops (
      id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES tenants(id), title text NOT NULL,
      description text NOT NULL, capacity integer NOT NULL CHECK(capacity > 0),
      starts_at timestamptz NOT NULL, UNIQUE(tenant_id,id));
    CREATE TABLE registrations (
      tenant_id uuid NOT NULL, workshop_id uuid NOT NULL, subject uuid NOT NULL,
      created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(tenant_id,workshop_id,subject),
      FOREIGN KEY(tenant_id,workshop_id) REFERENCES workshops(tenant_id,id));
    CREATE TABLE audit_events (
      id uuid PRIMARY KEY, tenant_id uuid NOT NULL, subject uuid NOT NULL, action text NOT NULL,
      resource_id uuid, correlation_id uuid NOT NULL, created_at timestamptz NOT NULL DEFAULT now());
    ''')
    for n in (1, 2):
        t = f'10000000-0000-4000-8000-{n:012d}'
        c = f'20000000-0000-4000-8000-{n:012d}'
        w = f'40000000-0000-4000-8000-{n:012d}'
        op.execute(f"INSERT INTO tenants VALUES ('{t}','Local Academy {n}')")
        op.execute(f"INSERT INTO memberships VALUES ('00000000-0000-4000-8000-{n:012d}','{t}','learner',true)")
        op.execute(f"INSERT INTO courses VALUES ('{c}','{t}','Evidence-led improvement','A local sample course: observe a process, test an improvement and submit evidence for human review.')")
        for p, title, content in [(1,'Observe the process','Choose a routine process. Record its steps and one observable delay. Separate facts from assumptions. Write a measurable improvement objective.'),(2,'Test and reflect','Design a small reversible change. Compare before and after measurements. Explain limitations and submit your observations for human review. Completion records participation, not certified competence.')]:
            l = f'30000000-0000-4000-8000-{n * 10 + p:012d}'
            op.execute(f"INSERT INTO lessons VALUES ('{l}','{t}','{c}',{p},'{title}','{content}')")
        op.execute(f"INSERT INTO workshops VALUES ('{w}','{t}','Improvement evidence workshop','Local registration exercise. Videoconferencing is not integrated.',10,'2026-12-15T10:00:00Z')")
    op.execute("INSERT INTO memberships VALUES ('00000000-0000-4000-8000-000000000003','10000000-0000-4000-8000-000000000001','reviewer',true)")
    # Control: forgotten tenant filters cannot bypass database isolation.
    for table in ('tenants','courses','lessons','enrollments','completions','submissions','workshops','registrations','audit_events'):
        col = 'id' if table == 'tenants' else 'tenant_id'
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY; ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(f"CREATE POLICY tenant_scope ON {table} USING ({col}::text = current_setting('app.tenant_id',true)) WITH CHECK ({col}::text = current_setting('app.tenant_id',true))")
    op.execute("ALTER TABLE memberships ENABLE ROW LEVEL SECURITY; ALTER TABLE memberships FORCE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY own_membership ON memberships FOR SELECT USING(subject::text=current_setting('app.subject',true))")
    op.execute('GRANT USAGE ON SCHEMA public TO academy_app')
    op.execute('GRANT SELECT ON ALL TABLES IN SCHEMA public TO academy_app')
    op.execute('GRANT INSERT ON enrollments,completions,submissions,registrations,audit_events TO academy_app')
    op.execute('GRANT UPDATE ON submissions, enrollments, workshops TO academy_app')
    op.execute('GRANT DELETE ON registrations TO academy_app')

def downgrade():
    raise RuntimeError('Destructive downgrade prohibited; restore into a new database')
