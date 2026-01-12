from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient

from app.models.comment_model import CommentModel
from app.models.part_model import PartModel
from app.models.user_model import UserModel
from tests.utils import compare_uuids


def test_get_comments_returns_empty_list_when_no_comments_exist(client: TestClient):
    response = client.get("/comments")
    response_json = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_json["total"] == 0
    assert len(response_json["data"]) == 0


def test_get_comments_returns_comment_list(
    client: TestClient, mock_comment: CommentModel
):
    response = client.get("/comments")
    response_json = response.json()
    data = response_json["data"]

    assert response.status_code == status.HTTP_200_OK
    assert response_json["total"] == 1
    assert len(response_json["data"]) == 1

    assert data[0]["content"] == mock_comment.content

    compare_uuids(data[0], mock_comment, "part_id")


def test_create_comment_with_valid_data_returns_created_comment(
    client: TestClient,
    current_user: UserModel,
    mock_parts: dict[str, PartModel],
    mock_crud_no_commit,
):
    part_a = mock_parts["part_a"]
    data = {"content": "New Comment", "part_id": str(part_a.id)}

    response = client.post("/comments", json=data)
    response_json = response.json()

    # Returns new created comment
    assert response.status_code == status.HTTP_200_OK
    assert response_json["content"] == data["content"]

    compare_uuids({"id": response_json["part_id"]}, part_a, "id")
    compare_uuids({"id": response_json["created_by"]}, current_user, "id")
    compare_uuids({"id": response_json["updated_by"]}, current_user, "id")


def test_create_comment_without_content_returns_400(
    client: TestClient, mock_parts: dict[str, PartModel], mock_crud_no_commit
):
    part_a = mock_parts["part_a"]
    data = {"content": None, "part_id": str(part_a.id)}

    response = client.post("/comments", json=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_comment_without_part_id_returns_400(
    client: TestClient, mock_crud_no_commit
):
    data = {"content": "New Comment", "part_id": None}

    response = client.post("/comments", json=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_comment_with_nonexistent_part_returns_404(
    client: TestClient, mock_crud_no_commit
):
    part_id = uuid4()
    data = {"content": "New Comment", "part_id": str(part_id)}

    response = client.post("/comments", json=data)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_exist_comment_return_updated_part(
    client: TestClient, mock_comment: CommentModel, mock_crud_no_commit
):
    updated_data = {"content": "Updated Comment"}

    response = client.put(f"/comments/{mock_comment.id}", json=updated_data)

    response_json = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_json["content"] == updated_data["content"]

    compare_uuids(response_json, mock_comment, "id")


def test_update_nonexistent_comment_returns_404(
    client: TestClient, mock_comment: CommentModel, mock_crud_no_commit
):
    comment_id = uuid4()
    updated_data = {"content": "Updated Comment"}

    response = client.put(f"/comments/{comment_id}", json=updated_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
