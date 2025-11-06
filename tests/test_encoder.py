import encoder


def test_json_roundtrip():
    sample = {"temperatura": 22.5, "humedad": 48, "direccion_viento": "NE"}
    b = encoder.encode_json(sample)
    out = encoder.decode_json(b)
    assert out == sample


def test_compact_roundtrip():
    sample = {"temperatura": 22.5, "humedad": 48, "direccion_viento": "NE"}
    b = encoder.encode_compact(sample)
    out = encoder.decode_compact(b)
    # temperatura may be float with 2 decimals; compare rounded
    assert round(out["temperatura"], 2) == round(sample["temperatura"], 2)
    assert out["humedad"] == sample["humedad"]
    assert out["direccion_viento"] == sample["direccion_viento"]
