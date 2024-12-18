from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.db.base_class import Base

class FoodAnalyze(Base):
    __tablename__ = "bloom_food_analyze"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("bloom_users.id"), nullable=False)
    
    # 图片信息
    file_path = Column(String, nullable=False)
    original_filename = Column(String)
    content_type = Column(String)
    
    # 食物列表
    foods = Column(JSON, nullable=False)  # [{"food": str, "count": float}]
    
    # 营养成分
    calories = Column(Float)  # 卡路里
    protein = Column(Float)   # 蛋白质(g)
    fat = Column(Float)       # 脂肪(g)
    carb = Column(Float)      # 碳水(g)
    
    # 微量元素
    dietary_fiber = Column(Float)  # 膳食纤维(g)
    vitamin_c = Column(Float)      # 维生素C(mg)
    vitamin_d = Column(Float)      # 维生素D(mcg)
    
    # 矿物质
    calcium = Column(Float)  # 钙(mg)
    iron = Column(Float)     # 铁(mg)
    zinc = Column(Float)     # 锌(mg)
    iodine = Column(Float)   # 碘(mcg)
    
    # 分析结果
    summary = Column(String)  # 总结
    advice = Column(String)   # 建议
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="food_analyses")

    def to_schema(self) -> "FoodAnalyze":
        from api.schemas.food import FoodAnalyze, FoodItem
        return FoodAnalyze(
            user_id=self.user_id,
            file_path=self.file_path,
            original_filename=self.original_filename,
            foods=[FoodItem(**food) for food in self.foods],
            nutrients={
                "macro": {
                    "calories": self.calories,
                    "protein": self.protein,
                    "fat": self.fat,
                    "carb": self.carb
                },
                "micro": {
                    "fa": self.dietary_fiber,
                    "vc": self.vitamin_c,
                    "vd": self.vitamin_d
                },
                "mineral": {
                    "calcium": self.calcium,
                    "iron": self.iron,
                    "zinc": self.zinc,
                    "iodine": self.iodine
                }
            },
            summary=self.summary,
            advice=self.advice,
            created_at=self.created_at
        )
