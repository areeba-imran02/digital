from app.services.analyzer import analyze_text, analyze_url

def test_high_risk_text():
    result = analyze_text('URGENT! Your bank account is suspended. Send OTP and payment immediately.')
    assert result['assessment']['level'] == 'HIGH RISK'
    assert len(result['evidence']) >= 3

def test_url_result():
    result = analyze_url('http://example.top/login')
    assert result['input_type'] == 'url'
    assert result['assessment']['score'] > 0
