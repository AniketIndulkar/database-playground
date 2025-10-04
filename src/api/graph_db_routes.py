from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph_db.graph_client import GraphDBClient

router = APIRouter(prefix="/graph-db", tags=["Graph Database"])
graph_db = GraphDBClient()

class UserInput(BaseModel):
    user_id: str
    name: str
    age: int

class FriendshipInput(BaseModel):
    user1_id: str
    user2_id: str

@router.post("/create-user")
def create_user(user: UserInput):
    """Create a user node"""
    try:
        graph_db.create_user(user.user_id, user.name, user.age)
        return {"success": True, "user_id": user.user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-friendship")
def create_friendship(friendship: FriendshipInput):
    """Create friendship between two users"""
    try:
        graph_db.create_friendship(friendship.user1_id, friendship.user2_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/friends/{user_id}")
def get_friends(user_id: str):
    """Get direct friends of a user"""
    try:
        friends = graph_db.find_friends(user_id)
        return {"friends": friends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/friends-of-friends/{user_id}")
def get_friends_of_friends(user_id: str):
    """Get friends of friends"""
    try:
        fofs = graph_db.find_friends_of_friends(user_id)
        return {"friends_of_friends": fofs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear")
def clear_database():
    """Clear all graph data"""
    try:
        graph_db.clear_database()
        return {"success": True, "message": "Database cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))