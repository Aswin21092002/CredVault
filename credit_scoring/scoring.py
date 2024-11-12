def normalize_value(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)

def calculate_credit_score(company_age, num_employees, industry_risk, profit_loss_ratio, on_time_payments):
    # define weights
    weights ={'company_age': 0.2,
            'num_employees': 0.1,
            'industry_risk': 0.3,
            'profit_loss_ratio': 0.2,
            'on_time_payments': 0.2,}
    
    # normalize inputs (assuming inputs are already normalized to a 0-1 scale)
    inputs = {
         'company_age': company_age,
        'num_employees': num_employees,
        'industry_risk': industry_risk,
        'profit_loss_ratio': profit_loss_ratio,
        'on_time_payments': on_time_payments,
    }
    
     # Calculate weighted sum
    score = sum(weights[key] * inputs[key] for key in weights)

    # Scale score to 0-100
    score_scaled = (score - min(weights.values())) / (max(weights.values()) - min(weights.values())) * 100

    # Return the final score (rounded to two decimal places)
    return round(score_scaled, 2)