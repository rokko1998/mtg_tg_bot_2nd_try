import redis

# ������������� ������� Redis
redis_client = redis.Redis(
    host='localhost',  # ����� Redis-�������
    port=6379,         # ���� Redis-�������
    db=0,              # ������������ ���� ������ Redis (�� ���������)
    decode_responses=True  # �������������� ������������� ������� �� ������ � ������
)