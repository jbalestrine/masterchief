"""Room management for WebSocket channels."""
import logging
from typing import Dict, Set
from flask_socketio import join_room as socketio_join, leave_room as socketio_leave

logger = logging.getLogger(__name__)


class RoomManager:
    """Manages WebSocket rooms and subscriptions."""
    
    def __init__(self):
        self.rooms: Dict[str, Set[str]] = {}  # room_name -> set of client_ids
        self.client_rooms: Dict[str, Set[str]] = {}  # client_id -> set of room_names
    
    def join(self, client_id: str, room: str):
        """Add client to a room."""
        if room not in self.rooms:
            self.rooms[room] = set()
        
        self.rooms[room].add(client_id)
        
        if client_id not in self.client_rooms:
            self.client_rooms[client_id] = set()
        
        self.client_rooms[client_id].add(room)
        
        socketio_join(room)
        logger.info(f"Client {client_id} joined room {room}")
    
    def leave(self, client_id: str, room: str):
        """Remove client from a room."""
        if room in self.rooms:
            self.rooms[room].discard(client_id)
            if not self.rooms[room]:
                del self.rooms[room]
        
        if client_id in self.client_rooms:
            self.client_rooms[client_id].discard(room)
            if not self.client_rooms[client_id]:
                del self.client_rooms[client_id]
        
        socketio_leave(room)
        logger.info(f"Client {client_id} left room {room}")
    
    def leave_all(self, client_id: str):
        """Remove client from all rooms."""
        if client_id in self.client_rooms:
            rooms = list(self.client_rooms[client_id])
            for room in rooms:
                self.leave(client_id, room)
    
    def get_room_clients(self, room: str) -> Set[str]:
        """Get all clients in a room."""
        return self.rooms.get(room, set()).copy()
    
    def get_client_rooms(self, client_id: str) -> Set[str]:
        """Get all rooms a client is in."""
        return self.client_rooms.get(client_id, set()).copy()
    
    def get_room_count(self, room: str) -> int:
        """Get number of clients in a room."""
        return len(self.rooms.get(room, set()))
    
    def get_stats(self) -> Dict:
        """Get room statistics."""
        return {
            "total_rooms": len(self.rooms),
            "total_clients": len(self.client_rooms),
            "rooms": {
                room: len(clients)
                for room, clients in self.rooms.items()
            }
        }


# Global room manager instance
_room_manager = RoomManager()


def get_room_manager() -> RoomManager:
    """Get the global room manager instance."""
    return _room_manager
