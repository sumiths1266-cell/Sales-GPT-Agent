from sales_gpt.crm import CSVCRMImporter


def test_csv_import_maps_account_opportunity_and_contact(tmp_path):
    csv_path = tmp_path / "crm.csv"
    csv_path.write_text(
        "account,website,industry,stage,amount,contact,title,role\n"
        "Acme,https://acme.example,Software,discovery,$25,000,Jane Doe,VP Sales,champion\n".replace("$25,000", "25000"),
        encoding="utf-8",
    )

    contexts = CSVCRMImporter(csv_path).pull_accounts()
    assert len(contexts) == 1
    context = contexts[0]
    assert context.account.name == "Acme"
    assert context.account.industry == "Software"
    assert context.opportunity.stage == "discovery"
    assert context.opportunity.amount == 25000.0
    assert context.stakeholders[0].name == "Jane Doe"
    assert context.stakeholders[0].role == "champion"


def test_csv_import_skips_rows_without_account(tmp_path):
    csv_path = tmp_path / "crm.csv"
    csv_path.write_text("account,stage\n,discovery\nGlobex,target\n", encoding="utf-8")
    contexts = CSVCRMImporter(csv_path).pull_accounts()
    assert [c.account.name for c in contexts] == ["Globex"]