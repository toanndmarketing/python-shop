from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base

class AdminActivityLog(Base):
    __tablename__ = "admin_activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    admin_username = Column(String, index=True) # Hoặc user_id nếu bạn có bảng admin users riêng
    action = Column(String) # Ví dụ: "Thêm sản phẩm", "Cập nhật sản phẩm", "Đăng nhập"
    target_type = Column(String, nullable=True) # Ví dụ: "Product", "Order"
    target_id = Column(Integer, nullable=True)
    details = Column(String, nullable=True) # Ví dụ: "Sản phẩm ID: 123, Tên: Áo Thun"

    def __repr__(self):
        return f"<AdminActivityLog(id={self.id}, admin='{self.admin_username}', action='{self.action}')>" 