from services.security_engine import SecurityEngine, SecurityEvent

def test_security_thresholds():
    e=SecurityEngine()
    d=e.record(SecurityEvent(1,2,'channel_delete'))
    assert d.action in {'log','alert'}
    for _ in range(12): d=e.record(SecurityEvent(1,2,'channel_delete'))
    assert d.action == 'lockdown'

def test_exemption():
    e=SecurityEngine();e.exempt(1,2)
    assert e.record(SecurityEvent(1,2,'role_delete')).action == 'allow'
