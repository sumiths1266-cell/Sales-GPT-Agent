from sales_gpt.models import Account, SalesContext
from sales_gpt.store import ContextStore


def test_store_round_trip(tmp_path):
    store = ContextStore(str(tmp_path))
    context = SalesContext(account=Account(name="Acme Corp", industry="Software"))
    context.opportunity.stage = "discovery"
    context.opportunity.next_actions = ["Meet economic buyer"]
    store.save(context)

    loaded = store.load("Acme Corp")
    assert loaded.account.industry == "Software"
    assert loaded.opportunity.stage == "discovery"
    assert loaded.opportunity.next_actions == ["Meet economic buyer"]


def test_store_lists_and_deletes_accounts(tmp_path):
    store = ContextStore(str(tmp_path))
    store.save(SalesContext(account=Account(name="Acme")))
    store.save(SalesContext(account=Account(name="Globex")))

    assert {c.account.name for c in store.list_contexts()} == {"Acme", "Globex"}
    assert store.delete("Acme") is True
    assert store.delete("Acme") is False
    assert [c.account.name for c in store.list_contexts()] == ["Globex"]