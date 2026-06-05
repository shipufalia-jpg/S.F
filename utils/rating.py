def get_avg_rating(doctor):

    ratings = doctor.ratings

    if not ratings:
        return 0

    total = sum(r.rating for r in ratings)

    return round(total / len(ratings), 1)
