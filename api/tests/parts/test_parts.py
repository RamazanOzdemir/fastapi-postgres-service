from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient

from app.models.part_model import PartModel
from app.models.user_model import UserModel
from tests.utils import compare_uuids


def test_get_parts_returns_empty_list_when_no_parts_exist(client: TestClient):
    response = client.get("/parts")
    response_json = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_json["total"] == 0
    assert len(response_json["data"]) == 0


def test_get_parts_returns_pars_list(
    client: TestClient, mock_parts: dict[str, PartModel]
):
    expected_parts = list(mock_parts.values())
    response = client.get("/parts")
    response_json = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_json["total"] == len(expected_parts)
    assert len(response_json["data"]) == len(expected_parts)

    # Get the expected parts and map the received parts by ID for order-independent comparison
    received_parts_map = {item["id"]: item for item in response_json["data"]}

    for expected_part in expected_parts:
        expected_id_str = str(expected_part.id)

        # Ensure the part exists in the response
        assert expected_id_str in received_parts_map

        received_part = received_parts_map[expected_id_str]

        # Compare core fields
        assert received_part["name"] == expected_part.name
        assert received_part["description"] == expected_part.description

        # Compare UUID fields (ID, created_by, updated_by)
        compare_uuids(received_part, expected_part, "id")
        compare_uuids(received_part, expected_part, "created_by")
        compare_uuids(received_part, expected_part, "updated_by")


def test_get_part_by_id_returns_part_when_part_exists(
    client: TestClient, mock_parts: dict[str, PartModel]
):
    part = mock_parts["part_a"]

    response = client.get(f"/parts/{part.id}")
    response_json = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_json["name"] == part.name
    compare_uuids(response_json, part, "id")


def test_get_part_by_id_with_invalid_id_returns_400(client: TestClient):
    response = client.get("/parts/1234")
    response_json = response.json()

    # Returns 400 because path parameter is invalid
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response_json["title"] == "Invalid request"


def test_get_part_by_id_with_nonexistent_id_returns_404(client: TestClient):
    id = "00000000-0b1e-4c5f-a6b7-8d9e0f1a2b3c"
    response = client.get(f"parts/{id}")
    response_json = response.json()

    # Returns 404 because there no part by this ID
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_json["title"] == "Not found"


def test_create_new_part_returns_new_part(
    client: TestClient, current_user: UserModel, mock_crud_no_commit
):
    data = {"name": "New Part", "description": "Description"}

    response = client.post("/parts", json=data)
    response_json = response.json()

    # Returns new created part
    assert response.status_code == status.HTTP_200_OK
    assert response_json["name"] == data["name"]
    assert response_json["description"] == data["description"]

    compare_uuids({"id": response_json["created_by"]}, current_user, "id")
    compare_uuids({"id": response_json["updated_by"]}, current_user, "id")


def test_create_new_part_with_existing_name_returns_400(
    client: TestClient, mock_crud_no_commit
):
    data = {"name": "New Part", "description": "Description"}

    response = client.post("/parts", json=data)

    response_json = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_json["name"] == data["name"]

    response = client.post("/parts", json=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_new_part_without_description_returns_new_part(
    client: TestClient, mock_crud_no_commit
):
    data = {"name": "New Part", "description": None}

    response = client.post("/parts", json=data)

    response_json = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_json["name"] == data["name"]
    assert response_json["description"] is None


def test_update_existing_part_returns_updated_part(
    client: TestClient, mock_parts: dict[str, PartModel], mock_crud_no_commit
):
    part = mock_parts["part_a"]
    updated_data = {"name": "Updated Part A", "description": "Part A was updated"}

    response = client.put(f"/parts/{part.id}", json=updated_data)

    response_json = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_json["name"] == updated_data["name"]
    assert response_json["description"] == updated_data["description"]

    compare_uuids(response_json, part, "id")


def test_update_nonexistent_part_returns_404(client: TestClient, mock_crud_no_commit):
    part_id = uuid4()
    updated_data = {"name": "Updated Part A", "description": "Part A was updated"}

    response = client.put(f"/parts/{part_id}", json=updated_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_comment_for_part_returns_new_comment(
    client: TestClient,
    current_user: UserModel,
    mock_parts: dict[str, PartModel],
    mock_crud_no_commit,
):
    part = mock_parts["part_a"]
    data = {
        "content": "New Comment",
    }

    response = client.post(f"/parts/{part.id}/comments", json=data)
    response_json = response.json()

    # Returns new created part
    assert response.status_code == status.HTTP_200_OK
    assert response_json["content"] == data["content"]

    compare_uuids({"id": response_json["created_by"]}, current_user, "id")
    compare_uuids({"id": response_json["updated_by"]}, current_user, "id")
    compare_uuids(response_json["creator"], current_user, "id")


def test_create_comment_for_nonexistent_part_returns_404(
    client: TestClient,
    mock_crud_no_commit,
):
    part_id = uuid4()
    data = {
        "content": "New Comment",
    }

    response = client.post(f"/parts/{part_id}/comments", json=data)

    # Returns new created part
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_part_comments_returns_empty_list_when_no_comments_exist(
    client: TestClient, mock_parts: dict[str, PartModel]
):
    part = mock_parts["part_a"]

    response = client.get(f"/parts/{part.id}/comments")
    response_json = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(response_json) == 0


def test_get_part_comments_returns_comments_list(
    client: TestClient, mock_parts: dict[str, PartModel], mock_crud_no_commit
):
    part = mock_parts["part_a"]

    comment = {"content": "Test Comment"}
    # // Add new comment
    client.post(f"/parts/{part.id}/comments", json=comment)

    response = client.get(f"/parts/{part.id}/comments")
    response_json = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_json[0]["content"] == comment["content"]
    assert len(response_json) == 1


def test_get_part_comments_with_nonexistent_part_returns_404(client: TestClient):
    part_id = uuid4()

    response = client.get(f"/parts/{part_id}/comments")

    assert response.status_code == status.HTTP_404_NOT_FOUND
