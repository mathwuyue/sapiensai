def cal_calories_met(weight: float, duration: float, met: float) -> float:
    met * duration / 60 * 1.05 * weight


def cal_max_bpm(age: int) -> float:
    if not age:
        age = 30
    return 208 - 0.7 * age


def cal_exercise_bpm_range(age: int) -> Tuple[int, int]:
    return (int(0.6 * (220 - age)), int(0.89 * (220 - age)))


async def get_exercise_summary(
    user_id: str,
    exercise: str,
    intensity: str,
    duration: float,
    bpm: float,
    start_time,
    remark: str,
) -> Tuple[EmmaComment, float]:
    """
    TODO: How to get the meal time?
    """
    # get from db
    with db.atomic():
        exercise_data = ExerciseDatabase.get_or_none(
            (ExerciseDatabase.exercise == exercise)
            & (ExerciseDatabase.type == intensity)
        )
        # Get exercise records
        previous_records = (
            ExerciseData.select()
            .where(
                (ExerciseData.user_id == user_id)
                & (
                    ExerciseData.created_at.between(
                        datetime.now() - timedelta(days=7), datetime.now()
                    )
                )
            )
            .order_by(ExerciseData.created_at.desc())
        )
    # calcualte caories. Check ExerciseDatabase for the formula
    if not exercise_data:
        met = 0.0  # Default value
    else:
        met = exercise_data.calories
    # get user info
    user_data_response = await httpx.AsyncClient().get(
        f"http://localhost:8000/api/v1/profile/user/{user_id}",
        headers={"Authorization": f"Bearer {BLOOM_KEY}"},
    )
    user_data_response.raise_for_status()
    # user_data = user_data_response.json()
    user_data = UserBasicInfo(**user_data_response.json())
    # print(user_data)
    # Calculate calories based on duration and base calories from database
    print("met: ", met)
    print("weight: ", user_data.cur_weight)
    calories = cal_calories_met(
        float(user_data.cur_weight), float(duration), float(met)
    )
    conditions = f"{user_data.condition} (Level {user_data.cond_level})"
    new_record = {
        "exercise": exercise,
        "intensity": intensity,
        "duration": duration,
        "calories": calories,
        "bpm": bpm,
        "start_time": start_time,
        "remark": remark,
    }
    # format records
    exercise_records = format_exercise_records(previous_records)
    # calculate exercise bpm range
    min_bpm, max_bpm = cal_exercise_bpm_range(user_data.age)
    print({"min": min_bpm, "max": max_bpm})
    # prompt
    prompt = emma_exercise_summary(
        new_record,
        exercise_records,
        user_data.cur_weight,
        user_data.ga,
        conditions,
        user_data.complications,
        {"min": min_bpm, "max": max_bpm},
    )
    print(prompt)
    llm_json = extract_json_from_text(await llm(prompt, is_text=True))
    if not calories:
        calories = llm_json["calories"]
    return EmmaComment(**llm_json), calories
