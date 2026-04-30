from tech_idea_digest.__main__ import main


def test_cli_dry_run_sample_data_prints_digest(capsys):
    exit_code = main(["--dry-run", "--sample-data", "--max-items", "3"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Daily Technology Ideas Digest" in output
    assert "Top Signals" in output
    assert "[" in output
