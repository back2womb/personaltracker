from sqlmodel import Session
from app.models.reward import Reward

def issue_reward(session: Session, task_id: int, streak_count: int):
    if streak_count in (3, 7, 30):
        reward = Reward(
            task_id=task_id,
            reward_type="streak_bonus",
            value=streak_count,
        )
        session.add(reward)
        session.commit()
        return reward

    return None
