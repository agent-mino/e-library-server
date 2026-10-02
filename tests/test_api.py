def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


# —— Auth ——


def test_first_admin_can_bootstrap_but_later_signups_need_an_admin(client, admin):
    payload = {"name": "Eve", "email": "eve@example.com", "password": "eve-pass-123"}
    assert client.post("/admin/signup", json=payload).status_code == 403
    assert client.post("/admin/signup", json=payload, headers=admin["headers"]).status_code == 201


def test_login_rejects_bad_password_without_revealing_which_field(client, admin):
    res = client.post("/admin/login", json={"email": "admin@example.com", "password": "wrong-password"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid email or password"


def test_user_login_returns_token_and_profile(client):
    client.post("/user/signup", json={"name": "Sam", "email": "sam@example.com", "password": "sam-pass-123"})
    body = client.post("/user/login", json={"email": "sam@example.com", "password": "sam-pass-123"}).json()
    assert body["access_token"] and body["name"] == "Sam" and body["token_type"] == "bearer"


def test_duplicate_email_is_rejected(client, user):
    res = client.post("/user/signup", json={"name": "X", "email": "reader@example.com", "password": "another-pass"})
    assert res.status_code == 409


def test_invalid_token_is_rejected(client):
    assert client.get("/user/", headers={"Authorization": "Bearer not-a-token"}).status_code == 401


# —— Authorisation ——


def test_writes_require_admin(client, user):
    assert client.post("/categories/", json={"name": "Science"}).status_code == 401
    assert client.post("/categories/", json={"name": "Science"}, headers=user["headers"]).status_code == 403


def test_only_admins_can_list_users(client, admin, user):
    assert client.get("/user/", headers=user["headers"]).status_code == 403
    users = client.get("/user/", headers=admin["headers"]).json()
    assert [u["email"] for u in users] == ["reader@example.com"]
    assert "password" not in users[0]


def test_users_can_only_edit_themselves(client, user):
    other = client.post("/user/signup", json={"name": "O", "email": "o@example.com", "password": "other-pass-1"}).json()
    assert client.put(f"/user/{other['id']}", json={"name": "Hacked"}, headers=user["headers"]).status_code == 403
    res = client.put(f"/user/{user['id']}", json={"name": "Rita R."}, headers=user["headers"])
    assert res.status_code == 200 and res.json()["name"] == "Rita R."


def test_password_change_requires_old_password(client, user):
    url = f"/user/{user['id']}/password"
    bad = client.put(url, json={"old_password": "nope", "new_password": "brand-new-pass"}, headers=user["headers"])
    assert bad.status_code == 400
    ok = client.put(
        url, json={"old_password": "reader-pass-123", "new_password": "brand-new-pass"}, headers=user["headers"]
    )
    assert ok.status_code == 200
    login = client.post("/user/login", json={"email": "reader@example.com", "password": "brand-new-pass"})
    assert login.status_code == 200


# —— Books & categories ——


def _category(client, admin, name="Fiction"):
    return client.post("/categories/", json={"name": name}, headers=admin["headers"]).json()


def _book(client, admin, category_id, title="Things Fall Apart"):
    payload = {"title": title, "author": "Chinua Achebe", "publisher": "Heinemann", "category_id": category_id}
    return client.post("/books/", json=payload, headers=admin["headers"])


def test_book_crud_with_category_name(client, admin):
    cat = _category(client, admin)
    created = _book(client, admin, cat["id"])
    assert created.status_code == 201
    book = created.json()
    assert book["category_name"] == "Fiction"

    assert client.get(f"/books/{book['id']}").json()["title"] == "Things Fall Apart"
    updated = client.put(f"/books/{book['id']}", json={"title": "Arrow of God"}, headers=admin["headers"]).json()
    assert updated["title"] == "Arrow of God" and updated["author"] == "Chinua Achebe"

    assert client.delete(f"/books/{book['id']}", headers=admin["headers"]).status_code == 204
    assert client.get(f"/books/{book['id']}").status_code == 404


def test_book_needs_an_existing_category(client, admin):
    assert _book(client, admin, "64b000000000000000000000").status_code == 400


def test_book_search_is_case_insensitive_and_literal(client, admin):
    cat = _category(client, admin)
    _book(client, admin, cat["id"], "Half of a Yellow Sun")
    _book(client, admin, cat["id"], "Purple Hibiscus")
    assert [b["title"] for b in client.get("/books/", params={"q": "yellow"}).json()] == ["Half of a Yellow Sun"]
    assert client.get("/books/", params={"q": ".*"}).json() == []  # treated as text, not a regex


def test_invalid_ids_return_400_not_500(client):
    assert client.get("/books/not-an-id").status_code == 400


def test_category_names_are_unique_case_insensitively(client, admin):
    _category(client, admin, "History")
    assert client.post("/categories/", json={"name": "history"}, headers=admin["headers"]).status_code == 409


def test_category_with_books_cannot_be_deleted(client, admin):
    cat = _category(client, admin)
    _book(client, admin, cat["id"])
    assert client.get("/categories/").json()[0]["book_count"] == 1
    assert client.delete(f"/categories/{cat['id']}", headers=admin["headers"]).status_code == 409


def test_videos_are_mounted_and_admin_only(client, admin):
    cat = _category(client, admin)
    video = {"title": "Intro", "url": "https://example.com/v.mp4", "category_id": cat["id"]}
    assert client.post("/videos/", json=video).status_code == 401
    assert client.post("/videos/", json=video, headers=admin["headers"]).status_code == 201
    assert len(client.get(f"/videos/category/{cat['id']}").json()) == 1
