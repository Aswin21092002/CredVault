def calculate_max_credit_recommendation(num_tradelines, total_tradelines_amount, sendesta_score):
    WEIGHT_PAYMENT_HISTORY= 0.2
    WEIGHT_TIME_IN_BUSINESS = 0.2
    WEIGHT_BUSINESS_TRADELINE_COUNT = 0.1
    WEIGHT_CREDIT_HISTORY = 0.2
    WEIGHT_REVENUE = 0.1
    WEIGHT_EMPLOYEES = 0.1

    sendesta_contribution = (sendesta_score['payment_history'] * WEIGHT_PAYMENT_HISTORY +
                             sendesta_score['time_in_business'] * WEIGHT_TIME_IN_BUSINESS +
                             sendesta_score['business_tradelines'] * WEIGHT_BUSINESS_TRADELINE_COUNT +
                             sendesta_score['credit_history'] * WEIGHT_CREDIT_HISTORY +
                             sendesta_score['revenue'] * WEIGHT_REVENUE +
                             sendesta_score['employees'] * WEIGHT_EMPLOYEES)

    if num_tradelines >= 5 and total_tradelines_amount >= 100000 and sendesta_contribution >= 70:
        return "Maximum credit recommendation"
    elif num_tradelines >= 3 and total_tradelines_amount >= 50000 and sendesta_contribution >= 50:
        return "High credit recommendation"
    elif num_tradelines >= 1 and total_tradelines_amount >= 10000 and sendesta_contribution >= 30:
        return "Moderate credit recommendation"
    else:
        return "Low credit recommendation or decline"