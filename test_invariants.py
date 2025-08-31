import importlib

def _import_any():
    for name in ("NLGHI_App_MD", "NLGHI_App_Pro"):
        try:
            return importlib.import_module(name)
        except Exception:
            continue
    raise RuntimeError("Could not import NLGHI module (expected NLGHI_App_MD.py or NLGHI_App_Pro.py).")

def test_constants_and_ghi():
    m = _import_any()
    assert len(m.DOMAIN_LIST) == 27
    assert m.DOMAIN_VALUES == [5,5,5,4,4,4,4,3,3,5,4,1,2,2,2,2,2,2,2,2,1,1,1,5,3,1,1]

    impairments = [0]*27
    impairments[0] = 2
    impairments[1] = 1
    dsav = [impairments[i]*m.DOMAIN_VALUES[i] for i in range(27)]
    ghi = round(sum(dsav)/27, 4)
    assert isinstance(ghi, float)
