"""Read-only bed projections; no additional business rows or cloud solution."""
from datetime import timezone
from .master_validation import timestamp
from .operational_validation import resolve_events,START,CUTOFF


def availability(tables,at,known_at=None,request=None):
    """Reconstruct delivered bed state, with conservative compatibility for unavailable demographics.

    request is an explicit scenario input: administrative_sex, isolation_required,
    and allowed_services. It does not infer a future requirement from an outcome.
    """
    at=timestamp(at).astimezone(timezone.utc).isoformat().replace('+00:00','Z')
    if known_at:known_at=timestamp(known_at).astimezone(timezone.utc).isoformat().replace('+00:00','Z')
    if not START<=at<=CUTOFF:raise ValueError('availability outside the three-year observation window')
    if known_at and at>known_at:raise ValueError('availability is an observed historical projection, not a forecast')
    locations={r['location_id']:r for r in tables['location'] if r['location_type']=='BED'}
    latest={}
    for event in resolve_events(tables['bed_event'],known_at):
        if event['effective_at']<=at:latest[event['bed_location_id']]=event
    enc={r['encounter_version_id']:r for r in tables.get('encounter',[])}
    patients={r['patient_version_id']:r for r in tables.get('patient',[])}
    rooms={}
    for bid,state in latest.items():
        if state['occupancy_state']=='OCCUPIED':rooms.setdefault(locations[bid]['parent_location_id'],[]).append(state)
    available=[];compatible=[];unknown_compatibility=0
    for bid,state in latest.items():
        if state['occupancy_state']!='EMPTY' or state['service_state']!='IN_SERVICE' or not state['staffing_enabled'] or state['reserved']:continue
        peers=rooms.get(locations[bid]['parent_location_id'],[])
        if any('PRIVATE_ISOLATION_PLACEMENT' in p['reason'] or 'PRIVATE_ROOM_PLACEMENT' in p['reason'] for p in peers):continue
        available.append(bid)
        if request is None:continue
        if locations[bid]['service_line'] not in request['allowed_services']:continue
        if request['administrative_sex'] not in ('M','F') and peers:continue
        if request['isolation_required'] and (not locations[bid]['isolation_capable'] or peers):continue
        matches=True
        for peer in peers:
            context=enc.get(peer['encounter_version_id']);p=patients.get(context['patient_version_id']) if context else None
            if p is None or known_at and p['export_available_at']>known_at:
                matches=False;unknown_compatibility+=1;break
            if p['administrative_sex']!=request['administrative_sex']:matches=False;break
        if matches:compatible.append(bid)
    return {'effective_at':at,'delivery_known_at':known_at,'licensed':len(locations),'unknown_bed_states':len(locations)-len(latest),
        'in_service':sum(r['service_state']=='IN_SERVICE' for r in latest.values()),
        'staffed':sum(r['service_state']=='IN_SERVICE' and r['staffing_enabled'] for r in latest.values()),
        'occupied':sum(r['occupancy_state']=='OCCUPIED' for r in latest.values()),'reserved':sum(r['reserved'] for r in latest.values()),
        'immediately_available':len(available),'patient_compatible':len(compatible) if request else None,'unknown_peer_compatibility':unknown_compatibility,
        'available_bed_ids':sorted(available),'compatible_bed_ids':sorted(compatible)}
