import pandas as pd
import pytest

import translatesheet as ts


def fake_factory(calls):
    def factory(lang):
        def translate(text):
            calls.append(text)
            if text == "boom":
                raise RuntimeError("network down")
            return f"{text}-{lang}"
        return translate
    return factory


@pytest.fixture
def workbook(tmp_path):
    path = tmp_path / "input.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        pd.DataFrame({"Text": ["hello", "hello", None, 42, "boom"], 2024: [1, 2, 3, 4, 5]}).to_excel(
            writer, sheet_name="Main", index=False
        )
        pd.DataFrame({"Other": ["keep me"]}).to_excel(writer, sheet_name="Notes", index=False)
    return path


def test_translate_series_caches_and_handles_non_text():
    calls = []
    series = pd.Series(["hi", "hi", None, 3, "  ", "boom"])
    out, errors = ts.translate_series(series, fake_factory(calls)("fr"), log=lambda *_: None)
    assert list(out) == ["hi-fr", "hi-fr", "", "3-fr", "  ", ts.ERROR_PLACEHOLDER]
    assert calls == ["hi", "3", "boom"]
    assert errors == 1


def test_resolve_language():
    assert ts.resolve_language(" FR ") == "fr"
    assert ts.resolve_language("French") == "fr"
    with pytest.raises(ValueError):
        ts.resolve_language("klingon")
    with pytest.raises(ValueError):
        ts.resolve_language("")


def test_clean_path_and_ensure_xlsx():
    assert ts.clean_path('  "C:\\data\\file.xlsx" ') == "C:\\data\\file.xlsx"
    assert ts.ensure_xlsx("out") == "out.xlsx"
    assert ts.ensure_xlsx("out.XLSX") == "out.XLSX"


def test_main_end_to_end_preserves_all_sheets(workbook, tmp_path):
    out = tmp_path / "out.xlsx"
    calls = []
    code = ts.main(
        [str(workbook), "-s", "Main", "-c", "text", "-l", "fr", "-o", str(out)],
        translator_factory=fake_factory(calls),
    )
    assert code == 0
    result = pd.read_excel(out, sheet_name=None)
    assert list(result) == ["Main", "Notes"]
    assert result["Main"]["Text_fr"].fillna("").tolist() == [
        "hello-fr", "hello-fr", "", "42-fr", ts.ERROR_PLACEHOLDER
    ]
    assert result["Notes"]["Other"].tolist() == ["keep me"]
    assert calls.count("hello") == 1


def test_main_numeric_header_column(workbook, tmp_path):
    out = tmp_path / "out.xlsx"
    code = ts.main([str(workbook), "-s", "Main", "-c", "2024", "-l", "de", "-o", str(out)],
                   translator_factory=fake_factory([]))
    assert code == 0
    assert "2024_de" in pd.read_excel(out).columns


def test_main_rejects_bad_inputs(workbook, tmp_path):
    f = fake_factory([])
    assert ts.main([str(tmp_path / "missing.xlsx"), "-c", "Text", "-l", "fr"], translator_factory=f) == 1
    assert ts.main([str(workbook), "-s", "Main", "-c", "Nope", "-l", "fr"], translator_factory=f) == 1
    assert ts.main([str(workbook), "-s", "Main", "-c", "Text", "-l", "xx"], translator_factory=f) == 1
    assert ts.main([str(workbook), "-s", "Missing", "-c", "Text", "-l", "fr"], translator_factory=f) == 1
    assert ts.main([str(workbook), "-s", "Main", "-c", "Text", "-l", "fr", "-o", str(workbook)], translator_factory=f) == 1


def test_main_does_not_overwrite_without_confirmation(workbook, tmp_path, monkeypatch):
    out = tmp_path / "out.xlsx"
    out.write_text("existing")
    monkeypatch.setattr("builtins.input", lambda _: "n")
    code = ts.main([str(workbook), "-s", "Main", "-c", "Text", "-l", "fr", "-o", str(out)],
                   translator_factory=fake_factory([]))
    assert code == 1
    assert out.read_text() == "existing"

    code = ts.main([str(workbook), "-s", "Main", "-c", "Text", "-l", "fr", "-o", str(out), "-y"],
                   translator_factory=fake_factory([]))
    assert code == 0
