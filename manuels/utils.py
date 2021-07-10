def validate_isbn(isbn):
    _sum = 0
    if len(isbn) == 10:
        for i, digit in enumerate(isbn):
            if digit == "X":
                digit = 10
            else:
                digit = int(digit)
            _sum += digit * (i + 1)

        return _sum % 11 == 0

    elif len(isbn) == 13:
        for i, digit in enumerate(isbn):
            weight = 3 if i % 2 == 1 else 1
            digit = int(digit)
            _sum += digit * weight

        return _sum % 10 == 0

    return False
