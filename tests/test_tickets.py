"""Helpdesk ticket workflow."""


def _create(client, **overrides):
    payload = {
        "student_name": "Sample Student",
        "contact": "student@example.edu",
        "category": "Examinations",
        "programme": "BSc CS",
        "semester": "1",
        "subject": "Mathematics",
        "description": "The notice and my hall ticket disagree on the exam room.",
    }
    payload.update(overrides)
    resp = client.post("/tickets", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_create_ticket_returns_reference_and_open_status(client):
    ticket = _create(client)
    assert ticket["reference"].startswith("CM-")
    assert ticket["status"] == "open"


def test_student_can_look_up_their_ticket(client):
    ticket = _create(client)
    found = client.get(f"/tickets/{ticket['reference']}").json()
    assert found["reference"] == ticket["reference"]


def test_unknown_ticket_reference_is_404(client):
    assert client.get("/tickets/CM-NOPE00").status_code == 404


def test_short_description_is_rejected(client):
    resp = client.post(
        "/tickets",
        json={"category": "Fees", "description": "hi"},
    )
    assert resp.status_code == 422


def test_admin_can_reply_and_change_status(client, auth_headers):
    ticket = _create(client)
    reply = client.post(
        f"/admin/tickets/{ticket['id']}/messages",
        json={"body": "We checked the notice; the room is 204.", "is_internal": False},
        headers=auth_headers,
    )
    assert reply.status_code == 201, reply.text

    updated = client.patch(
        f"/admin/tickets/{ticket['id']}",
        json={"status": "resolved"},
        headers=auth_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "resolved"


def test_internal_notes_are_hidden_from_the_student(client, auth_headers):
    ticket = _create(client)
    client.post(
        f"/admin/tickets/{ticket['id']}/messages",
        json={"body": "Internal: escalate to exams cell.", "is_internal": True},
        headers=auth_headers,
    )
    student_view = client.get(f"/tickets/{ticket['reference']}").json()
    assert all(not m["is_internal"] for m in student_view["messages"])
    assert "Internal" not in str(student_view["messages"])


def test_admin_can_filter_tickets_by_status(client, auth_headers):
    _create(client)
    tickets = client.get(
        "/admin/tickets", params={"status": "open"}, headers=auth_headers
    ).json()
    assert all(t["status"] == "open" for t in tickets)


def test_ticket_listing_requires_auth(client):
    assert client.get("/admin/tickets").status_code == 401
