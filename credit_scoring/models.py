from django.db import models

class Business(models.Model):
    name = models.CharField(max_length=255)
    company_age = models.FloatField()
    num_employees = models.FloatField()
    industry_risk = models.FloatField()
    profit_loss_ratio = models.FloatField()
    on_time_payments = models.FloatField()
    sendesta_score = models.FloatField(null = True, blank=True)
    
    def save(self , *args, **kwargs):
        #Normalize values(assuming hypothetical min and max values)
        from .scoring import calculate_credit_score
        # normalized_age = normalize_value(self.company_age, 0, 50)
        # normalized_employees = normalize_value(self.num_employees, 0 , 500)
        # normalized_industry_risk = normalize_value(self.industry_risk, 0, 1)
        # normalized_profit_loss = normalize_value(self.profit_loss_ratio, -1, 1)
        # normalized_on_time_payments = normalize_value(self.on_time_payments, 0, 1)
        
        #calculate sendesta score
        self.sendesta_score = calculate_credit_score(
            self.company_age, 
            self.num_employees,
            self.industry_risk,
            self.profit_loss_ratio,
            self.on_time_payments
            # normalized_age, normalized_employees, normalized_industry_risk,
            # normalized_profit_loss, normalized_on_time_payments
        )
        super(Business, self).save(*args, **kwargs)
        
        
    
