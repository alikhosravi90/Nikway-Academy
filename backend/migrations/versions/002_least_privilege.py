"""Constrain application privileges, including installations with broad defaults."""
from alembic import op
revision='002_least_privilege'
down_revision='001_core'
def upgrade():
    op.execute('REVOKE ALL ON ALL TABLES IN SCHEMA public FROM academy_app')
    op.execute('ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE SELECT,INSERT,UPDATE,DELETE ON TABLES FROM academy_app')
    op.execute('GRANT SELECT ON tenants,memberships,courses,lessons,enrollments,completions,submissions,workshops,registrations,audit_events TO academy_app')
    op.execute('GRANT INSERT ON enrollments,completions,submissions,registrations,audit_events TO academy_app')
    op.execute('GRANT UPDATE ON enrollments,submissions,workshops TO academy_app')
    op.execute('GRANT DELETE ON registrations TO academy_app')
def downgrade():
    raise RuntimeError('Privilege widening downgrade prohibited')
