
def micronutrient_guideline():
    """ Return the guideline for the micronutrient module """
    guideline = """
        Should intake Folic Acid 60 mcg/day, Vitamin C 85 mg/day, Vitamin D 600 IU/day, Calcium 1000 mg/day, Iron 27 mg/day, Zinc 11 mg/day, Iodine 220 mcg/day"""
    return guideline


def macronutrient_guideline(calories: int, trimester: int):
    """ Return the guideline for the macronutrient module """
    protein = 46 if trimester <= 12 else 71
    guideline = f"""
        Should intake {calories} kcal/day, {protein} g protein/day, 70 g fat/day, 150 to 175 g carb/day"""
    return guideline
        
        
def wz_guideline():
    """ Return the guideline for the nutrition module """
    guideline = """
        1. 食谱建议为早餐、早加餐、午餐、下午茶、晚餐、晚加餐，每天6餐 \n
        2. 每日食谱应该涵盖五大类食物：谷薯类、蔬菜类、水果类、奶类、肉蛋类。 \n
        3. 1至2杯奶制品，250毫升/杯，大约是马克杯、中型玻璃杯几乎倒满、大号玻璃杯（如宜家玻璃杯）的四分之三（离敞口处一小拇指的距离）。早餐、早加餐、下午茶和晚加餐可以安排 \n
        4. 早、中、晚餐一份100g主食，大约是一碗米饭、一大碗面条、两碗粥、一个馒头、一个面包、一个玉米饼、一个玉米粥、一个玉米面饼、一个玉米馒头、一个玉米面包等。红薯、土豆和山药也计算入主食。如土豆牛肉中的土豆，应计算为主食 \n
        5. 主食当中需包括粗粮，每天食用100g，大约是一碗燕麦片、一碗玉米片、一个玉米、红薯或土豆等。 \n
        6. 500g，1斤绿色叶菜，分成午餐和晚餐进食 \n
        7. 早加餐和下午茶可建议食用水果200g，大约是一个普通苹果或者梨大小 \n
        8. 食用一个鸡蛋，建议早餐、早加餐食用 \n
        9. 早餐、早加餐、下午茶、晚加餐可选择一餐食用坚果，每次食用30g \n
        10. 午餐、晚餐可建议食用肉类，每次食用100g（2两），大约为巴掌大的鱼、两块排骨或一个鸡腿的总量。 \n
        11. 午餐和晚餐可选择一餐食用豆制品，每次食用100g，大约是一个拳头 \n
        12. 每周至食用2-3次海鲜，每次食用2两，大约是巴掌大的鱼的量 \n
        13. 推荐食用肝脏，每周食用一次，每次食用50g
    """
    return guideline


def salt_oil_guideline():
    return """
        1. 每天食用适量的食用油，每次食用10g，大约是一个汤匙，总量不超过20g，建议使用植物油
        2. 每天食用适量的盐，每次食用3g，大约是一个小勺，总量不超过6g"""
        
        
def cn_whole_grains_guideline():
    return """
        粗粮有玉米、小米、红米、黑米、紫米、高粱、大麦、燕麦、荞麦、黄豆、绿豆、红豆、黑豆、青豆、蚕豆、豌豆、芸豆、山药、红薯、土豆等。"""
        
        
def cn_example():
    return """
        Should intake 1850kcal/day, 71g protein/day, 70g fat/day, 150 to 175g carb/day
        {
            "meals": ["早餐1个花卷，1杯低脂奶，1个煮鸡蛋", "早加餐1片全麦面包，1杯豆浆", "午餐1碗杂豆饭，辣子鸡丁，素炒油麦菜", "下午茶2块饼干，1个橘子", "晚餐1个花卷，虾仁白菜煮豆腐，麻酱拌豌豆", "晚加餐1杯牛奶，2勺燕麦"],
        }"""