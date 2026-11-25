"""Record a declared review as a new immutable revision, never an approval."""
import copy
from engine.knowledge import accumulate, validate_records

def review_revision(records, record_id, version, new_version, reviewer, reviewed_at):
    errors=validate_records(records)
    if errors: raise ValueError('; '.join(errors))
    matches=[r for r in records if (r['id'],r['version'])==(record_id,version)]
    if not matches: raise ValueError('MISSING_RECORD')
    current=matches[0]
    if current['review']['status']!='proposed': raise ValueError('INVALID_TRANSITION: expected proposed')
    if not reviewer or reviewer==current['review']['author']: raise ValueError('INDEPENDENT_REVIEWER_REQUIRED')
    candidate=copy.deepcopy(current)
    candidate['version']=new_version
    candidate['review'].update(status='reviewed',reviewer=reviewer,reviewedAt=reviewed_at)
    candidate['relations']=[r for r in candidate['relations'] if r['type']!='supersedes']
    candidate['relations'].append({'type':'supersedes','target':{'id':record_id,'version':version}})
    # Control: accumulate validates ordering and refuses overwrite; rights cannot be cleared here.
    return accumulate(records,[candidate])
