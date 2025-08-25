from core.crud import CRUDBase
from models.role import Permission
from schemas.rbac import PermissionCreate, PermissionUpdate


class PermissionController(CRUDBase[Permission, PermissionCreate, PermissionUpdate]):
    def __init__(self):
        super().__init__(model=Permission)


permission_controller = PermissionController()
