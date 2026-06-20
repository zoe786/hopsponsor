from database import add_sponsor, get_sponsors

add_sponsor(
    "Test User",
    "Test Company",
    "123456",
    "test@test.com",
    "Testing"
)

print(get_sponsors())